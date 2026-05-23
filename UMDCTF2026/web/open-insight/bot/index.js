/**
 * OpenInsight admin review queue.
 *
 * Single-container service. Exposes a minimal form at `/` that accepts
 * sheet-id submissions. Each submission spawns its own puppeteer browser
 * concurrently — there is no shared queue, so one slow client cannot
 * block another. A per-IP rate limiter caps how often a single client
 * can submit.
 *
 * Response protocol for POST /report is two-step:
 *   1. Headers + first chunk flushed immediately as an ACK.
 *   2. Connection is held open while the bot processes the job.
 *   3. Final chunk ("Done" / "Error") flushes when processing finishes.
 */

const express = require("express");
const puppeteer = require("puppeteer");
const path = require("path");



const PORT = Number(process.env.PORT || 3001);
const WEB_URL = process.env.WEB_URL || "http://localhost:3000";
const ADMIN_USERNAME = process.env.ADMIN_USERNAME;
if (!ADMIN_USERNAME) {
  throw new Error("ADMIN_USERNAME environment variable is required");
}
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
if (!ADMIN_PASSWORD) {
  throw new Error("ADMIN_PASSWORD environment variable is required");
}
const JOB_TIMEOUT_MS = 20_000;
const RATE_WINDOW_MS = 60_000;
const RATE_MAX = 5;

const SHEET_ID_RE = /^[A-Za-z0-9_-]{1,64}$/;

/** @type {Map<string, number[]>} */
const rateHits = new Map();

function rateLimit(ip) {
  const now = Date.now();
  const cutoff = now - RATE_WINDOW_MS;
  const hits = (rateHits.get(ip) || []).filter((t) => t > cutoff);
  if (hits.length >= RATE_MAX) {
    rateHits.set(ip, hits);
    return Math.ceil((hits[0] + RATE_WINDOW_MS - now) / 1000);
  }
  hits.push(now);
  rateHits.set(ip, hits);
  return 0;
}

setInterval(() => {
  const cutoff = Date.now() - RATE_WINDOW_MS;
  for (const [ip, hits] of rateHits) {
    const fresh = hits.filter((t) => t > cutoff);
    if (fresh.length === 0) rateHits.delete(ip);
    else rateHits.set(ip, fresh);
  }
}, RATE_WINDOW_MS).unref();

function runWithTimeout(promise, ms, label) {
  return Promise.race([
    promise,
    new Promise((_, rej) =>
      setTimeout(() => rej(new Error(`timeout: ${label}`)), ms),
    ),
  ]);
}

async function processJob(sheetId) {
  const browser = await puppeteer.launch({
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
    headless: true,
  });
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(6000);

    // 1. Log in.
    await page.goto(`${WEB_URL}/login`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector('input[name="username"]');
    await page.type('input[name="username"]', ADMIN_USERNAME);
    await page.type('input[name="password"]', ADMIN_PASSWORD);
    await Promise.all([
      page.waitForNavigation({ waitUntil: "domcontentloaded" }),
      page.click('button[type="submit"]'),
    ]);

    // 2. Open the sheet.
    await page.goto(`${WEB_URL}/sheets/${encodeURIComponent(sheetId)}`, {
      waitUntil: "domcontentloaded",
    });

    // 3. Wait for initial render flag.
    await page.waitForSelector('[data-cell-rendered="true"]', { timeout: 6000 });

    // 4. Trigger export; wait for POST /export to complete.
    await Promise.all([
      page.waitForResponse(
        (r) =>
          r.url().endsWith(`/sheets/${encodeURIComponent(sheetId)}/export`) &&
          r.request().method() === "POST",
        { timeout: 6000 },
      ),
      page.click('[data-action="export"]'),
    ]);
  } finally {
    await browser.close();
  }
}

const app = express();
// Behind Traefik — trust one proxy hop so req.ip reflects the real client.
app.set("trust proxy", 1);
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, "public")));

app.post("/report", async (req, res) => {
  const sheetId = String(req.body.sheetId || "").trim();
  if (!SHEET_ID_RE.test(sheetId)) {
    res.status(400).type("text/plain").send("Bad sheet id.");
    return;
  }

  const retryAfter = rateLimit(req.ip);
  if (retryAfter > 0) {
    res
      .status(429)
      .set("Retry-After", String(retryAfter))
      .type("text/plain")
      .send(`Rate limit exceeded. Try again in ${retryAfter}s.\n`);
    return;
  }

  res.writeHead(200, {
    "Content-Type": "text/plain; charset=utf-8",
    "Transfer-Encoding": "chunked",
    "X-Accel-Buffering": "no",
    "Cache-Control": "no-store",
  });
  res.write(`Waiting for an admin to review ${sheetId}...\n`);
  if (typeof res.flush === "function") res.flush();

  let outcome = "Done. An admin reviewed your sheet.";
  try {
    await runWithTimeout(processJob(sheetId), JOB_TIMEOUT_MS, "processJob");
  } catch (e) {
    console.error("[bot] job failed:", sheetId, e && e.message);
    outcome = `Error: admin review failed (${e && e.message ? e.message : "unknown"}). Try again later.`;
  }
  try {
    res.write(outcome + "\n");
    res.end();
  } catch {
    /* client already gone */
  }
});

app.get("/healthz", (_req, res) => {
  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log(`[bot] listening on :${PORT}, web=${WEB_URL}`);
});
