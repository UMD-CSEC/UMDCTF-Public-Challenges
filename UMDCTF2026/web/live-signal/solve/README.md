# LiveSignal — reference solver

Leaks the embargoed `(ticker, side, contractPrice)` draft for
`@quant_sable` via Prisma relation-filter injection, then submits the
tuple to `/insiders` to receive the flag.

## Run

```sh
cd solve
npm install
TARGET=http://localhost:3000 npm run solve
```

On success the flag is printed to stdout; progress logs go to stderr.
Runtime is ~15 seconds on a cold solve due to the 600 req/min rate limit.

## Transport note

The solver hits `POST /api/solve-proxy/<action>` — a thin JSON passthrough
route that forwards directly to the real server actions. The vulnerability
is in the server action itself, not the proxy. The proxy exists so the
reference solver doesn't have to speak the Next.js server-action RPC
format (which changes between framework minors).

Players can use the proxy too, or they can replay the real server action
by copying the POST request they see in DevTools on `/analyst/quant_sable`
when the tier dropdown fires.

## The exploit, briefly

`signalsByAnalyst(author: {handle?, tier?}, limit)` forwards `author` to
`where: { analyst: author }`. `AnalystFilter` is TypeScript-only; at
runtime we send any `AnalystWhereInput`-shaped object, including:

```jsonc
{
  "author": {
    "handle": "quant_sable",
    "signals": {
      "some": {
        "publishedAt": { "gt": "<now>" },
        "ticker": { "startsWith": "KX..." },
        "side": "YES",
        "contractPrice": { "gte": 37 }
      }
    }
  },
  "limit": 1
}
```

The outer `publishedAt <= now` gate prunes which *rows* we get back; it
does not prune the predicate inside `signals.some`. The predicate acts
as a boolean oracle over the draft row's fields: non-empty `value` =
the draft matches, empty = miss. Binary-search the fields.

The action returns either the array of rows or a scrubbed error object:

```ts
SignalRow[] | { error: string }
```

Oracle = response is a non-empty array.
