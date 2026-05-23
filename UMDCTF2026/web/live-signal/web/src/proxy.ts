import { NextRequest, NextResponse } from "next/server";

const buckets = new Map<string, { count: number; resetAt: number }>();
const LIMIT = 600;
const WINDOW_MS = 60_000;

function clientIp(req: NextRequest) {
  const xff = req.headers.get("x-forwarded-for");
  if (xff) {
    const parts = xff.split(",");
    return parts[parts.length - 1].trim();
  }
  return (req as unknown as { ip?: string }).ip ?? "anon";
}

export function proxy(req: NextRequest) {
  const p = req.nextUrl.pathname;
  const isAction = req.headers.get("next-action") !== null;
  const isProxy = p.startsWith("/api/solve-proxy");
  if (!isAction && !isProxy) return NextResponse.next();

  const key = clientIp(req);
  const now = Date.now();
  const b = buckets.get(key);
  if (!b || now > b.resetAt) {
    buckets.set(key, { count: 1, resetAt: now + WINDOW_MS });
  } else {
    b.count += 1;
    if (b.count > LIMIT) {
      return new NextResponse(
        JSON.stringify({ error: "rate limited — 600 req/min/IP" }),
        {
          status: 429,
          headers: { "content-type": "application/json" },
        },
      );
    }
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/api/solve-proxy/:path*", "/analyst/:path*", "/insiders"],
};
