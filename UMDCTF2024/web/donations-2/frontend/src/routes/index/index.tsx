import UserCard from "../../components/UserCard";

export default function Index() {
  return <>
      <h1>Welcome to donations. Can you get the most donations?</h1>
      <br />
      <h2>Top Donated:</h2>
      <div className="flex flex-wrap gap-4">
        {Array.from({ length: 7 }, () => <UserCard/>)}
      </div>
  </>
}