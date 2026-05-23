import { db, type SheetRow } from "./db";

export type CellRef = string; // "A1"
export type Cells = Record<CellRef, { formula: string }>;

export function genSheetId(): string {
  // short, urlsafe, a-z0-9
  const alpha = "abcdefghijklmnopqrstuvwxyz0123456789";
  let out = "";
  for (let i = 0; i < 10; i++) {
    out += alpha[Math.floor(Math.random() * alpha.length)];
  }
  return out;
}

export function emptyCells(): Cells {
  return {};
}

export function createSheet(opts: {
  ownerId: number;
  title: string;
  cells: Cells;
  isPopular?: boolean;
  id?: string;
}): SheetRow {
  const id = opts.id ?? genSheetId();
  const now = Date.now();
  db()
    .prepare(
      `INSERT INTO sheets (id, owner_id, title, cells_json, is_popular, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
    )
    .run(
      id,
      opts.ownerId,
      opts.title,
      JSON.stringify(opts.cells),
      opts.isPopular ? 1 : 0,
      now,
      now,
    );
  return db().prepare("SELECT * FROM sheets WHERE id = ?").get(id) as SheetRow;
}

export function updateSheet(
  id: string,
  patch: { title?: string; cells?: Cells },
): SheetRow | null {
  const existing = db()
    .prepare("SELECT * FROM sheets WHERE id = ?")
    .get(id) as SheetRow | undefined;
  if (!existing) return null;

  const title = patch.title ?? existing.title;
  const cells_json =
    patch.cells !== undefined ? JSON.stringify(patch.cells) : existing.cells_json;
  const now = Date.now();
  db()
    .prepare(
      "UPDATE sheets SET title = ?, cells_json = ?, updated_at = ? WHERE id = ?",
    )
    .run(title, cells_json, now, id);
  return db().prepare("SELECT * FROM sheets WHERE id = ?").get(id) as SheetRow;
}

export function getSheet(id: string): SheetRow | null {
  const row = db()
    .prepare("SELECT * FROM sheets WHERE id = ?")
    .get(id) as SheetRow | undefined;
  return row ?? null;
}

export function listPopular(limit = 12): SheetRow[] {
  return db()
    .prepare(
      "SELECT * FROM sheets WHERE is_popular = 1 ORDER BY updated_at DESC LIMIT ?",
    )
    .all(limit) as SheetRow[];
}

export function listRecent(limit = 20): SheetRow[] {
  return db()
    .prepare("SELECT * FROM sheets ORDER BY updated_at DESC LIMIT ?")
    .all(limit) as SheetRow[];
}

export function listBySheetOwner(ownerId: number): SheetRow[] {
  return db()
    .prepare("SELECT * FROM sheets WHERE owner_id = ? ORDER BY updated_at DESC")
    .all(ownerId) as SheetRow[];
}

export function ownerOf(id: string): number | null {
  const row = db()
    .prepare("SELECT owner_id FROM sheets WHERE id = ?")
    .get(id) as { owner_id: number } | undefined;
  return row?.owner_id ?? null;
}

export function parseCells(row: SheetRow): Cells {
  try {
    const parsed = JSON.parse(row.cells_json);
    if (parsed && typeof parsed === "object") return parsed as Cells;
  } catch {
    // fall through
  }
  return {};
}

