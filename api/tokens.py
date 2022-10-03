from apiflask import abort, APIBlueprint
from flask import current_app, url_for, request
from werkzeug.http import dump_cookie

from .auth import basic_auth, token_auth
from .models import db, Token, User
from .schemas import TokenSchema

tokens = APIBlueprint("tokens", __name__)


def token_response(token: Token):
    """Generate token response."""
    headers = {}
    samesite = "strict"
    if current_app.config["USE_CORS"]:
        samesite = "none" if not current_app.debug else "lax"
    if current_app.config["REFRESH_TOKEN_IN_COOKIE"]:
        headers["Set-Cookie"] = dump_cookie(
            "refresh_token", token.refresh_token, httponly=True,
            secure=not current_app.debug, path=url_for("tokens.new"),
            samesite=samesite
        )
    
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token 
        if current_app.config["REFRESH_TOKEN_IN_BODY"] else None
    }, headers


@tokens.post("/tokens")
@tokens.auth_required(basic_auth)
@tokens.output(TokenSchema, status_code=201)
@tokens.doc(summary="Create access token.", description="Create access token for token authentication.")
def new():
    """Create access token."""
    user = basic_auth.current_user
    token = user.generate_access_token()
    db.session.add(token)
    Token.clean()
    db.session.commit()
    return token_response(token)


@tokens.put("/tokens")
@tokens.input(TokenSchema)
@tokens.output(TokenSchema)
@tokens.doc(summary="Refresh access token.", description="Refresh access token with new token.")
def put(data):
    """Refresh access token."""
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token", request.cookies.get("refresh_token"))
    if not access_token or not refresh_token:
        abort(401) 
    token = User.verify_refresh_token(refresh_token, access_token) 
    if not token:
        abort(401)
    token.expire()
    new_token = token.user.generate_access_token()
    db.session.add(new_token)
    db.session.commit()
    return token_response(new_token)


@tokens.delete("/tokens")
@tokens.auth_required(token_auth)
@tokens.output({}, status_code=204)
@tokens.doc(summary="Revoke access token.", description="Revoke access token to make it invalid for further authentication.")
def delete():
    """Revoke access token."""
    access_token = request.headers["Authorization"].split()[1]
    if not access_token:
        abort(400, "Provide access token.")
    token = Token.query.filter_by(access_token=access_token).first()
    if not token:
        abort(400, "Invalid token.")
    token.expire()
    db.session.commit()
    return "", 204
