create table active_sessions
(
    "user"  authenticated_user,
    token user_token,
    unique("user", token)
);

