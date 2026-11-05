# Personal Expense Tracker

## Description

A personal expense tracker built with a Flask REST API and a React frontend.

The backend uses Flask sessions for authentication and SQLAlchemy for database-backed expense management. Each authenticated user can access only their own expenses.

## Technologies

- Python 3.8
- Flask
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- SQLite
- Pipenv
- React

## Features

- User registration and login
- Bcrypt password hashing
- Flask session authentication
- Session checking and logout
- Database-backed expense CRUD operations
- User-specific expense access
- Expense input validation
- Expense pagination
- Database migrations
- Sample seed data
- Automated backend tests

## Project Structure

- `server/` - Flask backend, API routes, models, migrations, and tests
- `client-with-sessions/` - Session-based React frontend

## Installation

Install backend dependencies from the project root:

    pipenv install

Install frontend dependencies:

    cd client-with-sessions
    npm ci

## Database Setup

From the project root:

    cd server
    pipenv run flask --app app db upgrade

SQLite is used by default.

You can configure another database using the `DATABASE_URL` environment variable.

## Seed the Database

From the `server` directory:

    pipenv run python seed.py

Sample development accounts:

| Username | Password |
|---|---|
| alice | AlicePass123! |
| bob | BobPass123! |

Do not use these sample credentials in production.

## Run the Backend

From the `server` directory:

    pipenv run python app.py

The API runs at:

    http://localhost:5555

## Run the Frontend

Open another terminal:

    cd ~/flask-c10-summative-lab-sessions-and-jwt-clients/client-with-sessions
    npm start

The React development server uses the backend proxy at:

    http://localhost:5555

## Authentication

Authentication uses Flask sessions. Successful signup and login establish a session using a session cookie.

The frontend must send requests with credentials enabled when communicating with the backend.

### Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/signup` | Register a user and establish a session |
| POST | `/login` | Authenticate a user and establish a session |
| GET | `/check_session` | Check the current session |
| DELETE | `/logout` | Clear the current session |

### Signup Request

    {
      "username": "alice",
      "password": "AlicePass123!",
      "password_confirmation": "AlicePass123!"
    }

### Login Request

    {
      "username": "alice",
      "password": "AlicePass123!"
    }

## Expense API

All expense endpoints require an authenticated Flask session.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/expenses` | List the current user's expenses |
| POST | `/expenses` | Create an expense |
| GET | `/expenses/<id>` | Retrieve one of the user's expenses |
| PATCH | `/expenses/<id>` | Update one of the user's expenses |
| DELETE | `/expenses/<id>` | Delete one of the user's expenses |

Users cannot access expenses belonging to other users.

### Create an Expense

Send a POST request to `/expenses` with a JSON body:

    {
      "title": "Groceries",
      "amount": 1500,
      "category": "Food",
      "date": "2026-11-05"
    }

The date is optional. If omitted, the model uses its configured default.

### Pagination

Use query parameters:

    GET /expenses?page=1&per_page=10

- `page` defaults to 1.
- `per_page` defaults to 10.
- Maximum `per_page` is 100.

The response includes:

- `expenses`
- `page`
- `per_page`
- `total`
- `pages`

Note: The current React frontend's expense entries are managed in frontend state. The backend expense API supports database persistence, but the frontend expense interface still needs to be connected to these endpoints for expenses to persist through the UI.

## Data Models

### User

- `id`
- `username`
- `_password_hash`
- `expenses` relationship

### Expense

- `id`
- `title`
- `amount`
- `category`
- `date`
- `user_id`

## Validation and Security

- Usernames cannot be empty and must be unique.
- Signup passwords require at least eight characters.
- Passwords are hashed using Bcrypt.
- Password hashes are not exposed through API responses.
- Expense endpoints require an authenticated session.
- Users cannot access another user's expenses.
- Expense amounts must be greater than zero.
- Dates must use `YYYY-MM-DD` format.
- Pagination is limited to 100 records per page.

## Running Backend Tests

From the project root:

    cd server
    pipenv run pytest -v

The tests cover authentication, password hashing, expense CRUD, pagination, validation, and user-specific access restrictions.
