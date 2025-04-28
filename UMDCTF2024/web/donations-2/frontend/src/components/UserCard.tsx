import { Link } from "react-router-dom";

export default function UserCard() {
  return <div className="w-60 border border-black">
    <div className="bg-red-400 p-2">
      <p className="text-center text-2xl"><Link to="/user?username=lisanalgaib">Jeff Bezos</Link></p>
    </div>
    <div className="h-48">
      <div className="h-44 py-4 flex justify-center">
        <img className="max-w-full max-h-full" src="https://imageio.forbes.com/specials-images/imageserve/5bb22ae84bbe6f67d2e82e05/0x0.jpg?format=jpg&crop=1012,1013,x627,y129,safe&height=416&width=416&fit=bounds"></img>
      </div>
    </div>
    <p className="text-center">He needs more money</p>
  </div>
}