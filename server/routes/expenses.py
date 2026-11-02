from datetime import date

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from config import db
from models import Expense


def current_user_id():
    """Return the logged-in user's id from the JWT."""
    return int(get_jwt_identity())


def get_own_expense(expense_id):
    """Find an expense only if it belongs to the logged-in user."""
    return Expense.query.filter_by(id=expense_id, user_id=current_user_id()).first()


def parse_fields(data, partial=False):
    """Validate input. Returns (clean_data, error_message)."""
    clean = {}

    if "title" in data or not partial:
        title = (data.get("title") or "").strip()
        if not title:
            return None, "Title is required"
        clean["title"] = title

    if "amount" in data or not partial:
        try:
            amount = float(data.get("amount"))
        except (TypeError, ValueError):
            return None, "Amount must be a number"
        if amount <= 0:
            return None, "Amount must be greater than 0"
        clean["amount"] = amount

    if "category" in data:
        clean["category"] = data.get("category")

    if "date" in data:
        try:
            clean["date"] = date.fromisoformat(data["date"])
        except (TypeError, ValueError):
            return None, "Date must be in YYYY-MM-DD format"

    return clean, None


class ExpenseList(Resource):
    @jwt_required()
    def get(self):
        page = max(request.args.get("page", 1, type=int), 1)
        per_page = min(max(request.args.get("per_page", 10, type=int), 1), 100)

        pagination = (
            Expense.query.filter_by(user_id=current_user_id())
            .order_by(Expense.date.desc(), Expense.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "expenses": [e.to_dict() for e in pagination.items],
            "page": pagination.page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    @jwt_required()
    def post(self):
        clean, error = parse_fields(request.get_json() or {})
        if error:
            return {"error": error}, 422

        expense = Expense(user_id=current_user_id(), **clean)
        db.session.add(expense)
        db.session.commit()
        return expense.to_dict(), 201


class ExpenseDetail(Resource):
    @jwt_required()
    def patch(self, id):
        expense = get_own_expense(id)
        if not expense:
            return {"error": "Expense not found"}, 404

        clean, error = parse_fields(request.get_json() or {}, partial=True)
        if error:
            return {"error": error}, 422

        for field, value in clean.items():
            setattr(expense, field, value)
        db.session.commit()
        return expense.to_dict(), 200

    @jwt_required()
    def delete(self, id):
        expense = get_own_expense(id)
        if not expense:
            return {"error": "Expense not found"}, 404

        db.session.delete(expense)
        db.session.commit()
        return {}, 204
