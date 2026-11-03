"""Marshmallow schemas: validate incoming JSON and serialize outgoing data."""
from datetime import date

from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)


class SignupSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=30))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    # The frontend's signup form sends this field.
    password_confirmation = fields.Str(required=True)

    @validates_schema
    def passwords_match(self, data, **kwargs):
        if data.get("password") != data.get("password_confirmation"):
            raise ValidationError("Passwords do not match.", field_name="password_confirmation")


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class ExpenseSchema(Schema):
    # dump_only fields can't be set by clients, so nobody can inject user_id.
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    # Amounts must be positive and fit the Numeric(10, 2) column.
    amount = fields.Float(required=True, validate=validate.Range(min=0.01, max=99999999.99))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(allow_none=True, load_default=None)
    # Accepts "YYYY-MM-DD". Defaults to today when omitted on create.
    date = fields.Date(load_default=date.today)


user_schema = UserSchema()
signup_schema = SignupSchema()
login_schema = LoginSchema()
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)