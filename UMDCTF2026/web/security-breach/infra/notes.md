hey. i got this far and then had to drop it. you take it from here.

## what i know

we're on the internal umdmarket network. their admin is a
compulsive insider trader and keeps their private watchlist open in a browser
tab. their browser is literally **hammering their own dashboard endpoint on a loop** to get live updates.

## the hosts

- **10.0.0.1**  — the admin box. no services listening, just an outbound browser tab. i can ping it but there's nothing to poke.
- **10.0.0.2**  — the server. it's https on :443 with a self-signed cert (needs `-k`).
- **10.0.0.3**  — you.

the admin box has no login from me; i don't have creds and didn't get around to
trying to crack anything. the server has *some* stuff open to anyone though:

```
POST /api/suggestions          # anyone can submit a "filter suggestion"
GET  /api/suggestions/latest   # anyone can read the latest one
GET  /api/dashboard?filter=X   # admin-only, 401 without the right session cookie
POST /login                    # admin login, i don't have the password
```

the admin is hitting `/api/dashboard` every ~50ms. their browser (probably Chrome?) is probably using some kind of compression and TLS, so there's no way i can inspect the responses. not sure where to go from here.

## the flag
did some osint, I know the flag format is `UMDCTF{[a-z0-9_]+}`.

I installed some tools that might help you out...
