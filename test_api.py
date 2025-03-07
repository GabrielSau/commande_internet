import unittest, json
from unittest.mock import patch
from inf349 import app
from datetime import datetime


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # test récupération des informations des produits 
    @patch("inf349.Product.select")
    def test_get_products(self, mock_select):
        mock_select.return_value.dicts.return_value = [
            {"id": 1, "name": "produit", "description": "unProduit", "price": 1000, "in_stock": True, "image": "0.jpg", "weight": 400}
        ]
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("products", data)
        self.assertEqual(len(data["products"]), 1)

    # test création d'une commande
    @patch("inf349.Product.get")
    @patch("inf349.Order.create") 
    def test_create_order(self, mock_create, mock_get):
        mock_get.return_value = type("Product", (), {"id": 1, "price": 1000, "in_stock": True, "weight": 400})()
        mock_create.return_value = type("Order", (), {"id": 1})()

        response = self.app.post('/order', json={
            "product": {"id": 1, "quantity": 2},
            "email": "test@gmail.com",
            "shipping_information": {
                "country": "Canada",
                "city": "Quebec",
                "address": "Rue du test",
                "postal_code": "G1V 0A6",
                "province": "QC"
            }
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn("Location", json.loads(response.data))

    # test de produit hors stock
    @patch("inf349.Product.get")
    def test_create_order_out_of_stock(self, mock_get):
        mock_get.return_value = type("Product", (), {"id": 1, "price": 1000, "in_stock": False, "weight": 400})()
        response = self.app.post('/order', json={
            "product": {"id": 1, "quantity": 1}
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("out-of-inventory", json.loads(response.data)["errors"]["product"]["code"])

    # test de la création de commande avec des mauvaises infos
    @patch("inf349.Product.get")
    def test_create_order_invalid_data(self, mock_get):
        mock_get.return_value = type("Product", (), {"id": 1, "price": 1000, "in_stock": True, "weight": 400})()
        
        # manque des informations dans la requête
        response = self.app.post('/order', json={})
        self.assertEqual(response.status_code, 422)
        
        # Pas de id/quantité 
        response = self.app.post('/order', json={"product": {}})
        self.assertEqual(response.status_code, 422)

        # quantité nulle ou négative
        response = self.app.post('/order', json={"product": {"id": 1, "quantity": 0}})
        self.assertEqual(response.status_code, 422)

        response = self.app.post('/order', json={"product": {"id": 1, "quantity": -1}})
        self.assertEqual(response.status_code, 422)


    # test récupération des détails d'une commande
    @patch("inf349.Order.get_or_none")
    def test_get_order(self, mock_get):
        product_mock = type("Product", (), {"id": 1})()
        order_mock = type("Order", (), {
            "id": 1,
            "email": "test@example.com",
            "total_price": 1000,
            "total_price_tax": 1150,
            "shipping_price": 5,
            "paid": False,
            "product": product_mock,
            "product_quantity": 1,
            "created_at": datetime.now(),
            "shipping_information_country": "Canada",
            "shipping_information_city": "Quebec",
            "shipping_information_address": "123 Test St",
            "shipping_information_postal_code": "G1V 0A6",
            "shipping_information_province": "QC"
        })()

        mock_get.return_value = order_mock

        response = self.app.get('/order/1')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("order", data)
        self.assertEqual(data["order"]["id"], 1)
        self.assertEqual(data["order"]["email"], "test@example.com")

    # test de la route GET /order/<id> pour une commande inexistante
    @patch("inf349.Order.get_or_none")
    def test_get_order_not_found(self, mock_get):
        mock_get.return_value = None
        response = self.app.get('/order/1000')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("order", data["errors"])
        self.assertEqual(data["errors"]["order"]["code"], "not-found")

    




    """
    Nous n'avons pas pu tester le PUT avec la credit card car le serveur nous renvoyé un timeout à chaque fois comme ci le serveur n'était pas ouvert.
    Donc nous n'avons pas pu vérifier que cela fonctionne
    """
        
        

if __name__ == '__main__':
    unittest.main()
