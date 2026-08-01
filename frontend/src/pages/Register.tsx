import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { register } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await register(email, password);
    navigate("/login");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="w-full max-w-sm bg-white p-8 rounded-xl shadow">
        <h1 className="text-2xl font-semibold mb-6 text-slate-800">Create your account</h1>
        <div>
          <label className="block text-sm text-slate-600 mb-1">Email</label>
          <input
            className="w-full border rounded-lg px-3 py-2 mb-4"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            required
          />
          <label className="block text-sm text-slate-600 mb-1">Password</label>
          <input
            className="w-full border rounded-lg px-3 py-2 mb-4"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
          />
          <button
            onClick={handleSubmit}
            className="w-full bg-slate-800 text-white rounded-lg py-2 font-medium"
          >
            Register
          </button>
        </div>
        <p className="text-sm text-slate-500 mt-4">
          Already have an account? <Link to="/login" className="underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}