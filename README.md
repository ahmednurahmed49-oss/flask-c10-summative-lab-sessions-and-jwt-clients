# Personal Expense Tracker

## Description

A Flask application with user registration, authentication, and personal expense management.

The backend supports two authentication methods:

- JWT authentication for protected expense API operations.
- Flask sessions for session-based login and session checking.

Each user can only access their own expenses.

## Technologies

- Python 3.8
- Flask
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Flask-JWT-Extended
- SQLite
- Pipenv
- React

## Features

- User registration and login
- Bcrypt password hashing
- JWT access tokens
- Flask session authentication
- Current-user endpoint
- Expense CRUD operations
- Pagination
- User-specific expense access
- Input validation
- Database migrations
- Sample seed data

## Project Structure

- `server/` - Flask backend and API
- `client-with-jwt/` - JWT-based React frontend
- `client-with-sessions/` - Session-based React frontend

## Installation

Install the backend dependencies from the project root:

    pipenv install

Install frontend dependencies separately:

    cd client-with-jwt
    npm ci

    cd ../client-with-sessions
    npm ci

## Database Setup

From the project root:

    cd server
    pipenv run flask --app app db upgrade

The application uses SQLite by default.

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

## Authentication

### JWT authentication

Signup and login return a user object and a JWT access token.

Send the token with protected requests:

    Authorization: Bearer YOUR_ACCESS_TOKEN

Access tokens expire after one hour.

### Session authentication

Signup and login also establish a Flask session.

The session endpoints allow a client to check the currently authenticated user and log out.

The session-based frontend uses these authentication endpoints. Its expense entries are maintained in frontend state; it does not use the backend expense CRUD endpoints.

## Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/signup` | Register a user and establish authentication |
| POST | `/login` | Authenticate a user |
| GET | `/check_session` | Check the current Flask session |
| GET | `/me` | Get the JWT-authenticated user |
| DELETE | `/logout` | End the session and/or revoke the current JWT |

## Expense Endpoints

All expense endpoints require JWT authentication.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/expenses` | List expenses with pagination |
| POST | `/expenses` | Create an expense |
| GET | `/expenses/<id>` | Retrieve one expense |
| PATCH | `/expenses/<id>` | Update an expense |
| DELETE | `/expenses/<id>` | Delete an expense |

Users can only retrieve, update, or delete their own expenses.

## Create an Expense

Send a POST request to `/expenses` with a JSON body:

    {
      "title": "Groceries",
      "amount": 1500,
      "category": "Food",
      "date": "2026-11-05"
    }

The date is optional. If omitted, the current date is used.

## Pagination

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

### TokenBlocklist

Stores revoked JWT identifiers so logged-out tokens cannot be reused.

## Validation and Security

- Usernames cannot be empty and must be unique.
- Signup passwords require at least eight characters.
- Passwords are hashed using Bcrypt.
- Password hashes are not exposed through API responses.
- Expense endpoints require a valid JWT.
- Users cannot access another user's expenses.
- Expense amounts must be greater than zero.
- Dates must use `YYYY-MM-DD` format.
- Pagination is limited to 100 records per page.
- Revoked JWTs are checked against the token blocklist.

## Running the Frontends

Build either frontend from its own directory:

    npm run build

For local development, start the backend on port 5555 and run the chosen React client using:

    npm start

Both frontend projects have a development proxy configured for the backend at `http://localhost:5555`.

## Running Backend Tests

From the project root:

    cd server
    pipenv run pytest -v

The test suite covers authentication, session handling, expense CRUD, validation, pagination, and user ownership.

## Database Migrations

From the `server` directory:

Create a migration after changing models:

    pipenv run flask --app app db migrate -m "describe your changes"

Apply migrations:

    pipenv run flask --app app db upgrade
