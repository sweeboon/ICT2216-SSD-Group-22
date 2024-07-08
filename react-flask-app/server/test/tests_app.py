import unittest
from flask import current_app
from server.api import create_app, db
from server.api.models import Account, Cart, Order, Product
from flask_login import login_user

class MainTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()
        db.create_all()

        # Create a test user and log in
        cls.user = Account(username='testuser', email='testuser@example.com', password='password')
        db.session.add(cls.user)
        db.session.commit()
        login_user(cls.user)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_add_to_cart(self):
        response = self.client.post('/cart', json={
            'product_id': 1,
            'quantity': 2,
            'cart_item_price': 19.99
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Item added to cart', response.data)

    def test_remove_from_cart(self):
        # First, add an item to the cart
        self.client.post('/cart', json={
            'product_id': 1,
            'quantity': 2,
            'cart_item_price': 19.99
        })
        cart_item = Cart.query.first()

        # Now, remove the item
        response = self.client.delete(f'/cart/{cart_item.cart_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item removed from cart', response.data)

    def test_get_cart_total(self):
        # Add an item to the cart
        self.client.post('/cart', json={
            'product_id': 1,
            'quantity': 2,
            'cart_item_price': 19.99
        })

        response = self.client.get('/cart/total')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'total_amount', response.data)

    def test_get_orders(self):
        # Add an order
        order = Order(
            account_id=self.user.account_id,
            payment_id=1,
            product_id=1,
            order_status='Pending',
            order_price=19.99,
            order_date=datetime.utcnow(),
            quantity=2
        )
        db.session.add(order)
        db.session.commit()

        response = self.client.get('/orders')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'order_id', response.data)

if __name__ == "__main__":
    unittest.main()
