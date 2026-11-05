import React, { useEffect, useState } from "react";
import NavBar from "./NavBar";
import Login from "../pages/Login";

function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("Dashboard");
  const [expenses, setExpenses] = useState([]);
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("Food");

  useEffect(() => {
    fetch("/check_session")
      .then((r) => r.json())
      .then((data) => setUser(data.id ? data : null))
      .catch(() => setUser(null));
  }, []);

  if (!user) return <Login onLogin={setUser} />;

  const total = expenses.reduce(
    (sum, expense) => sum + expense.amount,
    0
  );

  function addExpense(e) {
    e.preventDefault();

    if (!description.trim() || Number(amount) <= 0) return;

    setExpenses([
      ...expenses,
      {
        id: Date.now(),
        description,
        amount: Number(amount),
        category,
      },
    ]);

    setDescription("");
    setAmount("");
    setCategory("Food");
    setPage("Expenses");
  }

  const navStyle = {
    padding: "12px 20px",
    margin: "5px",
    border: "none",
    borderRadius: "8px",
    background: "#1e3a8a",
    color: "white",
    cursor: "pointer",
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f1f5f9" }}>
      <NavBar user={user} setUser={setUser} />

      <nav style={{ padding: "15px", background: "#172554" }}>
        {["Dashboard", "Expenses", "Add Expense", "Profile"].map((item) => (
          <button
            key={item}
            style={{
              ...navStyle,
              background: page === item ? "#3b82f6" : "#1e3a8a",
            }}
            onClick={() => setPage(item)}
          >
            {item}
          </button>
        ))}
      </nav>

      <main style={{ padding: "30px", maxWidth: "1100px", margin: "auto" }}>
        {page === "Dashboard" && (
          <>
            <h1>Expense Tracker Dashboard</h1>
            <p>Welcome back, {user.username}!</p>

            <div style={cardStyle}>
              <h3>Total Expenses</h3>
              <h1>KSh {total.toLocaleString()}</h1>
            </div>

            <div style={cardStyle}>
              <h3>Number of Transactions</h3>
              <h1>{expenses.length}</h1>
            </div>

            <button style={navStyle} onClick={() => setPage("Add Expense")}>
              + Add New Expense
            </button>
          </>
        )}

        {page === "Expenses" && (
          <>
            <h1>My Expenses</h1>
            {expenses.length === 0 ? (
              <p>No expenses recorded yet.</p>
            ) : (
              expenses.map((expense) => (
                <div key={expense.id} style={cardStyle}>
                  <strong>{expense.description}</strong>
                  <p>{expense.category}</p>
                  <h3>KSh {expense.amount.toLocaleString()}</h3>
                </div>
              ))
            )}
          </>
        )}

        {page === "Add Expense" && (
          <>
            <h1>Add New Expense</h1>
            <form onSubmit={addExpense} style={cardStyle}>
              <p>Description</p>
              <input
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. Shopping"
                style={inputStyle}
              />

              <p>Amount (KSh)</p>
              <input
                required
                type="number"
                min="0.01"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Enter amount"
                style={inputStyle}
              />

              <p>Category</p>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={inputStyle}
              >
                <option>Food</option>
                <option>Transport</option>
                <option>Shopping</option>
                <option>Bills</option>
                <option>Other</option>
              </select>

              <br /><br />
              <button type="submit" style={navStyle}>
                Save Expense
              </button>
            </form>
          </>
        )}

        {page === "Profile" && (
          <>
            <h1>My Profile</h1>
            <div style={cardStyle}>
              <h3>Account Information</h3>
              <p>Username: {user.username}</p>
              <p>Account ID: {user.id}</p>
              <p>Authentication: Session-based</p>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

const cardStyle = {
  background: "white",
  padding: "22px",
  margin: "15px 0",
  borderRadius: "12px",
  boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
};

const inputStyle = {
  width: "100%",
  padding: "12px",
  border: "1px solid #cbd5e1",
  borderRadius: "8px",
  marginTop: "5px",
};

export default App;