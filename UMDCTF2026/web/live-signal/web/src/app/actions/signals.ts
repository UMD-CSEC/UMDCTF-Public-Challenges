"use server";

import { prisma } from "@/lib/db";

type AnalystFilter = {
  handle?: string;
  tier?: "BRONZE" | "GOLD" | "DIAMOND";
};

export type SignalRow = {
  id: string;
  ticker: string;
  side: string;
  contractPrice: number;
  signalHmac: string;
  publishedAt: Date;
};

export async function signalsByAnalyst(
  author: AnalystFilter,
  limit: number,
): Promise<SignalRow[]> {
  return prisma.signal.findMany({
    where: {
      analyst: author,
      publishedAt: { lte: new Date() },
    },
    orderBy: { publishedAt: "desc" },
    select: {
      id: true,
      ticker: true,
      side: true,
      contractPrice: true,
      signalHmac: true,
      publishedAt: true,
    },
    take: Math.min(Math.max(1, Number(limit) || 1), 25),
  });
}
