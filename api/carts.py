import stripe
from apiflask import abort, APIBlueprint
from flask import current_app, request

from .auth import token_auth
from .email import send_mail
from .schemas import CartSchema, CheckoutSchema
from .models import db, Cart, Product, CartItem, CartStatus
from .utils import checkout_response

carts = APIBlueprint("carts", __name__)


@carts.post("/carts")
@carts.auth_required(token_auth)
@carts.output(CartSchema, status_code=201)
@carts.doc(summary="Create new cart.", description="Create new shopping cart.")
def new():
    """Create new cart."""
    user = token_auth.current_user
    status = CartStatus.query.filter_by(name="ready to pay").first()
    cart = Cart(user=user, status=status)
    db.session.add(user)
    db.session.commit()
    return cart 


@carts.post("/carts/<int:cart_id>/products/<int:product_id>")
@carts.auth_required(token_auth)
@carts.output(CartSchema, status_code=201)
@carts.doc(summary="Put a product in the cart.", description="Put a product in the cart.")
def add(cart_id, product_id):
    """Put a product in the cart."""
    cart = Cart.query.filter_by(cart_id=cart_id).first() or abort(404, "Cart not found.")
    product = Product.query.filter_by(product_id=product_id).first() or abort(404, "Product not found.")
    if cart.user != token_auth.current_user:
        abort(403, "This is not your cart.")
    if cart.status.name == "paid":
        abort(400, "Cart is paid.")

    item = cart.items.filter_by(product=product).first()
    if not item:
        item = CartItem(cart=cart, product=product)
    item.quantity = (item.quantity + 1) if item.quantity else 1
    db.session.add(item)
    db.session.commit()
    return cart


@carts.get("/carts/<int:cart_id>")
@carts.auth_required(token_auth)
@carts.output(CartSchema)
@carts.doc(summary="Retrieve information about cart.", description="Retrieve information about cart. You have to own this cart to get it.")
def get(cart_id):
    """Retrieve information about cart."""
    cart = Cart.query.filter_by(cart_id=cart_id).first() or abort(404, "Cart not found.")
    if cart.user != token_auth.current_user:
        abort(403, "This is not your cart.")
    return cart


@carts.delete("/carts/<int:cart_id>/products/<int:product_id>")
@carts.auth_required(token_auth)
@carts.output({}, status_code=204)
@carts.doc(summary="Delete product from cart.", description="Delete product from cart. You have to own this cart to get it.")
def delete(cart_id, product_id):
    """Delete product from cart."""
    cart = Cart.query.filter_by(cart_id=cart_id).first() or abort(404, "Cart not found.")
    if cart.user != token_auth.current_user:
        abort(403, "This is not your cart.")
    if cart.status.name == "paid":
        abort(400, "Cart is paid.")
    
    item = cart.items.filter_by(product_id=product_id).first()
    if not item:
        abort(404, "Product not found.")

    item.quantity -= 1
    if item.quantity == 0:
        cart.items.remove(item)
        db.session.delete(item)
    db.session.commit()
    return "", 204


@carts.post("/carts/<int:cart_id>/checkout")
@carts.auth_required(token_auth)
@carts.output(CheckoutSchema)
@carts.doc(summary="Create checkout session.", description="Create checkout session so user can pay for his cart.")
def checkout(cart_id):
    """Create checkout session."""
    cart = Cart.query.filter_by(cart_id=cart_id).first() or abort(404, "Cart not found.")
    if cart.user != token_auth.current_user:
        abort(403, "This is not your cart.")
    if cart.status.name == "paid":
        abort(400, "Cart is paid.")
    if not cart.items.all():
        abort(400, "Cart is empty.")

    url = cart.create_checkout_session()
    return checkout_response(url)


@carts.post("/event")
@carts.doc(hide=True)
def new_event():
    """Event for Stripe Checkout Webhook."""
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    event = None
    payload = request.data 
    signature = request.headers["STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, current_app.config["STRIPE_WEBHOOK_SECRET"]
        )
    except Exception as e:
        abort(400)

    if event["type"] == "checkout.session.completed":
        session = stripe.checkout.Session.retrieve(
            event["data"]["object"]["id"], expand=["line_items"]
        )

        cart_id = session.metadata["cart_id"]
        cart = Cart.query.filter_by(cart_id=cart_id).first()
        status = CartStatus.query.filter_by(name="paid").first()
        cart.status = status
        db.session.commit()

        send_mail("Thanks for purchase!", cart.user.email, "user/success", cart=cart)
        send_mail(f"Purchase from {cart.user.username}!", current_app.config["ADMIN_EMAIL"], "admin/success", cart=cart)
    
    return {"success": True}
