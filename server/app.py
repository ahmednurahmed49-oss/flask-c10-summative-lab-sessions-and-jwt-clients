from config import app, api
from routes.auth import Signup, Login, Logout, CheckSession
from routes.expenses import ExpenseList, ExpenseDetail

api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")
api.add_resource(ExpenseList, "/expenses")
api.add_resource(ExpenseDetail, "/expenses/<int:id>")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
