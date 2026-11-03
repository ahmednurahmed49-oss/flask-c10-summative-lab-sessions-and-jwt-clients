# Expense Tracker API

A Flask API for signing up, logging in, and managing personal expenses. It uses session-based authentication, Bcrypt password hashing, and pagination.

## Requirements

- Python 3.8+
- Pipenv

## Setup

```bash
git clone <your-repo-url>
cd <your-project-folder>
pipenv install
pipenv shell

flask db upgrade
python seed.py
```

The seed script creates sample data. For the demo account, use:

- Username: `demo`
- Password: `password123`

## Run the app

```bash
python app.py
```

The API runs at `http://localhost:5555`.

## Run tests

```bash
pytest
```

## API endpoints

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/signup` | Create an account and log in |
| POST | `/login` | Log in |
| GET | `/check_session` | Check the current login |
| DELETE | `/logout` | Log out |

### Expenses

You must be logged in to use these endpoints. You can only access your own expenses.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/expenses?page=1&per_page=5` | List expenses |
| POST | `/expenses` | Create an expense |
| PATCH | `/expenses/<id>` | Update an expense |
| DELETE | `/expenses/<id>` | Delete an expense |

Expense requests and responses use JSON. The list endpoint returns paginated results.