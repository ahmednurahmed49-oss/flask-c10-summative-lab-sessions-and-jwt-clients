import random

from faker import Faker

from config import app, db
from models import Expense, User

fake = Faker()
CATEGORIES = ["Food", "Transport", "Rent", "Fun", "Health", "Shopping"]


def seed():
    print("Clearing old data...")
    Expense.query.delete()
    User.query.delete()

    print("Creating users...")
    users = []
  
    for username in ["Peter"] + [fake.unique.user_name() for _ in range(3)]:
        user = User(username=username)
        user.password_hash = "TONKATONKA"
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    print("Creating expenses...")
    for user in users:
        for _ in range(12):  
            db.session.add(
                Expense(
                    title=fake.sentence(nb_words=3).rstrip("."),
                    amount=round(random.uniform(2, 250), 2),
                    category=random.choice(CATEGORIES),
                    user_id=user.id,
                )
            )
    db.session.commit()
    print(f"Done! {User.query.count()} users, {Expense.query.count()} expenses.")


if __name__ == "__main__":
    with app.app_context():
        seed()