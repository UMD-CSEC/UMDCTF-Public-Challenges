import bcrypt from "bcryptjs";
import { db, type UserRow } from "./db";

const USERNAME_RE = /^[a-zA-Z0-9_]{3,32}$/;

export function validateUsername(u: string): string | null {
  if (!USERNAME_RE.test(u)) {
    return "Username must be 3-32 chars, letters / digits / underscore.";
  }
  return null;
}

export function validatePassword(p: string): string | null {
  if (p.length < 12) {
    return "Password must be at least 12 characters.";
  }
  if (p.length > 200) return "Password too long.";
  if (!/[a-z]/.test(p) || !/[A-Z]/.test(p) || !/[0-9]/.test(p)) {
    return "Password must include lower + upper case letters and a digit.";
  }
  return null;
}

export async function createUser(
  username: string,
  password: string,
  role: "user" | "admin" = "user",
): Promise<UserRow> {
  const hash = await bcrypt.hash(password, 10);
  const now = Date.now();
  const info = db()
    .prepare(
      "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
    )
    .run(username, hash, role, now);
  return db()
    .prepare("SELECT * FROM users WHERE id = ?")
    .get(info.lastInsertRowid) as UserRow;
}

export async function verifyLogin(
  username: string,
  password: string,
): Promise<UserRow | null> {
  const row = db()
    .prepare("SELECT * FROM users WHERE username = ?")
    .get(username) as UserRow | undefined;
  if (!row) return null;
  const ok = await bcrypt.compare(password, row.password_hash);
  return ok ? row : null;
}
