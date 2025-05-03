import { Link } from "react-router-dom";
import { useLoggedIn } from "../util";
import { useEffect } from "react";
import { API_URL } from "../constants";

export default function NavBar() {
  const [loggedIn, setLoggedIn] = useLoggedIn();

  useEffect(() => {
    (async () => {
      const response = await fetch(`${API_URL}/me`, { credentials: "include" });
      if (response.ok) {
        setLoggedIn(true);
      }
    })();
  });

  return (
    <nav className="bg-[#52a535] shadow-lg p-4 mb-8">
      <div className="flex items-center justify-between">
        <Link to="/" className="text-xl font-semibold tracking-wide text-white cursor-pointer">Minecraft Movie Fanclub</Link>
        <div className="space-x-6">
          <Link to="/create-post" className="text-white hover:underline cursor-pointer">Create a Post</Link>
          {loggedIn ? <Link to="/account" className="text-white hover:underline cursor-pointer">Account</Link>
            : <Link to="/login" className="text-white hover:underline cursor-pointer">Login / Register</Link>}
        </div>
      </div>
    </nav>
  );
}