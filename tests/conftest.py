import os
import sys


os.environ["DATABASE_URI"] = "sqlite:///:memory:"
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

import app as _routes  
from config import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def logged_in(client):
    """A client that has already signed up as 'peter'."""
    client.post("/signup", json={"username": "peter", "password": "TONKATONKA"})
    return client