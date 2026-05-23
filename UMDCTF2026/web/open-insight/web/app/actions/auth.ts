"use server";

import { redirect } from "next/navigation";
import {
  createUser,
  validatePassword,
  validateUsername,
  verifyLogin,
} from "@/lib/auth";
import { db } from "@/lib/db";
import { getSession } from "@/lib/session";

export async function loginAction(formData: FormData) {
  const username = String(formData.get("username") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  const user = await verifyLogin(username, password);
  if (!user) {
    redirect("/login?error=invalid");
  }
  const session = await getSession();
  session.userId = user.id;
  await session.save();
  redirect("/");
}

export async function signupAction(formData: FormData) {
  const username = String(formData.get("username") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  const errs =
    validateUsername(username) ??
    validatePassword(password) ??
    (db().prepare("SELECT 1 FROM users WHERE username = ?").get(username)
      ? "Username already taken."
      : null);
  if (errs) {
    redirect(`/signup?error=${encodeURIComponent(errs)}`);
  }
  const user = await createUser(username, password, "user");
  const session = await getSession();
  session.userId = user.id;
  await session.save();
  redirect("/");
}

export async function logoutAction() {
  const session = await getSession();
  session.destroy();
  redirect("/");
}
