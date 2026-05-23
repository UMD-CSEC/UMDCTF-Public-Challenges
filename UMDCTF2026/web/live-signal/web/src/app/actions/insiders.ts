"use server";

import { prisma } from "@/lib/db";

export async function verifyInsider(
  ticker: string,
  side: "YES" | "NO",
  contractPrice: number,
  signalHmac: string,
) {
  if (
    typeof ticker !== "string" ||
    typeof signalHmac !== "string" ||
    (side !== "YES" && side !== "NO")
  ) {
    return { ok: false, message: "Malformed credentials." };
  }
  const price = Number(contractPrice);
  if (!Number.isInteger(price) || price < 1 || price > 99) {
    return { ok: false, message: "Price out of range." };
  }

  const draft = await prisma.signal.findFirst({
    where: {
      analyst: { handle: "quant_sable" },
      publishedAt: { gt: new Date() },
    },
    orderBy: { publishedAt: "asc" },
  });

  if (!draft) return { ok: false, message: "No active drafts." };

  const matches =
    draft.ticker === ticker.toUpperCase() &&
    draft.side === side &&
    draft.contractPrice === price &&
    draft.signalHmac === signalHmac;

  if (!matches) {
    return { ok: false, message: "We can't verify your access." };
  }

  const flag = process.env.FLAG;
  if (!flag) {
    throw new Error("FLAG environment variable is required");
  }

  return {
    ok: true,
    message: "Welcome to the inside.",
    flag,
  };
}
