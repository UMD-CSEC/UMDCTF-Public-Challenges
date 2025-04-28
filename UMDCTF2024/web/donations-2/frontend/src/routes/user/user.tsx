import { FormEvent, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom"
import { API_BASE_URL } from "../../globals";

interface UserInfo {
  username: string,
  url?: string,
  currency: number
}

export default function User() {
  const [searchParams] = useSearchParams();
  const [data, setData] = useState<UserInfo>();
  const [error, setError] = useState("");
  const [flag, setFlag] = useState<string>();

  const requestFlag = useCallback(async () => {
    const response = await fetch(`${API_BASE_URL}/api/flag`, {
      credentials: "include",
      mode: "cors"
    });
    if (response.status === 200) {
      setFlag(await response.text());
    }
  }, []);

  const loadData = useCallback(async (username: string) => {
    const response = await fetch(`${API_BASE_URL}/api/user?username=${username}`, {
      mode: "cors"
    });

    if (response.status !== 200) {
      setError(await response.text());
      return;
    }

    const newData = await response.json();
    setData(newData);

    if (localStorage.getItem("username") === newData.username && newData.currency >= 5_000) {
      requestFlag();
    }
  }, [requestFlag]);

  const donate = useCallback(async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (data) {
      const response = await fetch(`${API_BASE_URL}/api/donate`, {
        credentials: "include",
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          "to": data.username,
          "currency": e.currentTarget["currency"].value
        }).toString()
      });

      if (response.status === 200) {
        loadData(data.username);
        return;
      }

      setError(await response.text());
    }
  }, [data, loadData]);

  useEffect(() => {
    const username = searchParams.get("username");
    if (!username) {
      setError("Invalid username");
      return;
    }

    loadData(username);
  }, [loadData, searchParams]);

  if (!data) {
    return undefined;
  }

  return <div className="mx-40">
    <div className="border border-black">
      <div className="bg-red-400 p-2">
        <p className="text-center text-2xl">{data.username === "lisanalgaib" ? "Jeff Bezos" : data.username}</p>
      </div>
      <div className="h-48">
        {
          data.url
            ? (<div className="h-44 py-4 flex justify-center">
                <img className="max-w-full max-h-full" src={data.url}></img>
              </div>)
            : (<div className="h-44 py-4 flex justify-center">
                <span className="text-center">No image found.</span>
              </div>)
        }
      </div>
      <div className="p-4">
        <p>Currency: {data.currency}</p>
        {localStorage.getItem("username") !== data.username &&
          <form onSubmit={donate}>
            <label htmlFor="currency">Amount: </label>
            <input id="currency" className="border-2" type="number" min={0} />
            &nbsp;
            <button className="p-2 bg-gray-300 rounded" type="submit">Donate</button>
          </form>
        }
      </div>
    </div>
    {flag && 
      <p>Wow, you're rich! Your reward is {flag}.</p>
    }
    <p className="text-red-600">{error}</p>
  </div>
}