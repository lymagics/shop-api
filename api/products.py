from apiflask import abort, APIBlueprint
from flask import current_app

from .auth import token_auth
from .decorators import admin_required
from .models import db, Product, ProductCategory
from .schemas import ProductSchema, ProductPaginationSchema, PaginationSchema
from .utils import paginated_response

products = APIBlueprint("products", __name__)


@products.post("/products")
@products.auth_required(token_auth)
@admin_required
@products.input(ProductSchema)
@products.output(ProductSchema, status_code=201)
@products.doc(summary="Create new product.", description="Create new product. You need to be admin to access this resource.")
def new(data):
    """Create new product."""
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    return product


@products.get("/category/<int:category_id>/products")
@products.auth_required(token_auth)
@products.input(PaginationSchema, location="query")
@products.output(ProductPaginationSchema)
@products.doc(summary="Retrieve all products.", description="Retrieve all products. You need to be authenticated to access this resource.")
def all(category_id, query):
    """Retrieve all products."""
    category = ProductCategory.query.filter_by(category_id=category_id).first() or abort(404, "Category not found.")
    pagination = category.products.paginate(
        page=query.get("page", 1),
        per_page=query.get("per_page", current_app.config["PRODUCTS_PER_PAGE"])
    )
    products = pagination.items
    return paginated_response(products, pagination)


@products.get("/products/<int:product_id>")
@products.auth_required(token_auth)
@products.output(ProductSchema)
@products.doc(summary="Retieve product by id.", description="Retieve product by id. You need to be authenticated to access this resource.")
def get(product_id):
    """Retieve product by id."""
    return Product.query.filter_by(product_id=product_id).first() or abort(404, "Product not found.")


@products.put("/products/<int:product_id>")
@products.auth_required(token_auth)
@admin_required
@products.input(ProductSchema(partial=True))
@products.output(ProductSchema)
@products.doc(summary="Edit product information.", description="Edit product information. You need to be admin to access this resource.")
def put(product_id, data):
    """Edit product information."""
    product = Product.query.filter_by(product_id=product_id).first() or abort(404, "Product not found.")
    product.update(data)
    db.session.commit()
    return product


@products.delete("/products/<int:product_id>")
@products.auth_required(token_auth)
@admin_required
@products.output({}, status_code=204)
@products.doc(summary="Delete product.", description="Delete product. You need to be admin to access this resource.")
def delete(product_id):
    """Delete product."""
    product = Product.query.filter_by(product_id=product_id).first() or abort(404, "Product not found.")
    db.session.delete(product)
    db.session.commit()
    return "", 204
