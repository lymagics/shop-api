import click
from faker import Faker
from flask import current_app, Blueprint

from .models import db, CartStatus, User

fake = Faker()
populate = Blueprint("populate", __name__)


@populate.cli.command()
def statuses():
    """Populate database with checkout statuses."""
    for status in current_app.config["CART_STATUSES"]:
        s = CartStatus(name=status)
        db.session.add(s)
    db.session.commit()
    print(f"Successfully added to db {len(current_app.config['CART_STATUSES'])} statuses.")


@populate.cli.command()
@click.argument("num", type=int)
def users(num):
    """Populate db with fake users."""
    for i in range(num):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            name=fake.name(),
            password="12345"
        )
        db.session.add(user)
    db.session.commit()
    print(f"Successfully added to db {num} users.")
