import unittest, json
from unittest.mock import patch
from inf349 import app

class ApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # test récupération des informations des produits 
    @patch("inf349.Product.select")
    def test_get_products(self, mock_select):
        mock_select.return_value.dicts.return_value = [
            {"id": 1, "name": "produits", "description": "unProduit", "price": 1000, "in_stock": True, "image": "0.jpg", "weight": 400}
        ]
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("products", data)
        self.assertEqual(len(data["products"]), 1)

    # test création d'une commande
    @patch("inf349.Product.get")
    def test_create_order(self, mock_get):
        mock_get.return_value = type("Product", (), {"id": 1, "price": 1000, "in_stock": True, "weight": 400})()
        response = self.app.post('/order', json={
            "product": {"id": 1, "quantity": 2},
            "credit_card": "", 
            "email": "test@example.com",
            "shipping_information": "rue du test"
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
        self.assertIn("Produit hors stock", json.loads(response.data)["error"])

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
        mock_get.return_value = None
        response = self.app.get('/order/1')
        self.assertEqual(response.status_code, 404)

    # Test de la route GET /order/<id> pour une commande inexistante
    @patch("inf349.Order.get_or_none")
    def test_get_order_not_found(self, mock_get):
        mock_get.return_value = None
        
        response = self.app.get('/order/1000')
        self.assertEqual(response.status_code, 404)
        self.assertIn("order", json.loads(response.data)["errors"])


if __name__ == '__main__':
    unittest.main()
