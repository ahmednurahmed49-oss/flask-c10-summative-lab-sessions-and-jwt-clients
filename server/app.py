from pathlib import Path

from flask import send_from_directory

from config import app, api
from routes.auth import Signup, Login, Logout, CheckSession
from routes.expenses import ExpenseList, ExpenseDetail


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")
api.add_resource(ExpenseList, "/expenses")
api.add_resource(ExpenseDetail, "/expenses/<int:id>")


FRONTEND_BUILD = (
    Path(__file__).resolve().parent.parent
    / "client-with-sessions"
    / "build"
)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react_app(path):
    if path and (FRONTEND_BUILD / path).is_file():
        return send_from_directory(FRONTEND_BUILD, path)

    return send_from_directory(FRONTEND_BUILD, "index.html")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
