const express = require("express");
const { spawn } = require('node:child_process');

const app = express();

const indexHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Admin Bot Interface</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f9f9f9;
      padding: 2rem;
      max-width: 600px;
      margin: auto;
    }

    h1 {
      color: #2d8a39;
    }

    p {
      margin-top: 0.5rem;
      margin-bottom: 2rem;
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    input[type="text"] {
      padding: 0.5rem;
      font-size: 1rem;
    }

    input[type="submit"] {
      padding: 0.5rem;
      font-size: 1rem;
      background-color: #2d8a39;
      color: white;
      border: none;
      cursor: pointer;
    }

    input[type="submit"]:hover {
      background-color: #256f2f;
    }

    em {
      color: #aa0000;
    }
  </style>
</head>
<body>
  <h1>Admin Bot</h1>
  <p>Think you can get an admin to like your post? Put in your Post ID and they'll see for themselves!</p>
  <p><em>Note: The admin is <strong>very</strong> difficult to please.</em> They may dislike your post. Please give them a few seconds to log in.</p>

  <form action="/submit" method="POST">
    <label for="postId">Post ID:</label>
    <input type="text" id="postId" name="postId" pattern="[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}" required>
    <input type="submit" value="Submit for Judgement">
  </form>
</body>
</html>`;

app.get("/", (_req, res) => {
  res.send(indexHtml);
});

app.post("/submit", express.urlencoded({ extended: false }), (req, res) => {
  const { postId } = req.body
	if (!postId || !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(postId)) {
		return res.status(400).send("Invalid post ID");
	}

	try {
		console.log(`Sending ${postId} to bot`)
		spawn("node", ["bot.js", postId], { stdio: "inherit" })
		res.send("OK");
	} catch (e) {
		console.error(e);
		res.status(500).send("Something went wrong");
	}
});

const port = 4000;
app.listen(port, "0.0.0.0", () => {
	console.log(`Listening on http://localhost:${port}`)
})