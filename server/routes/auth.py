from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import db
from models import User


def error_response(message, status):
    return {"errors": [message]}, status


def establish_session(user):
    session.clear()
    session["user_id"] = user.id
    return user.to_dict()


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

        return establish_session(user), 201


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

        return establish_session(user), 200


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


class Logout(Resource):
    def delete(self):
        session.clear()
        return {}, 204
