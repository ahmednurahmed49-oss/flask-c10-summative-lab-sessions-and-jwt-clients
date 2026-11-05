import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)

# Application security settings
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "development-secret-change-in-production"
)

# JWT authentication settings
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", app.config["SECRET_KEY"]
)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

# Database settings
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.json.compact = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    from models import TokenBlocklist

    token = db.session.get(TokenBlocklist, jwt_payload["jti"])
    return token is not None
