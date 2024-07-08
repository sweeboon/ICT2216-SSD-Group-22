import unittest
from server import app

class BasicTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_api_endpoint(self):
        response = self.client.get('/api/v1/some-endpoint')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Expected response content', response.data)

if __name__ == "__main__":
    unittest.main()
