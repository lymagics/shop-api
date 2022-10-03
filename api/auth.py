from apiflask import HTTPBasicAuth, HTTPTokenAuth
from .models import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    """HTTP Basic Authentication."""
    user = User.query.filter_by(username=username).first()
    if user is not None and user.verify_password(password):
        return user


@token_auth.verify_token
def verify_token(token):
    """HTTP Token Authentication."""
    return User.verify_access_token(token)
