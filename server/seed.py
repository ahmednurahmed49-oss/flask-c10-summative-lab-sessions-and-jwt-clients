from datetime import date, timedelta

from config import app, db
from models import User, Expense


def seed_data():
    with app.app_context():
        db.create_all()

        sample_users = [
            {
                "username": "alice",
                "password": "AlicePass123!"
            },
            {
                "username": "bob",
                "password": "BobPass123!"
            }
        ]

        for user_data in sample_users:
            user = User.query.filter_by(
                username=user_data["username"]
            ).first()

            if user is None:
                user = User(username=user_data["username"])
                user.password_hash = user_data["password"]

                db.session.add(user)
                db.session.flush()

                print("Created user:", user.username)
            else:
                print("User already exists:", user.username)

            if not user.expenses:
                sample_expenses = [
                    {
                        "title": "Groceries",
                        "amount": 2500,
                        "category": "Food",
                        "date": date.today()
                    },
                    {
                        "title": "Transport",
                        "amount": 800,
                        "category": "Travel",
                        "date": date.today() - timedelta(days=1)
                    },
                    {
                        "title": "Internet",
                        "amount": 1500,
                        "category": "Utilities",
                        "date": date.today() - timedelta(days=2)
                    }
                ]

                for expense_data in sample_expenses:
                    expense = Expense(**expense_data)
                    user.expenses.append(expense)

                print("Added sample expenses for:", user.username)
            else:
                print("Expenses already exist for:", user.username)

        db.session.commit()
        print("\nDatabase seeding completed successfully.")


if __name__ == "__main__":
    seed_data()
