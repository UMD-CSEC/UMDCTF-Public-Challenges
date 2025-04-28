import { Link, Outlet } from "react-router-dom";

export default function Root() {
  const username = localStorage.getItem("username");

  function logOut() {
    localStorage.removeItem("username");
    window.location.reload();
  }

  let mainNavLink;
  if (username) {
    mainNavLink = [
      <span className="text-xl"><Link to={`/user?username=${username}`}>Profile</Link></span>,
      <span className="text-xl" onClick={logOut}>Log Out</span>
    ]
  } else if (username === null) {
    mainNavLink = <span className="text-xl"><Link to="/login">Log In</Link></span>
  } else {
    mainNavLink = undefined;
  }

  return <>
    <div className="p-8 bg-red-400 flex">
      <div>
        <span className="text-5xl"><Link to="/">Donations</Link></span>
      </div>
      <div className="flex grow justify-end items-center gap-4">
        {mainNavLink}
      </div>
    </div>
    <div className="p-16">
      <Outlet/>
    </div>
  </>
}