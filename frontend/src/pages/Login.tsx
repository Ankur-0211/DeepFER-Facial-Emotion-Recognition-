import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      if (err?.response?.status === 401) {
        setError("Invalid email or password");
      } else if (err?.message === "Network Error") {
        setError("Can't reach the server — is the backend running?");
      } else {
        setError("Something went wrong logging in. Check the console for details.");
      }
      console.error("login failed:", err);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="w-full max-w-sm bg-white p-8 rounded-xl shadow">
        <h1 className="text-2xl font-semibold mb-6 text-slate-800">Log in to DeepFER</h1>
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
          {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
          <button
            onClick={handleSubmit}
            className="w-full bg-slate-800 text-white rounded-lg py-2 font-medium"
          >
            Log in
          </button>
        </div>
        <p className="text-sm text-slate-500 mt-4">
          No account? <Link to="/register" className="underline">Register</Link>
        </p>
      </div>
    </div>
  );
}