import { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { API_URL } from "../../constants";
import DOMPurify from "dompurify";
import { ensureSessionNumber } from "../../util";

interface PostData {
  title: string;
  content: string;
  username: string;
  likes: number;
  likedByAdmin: boolean;
}

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function isUUID(candidate: string) {
  return UUID_REGEX.test(candidate);
}

export default function Post() {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const postId = queryParams.get("postId");

  const [post, setPost] = useState<PostData>();
  const [postError, setPostError] = useState<string>();

  const [likeError, setLikeError] = useState<string>();

  const refreshPost = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/post?postId=${postId}`);
      if (!response.ok) {
        setPostError(await response.text());
        return;
      }
      setPost(await response.json());
    } catch (err) {
      setPostError("Failed to fetch post.");
    }
  }, [postId, setPost, setPostError]);

  const changeLikes = useCallback(async (likes: number) => {
    await ensureSessionNumber();

    const response = await fetch(`${API_URL}/legacy-social`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: `sessionNumber=${window.sessionNumber}&postId=${postId}&likes=${likes}`,
      credentials: "include"
    });

    if (!response.ok) {
      setLikeError(await response.text());
      return;
    }

    await refreshPost();
  }, [postId, refreshPost, setLikeError]);

  useEffect(() => {
    if (postId != null && isUUID(postId)) {
      refreshPost();
    }
  }, [postId]);

  if (postId != null && !isUUID(postId)) {
    return (
      <div className="flex justify-center items-center">
        <p className="text-lg font-semibold text-red-600">Invalid post id!</p>
      </div>
    );
  }

  if (postError) {
    return (
      <div className="flex justify-center items-center">
        <p className="text-lg font-semibold text-red-600">Error: {postError}</p>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="flex justify-center items-center">
        <p className="text-lg font-semibold text-gray-600">Loading...</p>
      </div>
    );
  }

  const clean = DOMPurify.sanitize(post.content, {
    ADD_TAGS: ['iframe'],
    ADD_ATTR: ['allow', 'allowfullscreen', 'frameborder', 'scrolling', 'src', 'width', 'height']
  });

  return (
    <div className="flex justify-center items-center">
      <div className="w-xl rounded-xl shadow-md overflow-hidden">
        <div className="bg-[#52a535] p-4">
          <h2 className="text-white text-xl font-bold">{post.title}</h2>
          <p className="text-white text-sm">Posted by <span className="font-semibold">@{post.username}</span></p>
        </div>

        <div className="p-6 bg-white space-y-4">
          <div
            className="text-gray-700"
            dangerouslySetInnerHTML={{ __html: clean }}
          />

          {post.likedByAdmin && (
            <div className="bg-yellow-100 text-yellow-800 text-sm font-medium px-4 py-2 rounded-md shadow">
              🌟 This post was liked by an admin!
            </div>
          )}

          {likeError && (
            <p className="text-sm text-red-600 font-medium">{likeError}</p>
          )}

          <div dangerouslySetInnerHTML={{ __html: "<!-- TODO: Migrate social endpoint, switch to useState/useContext -->" }}></div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">{post.likes} Likes</span>
            <div className="flex items-center space-x-2">
              <button
                className="cursor-pointer px-3 py-1 text-sm font-medium text-white bg-[#52a535] rounded-md hover:bg-green-600 transition"
                onClick={() => changeLikes(1)}
              >
                👍 Like
              </button>
              <button
                id="dislike-button"
                className="cursor-pointer px-3 py-1 text-sm font-medium text-white bg-red-500 rounded-md hover:bg-red-600 transition"
                onClick={() => changeLikes(-1)}
              >
                👎 Dislike
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
