import Link from "next/link";
import type { UserRow } from "@/lib/db";
import { logoutAction } from "@/app/actions/auth";

export function Nav({ user }: { user: UserRow | null }) {
  return (
    <header className="sticky top-0 z-20 border-b border-[color:var(--color-rule)] bg-[color:var(--color-bg)]/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <div className="flex items-baseline gap-10">
          <Link href="/" className="group flex items-baseline gap-3">
            <span
              aria-hidden
              className="relative inline-block h-[14px] w-[14px] -translate-y-[1px] bg-[color:var(--color-signal)]"
            >
              <span className="absolute inset-0 bg-[color:var(--color-signal)] opacity-60 blur-[6px]" />
            </span>
            <span
              className="display text-[22px] leading-none tracking-tight"
              style={{ fontVariationSettings: '"opsz" 30, "SOFT" 30' }}
            >
              OpenInsight
            </span>
          </Link>
          <nav className="hidden items-center gap-6 md:flex">
            {user && <NavLink href="/sheets/new">New sheet</NavLink>}
            <Link
              href="/admin"
              hidden={user?.role !== "admin"}
              className="eyebrow text-[color:var(--color-signal)] hover:brightness-110"
            >
              Admin ▸
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <div
                id="user-profile"
                data-role={user.role}
                className="hidden items-baseline gap-2 border-l border-[color:var(--color-rule)] pl-3 md:flex"
              >
                <span className="eyebrow">Signed in</span>
                <span
                  id="current-user"
                  className="font-mono text-xs text-[color:var(--color-paper)]"
                >
                  {user.username}
                </span>
              </div>
              <form action={logoutAction}>
                <button
                  type="submit"
                  className="eyebrow border border-[color:var(--color-rule)] px-3 py-1 text-[color:var(--color-paper-dim)] transition-colors hover:border-[color:var(--color-rule-strong)] hover:text-[color:var(--color-paper)]"
                >
                  Sign out
                </button>
              </form>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="eyebrow text-[color:var(--color-paper-dim)] hover:text-[color:var(--color-paper)]"
              >
                Sign in
              </Link>
              <Link
                href="/signup"
                className="bg-[color:var(--color-signal)] px-3 py-1.5 font-mono text-xs font-medium text-[#0b0c0e] hover:brightness-110"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

function NavLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="eyebrow text-[color:var(--color-paper-dim)] transition-colors hover:text-[color:var(--color-paper)]"
    >
      {children}
    </Link>
  );
}
