import secrets
from datetime import datetime, timedelta

import stripe
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Updateable:
    """Class with update functionality."""
    def update(self, data):
        """Update object fields."""
        for attr, value in data.items():
            setattr(self, attr, value)


class Token(db.Model):
    """SQLAlchemy model to represent 'tokens' table."""
    __tablename__ = "tokens"
    
    token_id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(64), nullable=False, index=True)
    access_expiration = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False, index=True)
    refresh_expiration = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    def generate(self):
        """Generate access token."""
        self.access_token = secrets.token_urlsafe(16)
        self.access_expiration = datetime.utcnow() + \
            timedelta(minutes=current_app.config["ACCESS_EXPIRATION_IN_MINUTES"])
        self.refresh_token = secrets.token_urlsafe(16)
        self.refresh_expiration = datetime.utcnow() + \
            timedelta(days=current_app.config["REFRESH_EXPIRATION_IN_DAYS"])

    def expire(self):
        """Expire token."""
        self.access_expiration = datetime.utcnow()
        self.refresh_expiration = datetime.utcnow()

    @staticmethod
    def clean():
        """Delete all tokens that expired more than yesterday."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        Token.query.filter(Token.refresh_expiration < yesterday).delete()


class CartItem(db.Model):
    """SQLAlchemy model to represent 'cart_items' table."""
    __tablename__ = "cart_items"

    item_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"))
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.cart_id"))


class CartStatus(db.Model):
    """SQLAlchemy model to represent 'cart_statuses' table."""
    __tablename__ = "cart_statuses"

    status_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    carts = db.relationship("Cart", backref="status", cascade="all,delete", lazy="dynamic")


class Cart(db.Model):
    """SQLAlchemy model to represent 'carts' table."""
    __tablename__ = "carts"

    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    status_id = db.Column(db.Integer, db.ForeignKey("cart_statuses.status_id"))

    items = db.relationship("CartItem", backref="cart", cascade="all,delete", lazy="dynamic")

    def create_checkout_session(self, currency: str="usd"):
        """Create Stripe Checkout Session."""
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
        line_items = [
            {
                "price_data": {
                    "product_data": {
                        "name": item.product.name
                    },
                    "unit_amount": int(item.product.price * 100.0),
                    "currency": currency,
                },
                "quantity": item.quantity,
            }
            for item in self.items
        ]

        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            payment_method_types=["card"],
            mode="payment",
            metadata={"cart_id": self.cart_id},
            success_url=current_app.config["CHECKOUT_SUCCESS"],
            cancel_url=current_app.config["CHECKOUT_FAIL"]
        )
        return checkout_session.url


class ProductCategory(Updateable, db.Model):
    """SQLAlchemy model to represent 'product_categories' table."""
    __tablename__ = "product_categories"

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False)

    products = db.relationship("Product", backref="category", cascade="all,delete", lazy="dynamic")


class Product(Updateable, db.Model):
    """SQLAlchemy model to represent 'products' table."""
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("product_categories.category_id"))

    cart_items = db.relationship("CartItem", backref="product", cascade="all,delete", lazy="dynamic")
    

class User(Updateable, db.Model):
    """SQLAlchemy model to represent 'users' table."""
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    tokens = db.relationship("Token", backref="user", cascade="all,delete", lazy="dynamic")
    carts = db.relationship("Cart", backref="user", cascade="all,delete", lazy="dynamic")

    @property
    def password(self):
        raise AttributeError("Can't read user password.")

    @password.setter 
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def ping(self):
        """Update user's last seen."""
        self.last_seen = datetime.utcnow()

    def verify_password(self, password):
        """Verify user's password."""
        return check_password_hash(self.password_hash, password)

    def generate_access_token(self):
        """Generate new access token."""
        token = Token(user=self)
        token.generate()
        return token

    def revoke_all(self):
        """Revoke all user tokens."""
        self.tokens.delete()

    @staticmethod
    def verify_access_token(access_token):
        """Verify access token."""
        token = Token.query.filter_by(access_token=access_token).first()
        if token:
            if token.access_expiration > datetime.utcnow():
                token.user.ping()
                db.session.commit()
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token):
        """Verify refresh token."""
        token = Token.query.filter_by(refresh_token=refresh_token, access_token=access_token).first()
        if token:
            if token.refresh_expiration > datetime.utcnow():
                return token
            
            # Revoke all tokens if someone try to use expired refresh token.
            token.user.revoke_all()
            db.session.commit()

    def __repr__(self) -> str:
        return f"<User {self.username}>"
