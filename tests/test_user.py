import unittest
from time import sleep

from api import create_app
from api.models import db, User
from config import TestConfig 


class UserTestCase(unittest.TestCase):
    """Test case for user model."""
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
        db.session.add(self.u)
        db.session.commit()

    def test_password_is_correct(self):
        """Test password verification works."""
        self.assertTrue(self.u.verify_password("cat"))
        self.assertFalse(self.u.verify_password("dog"))

    def test_cant_access_password(self):
        """Test password field is inaccessible."""
        with self.assertRaises(AttributeError):
            self.u.password

    def test_last_seen_changes(self):
        """Test user last_seen field changes."""
        last_seen = self.u.last_seen
        sleep(1)
        self.u.ping()
        db.session.commit()
        self.assertTrue(last_seen < self.u.last_seen)

    def test_password_salts_are_random(self):
        """Test password hash salts are random."""
        u2 = User(
            username="alice",
            email="alice@example.com",
            password="cat"
        )
        db.session.add(u2)
        db.session.commit()

        self.assertTrue(self.u.password_hash != u2.password_hash)

    def tearDown(self):
        """Instructions that will be executed after each test method"""
        db.drop_all()
        self.app_context.pop()
