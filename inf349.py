from flask import Flask, jsonify, request
from peewee import Model, SqliteDatabase, IntegerField, TextField, BooleanField, FloatField, ForeignKeyField, DateTimeField
import requests
from datetime import datetime

# Initialisation de l'application Flask
app = Flask(__name__)

# Connexion à la base de données SQLite
db = SqliteDatabase('shop.db')


### Modèle pour les Produits ###
class Product(Model):
    id = IntegerField(primary_key=True)
    name = TextField()
    description = TextField()
    price = FloatField() 
    in_stock = BooleanField()  
    image = TextField() 
    weight = IntegerField()  

    class Meta:
        database = db


### Modèle pour les Commandes ###
class Order(Model):
    shipping_information_country = TextField(null=True)
    shipping_information_city = TextField(null=True)
    shipping_information_address = TextField(null=True)
    shipping_information_postal_code = TextField(null=True)
    shipping_information_province = TextField(null=True)
    email = TextField(null=True)
    total_price = FloatField()
    total_price_tax = FloatField(null=True)
    paid = BooleanField(default=False)
    shipping_price = IntegerField() 
    product = ForeignKeyField(Product, backref='orders')
    product_quantity = IntegerField()
    credit_card_name = TextField(null=True)
    credit_card_first_digits = TextField(null=True)
    credit_card_last_digits = TextField(null=True)
    credit_card_expiration_year = IntegerField(null=True)
    credit_card_expiration_month = IntegerField(null=True)
    transaction_id = TextField(null=True)  
    transaction_success = BooleanField(default=False) 
    transaction_amount_charged = IntegerField(null=True)  
    created_at = DateTimeField(default=datetime.now)  

    class Meta:
        database = db


### Initialisation de la Base de Données ###
@app.cli.command("init-db")
def init_db():
    """
    Crée la base de données et télécharge les produits au démarrage
    """
    db.connect()
    db.create_tables([Product, Order], safe=True)
    fetch_and_store_products()


### Fonction pour Récupérer et Stocker les Produits ###
def fetch_and_store_products():
    url = "http://dimensweb.uqac.ca/~jgnault/shops/products/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        Product.delete().execute()  # On vide la table avant de recharger
        for item in data.get("products", []):
            Product.create(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                price=item["price"],
                in_stock=item["in_stock"],
                image=item["image"],
                weight=item["weight"]
            )
        print("Produits récupérés avec succès")
        print(f"Nombre de produits : {len(data['products'])}")
    else:
        print("Erreur lors de la récupération des produits")


### Route GET / pour afficher les Produits ###
@app.route('/', methods=['GET'])
def get_products():
    """
    Affiche tous les produits stockés en base de données
    """
    products = list(Product.select().dicts())
    return jsonify({"products": products}), 200



### Route POST /order pour Créer une Commande ###
@app.route('/order', methods=['POST'])
def create_order():
    data = request.json

    if "product" not in data or "id" not in data["product"] or "quantity" not in data["product"]:
        return jsonify({"errors" : {"product": {"code": "missing-fields","name": "La création d'une commande nécessite un produit"}}}), 422

    product_id = data["product"]["id"]
    quantity = data["product"]["quantity"]
    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except ValueError:
        return jsonify({"errors" : {"product": {"code": "error","name": "Les champs doivent être de type numérique"}}}), 422

    if quantity <= 0:
        return jsonify({"errors": {"product": {"code": "invalid-quantity", "name": "La quantité doit être supérieure à zéro"}}}), 422

    
    try:
        product = Product.get(Product.id == product_id)
    except Product.DoesNotExist:
        return jsonify({"errors" : { "product": {"code": "out-of-inventory","name": "Le produit demandé n'est pas en inventaire"}}}), 404

    if not product.in_stock:
        return jsonify({"errors" : { "product": {"code": "out-of-inventory","name": "Le produit demandé n'est pas en inventaire"}}}), 422

    total_price = product.price * quantity
    shipping_price = calculer_prix(product.weight, quantity)

    order = Order.create(
        total_price=total_price,
        shipping_price=shipping_price,
        product=product.id,
        product_quantity=quantity,
    )

    return jsonify({"Location": f"/order/{order.id}"}), 302


### GET d'une commande par ID ###
@app.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Route pour afficher une commande par son ID
    """
    order = Order.get_or_none(Order.id == order_id)

    if not order:
        return jsonify({"errors": {"order": {"code": "not-found", "name": "Commande non trouvée"}}}), 404

    return jsonify(get_order_json(order)), 200

### Fonction pour Calculer le Prix de Livraison ###
def calculer_prix(weight, quantity):
    total_weight = weight * quantity
    if total_weight <= 500:
        return 5
    elif total_weight <= 2000:
        return 10
    else:
        return 25


### Fonction pour Calculer la Taxe ###
def calculer_taxe(province, total_price):
    taxes = {
        "QC": 0.15,
        "ON": 0.13,
        "AB": 0.05,
        "BC": 0.12,
        "NS": 0.14
    }
    return total_price * (1 + taxes.get(province, 0.15))

def get_order_json(order):
    product = {
        "id": order.product.id,
        "quantity": order.product_quantity,
    }
    return {
        "order": {
            "id": order.id,
            "email": order.email,
            "total_price": order.total_price,
            "total_price_tax": order.total_price_tax,
            "shipping_price": order.shipping_price,
            "paid": order.paid,
            "product": product,
            "shipping_information": {"country": order.shipping_information_country, "address": order.shipping_information_address, "postal_code": order.shipping_information_postal_code, "city": order.shipping_information_city, "province": order.shipping_information_province} if order.shipping_information_country else {},
            "credit_card": {
                 "name" : order.credit_card_name,
                 "first_digits" : order.credit_card_first_digits,
                 "last_digits": order.credit_card_last_digits,
                 "expiration_year" : order.credit_card_expiration_year,
                 "expiration_month" : order.credit_card_expiration_month,
                } if order.paid else {},
            "transaction": {
                "id": order.transaction_id,
                "success": order.transaction_success,
                "amount_charged": order.transaction_amount_charged
            } if order.paid else {},
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

@app.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    order = Order.get_or_none(Order.id == order_id)

    # Vérification de l'existence de la commande
    if not order:
        return jsonify({"errors": {"order": {"code": "not-found", "name": "Commande non trouvée"}}}), 404

    # Vérification de la dissociation du paiement et de la modification de la commande
    if "credit_card" in data and ("order" in data or "email"  in data):
        return jsonify({"errors": {"order": {"code": "error",
                                             "name": "Impossible d'effectuer le paiement et de modifier les informations de la commande en même temps"}}}), 422

    # Paiement de la commande
    if "credit_card" in data:

        if not order.email or not order.shipping_information_country or not order.shipping_information_address or not order.shipping_information_city or not order.shipping_information_province:
            return jsonify({"errors": {"order": {"code": "error", "name": "Impossible d'effectuer le paiement, données d'expedition ou email manquant"}}})

        if order.paid:
            return jsonify({"errors": {"order": {"code": "already-paid",
                                                 "name": "La commande a déjà été payée"}}}), 422

        # Préparation des données pour l'API de paiement
        url = "http://dimensweb.uqac.ca/~jgnault/shops/pay/"
        payload = {
            "credit_card": data["credit_card"],
            "amount_charged": order.total_price_tax + order.shipping_price
        }

        headers = {
            "Host": "dimprojetu.uqac.ca",
            "Content-Type": "application/json"
        }

        print(f"Requête envoyée à {url}")
        print(f"Payload : {payload}")

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            # Mise à jour de la BD
            transaction = response.json()["transaction"]
            credit_card = transaction["credit_card"]
            order.paid = True
            order.credit_card_name = credit_card["name"]
            order.credit_first_digits = credit_card["first_digits"]
            order.credit_card_last_digits = credit_card["last_digits"]
            order.credit_card_expiration_year = credit_card["expiration_year"]
            order.credit_card_expiration_month = credit_card["expiration_month"]
            order.transaction_id = transaction["id"]
            order.transaction_success = transaction["success"]
            order.transaction_amount_charged = transaction["amount_charged"]
            order.save()

            return jsonify(get_order_json(order), 200)

        # Gestion des erreurs de la carte
        try:
            return jsonify(response.json()), 422
        except requests.exceptions.JSONDecodeError:
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            return jsonify({"errors": {
                "credit_card": {"code": "invalid-response",
                                "name": "Service de paiement distant indisponible"}}}), 422


    # Vérification des champs obligatoires pour modifier la commande
    if "order" not in data or "email" not in data["order"] or "shipping_information" not in data["order"]:
        return jsonify({"errors": {"order": {"code": "missing-fields", "name": "Il manque un ou plusieurs champs qui sont obligatoires"}}}), 422

    shipping_info = data["order"]["shipping_information"]
    required_fields = ["country", "address", "postal_code", "city", "province"]
    for field in required_fields:
        if field not in shipping_info:
            return jsonify({"errors": {"order": {"code": "missing-fields", "name": f"Champ manquant: {field}"}}}), 422

    # Empêcher la modification des champs interdits
    if "total_price" in data["order"] or "total_price_tax" in data["order"] or "transaction" in data["order"] or "paid" in data["order"] or "product" in data["order"] or "shipping_price" in data["order"]:
        return jsonify({"errors": {"order": {"code": "field-not-modifiable", "name": "Certains champs ne peuvent pas être modifiés"}}}), 422

    # Mise à jour des informations de la commande
    order.email = data["order"]["email"]
    order.shipping_information_country = data["order"]["shipping_information"]["country"]
    order.shipping_information_address = data["order"]["shipping_information"]["address"]
    order.shipping_information_postal_code = data["order"]["shipping_information"]["postal_code"]
    order.shipping_information_city = data["order"]["shipping_information"]["city"]
    order.shipping_information_province = data["order"]["shipping_information"]["province"]
    order.total_price_tax = calculer_taxe(shipping_info["province"], order.total_price)
    order.save()

    return jsonify(get_order_json(order)), 200

### Lancer l'application ###
if __name__ == '__main__':
    app.run(debug=True)
