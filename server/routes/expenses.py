from datetime import date
from math import isfinite

from flask import request, session
from flask_restful import Resource

from config import db
from models import Expense


def error_response(message, status):
    return {"errors": [message]}, status


def current_user_id():
    return session.get("user_id")


def get_own_expense(expense_id):
    return Expense.query.filter_by(
        id=expense_id,
        user_id=current_user_id()
    ).first()


def parse_fields(data, partial=False):
    if not isinstance(data, dict):
        return None, "A valid JSON object is required."

    clean = {}

    if "title" in data or not partial:
        title = data.get("title")

        if not isinstance(title, str) or not title.strip():
            return None, "A valid title is required."

        clean["title"] = title.strip()

    if "amount" in data or not partial:
        amount = data.get("amount")

        if isinstance(amount, bool):
            return None, "Amount must be a number."

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return None, "Amount must be a number."

        if not isfinite(amount) or amount <= 0:
            return None, "Amount must be greater than zero."

        clean["amount"] = amount

    if "category" in data:
        category = data["category"]

        if category is not None and not isinstance(category, str):
            return None, "Category must be text or null."

        clean["category"] = category.strip() if category else None

    if "date" in data:
        try:
            if not isinstance(data["date"], str):
                raise ValueError

            clean["date"] = date.fromisoformat(data["date"])
        except (TypeError, ValueError):
            return None, "Date must use YYYY-MM-DD format."

    if partial and not clean:
        return None, "Provide at least one field to update."

    return clean, None


class ExpenseList(Resource):

    def get(self):
        user_id = current_user_id()

        if not user_id:
            return error_response("Authentication required.", 401)

        page = max(request.args.get("page", 1, type=int), 1)
        per_page = min(
            max(request.args.get("per_page", 10, type=int), 1),
            100
        )

        pagination = (
            Expense.query
            .filter_by(user_id=user_id)
            .order_by(Expense.date.desc(), Expense.id.desc())
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        )

        return {
            "expenses": [
                expense.to_dict()
                for expense in pagination.items
            ],
            "page": pagination.page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }, 200

    def post(self):
        user_id = current_user_id()

        if not user_id:
            return error_response("Authentication required.", 401)

        data = request.get_json(silent=True)
        clean, error = parse_fields(data)

        if error:
            return error_response(error, 422)

        expense = Expense(user_id=user_id, **clean)

        db.session.add(expense)
        db.session.commit()

        return expense.to_dict(), 201


class ExpenseDetail(Resource):

    def get(self, id):
        if not current_user_id():
            return error_response("Authentication required.", 401)

        expense = get_own_expense(id)

        if not expense:
            return error_response("Expense not found.", 404)

        return expense.to_dict(), 200

    def patch(self, id):
        if not current_user_id():
            return error_response("Authentication required.", 401)

        expense = get_own_expense(id)

        if not expense:
            return error_response("Expense not found.", 404)

        data = request.get_json(silent=True)
        clean, error = parse_fields(data, partial=True)

        if error:
            return error_response(error, 422)

        for field, value in clean.items():
            setattr(expense, field, value)

        db.session.commit()

        return expense.to_dict(), 200

    def delete(self, id):
        if not current_user_id():
            return error_response("Authentication required.", 401)

        expense = get_own_expense(id)

        if not expense:
            return error_response("Expense not found.", 404)

        db.session.delete(expense)
        db.session.commit()

        return {}, 204
