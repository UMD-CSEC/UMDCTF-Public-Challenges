/**
 * Minimal CSV export.
 * Exports the rendered display values of every non-empty cell, preserving
 * the A..L × 1..30 grid shape. Trims trailing empty columns/rows for a
 * cleaner file.
 */
export function renderCsv(rendered: Map<string, string>): string {
  const COLS = "ABCDEFGHIJKL".split("");
  const ROWS = 30;

  // Find the bounding box of non-empty cells.
  let maxCol = 0;
  let maxRow = 0;
  for (const [ref, val] of rendered) {
    if (!val) continue;
    const col = ref.charCodeAt(0) - "A".charCodeAt(0);
    const row = parseInt(ref.slice(1), 10);
    if (col > maxCol) maxCol = col;
    if (row > maxRow) maxRow = row;
  }

  if (maxRow === 0) return "";

  const lines: string[] = [];
  for (let r = 1; r <= maxRow; r++) {
    const row: string[] = [];
    for (let c = 0; c <= maxCol; c++) {
      const ref = `${COLS[c]}${r}`;
      const v = rendered.get(ref) ?? "";
      row.push(csvField(v));
    }
    lines.push(row.join(","));
  }
  void ROWS; // documented max
  return lines.join("\n");
}

function csvField(v: string): string {
  if (v === "") return "";
  if (/[",\n\r]/.test(v)) {
    return `"${v.replace(/"/g, '""')}"`;
  }
  return v;
}
