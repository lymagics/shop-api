from apiflask import abort, APIBlueprint

from .auth import token_auth
from .decorators import admin_required
from .schemas import ProductCategorySchema
from .models import db, ProductCategory

categories = APIBlueprint("categories", __name__)


@categories.post("/categories")
@categories.auth_required(token_auth)
@admin_required
@categories.input(ProductCategorySchema)
@categories.output(ProductCategorySchema, status_code=201)
@categories.doc(summary="Create new category.", description="Create new product category. You need to be admin to access this resource.")
def new(data):
    """Create new category."""
    category = ProductCategory(**data)
    db.session.add(category)
    db.session.commit()
    return category


@categories.put("/categories/<int:category_id>")
@categories.auth_required(token_auth)
@admin_required
@categories.input(ProductCategorySchema)
@categories.output(ProductCategorySchema)
@categories.doc(summary="Edit product category information.", description="Edit product category information. You need to be admin to access this resource.")
def put(category_id, data):
    """Edit product category information."""
    category = ProductCategory.query.filter_by(category_id=category_id).first() or abort(404, "Category not found.")
    category.update(data)
    db.session.commit()
    return category


@categories.delete("/categories/<int:category_id>")
@categories.auth_required(token_auth)
@admin_required
@categories.output({}, status_code=204)
@categories.doc(summary="Delete product category.", description="Delete product category. You need to be admin to access this resource.")
def delete(category_id):
    """Delete product category."""
    category = ProductCategory.query.filter_by(category_id=category_id).first() or abort(404, "Category not found.")
    db.session.delete(category)
    db.session.commit()
    return "", 204
