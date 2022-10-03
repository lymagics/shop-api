from apiflask import abort, APIBlueprint
from flask import current_app

from .auth import token_auth
from .schemas import UserSchema, UserPaginationSchema, PaginationSchema
from .models import db, User
from .utils import paginated_response

users = APIBlueprint("users", __name__)


@users.post("/users")
@users.input(UserSchema)
@users.output(UserSchema, status_code=201)
@users.doc(summary="Create new user.", description="Create new user. To create new user you have to specify all required fields.")
def new(data):
    """Create new user."""
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user


@users.get("/users/<username>")
@users.auth_required(token_auth)
@users.output(UserSchema)
@users.doc(summary="Retrieve user by username.", description="Retrieve user by username. If user not found return 404 error.")
def get_by_username(username):
    """Retrieve user by username."""
    return User.query.filter_by(username=username).first() or abort(404, "User not found")


@users.get("/users")
@users.auth_required(token_auth)
@users.input(PaginationSchema, location="query")
@users.output(UserPaginationSchema)
@users.doc(summary="Retrieve all users.", description="Retrieve all users. ")
def all(query):
    """Retrieve all users."""
    pagination = User.query.paginate(
        page=query.get("page", 1),
        per_page=query.get("per_page", current_app.config["USERS_PER_PAGE"])
    )
    users = pagination.items
    return paginated_response(users, pagination)


@users.get("/me")
@users.auth_required(token_auth)
@users.output(UserSchema)
@users.doc(summary="Retrieve the authenticated user.", description="Retrieve information about authenticated user.")
def me():
    """Retrieve the authenticated user."""
    return token_auth.current_user


@users.put("/me")
@users.auth_required(token_auth)
@users.input(UserSchema(partial=True))
@users.output(UserSchema)
@users.doc(summary="Edit user information.", description="Update information about authenticated user.")
def put(data):
    """Edit user information."""
    user = token_auth.current_user
    user.update(data)
    db.session.commit()
    return user
