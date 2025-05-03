import { useEffect, useState } from "react";
import { API_URL } from "../../constants";
import SmallPost from "../../ui/SmallPost";

interface PostSummary {
	postId: string;
	title: string;
	username: string;
	likes: number;
}

export default function Home() {
	const [posts, setPosts] = useState<PostSummary[]>([]);
	const [error, setError] = useState<string>();

	useEffect(() => {
		fetch(`${API_URL}/top-posts`)
			.then((res) => {
				if (!res.ok) throw new Error("Failed to load posts");
				return res.json();
			})
			.then(newPosts => {
				setPosts(newPosts.sort((a: PostSummary, b: PostSummary) => b.likes - a.likes));
			})
			.catch((err) => setError(err.message));
	}, []);

	return (
		<div className="p-6 bg-white min-h-screen">
			<h1 className="text-3xl font-extrabold text-[#52a535] mb-6 text-center">
				Top Minecraft Movie Posts!!!!!!
			</h1>

			{error && <p className="text-red-600 text-center mb-4">{error}</p>}

			<div className="flex flex-wrap justify-start gap-6 pl-4">
				{posts.map((post) => (
					<SmallPost key={post.postId} postId={post.postId} title={post.title} username={post.username} likes={post.likes}></SmallPost>
				))}
			</div>
		</div>
	);
}
