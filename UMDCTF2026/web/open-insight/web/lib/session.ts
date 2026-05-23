import { getIronSession, type SessionOptions } from "iron-session";
import { cookies } from "next/headers";
import { db, type UserRow } from "./db";

export type SessionData = {
  userId?: number;
};

function getSessionOptions(): SessionOptions {
  const secret = process.env.SESSION_SECRET;
  if (!secret) {
    throw new Error("SESSION_SECRET environment variable is required");
  }
  return {
    password: secret,
    cookieName: "openinsight_session",
    cookieOptions: {
      httpOnly: true,
      sameSite: "lax",
      secure: false,
      path: "/",
    },
  };
}

export async function getSession() {
  const c = await cookies();
  return getIronSession<SessionData>(c, getSessionOptions());
}

export async function getSessionUser(): Promise<UserRow | null> {
  const s = await getSession();
  if (!s.userId) return null;
  const row = db()
    .prepare("SELECT * FROM users WHERE id = ?")
    .get(s.userId) as UserRow | undefined;
  return row ?? null;
}
