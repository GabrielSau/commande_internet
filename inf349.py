from flask import Flask, jsonify, request
from peewee import Model, SqliteDatabase, IntegerField, TextField, BooleanField, FloatField
import requests

app = Flask(__name__)

# Connexion à la base de données SQLite
db = SqliteDatabase('shop.db')

# Modèle de la base de données
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

# Initialisation de la base de données

@app.cli.command("init-db")
def init_db():
    db.connect()
    db.create_tables([Product], safe=True)
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





@app.route('/', methods=['GET'])
def get_products():
    """
    Route pour récupérer les produits stockés en base de données
    """
    products = list(Product.select().dicts())
    return jsonify({"products": products}), 200


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
