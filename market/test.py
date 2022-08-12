import sys
import requests
import json

URL = "http://127.0.0.1:5000"
HDR =  {"Content-Type":"application/json"}

def get(*endpoint,**kwargs):
    return requests.get(f"{URL}/{'/'.join(endpoint)}",kwargs).json()

def post(*endpoint,**kwargs):
    return requests.post(f"{URL}/{'/'.join(endpoint)}",kwargs).json()

def delete(*endpoint,**kwargs):
    return requests.delete(f"{URL}/{'/'.join(endpoint)}",kwargs).json()

if __name__ == "__main__":
    import unittest

    class TestUsers(unittest.TestCase):

        def test_get(self):
            result = get("users")
            self.assertEqual(result['data']['1']['name'],'Test User 1')

    class TestUser(unittest.TestCase):

        def test_get_ok(self):
            result = get("user","1")
            self.assertEqual(result["data"]["name"],"Test User 1")
        
        def test_get_notfound(self):
            result = get("user/0")
            self.assertEqual(result["message"],"not found")

        def test_post(self):
            result = post("user","3",name="Test User 3")
            self.assertEqual(result["data"]["name"],"Test User 3")

    class TestOrders(unittest.TestCase):

        def test_get(self):
            result = get("orders")
            self.assertEqual(result["data"]["1001"]["status"],"PENDING")
            
    class TestOrder(unittest.TestCase):

        def test_get(self):
            result = get("order","1001")
            self.assertEqual(result["data"]["status"],"PENDING")

    unittest.main()