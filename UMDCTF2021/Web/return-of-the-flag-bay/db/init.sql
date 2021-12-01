CREATE DATABASE umdctf;
use umdctf;

CREATE TABLE users (
  username VARCHAR(20) NOT NULL UNIQUE,
  password VARCHAR(50) NOT NULL
);


-- CREATE TABLE posts (
--   username VARCHAR(20),
--   ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   picture VARCHAR(160),
--   body VARCHAR(1000),
--   likes INT,
--   comments VARCHAR(1000),
--   share VARCHAR(1000)

-- );

CREATE TABLE sessions (
  session_token INT,
  username VARCHAR(20)
);

-- CREATE TABLE following_relations (
--   followed_uname VARCHAR(20) NOT NULL,
--   follower_uname VARCHAR(20) NOT NULL
-- );

INSERT INTO users
  (username, password)
VALUES
  ('d3f1n1731y n07 7h3 f149', '900d8y3d w021d'),
  ('wh47 7h3 h3ck', '7h15 15 d1ff323n7');

-- INSERT INTO following_relations
--   (followed_uname, follower_uname)
-- VALUES
--   ('alice', 'charlie'),
--   ('alice', 'bob'),
--   ('bob', 'alice');

--   INSERT INTO posts
--     (username, picture, body, likes, comments, share)
--   VALUES
--     ('alice', 'static/uploads/wargames.jpg', 'I love #wargames', 10, '{"bob":"Hello, comment"}', 'yes'),
--     ('bob', 'static/uploads/cyber.jpg', 'recently started researching #embedded #security', 10, '{"alice":"Hello, foo"}', 'yes'),
--     ('charlie', 'static/uploads/car.jpg', 'check out my new car', 10, '{"kathy":"nice"}', 'yes'),
--     ('alice','static/uploads/private.png','THIS IS A VERY PRIVATE PICTURE. DO NOT SHARE!', 0, '{}', 'no');
