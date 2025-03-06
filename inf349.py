from flask import Flask, jsonify, request
from peewee import Model, SqliteDatabase, IntegerField, TextField, BooleanField, FloatField, ForeignKeyField, DateTimeField
import requests
from datetime import datetime

app = Flask(__name__)

# Connexion à la base de données SQLite
db = SqliteDatabase('shop.db')

# Modèle de la base de données pour les produits
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

# Modèle de la base de données pour les commandes
class Order(Model):
    shipping_information = TextField()
    email = TextField()
    total_price = IntegerField()
    total_price_tax = IntegerField()
    paid = BooleanField(default=False)
    shipping_price = IntegerField()
    product = ForeignKeyField(Product, backref='orders')
    transaction_id = TextField(null=True)  
    transaction_success = BooleanField(default=False)
    transaction_amount_charged = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db


# Initialisation de la base de données
@app.cli.command("init-db")
def init_db():
    db.connect()
    db.create_tables([Product, Order], safe=True)
    fetch_and_store_products()

# Récupération des produits depuis l'API et stockage en base de données
def fetch_and_store_products():
    url = "http://dimensweb.uqac.ca/~jgnault/shops/products/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        Product.delete().execute()  # Nettoyage avant d'insérer de nouveaux produits
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
        print("Produits récupérés et enregistrés avec succès.")
        print(f"Nombre de produits récupérés : {len(data.get('products', []))}")
    else:
        print("Échec de la récupération des produits.")




# Route pour récupérer et affier les produits
@app.route('/', methods=['GET'])
def get_products():
    """
    Route pour récupérer les produits stockés en base de données
    """
    products = list(Product.select().dicts())
    return jsonify({"products": products}), 200

# Route pour l'ajout de commandes avec la class order
@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    
    required_fields = ['shipping_information', 'email', 'total_price', 'total_price_tax', 'shipping_price', 'product']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 422

    try:
        product = Product.get(Product.id == data['product']['id'])
    except Product.DoesNotExist:
        return jsonify({"error": "Product not found"}), 404
    
    order = Order.create(
        shipping_information=data['shipping_information'],
        email=data['email'],
        total_price=data['total_price'],
        total_price_tax=data['total_price_tax'],
        shipping_price=data['shipping_price'],
        product=product
    )
    
    return jsonify({"order_id": order.id}), 201

#C'est juste pour vérifier que c'est en bd
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = list(Order.select().dicts())
    return jsonify({"orders": orders}), 200



if __name__ == '__main__':
    app.run(debug=True)
