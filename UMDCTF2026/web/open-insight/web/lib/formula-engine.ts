export type CellRef = string;

export type EvalResult =
  | { kind: "value"; value: unknown; display: string }
  | { kind: "error"; message: string; display: string };

const RE_CELL_REF = /^[A-L](?:[1-9]|[12][0-9]|30)$/;

function displayOf(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "number") {
    if (!Number.isFinite(v)) return String(v);
    return Number.isInteger(v) ? v.toString() : String(Number(v.toFixed(6)));
  }
  if (typeof v === "string") return v;
  if (typeof v === "boolean") return v ? "TRUE" : "FALSE";
  try {
    return String(v);
  } catch {
    return "";
  }
}

function buildDocProxy(): unknown {
  if (typeof document === "undefined") return undefined;
  return new Proxy(document, {
    get(_target, key) {
      const v = (document as unknown as Record<PropertyKey, unknown>)[key];
      if (v === null) return null;
      if (typeof v === "object") return undefined;
      if (typeof v === "function") return undefined;
      return v;
    },
  });
}

function buildScope(computed: Map<CellRef, unknown>) {
  const safe: Record<string, unknown> = {
    Math,
    JSON: { parse: JSON.parse, stringify: JSON.stringify },
    Number,
    String,
    Boolean,
    RegExp,
    parseInt,
    parseFloat,
    isNaN,
    isFinite,
    document: buildDocProxy(),
    cells(ref: string): unknown {
      if (typeof ref !== "string") return undefined;
      return computed.get(ref);
    },
  };

  return new Proxy(safe, {
    has: () => true,
    get(target, k) {
      if (k === Symbol.unscopables) return undefined;
      if (k in target) return target[k as string];
      return undefined;
    },
  });
}

function isFormula(src: string): boolean {
  return src.startsWith("=");
}

function runExpression(expr: string, computed: Map<CellRef, unknown>): unknown {
  const scope = buildScope(computed);
  // eslint-disable-next-line no-new-func
  const fn = new Function(
    "S",
    `with (S) { "use strict"; return (${expr}); }`,
  );
  return fn(scope);
}

function evalOne(
  src: string,
  computed: Map<CellRef, unknown>,
): EvalResult {
  const trimmed = src.trim();
  if (trimmed === "") return { kind: "value", value: "", display: "" };
  if (!isFormula(trimmed)) {
    if (/^-?\d+(\.\d+)?$/.test(trimmed)) {
      const n = Number(trimmed);
      return { kind: "value", value: n, display: displayOf(n) };
    }
    return { kind: "value", value: src, display: src };
  }
  const expr = trimmed.slice(1);
  try {
    const v = runExpression(expr, computed);
    return { kind: "value", value: v, display: displayOf(v) };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { kind: "error", message: msg, display: `#ERR: ${msg}` };
  }
}

export function evalSheet(
  cells: Record<CellRef, { formula: string }>,
): Map<CellRef, EvalResult> {
  const results = new Map<CellRef, EvalResult>();
  const computed = new Map<CellRef, unknown>();

  const entries = Object.entries(cells).filter(([ref]) => RE_CELL_REF.test(ref));

  for (let pass = 0; pass < 2; pass++) {
    for (const [ref, cell] of entries) {
      const res = evalOne(cell.formula ?? "", computed);
      results.set(ref, res);
      computed.set(ref, res.kind === "value" ? res.value : undefined);
    }
  }
  return results;
}
