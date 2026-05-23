import { createHmac } from "node:crypto";
import { PrismaClient } from "@prisma/client";
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";

const url = process.env.DATABASE_URL ?? "file:./data/signal.db";
const prisma = new PrismaClient({ adapter: new PrismaBetterSqlite3({ url }) });

const HMAC_SECRET = process.env.HMAC_SECRET;
if (!HMAC_SECRET) {
  throw new Error("HMAC_SECRET environment variable is required");
}

function signalHmac(ticker: string, side: string, contractPrice: number) {
  return createHmac("sha256", HMAC_SECRET)
    .update(`${ticker}|${side}|${contractPrice}`)
    .digest("hex")
    .slice(0, 32);
}

const TICKER_POOL = [
  "KXBTC200K-26DEC",
  "KXETHFLIP-27Q1",
  "KXRECESSION-26H2",
  "KXELECTION-28NOV",
  "KXFEDCUT-26JUL",
  "KXAGI-27DEC",
  "KXSPXATH-26Q4",
  "KXOILSPIKE-26SEP",
  "KXNVDA5T-27Q2",
  "KXMARSLAND-30DEC",
  "KXTIKTOKBAN-26OCT",
  "KXGPT6SHIP-27JUN",
  "KXGOLD3K-26Q3",
  "KXNKTEST-26AUG",
  "KXCPI2PCT-27MAY",
  "KXDOGETOMOON-26Q4",
  "KXUNEMPL5-27Q1",
  "KXHOUSECRASH-27H1",
  "KXTAYLORENGAGED-26DEC",
  "KXBITCOINETF-26Q2",
];

const ANALYSTS = [
  {
    handle: "quant_sable",
    displayName: "Quant Sable",
    tier: "DIAMOND",
    claimedRoi: 2847,
    claimedWinRate: 94.7,
    bio:
      "Former quant at a three-letter firm you've heard of. I don't publish my edge, I publish the outcome. $500/mo. Subscribers only. No refunds, no screenshots, no leaks. Accuracy matters.",
  },
  {
    handle: "oracle_byzantine",
    displayName: "Oracle Byzantine",
    tier: "DIAMOND",
    claimedRoi: 1920,
    claimedWinRate: 91.2,
    bio:
      "Called the 2020 election. And 2016. And every Fed meeting since Bernanke. The process is the process. If you have to ask what that means, you aren't ready.",
  },
  {
    handle: "alpha_hyena",
    displayName: "ALPHA HYENA",
    tier: "GOLD",
    claimedRoi: 14320,
    claimedWinRate: 97.1,
    bio:
      "18 YEARS ON THE STREET. SIX FIGURE WINS WEEKLY. NOT FINANCIAL ADVICE (THEY MAKE ME SAY THIS). DM FOR MENTORSHIP. SERIOUS INQUIRIES ONLY. WIRES ONLY.",
  },
  {
    handle: "moon_vector",
    displayName: "Moon Vector",
    tier: "GOLD",
    claimedRoi: 840,
    claimedWinRate: 88.0,
    bio:
      "Ex-professional poker player turned prediction whisperer. Read the vibes. Trade the outcome. The market is a room and I'm the guy reading the room.",
  },
  {
    handle: "retail_phoenix",
    displayName: "Retail Phoenix",
    tier: "GOLD",
    claimedRoi: 2100,
    claimedWinRate: 85.3,
    bio:
      "Lost everything in '22. Rebuilt from $47 to seven figures on prediction contracts alone. Signals daily at 6am ET. DMs open. I answer. I am real. I am you.",
  },
  {
    handle: "probability_oracle",
    displayName: "probability_oracle",
    tier: "BRONZE",
    claimedRoi: 612,
    claimedWinRate: 82.5,
    bio:
      "PhD dropout (ABD, Bayesian statistics, won't name the school). Enter the temple. Leave richer. The posterior does not lie. My subscribers know.",
  },
  {
    handle: "delta_savage",
    displayName: "DELTA SAVAGE",
    tier: "BRONZE",
    claimedRoi: 4200,
    claimedWinRate: 93.8,
    bio:
      "BETA CUCKS TRADE VOLATILITY. I TRADE CONVICTION. Backtest verified (backtest available in Discord, gated behind $99/mo). Iron stomach. Diamond hands. Lambo pending.",
  },
  {
    handle: "market_sherpa",
    displayName: "Market Sherpa",
    tier: "BRONZE",
    claimedRoi: 380,
    claimedWinRate: 77.4,
    bio:
      "Helping retail climb the mountain since 2023. Patient. Process-driven. Bronze tier welcome. No get-rich-quick here — just get-rich-eventually. Referrals appreciated.",
  },
];

function rand<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}
function randInt(lo: number, hi: number) {
  return Math.floor(Math.random() * (hi - lo + 1)) + lo;
}

const SIDES = ["YES", "NO"] as const;

const HISTORICAL_THESES = [
  "Setup is clean. Flow has been accumulating since last week. This one resolves our way.",
  "Cross-market correlation is screaming. Anyone with eyes sees it. Positioning accordingly.",
  "Retail is on the wrong side. That is all I need to know.",
  "Base rate favors this outcome. Implied is mispriced by ~14c. Taking the fade.",
  "Narrative has rotated. Old money is out. New money hasn't arrived yet. Window is now.",
  "Pattern matched to Q3 2024 setup. That one paid 11:1. This is the echo.",
  "Onchain signals aligned with offchain positioning. Both say the same thing.",
  "I was told something I can't repeat here. Draw your own conclusions.",
];

async function main() {
  const existing = await prisma.analyst.count();
  if (existing > 0) {
    console.log("[seed] analysts already present, resetting signals only");
    await prisma.signal.deleteMany();
  } else {
    for (const a of ANALYSTS) {
      await prisma.analyst.create({ data: a });
    }
  }

  const analysts = await prisma.analyst.findMany();
  const now = Date.now();

  for (const a of analysts) {
    const count = 5 + Math.floor(Math.random() * 2);
    for (let i = 0; i < count; i++) {
      const daysAgo = randInt(3, 120);
      const ticker = rand(TICKER_POOL);
      const side = rand([...SIDES]);
      const contractPrice = randInt(5, 95);
      await prisma.signal.create({
        data: {
          analystId: a.id,
          ticker,
          side,
          contractPrice,
          signalHmac: signalHmac(ticker, side, contractPrice),
          thesis: rand(HISTORICAL_THESES),
          publishedAt: new Date(now - daysAgo * 86400_000),
        },
      });
    }
  }

  const target = await prisma.analyst.findUnique({ where: { handle: "quant_sable" } });
  if (!target) throw new Error("seed: quant_sable missing");

  const draftTicker = rand(TICKER_POOL);
  const draftSide = rand([...SIDES]);
  const draftPrice = randInt(1, 99);

  const signalDrop = 1777849200 * 1000;
  const publishedAt = new Date(now < signalDrop ? signalDrop : now + 3 * 86400_000);

  const draftHmac = signalHmac(draftTicker, draftSide, draftPrice);

  await prisma.signal.create({
    data: {
      analystId: target.id,
      ticker: draftTicker,
      side: draftSide,
      contractPrice: draftPrice,
      signalHmac: draftHmac,
      thesis:
        "[DRAFT — embargoed until publish window] Conviction: maximum. Details reserved for paid subscribers. If you're reading this in the admin panel: the lambo dealer called.",
      publishedAt,
    },
  });

  console.log(
    `[seed] draft seeded — ticker=${draftTicker} side=${draftSide} price=${draftPrice} hmac=${draftHmac} publishedAt=${publishedAt.toISOString()}`,
  );
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
