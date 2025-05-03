import { FormEvent, useCallback, useState } from "react";
import { API_URL } from "../../constants";
import { useNavigate } from "react-router-dom";
import { useLoggedIn } from "../../util";

export default function LoginForm() {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const [_, setLoggedIn] = useLoggedIn();
  const navigate = useNavigate();

  const handleSubmit = useCallback(async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const endpoint = mode === "login" ? "/login" : "/register";

    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      setError(await response.text());
      return;
    }

    setLoggedIn(true);
    navigate("/");
  }, [username, password, mode, navigate]);

  return (
    <div className="flex justify-center items-center">
      <div className="w-full max-w-md p-8 bg-white rounded-xl shadow-md">
        <h2 className="text-2xl font-bold text-center text-[#52a535] mb-6">
          {mode === "login" ? "Login" : "Register"}
        </h2>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-[#52a535] focus:border-[#52a535]"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-[#52a535] focus:border-[#52a535]"
              required
            />
          </div>

          {error && (
            <p className="text-red-600 text-sm font-medium">{error}</p>
          )}

          <button
            type="submit"
            className="cursor-pointer w-full py-2 px-4 bg-[#52a535] text-white rounded-md font-semibold hover:bg-green-600 transition"
          >
            {mode === "login" ? "Log In" : "Sign Up"}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            {mode === "login" ? "Don't have an account?" : "Already registered?"}
            <button
              type="button"
              onClick={() => setMode(mode === "login" ? "register" : "login")}
              className="cursor-pointer ml-1 text-[#52a535] font-medium hover:underline"
            >
              {mode === "login" ? "Register" : "Login"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
