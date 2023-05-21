create type user_token as
(
    _plain  varchar(255),
    _expiry timestamp
);

create type authenticated_user as
(
    _name  varchar(255),
    _token user_token
);
