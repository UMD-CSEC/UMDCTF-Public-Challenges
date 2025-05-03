import { useEffect, useState } from "react";
import { API_URL } from "../../constants";
import SmallPost from "../../ui/SmallPost";

interface MyPost {
  postId: string;
  title: string;
  likes: number;
}

interface AccountInfo {
  username: string;
  posts: MyPost[];
  flag?: string;
}


export default function Account() {
  const [account, setAccount] = useState<AccountInfo>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    fetch(`${API_URL}/me`, {
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load account info");
        return res.json();
      })
      .then(setAccount)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="p-6 bg-white min-h-screen">
      <h1 className="text-3xl font-extrabold text-[#52a535] mb-6 text-center">
        Account Summary
      </h1>

      {error && <p className="text-red-600 text-center mb-4">{error}</p>}

      {account && (
        <>
          <div className="text-center text-gray-800 mb-8 space-y-2">
            <p className="text-xl font-semibold">Username: {account.username}</p>
            <p className="text-lg">Current Session Number: {window.sessionNumber ? window.sessionNumber : "undefined"}</p>

            {"flag" in account && account.flag && (
              <div className="mt-4 text-green-700 font-medium">
                <p>Wow, an admin liked your post! ⛏️</p>
                <p>Your flag is: {account.flag}</p>
              </div>
            )}
          </div>

          <h2 className="text-2xl font-bold text-[#52a535] mb-4 pl-4">
            Your Posts
          </h2>
          {account.posts.length === 0 ? (
            <p className="pl-4 text-gray-600 italic">You haven't posted anything yet.</p>
          ) : (
            <div className="flex flex-wrap justify-start gap-6 pl-4">
              {account.posts.map((post) => (
                <SmallPost
                  key={post.postId}
                  postId={post.postId}
                  title={post.title}
                  username={account.username}
                  likes={post.likes}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
