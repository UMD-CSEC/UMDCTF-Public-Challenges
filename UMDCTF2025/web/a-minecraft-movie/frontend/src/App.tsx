import { Route, Routes } from 'react-router-dom';
import LoginForm from './routes/login/LoginForm';
import NavBar from './ui/NavBar';
import Post from './routes/post/Post';
import CreatePost from './routes/create-post/CreatePost';
import { useEffect, useState } from 'react';
import DOMPurify from "dompurify";
import Home from './routes/home/Home';
import Account from './routes/account/Account';
import { AccountContext } from './util';

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    DOMPurify.addHook("uponSanitizeElement", (node, data) => {
      if (data.tagName === "iframe" && node instanceof Element) {
        const src = node.getAttribute("src") || "";
        if (!src.startsWith("https://www.youtube.com/embed/")) {
          node.parentNode?.removeChild(node);
        }
      }
    });
  });

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <AccountContext.Provider value={[loggedIn, setLoggedIn]}>
        <NavBar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/post" element={<Post />} />
          <Route path="/create-post" element={<CreatePost />} />
          <Route path="/account" element={<Account />} />
        </Routes>
      </AccountContext.Provider>
    </div>
  );
}
