# LiveSignal

Prediction-market signal platform. CTF web challenge built around a
**Prisma relation-filter injection via an unvalidated Next.js server
action argument**.

## Services

- `web` (port **3000**) — the Next.js 16 app. Homepage, analyst
  directory, analyst profile, insiders portal.
- Backend: SQLite file at `/app/data/signal.db` (persisted via a named
  Docker volume). The schema is synced and seeded on boot.

## Run

```sh
docker compose up --build
```

Then:

- `http://localhost:3000` — the desk.
- `http://localhost:3000/analyst/quant_sable` — the exploit surface.
- `http://localhost:3000/insiders` — flag redemption.

On container boot the seed creates 8 scammer analysts with historical
signals plus a random embargoed draft for `quant_sable`. The flag is
fixed by the `FLAG` env var; only the `(ticker, side, contractPrice)`
draft randomizes per boot.

## The flag

`UMDCTF{z0d_1s_f0r_sc4r3dy_c4ts}` (set on the `web` service
via the `FLAG` env var in `docker-compose.yml`).

## Intended solve

1. Notice `/analyst/<handle>` has two filter controls (handle input +
   tier dropdown). DevTools shows they invoke a Next.js server action
   that POSTs `{handle, tier}` to the server.
2. TypeScript types on server actions are runtime-erased — they only
   constrain the *client*. The server does `where: { analyst: author }`,
   passing the client's object straight into a Prisma relation slot.
3. Prisma walks the object as an `AnalystWhereInput`, which includes
   the `signals` relation. Send any Prisma operator Prisma accepts:

   ```json
   {
     "author": {
       "handle": "quant_sable",
       "signals": {
         "some": {
           "publishedAt": { "gt": "<now>" },
           "side": "YES",
           "ticker": { "startsWith": "KX" },
           "contractPrice": { "gte": 40 }
         }
       }
     },
     "limit": 1
   }
   ```

4. The outer `publishedAt: { lte: now }` gates which signals are
   *returned*, but does not restrict the predicate inside `signals.some`.
   So the nested predicate is an oracle over the embargoed draft.
5. Boolean-oracle the draft's `side` (1 req), `ticker` (prefix scan),
   `contractPrice` (binary search). ~70 requests. Rate limit is
   60/min/IP so expect ~15 sec.
6. Submit the leaked tuple at `/insiders` to receive the flag.

## Recon trail

There's no explicit "this is Prisma" signal. The challenge rewards
players who poke at the action and read the errors:

- Client chunks hard-code the enum-shaped strings (`"YES"`, `"NO"`,
  `"BRONZE"`, `"GOLD"`, `"DIAMOND"`) from `@/lib/signalFormat` because
  that module is imported by a `"use client"` component. Grep
  `.next/static/chunks/*.js` for `"YES"` to find them next to UI code.
  Confirms these are the valid enum values to probe with.
- The vulnerable action catches server-side errors and echoes back any
  rejected keys + suggestions from the underlying query builder, e.g.
  `invalid filter key: foo — did you mean is?`. That surface narrows
  the valid-key set (`is`, `isNot`, `AND`, `OR`, `NOT`, `signals`, …)
  without naming the ORM. Fuzzing the action with nested objects
  reveals the `signals` relation accepts `some`/`every`/`none` with
  nested WhereInput-shaped predicates.
- From there, the shape of the suggestions is recognizable to anyone
  who's used a JS query builder. The ORM is not leaked; the query
  grammar is.

## Notable files

- `web/src/app/actions/signals.ts` — `signalsByAnalyst`, the vulnerable action.
- `web/src/app/actions/insiders.ts` — `verifyInsider`, the clean flag gate.
- `web/src/app/api/solve-proxy/[action]/route.ts` — JSON passthrough for
  the reference solver. Not the vulnerability; just a stable transport.
- `web/prisma/seed.ts` — 8 analysts + historical signals + randomized
  `quant_sable` draft.
- `web/src/proxy.ts` — Next 16 proxy (fka middleware) enforcing 600 req/min/IP on actions and the solve-proxy route.

## Reference solver

`solve/solve.ts` extracts side, ticker, and price via the oracle and
POSTs them to `verifyInsider`:

```sh
cd solve
npm install
TARGET=http://localhost:3000 npm run solve
```

See `solve/README.md` for the full exploit writeup.

## Verification checklist

1. `docker compose up --build` — app boots on SQLite volume, seed
   creates 8 analysts + one embargoed `quant_sable` draft,
   `publishedAt = max(2026-05-01, now+3d)`.
2. Homepage: countdown renders, leaderboard shows ridiculous ROI, recent
   signals grid populated.
3. `/analysts`: all 8 scammer cards visible.
4. `/analyst/quant_sable` + apply filters: honest path works.
5. Malformed probe via `POST /api/solve-proxy/signalsByAnalyst` with
   `{"author": {"foo": "bar"}, "limit": 1}` — response is
   `{"error": "invalid filter key: foo — did you mean is?"}` (no ORM
   name surfaced; the suggestion vocabulary is the hint).
6. `cd solve && npm install && TARGET=http://localhost:3000 npm run solve`
   — prints the flag to stdout after ~15 sec.
7. `docker compose down -v && docker compose up --build` → fresh random
   draft → solver extracts the new tuple → same fixed flag.
