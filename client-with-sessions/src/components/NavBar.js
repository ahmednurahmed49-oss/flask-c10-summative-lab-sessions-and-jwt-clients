import React from "react";
import styled from "styled-components";
import { Button } from "../styles";

function NavBar({ user, setUser }) {
  function handleLogoutClick() {
    fetch("/logout", { method: "DELETE" }).then((r) => {
      if (r.ok) {
        setUser(null);
      }
    });
  }

  return (
    <Wrapper>
      <Logo>Expense Tracker</Logo>

      <Nav>
        <Welcome>Welcome, {user.username}</Welcome>
        <Button variant="outline" onClick={handleLogoutClick}>
          Logout
        </Button>
      </Nav>
    </Wrapper>
  );
}

const Wrapper = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 35px;
  background: #101c3a;
  color: white;
`;

const Logo = styled.h1`
  font-size: 25px;
  margin: 0;
  color: white;
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const Welcome = styled.span`
  font-size: 14px;
  color: #dbe4ff;
`;

export default NavBar;