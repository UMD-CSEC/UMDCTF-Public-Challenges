import Database from "better-sqlite3";
import path from "node:path";
import fs from "node:fs";

const DB_DIR = process.env.DB_DIR ?? path.join(process.cwd(), "data");
const DB_PATH = path.join(DB_DIR, "openinsight.db");

fs.mkdirSync(DB_DIR, { recursive: true });

let _db: Database.Database | null = null;

export function db(): Database.Database {
  if (_db) return _db;
  _db = new Database(DB_PATH);
  _db.pragma("journal_mode = WAL");
  _db.pragma("foreign_keys = ON");
  migrate(_db);
  return _db;
}

function migrate(d: Database.Database) {
  d.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'user',
      created_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sheets (
      id TEXT PRIMARY KEY,
      owner_id INTEGER NOT NULL REFERENCES users(id),
      title TEXT NOT NULL,
      cells_json TEXT NOT NULL,
      is_popular INTEGER NOT NULL DEFAULT 0,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_sheets_owner ON sheets(owner_id);
    CREATE INDEX IF NOT EXISTS idx_sheets_popular ON sheets(is_popular, updated_at);
  `);
}

export type UserRow = {
  id: number;
  username: string;
  password_hash: string;
  role: "user" | "admin";
  created_at: number;
};

export type SheetRow = {
  id: string;
  owner_id: number;
  title: string;
  cells_json: string;
  is_popular: number;
  created_at: number;
  updated_at: number;
};

