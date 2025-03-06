import pytest
from inf349 import app, db, Product, Order

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_create_order(client):
    # Préparer un produit pour le test
    product = Product.create(name="Test Product", price=100, in_stock=True, weight=200, description="Test", image="test.jpg")
    
    order_data = {
        "shipping_information": "Some address",
        "email": "test@example.com",
        "total_price": 100,
        "total_price_tax": 120,
        "shipping_price": 20,
        "product": {"id": product.id}
    }

    response = client.post('/order', json=order_data)
    assert response.status_code == 201
    assert "order_id" in response.json
