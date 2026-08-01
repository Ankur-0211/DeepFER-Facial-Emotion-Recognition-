import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../hooks/useAuth";
import Login from "../pages/Login";

test("renders login form fields", () => {
  render(
    <BrowserRouter>
      <AuthProvider>
        <Login />
      </AuthProvider>
    </BrowserRouter>
  );
  expect(screen.getByText(/log in to deepfer/i)).toBeInTheDocument();
  expect(screen.getByText(/email/i)).toBeInTheDocument();
});