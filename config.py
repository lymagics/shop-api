import os
from dotenv import load_dotenv

load_dotenv()
# Base directory for local database.
base_dir = os.path.abspath(os.path.dirname(__file__))


def as_bool(val: str) -> bool:
    """Config boolean value loader."""
    if str(val).lower() in ["yes", "true", "1"]:
        return True 
    return False


class Config:
    """Application config."""
    # Secret key for data encryption.
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Database connection.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(base_dir, "db.sqlite")

    # Pagination.
    USERS_PER_PAGE = os.environ.get("USERS_PER_PAGE") or 10
    PRODUCTS_PER_PAGE = os.environ.get("PRODUCTS_PER_PAGE") or 10

    # OAuth 2.0
    REFRESH_EXPIRATION_IN_DAYS = int(os.environ.get("REFRESH_EXPIRATION_IN_DAYS") or "7")
    ACCESS_EXPIRATION_IN_MINUTES = int(os.environ.get("ACCESS_EXPIRATION_IN_MINUTES") or "15")
    REFRESH_TOKEN_IN_COOKIE = as_bool(os.environ.get("REFRESH_TOKEN_IN_COOKIE", "yes"))
    REFRESH_TOKEN_IN_BODY = as_bool(os.environ.get("REFRESH_TOKEN_IN_BODY"))

    # Administration config
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

    # Checkout statuses
    CART_STATUSES = ["paid", "ready to pay", "failed"]

    # Stripe checkout.
    CHECKOUT_SUCCESS = os.environ.get("CHECKOUT_SUCCESS") or "http://locahost:3000/success"
    CHECKOUT_FAIL = os.environ.get("CHECKOUT_FAIL") or "http://localhost:3000/fail"
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

    # Mail config
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.googlemail.com"
    MAIL_PORT = os.environ.get("MAIL_PORT") or 587
    MAIL_USE_TLS = as_bool(os.environ.get("MAIL_USE_TLS", "yes"))

    # Cross origin resource sharing
    USE_CORS = as_bool(os.environ.get("USE_CORS", "yes"))


class TestConfig:
    """Application test config."""
    # Enable testing mode
    TESTING = True

    # Test secret key
    SECRET_KEY = os.environ.get("TEST_SECRET_KEY", "test_key") 

    # Test database connection.
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        "sqlite:///" + os.path.join(base_dir, "test_db.sqlite")

    # Cross origin resource sharing
    USE_CORS = False

    # OAuth 2.0
    REFRESH_EXPIRATION_IN_DAYS = 15
    ACCESS_EXPIRATION_IN_MINUTES = 2
    REFRESH_TOKEN_IN_COOKIE = True 
    REFRESH_TOKEN_IN_BODY = False
