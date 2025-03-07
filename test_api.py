import unittest, json
from unittest.mock import patch
from inf349 import app

class ApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

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


    @patch("inf349.Product.get")
    def test_create_order(self, mock_get):
        mock_get.return_value = type("Product", (), {"id": 1, "price": 1000, "in_stock": True, "weight": 400})()
        response = self.app.post('/order', json={
            "product": {"id": 1, "quantity": 2}
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("Location", json.loads(response.data))

    @patch("inf349.Order.get_or_none")
    def test_get_order(self, mock_get):
        mock_get.return_value = None
        response = self.app.get('/order/1')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
