import { FormEvent, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_URL } from "../../constants";

export default function CreatePost() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState<string>();
  const navigate = useNavigate();

  const handleSubmit = useCallback(async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const response = await fetch(`${API_URL}/create-post`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include",
      body: JSON.stringify({ title, content })
    });

    if (!response.ok) {
      setError(await response.text());
      return;
    }

    const postId = await response.text();
    navigate(`/post?postId=${postId}`);
  }, [title, content, navigate]);

  return (
    <div className="flex justify-center items-center">
      <form
        className="w-full max-w-md rounded-xl shadow-md overflow-hidden bg-white"
        onSubmit={handleSubmit}
      >
        <div className="bg-[#52a535] p-4">
          <h2 className="text-white text-xl font-bold">Create a Post</h2>
        </div>

        <div className="p-6 space-y-4">
          {error && (
            <p className="text-sm text-red-600 font-medium">{error}</p>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-[#52a535] focus:border-[#52a535]"
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
            <textarea
              className="w-full h-32 px-3 py-2 border rounded-md shadow-sm resize-none focus:outline-none focus:ring-[#52a535] focus:border-[#52a535]"
              value={content}
              onChange={e => setContent(e.target.value)}
              required
            />
          </div>

          <div className="text-right">
            <button
              type="submit"
              className="cursor-pointer px-4 py-2 bg-[#52a535] text-white text-sm font-medium rounded-md hover:bg-green-600 transition"
            >
              📤 Submit Post
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
