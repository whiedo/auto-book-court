import unittest
import app
import requests

class TestInternetConnection(unittest.TestCase):
    def test_website_connection(self):
        req = requests.get(app.SPORTCENTER_KAUTZ_SQUASH_URL, timeout=5)
        self.assertEqual(req.status_code, 200)
            
if __name__ == '__main__':
    unittest.main()