import unittest 
import secrets
from datetime import datetime, timedelta
from time import sleep

from api import create_app
from api.models import db, User, Token
from api.tokens import token_response
from config import TestConfig


class TokensTestCase(unittest.TestCase):
    """Test case for tokens models."""
    config = TestConfig

    def setUp(self):
        """Instructions that will be executed before each test method."""
        self.app = create_app(self.config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.u = User(
            username="bob",
            email="bob@example.com",
            password="cat"
        )
        self.token = self.u.generate_access_token()
        db.session.add(self.u)
        db.session.add(self.token)
        db.session.commit()

    def test_access_token_correct(self):
        """Test genearted access token is correct."""
        u1 = User.verify_access_token(self.token.access_token)
        u2 = User.verify_access_token(secrets.token_urlsafe())
        self.assertTrue(self.u is u1)
        self.assertIsNone(u2)

    def test_refresh_token_correct(self):
        """Test genearted refresh token is correct."""
        t1 = User.verify_refresh_token(self.token.refresh_token, self.token.access_token)
        t2 = User.verify_refresh_token(secrets.token_urlsafe(), secrets.token_urlsafe())
        self.assertTrue(self.token is t1)
        self.assertIsNone(t2)

    def test_expired(self):
        """Test token expiration."""
        self.assertTrue(self.token.access_expiration > datetime.utcnow())
        self.token.expire()
        sleep(1)
        self.assertTrue(self.token.access_expiration < datetime.utcnow())

    def test_clean(self):
        """Test tokens are deleted after long expiration."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        self.token.refresh_expiration = yesterday
        db.session.commit()
        Token.clean()
        db.session.commit()
        self.assertFalse(self.u.tokens.all())

    def test_token_response(self):
        """Test token response."""
        with self.app.test_request_context():
            response, headers = token_response(self.token)

        self.assertTrue("access_token" in response)
        self.assertTrue("refresh_token" in response)
        self.assertIsNone(response.get("refresh_token"))
        self.assertTrue("Set-Cookie" in headers)

    def tearDown(self):
        """Instructions that will be executed after each test method"""
        db.drop_all()
        self.app_context.pop()
        