import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  if (!user) return null;

  return (
    <nav className="bg-white border-b px-6 py-3 flex items-center justify-between">
      <div className="space-x-4">
        <Link to="/dashboard" className="text-slate-700 font-medium hover:underline">
          Dashboard
        </Link>
        <Link to="/live" className="text-slate-700 font-medium hover:underline">
          Live Detect
        </Link>
      </div>
      <div className="flex items-center space-x-4">
        <span className="text-slate-500 text-sm">{user.email}</span>
        <button onClick={handleLogout} className="text-red-600 text-sm hover:underline">
          Log out
        </button>
      </div>
    </nav>
  );
}