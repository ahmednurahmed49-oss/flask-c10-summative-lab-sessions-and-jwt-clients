from flask import Flask, request, jsonify, session
from config import Config
from extensions import db, migrate, bcrypt
from models import User

app = Flask(__name__)

app.config.from_object(Config)

# Session cookie settings for local development
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)


@app.route("/")
def home():
    return jsonify({"message": "Expense Tracker API is running!"})


# SIGNUP
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")
    password_confirmation = data.get("password_confirmation", "")

    errors = []

    if not username:
        errors.append("Username is required.")

    if not password:
        errors.append("Password is required.")

    

    if password != password_confirmation:
        errors.append("Passwords do not match.")

    if username and User.query.filter_by(username=username).first():
        errors.append("Username already exists.")

    if errors:
        return jsonify({"errors": errors}), 422

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "username": user.username
    }), 201


# LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(
        user.password_hash, password
    ):
        return jsonify({
            "errors": ["Invalid username or password."]
        }), 401

    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "username": user.username
    }), 200


# CHECK SESSION
@app.route("/check_session", methods=["GET"])
def check_session():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({}), 200

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return jsonify({}), 200

    return jsonify({
        "id": user.id,
        "username": user.username
    }), 200


# LOGOUT
@app.route("/logout", methods=["DELETE"])
def logout():
    session.clear()
    return jsonify({}), 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)