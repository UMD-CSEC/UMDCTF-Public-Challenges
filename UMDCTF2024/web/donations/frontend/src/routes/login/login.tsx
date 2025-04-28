import { FormEvent, useCallback, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../../globals";

export default function Login() {
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const onSubmit = useCallback(async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const username = e.currentTarget["username"].value;

    const response = await fetch(`${API_BASE_URL}/api/login`, {
      credentials: "include",
      method: "POST",
      mode: "cors",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({
        "username": username,
        "password": e.currentTarget["password"].value
      }).toString()
    });

    if (response.status === 200) {
      console.log("hi")
      localStorage.setItem("username", username);
      window.location.href = `/user?username=${username}`;
      return;
    }

    setError(await response.text());
  }, [navigate]);

  return <>
    <h1 className="text-3xl">Login</h1>
    <br />
    <form onSubmit={onSubmit}>
      <div>
        <label htmlFor="username">Username</label>
        &nbsp;
        <input id="username" className="border-2" type="text"></input>
      </div>
      <br />
      <div>
        <label htmlFor="password">Password</label>
        &nbsp;
        <input id="password" className="border-2" type="password" minLength={8}></input>
      </div>
      <br />
      <button className="p-2 bg-gray-300 rounded" type="submit">Log In</button>
    </form>
    <p className="text-red-600">{error}</p>
    <br />
    <p className="underline"><Link to="/register">Register</Link></p>
  </>
}