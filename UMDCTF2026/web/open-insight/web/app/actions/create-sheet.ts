"use server";

import { redirect } from "next/navigation";
import { getSessionUser } from "@/lib/session";
import { createSheet, emptyCells } from "@/lib/sheets";

export async function createSheetAction(formData: FormData) {
  const user = await getSessionUser();
  if (!user) redirect("/login");
  const title =
    (formData.get("title")?.toString() || "Untitled sheet").slice(0, 200);
  const sheet = createSheet({
    ownerId: user.id,
    title,
    cells: emptyCells(),
  });
  redirect(`/sheets/${sheet.id}`);
}
