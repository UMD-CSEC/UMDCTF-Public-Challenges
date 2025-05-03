const express = require("express");
const session = require("express-session");
const cors = require("cors");

const app = express();
app.set("trust proxy", true);

const port = 3000;

const users = {
  admin: {
    password: "1ca937afd336064ffc5b6106d3a6d49a",
    sessionNumber: 0
  },
  chaoticmovieenjoyer: {
    password: crypto.randomUUID(),
    sessionNumber: 0
  },
  diggravelmineiron: {
    password: crypto.randomUUID(),
    sessionNumber: 0
  },
  alex: {
    password: crypto.randomUUID(),
    sessionNumber: 0
  },
  potatofarmer: {
    password: crypto.randomUUID(),
    sessionNumber: 0
  },
  thamid: {
    password: crypto.randomUUID(),
    sessionNumber: 0
  }
};

const frontendUrl = process.env.FRONTEND_URL || "http://localhost:5173";
const prod = frontendUrl.startsWith("https");

app.use(cors({
  origin: frontendUrl,
  credentials: true
}));
app.use(express.json());
app.use(session({
  secret: "a858919384418e2342717891ca07ed32",
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: prod,
    sameSite: prod ? "none" : "lax"
  }
}));

app.post("/register", (req, res) => {
  const { username, password } = req.body;
  if (username.length < 8 || password.length < 8) {
    return res.status(400).send("Username and password must be at least 8 characters!");
  }
  if (users[username]) {
    return res.status(403).send("User already exists");
  }

  users[username] = { password, sessionNumber: 0 };

  req.session.user = username;
  res.sendStatus(204);
});

app.post("/login", (req, res) => {
  const { username, password } = req.body;
  if (!users[username] || users[username].password !== password) {
    return res.status(401).send("Invalid credentials");
  }

  req.session.user = username;
  res.sendStatus(204);
});

app.post("/start-session", (req, res) => {
  if (!req.session.user) {
    return res.status(401).send("Not authenticated!");
  }

  const user = users[req.session.user];
  const sessionNumber = ++user.sessionNumber;

  res.json({ sessionNumber });
});

const defaultPosts = [
  {
    postId: "dde72e1e-6601-4575-b0ac-4eaae62aa315",
    title: "CHICKEN JOCKEY 🐔🧟",
    content: '<div class="flex justify-center"><iframe width="560" height="315" src="https://www.youtube.com/embed/vWQpiMd-v0A?si=t-7JeZ9JditR_Ns8" title="YouTube video player" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div><p>🍿🍿🍿 not sure why i got kicked out of the movie theater</p>',
    username: "chaoticmovieenjoyer",
    likes: 1,
    likedByAdmin: true,
  },
  {
    postId: "58eb18f6-1fb8-455c-b0cb-b764ec1f7048",
    title: "FLINT AND STEEL 🔥🪓",
    content: '<div class="flex justify-center"><iframe width="560" height="315" src="https://www.youtube.com/embed/LabBY9A1C3k?si=8SQVDg1ofZKyUs31" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div><p>bro lit the whole theater 💀</p>',
    username: "diggravelmineiron",
    likes: 1,
    likedByAdmin: true
  },
  {
    postId: "2cedd45a-1dcb-4d47-a047-0814a9345e38",
    title: "I...AM STEVE 🧍‍♂️🧱",
    content: '<div class="flex justify-center"><iframe width="560" height="315" src="https://www.youtube.com/embed/yILoDaIB4Y0?si=ToBvOyTYBFKoYlkJ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div><p>bro does NOT look like minecraft steve 🙏</p>',
    username: "alex",
    likes: 1,
    likedByAdmin: true
  },
  {
    postId: "5e7e16c8-6dd1-4ed4-840f-30a3877c888c",
    title: "that's a legend 🐷",
    content: '<div class="flex justify-center"><iframe width="560" height="315" src="https://www.youtube.com/embed/GXWsZxJpaos?si=-nyANMBduuwkWWFZ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div><p>rip technoblade 🕊️</p>',
    username: "potatofarmer",
    likes: 1,
    likedByAdmin: true
  },
  {
    postId: "008333e9-25ea-445c-8fbe-3b8cb51e2a55",
    title: "THE NETHER 🔥💀🌋",
    content: '<div class="flex justify-center"><iframe width="560" height="315" src="https://www.youtube.com/embed/tClZt6ab1yo?si=F-yeqmEahTA1-4RM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div><p>bro did NOT say the nether 😭</p>',
    username: "thamid",
    likes: 1,
    likedByAdmin: true
  }
]
const posts = [...defaultPosts];

app.get("/top-posts", (_, res) => {
  const copied = [];
  for (const { postId, title, username, likes } of defaultPosts) {
    copied.push({ postId, title, username, likes });
  }

  res.json(copied);
});

app.get("/post", (req, res) => {
  const postId = req.query.postId;
  for (const post of posts) {
    if (post.postId === postId) {
      const postCopy = { ...post };
      delete postCopy.postId;

      res.json(postCopy);
      return;
    }
  }

  res.status(404).send("Post not found!");
});

app.get("/me", (req, res) => {
  console.log(req.headers);
  if (!req.session.user) {
    return res.status(401).send("Not authenticated!");
  }

  let anyLikedByAdmin = false;
  const copied = [];
  for (const { postId, title, username, likes, likedByAdmin } of posts) {
    if (username === req.session.user) {
      copied.push({ postId, title, likes });

      if (likedByAdmin) {
        anyLikedByAdmin = true;
      }
    }
  }

  const result = { username: req.session.user, posts: copied };
  if (anyLikedByAdmin) {
    result.flag = "UMDCTF{I_y3@RNeD_f0R_7HE_Min3S}";
  }

  res.json(result);
});

app.post("/create-post", (req, res) => {
  if (!req.session.user) {
    return res.status(401).send("Not authenticated!");
  }

  const { title, content } = req.body;
  if (typeof title !== "string" || typeof content !== "string") {
    return res.status(400).send("Invalid post!");
  }

  const postId = crypto.randomUUID();
  posts.push({
    postId,
    title,
    content,
    username: req.session.user,
    likes: 0,
    likedByAdmin: false
  });

  res.send(postId);
});

app.post("/legacy-social", express.urlencoded({ extended: false }), (req, res) => {
  if (!req.session.user) {
    return res.status(401).send("Not authenticated!");
  }
  
  let { postId, likes: likesValue } = req.body;
  if (Array.isArray(likesValue)) {
    likesValue = likesValue[0];
  }

  const likes = Number(likesValue);
  if (isNaN(likes)) {
    return res.status(400).send("Invalid like count!");
  }
  if (typeof postId !== "string" || postId.trim() === "") {
    return res.status(400).send("Invalid post id!");
  }

  for (const post of posts) {
    if (post.postId === postId) {
      post.likes += likes;

      if (req.session.user === "admin" && likes > 0) {
        post.likedByAdmin = true;
      }

      res.sendStatus(204);
      return;
    }
  }

  res.status(404).send("Post not found!");
});

app.listen(port, "0.0.0.0", () => {
  console.log(`App listening on port ${port}`);
});
