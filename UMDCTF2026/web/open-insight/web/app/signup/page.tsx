import Link from "next/link";
import { signupAction } from "@/app/actions/auth";

export default async function SignupPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const { error } = await searchParams;
  return (
    <div className="mx-auto max-w-[420px] px-6 pt-24 pb-24">
      <div className="mb-10">
        <p className="eyebrow">Research Desk · New analyst</p>
        <h1 className="display mt-3 text-5xl">Open an account.</h1>
        <p className="mt-4 text-sm text-[color:var(--color-paper-dim)]">
          Publish models, share workbooks, and track your calls over time.
        </p>
      </div>
      <form action={signupAction} className="space-y-6">
        <div>
          <label htmlFor="username" className="eyebrow mb-2 block">
            Choose a handle
          </label>
          <input
            id="username"
            name="username"
            required
            autoComplete="username"
            className="w-full border-0 border-b border-[color:var(--color-rule-strong)] bg-transparent px-0 py-2 font-mono text-sm text-[color:var(--color-paper)] outline-none transition-colors focus:border-[color:var(--color-signal)]"
          />
        </div>
        <div>
          <label htmlFor="password" className="eyebrow mb-2 block">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            required
            autoComplete="new-password"
            className="w-full border-0 border-b border-[color:var(--color-rule-strong)] bg-transparent px-0 py-2 font-mono text-sm text-[color:var(--color-paper)] outline-none transition-colors focus:border-[color:var(--color-signal)]"
          />
        </div>
        {error && (
          <p className="font-mono text-xs text-[color:var(--color-down)]">
            ⚠ {error}
          </p>
        )}
        <button
          type="submit"
          className="mt-4 inline-flex items-center gap-2 bg-[color:var(--color-signal)] px-5 py-2.5 text-sm font-medium text-[#0b0c0e] transition-[filter] hover:brightness-110"
        >
          Create account
          <span aria-hidden>→</span>
        </button>
      </form>
      <p className="mt-10 text-sm text-[color:var(--color-paper-dim)]">
        Already have one?{" "}
        <Link
          href="/login"
          className="text-[color:var(--color-signal)] underline-offset-4 hover:underline"
        >
          Sign in
        </Link>
      </p>
    </div>
  );
}
