create table sessions
(
    identifier varchar(255),
    token      user_token,
    unique(identifier, token)
);

