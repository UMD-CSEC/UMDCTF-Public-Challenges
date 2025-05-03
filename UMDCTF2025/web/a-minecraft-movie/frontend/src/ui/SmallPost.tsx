import { Link } from "react-router-dom";

export default function SmallPost({ postId, title, username, likes }: {
  postId: string;
  title: string;
  username: string;
  likes: number;
}) {
  return <Link
    key={postId}
    to={`/post?postId=${postId}`}
    className="w-72 bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition transform hover:scale-[1.01]"
  >
    <div className="bg-[#52a535] text-white px-4 py-2 rounded-t-xl font-bold">
      {title}
    </div>
    <div className="p-4 space-y-2 text-sm text-gray-700">
      <p><strong>By:</strong> {username}</p>
      <p><strong>Likes:</strong> {likes}</p>
    </div>
  </Link>
}