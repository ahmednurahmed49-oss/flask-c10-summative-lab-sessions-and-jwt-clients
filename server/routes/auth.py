from flask import request, session
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from sqlalchemy.exc import IntegrityError

from config import db
from models import User, TokenBlocklist


def error_response(message, status):
    return {"errors": [message]}, status


def authentication_response(user, status):
    """Return data in a format accepted by both existing frontends."""
    token = create_access_token(identity=str(user.id))
    user_data = user.to_dict()

    session.clear()
    session["user_id"] = user.id

    return {
        **user_data,
        "token": token,
        "user": user_data
    }, status


class Signup(Resource):
    def post(self):
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return error_response("A valid JSON object is required.", 400)

        username = data.get("username")
        password = data.get("password")
        password_confirmation = data.get("password_confirmation")

        if not isinstance(username, str) or not username.strip():
            return error_response("Username is required.", 422)

        if not isinstance(password, str) or len(password) < 8:
            return error_response(
                "Password must contain at least 8 characters.",
                422
            )

        if password != password_confirmation:
            return error_response("Passwords do not match.", 422)

        user = User(username=username.strip())
        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error_response("Username is already taken.", 409)

        return authentication_response(user, 201)


class Login(Resource):
    def post(self):
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return error_response("A valid JSON object is required.", 400)

        username = data.get("username")
        password = data.get("password")

        if not isinstance(username, str) or not isinstance(password, str):
            return error_response("Username and password are required.", 422)

        user = User.query.filter_by(username=username.strip()).first()

        if not user or not user.authenticate(password):
            return error_response("Invalid username or password.", 401)

        return authentication_response(user, 200)


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")

        if not user_id:
            return {}, 200

        user = db.session.get(User, user_id)

        if not user:
            session.clear()
            return {}, 200

        return user.to_dict(), 200


class Me(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))

        if not user:
            return error_response("User not found.", 404)

        return user.to_dict(), 200


class Logout(Resource):
    @jwt_required(optional=True)
    def delete(self):
        token_data = get_jwt()

        if token_data and token_data.get("jti"):
            revoked_token = TokenBlocklist(jti=token_data["jti"])
            db.session.add(revoked_token)
            db.session.commit()
        elif not session.get("user_id"):
            return error_response("Authentication required.", 401)

        session.clear()
        return {}, 204
