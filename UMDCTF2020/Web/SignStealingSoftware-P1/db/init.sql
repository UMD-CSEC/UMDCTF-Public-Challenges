CREATE DATABASE umdctf;
use umdctf;

CREATE TABLE users (
  username VARCHAR(128) NOT NULL UNIQUE,
  pass VARCHAR(128) NOT NULL
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
-- UMDCTF-{1_CaN_S3e_Th3_S1gN5}
INSERT INTO users
  (username, pass)
VALUES
  ('user1', 'pass1'),
  ('user2', 'pass2'),
  ('user3', 'pass3'),
  ('user4', 'pass4'),
  ('user5', 'pass5'),
  ('user6', 'pass6'),
  ('user7', 'pass7'),
  ('user8', 'pass8'),
  ('user9', 'pass9'),
  ('user10', 'pass10'),
  ('user11', 'pass11'),
  ('user12', 'pass12'),
  ('user13', 'pass13'),
  ('user14', 'pass14'),
  ('user15', 'pass15'),
  ('user16', 'pass16'),
  ('user17', 'pass17'),
  ('UMDCTF-{', 'Y0u_Ar3_N0W_St341Ng_S1gns_Fr0m_Astr05}'),
  ('user18', 'pass18'),
  ('user19', 'pass19'),
  ('user20', 'pass29');

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
