from datetime import date

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from config import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)

    expenses = db.relationship(
        "Expense",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @validates("username")
    def validate_username(self, key, username):
        username = username.strip()

        if not username:
            raise ValueError("Username cannot be empty.")

        return username

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        if not isinstance(password, str) or not password.strip():
            raise ValueError("Password cannot be empty.")

        self._password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def authenticate(self, password):
        if not isinstance(password, str):
            return False

        return bcrypt.check_password_hash(
            self._password_hash,
            password
        )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80))
    date = db.Column(db.Date, default=date.today, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship("User", back_populates="expenses")

    @validates("title")
    def validate_title(self, key, title):
        title = title.strip()

        if not title:
            raise ValueError("Expense title cannot be empty.")

        return title

    @validates("amount")
    def validate_amount(self, key, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError("Amount must be a number.")

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        return amount

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "category": self.category,
            "date": self.date.isoformat() if self.date else None,
            "user_id": self.user_id
        }


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    jti = db.Column(db.String(36), primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
