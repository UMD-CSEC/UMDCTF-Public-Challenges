create or replace function authenticate_user(
    who character varying,
    vtoken character varying,
    "time" timestamp with time zone
)
    returns user_token
    language plpgsql
as
$$
declare
    auser  authenticated_user;
    ftoken user_token;
begin
    select identifier, token from sessions where sessions.identifier = who into auser._name, auser._token;
    -- Create new token
    if auser is null or auser._token is null then
        ftoken := ROW (vtoken, "time");
        insert into sessions(identifier, token) values (who, ftoken);
        insert into active_sessions("user", token) values (ROW (who, ftoken), ROW (vtoken, "time"));
        return ftoken;
    end if;
    -- Get existing token
    select (token)._plain, (token)._expiry
    from sessions
    where sessions.identifier = who
    into ftoken._plain, ftoken._expiry;
    update sessions set token = ftoken where sessions.identifier = who;
    update active_sessions set ("user") = ROW (auser), (token) = ROW (ftoken) where ("user")._name = who;
    return ftoken;
end
$$;

create or replace function deauthenticate_user(who character varying)
    returns void
    language plpgsql
as
$$
begin
    delete from active_sessions where ("user")._name like who;
    -- Clear token
    update sessions set token = null where identifier like who;
end
$$;

create or replace function get_expiry(token_value text)
    returns timestamp
    language plpgsql
as
$$
declare
    expiry timestamp;
begin
    select (token)._expiry from active_sessions where (token)._plain = token_value into expiry;
    return expiry;
end;
$$
