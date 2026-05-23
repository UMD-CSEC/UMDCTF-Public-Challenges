/**
 * Seed OpenInsight with users and popular sheets.
 * Idempotent — safe to re-run. Existing users/sheets are skipped.
 */
import { db } from "../lib/db";
import { createUser } from "../lib/auth";
import { createSheet, type Cells } from "../lib/sheets";

async function ensureUser(
  username: string,
  password: string,
  role: "user" | "admin" = "user",
): Promise<number> {
  const existing = db()
    .prepare("SELECT id FROM users WHERE username = ?")
    .get(username) as { id: number } | undefined;
  if (existing) return existing.id;
  const u = await createUser(username, password, role);
  console.log(`  + user ${username} (role=${role})`);
  return u.id;
}

function ensureSheet(opts: {
  id: string;
  ownerId: number;
  title: string;
  cells: Cells;
  isPopular?: boolean;
}) {
  const existing = db().prepare("SELECT id FROM sheets WHERE id = ?").get(opts.id);
  if (existing) return;
  createSheet(opts);
  console.log(`  + sheet ${opts.id} — "${opts.title}"`);
}

function buildCells(rows: Array<[string, string | number]>): Cells {
  const out: Cells = {};
  for (const [ref, v] of rows) {
    out[ref] = { formula: typeof v === "number" ? String(v) : v };
  }
  return out;
}

function requireEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`${name} environment variable is required`);
  return v;
}

async function main() {
  db();
  console.log("seeding openinsight…");

  const adminUsername = requireEnv("ADMIN_USERNAME");
  const adminPassword = requireEnv("ADMIN_PASSWORD");
  const bobPassword = requireEnv("BOB_PASSWORD");
  const benPassword = requireEnv("BEN_PASSWORD");
  const hannahPassword = requireEnv("HANNAH_PASSWORD");
  const politPassword = requireEnv("POLIT_PASSWORD");

  // Real admin. Credentials are only used by the bot service.
  const alice = await ensureUser(adminUsername, adminPassword, "admin");
  // Decoy owners for popular sheets.
  const bob = await ensureUser("forecaster_bob", bobPassword, "user");
  const ben = await ensureUser("bagholder_ben", benPassword, "user");
  const hannah = await ensureUser("sports_hannah", hannahPassword, "user");
  const polit = await ensureUser("polit_junkie", politPassword, "user");
  void alice;

  // 1. Fed rate cut model
  ensureSheet({
    id: "fed-rate-cut-dec-2026",
    ownerId: bob,
    isPopular: true,
    title: "Fed rate cut Dec 2026 — my model",
    cells: buildCells([
      ["A1", "Probability components"],
      ["A2", "CPI YoY (Nov)"], ["B2", 2.8],
      ["A3", "Unemployment (Nov)"], ["B3", 4.2],
      ["A4", "Core PCE (Oct)"], ["B4", 2.9],
      ["A6", "CPI weight"], ["B6", 0.4],
      ["A7", "Unemployment weight"], ["B7", 0.3],
      ["A8", "PCE weight"], ["B8", 0.3],
      ["A10", "Base probability"],
      ["B10", `=cells("B2")*cells("B6")+cells("B3")*cells("B7")+cells("B4")*cells("B8")`],
      ["A11", "Implied market odds"],
      ["B11", `=1/cells("B10")`],
    ]),
  });

  // 2. Share card (the document.* breadcrumb)
  ensureSheet({
    id: "openinsight-share-card",
    ownerId: bob,
    isPopular: true,
    title: "OpenInsight share card",
    cells: buildCells([
      ["A1", "Sheet title"], ["B1", "=document.title"],
      ["A2", "View this sheet at"], ["B2", `="View this sheet at: " + document.URL`],
      ["A4", "Share instructions"],
      ["A5", "Copy B2 and paste to share. These cells reflect whoever is viewing them."],
    ]),
  });

  // 3. Ben's portfolio
  ensureSheet({
    id: "my-prediction-market-portfolio",
    ownerId: ben,
    isPopular: true,
    title: "My prediction market portfolio — Q1 to Q3 2026",
    cells: buildCells([
      ["A1", "month"], ["B1", "start"], ["C1", "end"], ["D1", "P&L"], ["E1", "note"],
      ["A2", "January"], ["B2", 10000], ["C2", 8400], ["D2", "=C2-B2"], ["E2", "learning experience"],
      ["A3", "February"], ["B3", 8400], ["C3", 6100], ["D3", "=C3-B3"], ["E3", "should've listened to my gut"],
      ["A4", "March"], ["B4", 6100], ["C4", 7200], ["D4", "=C4-B4"], ["E4", "back baby"],
      ["A5", "April"], ["B5", 7200], ["C5", 4800], ["D5", "=C5-B5"], ["E5", "fed surprise ruined me"],
      ["A6", "May"], ["B6", 4800], ["C6", 3100], ["D6", "=C6-B6"], ["E6", ""],
      ["A7", "June"], ["B7", 3100], ["C7", 2400], ["D7", "=C7-B7"], ["E7", "grinding back"],
      ["A8", "July"], ["B8", 2400], ["C8", 1900], ["D8", "=C8-B8"], ["E8", ""],
      ["A9", "August"], ["B9", 1900], ["C9", 1200], ["D9", "=C9-B9"], ["E9", "strategic pause"],
      ["A10", "September"], ["B10", 1200], ["C10", 400], ["D10", "=C10-B10"], ["E10", "big move loading"],
      ["A12", "total P&L"], ["B12", `=cells("C10")-cells("B2")`],
      ["A14", "a lot of people DM me asking how i do it. signed copies of my course 'predict to profit' available, $499."],
    ]),
  });

  // 4. NBA MVP distractor
  ensureSheet({
    id: "nba-mvp-odds-pairwise",
    ownerId: hannah,
    isPopular: true,
    title: "NBA MVP odds — pairwise",
    cells: buildCells([
      ["A1", "candidate"], ["B1", "market odds"], ["C1", "my odds"], ["D1", "edge"],
      ["A2", "Wembanyama"], ["B2", 0.34], ["C2", 0.42], ["D2", "=C2-B2"],
      ["A3", "Jokic"], ["B3", 0.22], ["C3", 0.18], ["D3", "=C3-B3"],
      ["A4", "Gilgeous-Alexander"], ["B4", 0.18], ["C4", 0.16], ["D4", "=C4-B4"],
      ["A5", "Doncic"], ["B5", 0.12], ["C5", 0.11], ["D5", "=C5-B5"],
      ["A6", "Tatum"], ["B6", 0.08], ["C6", 0.07], ["D6", "=C6-B6"],
      ["A7", "Field"], ["B7", 0.06], ["C7", 0.06], ["D7", "=C7-B7"],
      ["A9", "sum check"],
      ["B9", `=cells("B2")+cells("B3")+cells("B4")+cells("B5")+cells("B6")+cells("B7")`],
    ]),
  });

  // 5. Election distractor
  ensureSheet({
    id: "2026-election-models-aggregate",
    ownerId: polit,
    isPopular: true,
    title: "2026 election models — aggregate",
    cells: buildCells([
      ["A1", "source"], ["B1", "weight"], ["C1", "prob"],
      ["A2", "Silver-style"], ["B2", 0.3], ["C2", 0.54],
      ["A3", "Economist"], ["B3", 0.25], ["C3", 0.51],
      ["A4", "Sabato"], ["B4", 0.2], ["C4", 0.58],
      ["A5", "Cook Political"], ["B5", 0.15], ["C5", 0.52],
      ["A6", "Manifold aggregate"], ["B6", 0.1], ["C6", 0.49],
      ["A8", "weighted"],
      ["B8", `=cells("B2")*cells("C2")+cells("B3")*cells("C3")+cells("B4")*cells("C4")+cells("B5")*cells("C5")+cells("B6")*cells("C6")`],
    ]),
  });

  console.log("done.");
  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
