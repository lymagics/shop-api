from apiflask import fields, Schema
from apiflask.validators import Length, Regexp, Email, Range
from marshmallow import validates, ValidationError

from .auth import token_auth
from .models import User, ProductCategory


class PaginationSchema(Schema):
    """Marshmallow schema to represent pagination. The schema is standard for whole application."""
    page = fields.Integer(load_default=1)
    per_page = fields.Integer()
    total = fields.Integer(dump_only=True)


class UserSchema(Schema):
    """Marshmallow schema to represent User entity."""
    user_id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=[
        Length(min=3, max=64),
        Regexp("^[A-Za-z][A-Za-z0-9._]*$", 0 , error="Username must only contain letters, numbers, dots and underscores.")
    ])
    email = fields.String(required=True, load_only=True, validate=[
        Length(max=120),
        Email()
    ])
    password = fields.String(required=True, load_only=True, validate=Length(min=3))
    name = fields.String()
    last_seen = fields.DateTime(dump_only=True)
    member_since = fields.DateTime(dump_only=True)

    @validates("username")
    def validate_username(self, value):
        """Validate dump username."""
        user = User.query.filter_by(username=value).first()
        if user is not None and user != token_auth.current_user:
            raise ValidationError("Use a different username.")

    @validates("email")
    def validate_email(self, value):
        """Validate dump email."""
        user = User.query.filter_by(email=value).first()
        if user is not None and user != token_auth.current_user:
            raise ValidationError("Use a different email.")


class UserPaginationSchema(Schema):
    """Marshmallow schema to represent User pagination."""
    data = fields.List(fields.Nested(UserSchema))
    pagination = fields.Nested(PaginationSchema)


class TokenSchema(Schema):
    """Marshmallow schema to represent Token entity."""
    access_token = fields.String(required=True, validate=Length(max=64))
    refresh_token = fields.String(validate=Length(max=64))


class ProductCategorySchema(Schema):
    """Marshmallow schema to represent Product Category entity."""
    category_id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=Length(max=64))

    @validates("name")
    def validate_name(self, value):
        """Validate product category name."""
        category = ProductCategory.query.filter_by(name=value).first()
        if category is not None:
            raise ValidationError("Category already exists.")


class ProductSchema(Schema):
    """Marshmallow schema to represent Product entity."""
    product_id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=Length(max=120))
    description = fields.String()
    price = fields.Float(reduired=True, validates=Range(min=0.0))
    category_id = fields.Integer(required=True)

    @validates("category_id")
    def validate_category_id(self, value):
        """Validate if category exists."""
        category = ProductCategory.query.filter_by(category_id=value).first()
        if category is None:
            raise ValidationError("Category doesn't exist.")


class ProductPaginationSchema(Schema):
    """Marshmallow schema to represent Product Pagination."""
    data = fields.List(fields.Nested(ProductSchema))
    pagination = fields.Nested(PaginationSchema)


class CartItem(Schema):
    """Marshmallow schema to represent Cart Item entity."""
    product = fields.Nested(ProductSchema)
    quantity = fields.Integer()


class StatusSchema(Schema):
    """Marshmallow schema to represent Checkout Status entity."""
    name = fields.String(dump_only=True)


class CartSchema(Schema):
    """Marshmallow schema to represent Cart entity."""
    cart_id = fields.Integer(dump_only=True)
    items = fields.List(fields.Nested(CartItem))
    status = fields.Nested(StatusSchema)


class CheckoutSchema(Schema):
    """Marshmallow schema to represent Checkout."""
    url = fields.URL(dump_only=True)
