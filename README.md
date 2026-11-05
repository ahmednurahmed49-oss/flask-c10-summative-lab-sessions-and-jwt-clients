# Personal Expense Tracker API

## Description

A Flask REST API for user registration, JWT authentication, and personal expense management. Each user can only manage their own expenses.

## Technologies

- Python 3.8+
- Flask and Flask-RESTful
- Flask-SQLAlchemy and Flask-Migrate
- Flask-Bcrypt
- Flask-JWT-Extended
- SQLite
- Pipenv

## Features

- User signup and login
- Bcrypt password hashing
- JWT authentication
- Current-user endpoint
- Expense CRUD operations
- Pagination
- User-specific expense access
- Input validation
- Database migrations and seed data

## Installation

From the project root:

    pipenv install

## Database Setup

    cd server
    pipenv run flask --app app db upgrade

## Seed the Database

From the server directory:

    pipenv run python seed.py

Sample development accounts:

| Username | Password |
|---|---|
| alice | AlicePass123! |
| bob | BobPass123! |

Do not use these sample credentials in production.

## Run the API

From the server directory:

    pipenv run python app.py

API address: http://localhost:5555

## Authentication

The API uses JSON Web Tokens (JWT).

Signup and login return a token and user object. Include the token in protected requests:

    Authorization: Bearer YOUR_ACCESS_TOKEN

Tokens expire after one hour.

## Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /signup | Register a user |
| POST | /login | Log in |
| GET | /me | Get the authenticated user |
| DELETE | /logout | Revoke the current JWT access token |

## Expense Endpoints

All expense endpoints require JWT authentication.

| Method | Endpoint | Description |
|---|---|---|
| GET | /expenses | List expenses with pagination |
| POST | /expenses | Create an expense |
| GET | /expenses/<id> | Retrieve one expense |
| PATCH | /expenses/<id> | Update an expense |
| DELETE | /expenses/<id> | Delete an expense |

## Create an Expense

POST /expenses

Example JSON:

    {
      "title": "Groceries",
      "amount": 1500,
      "category": "Food",
      "date": "2026-11-05"
    }

The date is optional. If omitted, the current date is used.

## Pagination

Use:

    GET /expenses?page=1&per_page=10

- page defaults to 1.
- per_page defaults to 10.
- Maximum per_page is 100.

The response includes expenses, page, per_page, total, and pages.

## Data Models

### User

- id
- username
- _password_hash
- expenses relationship

### Expense

- id
- title
- amount
- category
- date
- user_id

## Validation and Security

- Usernames cannot be empty and must be unique.
- Signup passwords require at least eight characters.
- Passwords are hashed using Bcrypt.
- Password hashes are not exposed through the API.
- Protected routes require a valid JWT.
- Users cannot access another user's expenses.
- Expense amounts must be greater than zero.
- Dates must use YYYY-MM-DD format.
- Pagination is limited to 100 records per page.

## Frontend Clients

- client-with-jwt: JWT-based client for this backend.
- client-with-sessions: Alternative session-based example.

This backend uses JWT authentication.

## Database Migrations

From the server directory:

    pipenv run flask --app app db migrate -m "describe your changes"
    pipenv run flask --app app db upgrade
