import unittest

from api import create_app
from api.utils import paginated_response, checkout_response

from config import TestConfig


class UtilsTestCase(unittest.TestCase):
    config = TestConfig

    def setUp(self):
        """Instructions that will be executed before each test method."""
        self.app = create_app(self.config)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def test_paginated_response(self):
        """Test pagination response."""
        data = {"username": "bob"}
        pagination = {"page": 1, "per_page": 10, "total": 10}
        response, code, headers = paginated_response(data, pagination)

        self.assertTrue("data" in response)
        self.assertTrue("pagination" in response)
        self.assertTrue(code == 200)
        self.assertIsNone(headers)

    def test_checkout_response(self):
        """Test checkout session response."""
        response = checkout_response("http://checkout.com")
        self.assertTrue("url" in response)

    def tearDown(self):
        """Instructions that will be executed after each test method"""
        self.app_context.pop()
