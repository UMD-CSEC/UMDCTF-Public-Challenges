import { NextResponse } from "next/server";
import { getSessionUser } from "@/lib/session";
import { getSheet } from "@/lib/sheets";

export async function POST(
  req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const user = await getSessionUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const { id } = await params;
  const sheet = getSheet(id);
  if (!sheet) return NextResponse.json({ error: "not found" }, { status: 404 });

  let body: { csv?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "bad json" }, { status: 400 });
  }
  const csv = String(body.csv ?? "").slice(0, 200_000);

  const filename = (sheet.title || "sheet").replace(/[^a-zA-Z0-9_-]+/g, "_");
  return new NextResponse(csv, {
    status: 200,
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="${filename}.csv"`,
    },
  });
}
