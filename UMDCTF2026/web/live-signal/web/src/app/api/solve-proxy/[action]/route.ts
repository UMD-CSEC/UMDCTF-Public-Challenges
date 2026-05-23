import { NextRequest } from "next/server";
import { signalsByAnalyst } from "@/app/actions/signals";
import { verifyInsider } from "@/app/actions/insiders";

export const dynamic = "force-dynamic";

const actions: Record<string, (body: Record<string, unknown>) => Promise<unknown>> = {
  signalsByAnalyst: async (b) =>
    signalsByAnalyst(b.author as never, Number(b.limit ?? 10)),
  verifyInsider: async (b) =>
    verifyInsider(
      String(b.ticker ?? ""),
      b.side as "YES" | "NO",
      Number(b.contractPrice ?? 0),
      String(b.signalHmac ?? ""),
    ),
};

export async function POST(
  req: NextRequest,
  ctx: { params: Promise<{ action: string }> },
) {
  const { action } = await ctx.params;
  const fn = actions[action];
  if (!fn) {
    return Response.json({ error: "unknown action" }, { status: 404 });
  }
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: "invalid json" }, { status: 400 });
  }
  const result = await fn(body);
  return Response.json(result);
}
