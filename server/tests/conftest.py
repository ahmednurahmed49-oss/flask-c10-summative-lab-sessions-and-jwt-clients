import os
import sys
from pathlib import Path

import pytest

# Set this BEFORE importing the Flask application and initializing SQLAlchemy.
os.environ["DATABASE_URL"] = "sqlite:////tmp/flask-c10-summative-tests.db"

SERVER_DIRECTORY = Path(__file__).resolve().parents[1]

if str(SERVER_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SERVER_DIRECTORY))

from app import app
from config import db


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        JWT_SECRET_KEY="test-secret-key",
    )

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()
