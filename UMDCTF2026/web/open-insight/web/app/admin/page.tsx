import { notFound } from "next/navigation";
import { getSessionUser } from "@/lib/session";

export default async function AdminPage() {
  const user = await getSessionUser();
  if (!user || user.role !== "admin") {
    notFound();
  }
  const FLAG = process.env.FLAG;
  if (!FLAG) {
    throw new Error("FLAG environment variable is required");
  }
  return (
    <div className="mx-auto max-w-3xl px-6 pt-16 pb-24">
      <p className="eyebrow">Restricted · Research Desk internal</p>
      <h1
        className="display mt-3 text-5xl"
        style={{ fontVariationSettings: '"opsz" 96, "SOFT" 40' }}
      >
        Admin console.
      </h1>
      <p className="mt-4 text-sm text-[color:var(--color-paper-dim)]">
        Welcome,{" "}
        <span className="font-mono text-[color:var(--color-paper)]">
          {user.username}
        </span>
        . Internal tools, review queue, and the backstage pass.
      </p>

      <div className="mt-12 border-t border-[color:var(--color-rule)]">
        <div className="flex items-baseline justify-between border-b border-[color:var(--color-rule)] py-4">
          <p className="eyebrow">Desk · Administrator credentials</p>
          <p className="eyebrow text-[color:var(--color-paper-faint)]">
            Rotate quarterly
          </p>
        </div>
        <div className="border-b border-[color:var(--color-rule)] py-6">
          <p className="eyebrow mb-2">Master flag</p>
          <p className="break-all font-mono text-lg text-[color:var(--color-signal)]">
            {FLAG}
          </p>
          <p className="mt-3 text-xs text-[color:var(--color-paper-faint)]">
            Paste this into the CTF submit box. Do not share.
          </p>
        </div>
        <div className="py-6">
          <p className="eyebrow mb-2">Notes</p>
          <p className="text-sm text-[color:var(--color-paper-dim)]">
            Review queue lives at the{" "}
            <span className="font-mono text-[color:var(--color-paper)]">
              bot
            </span>{" "}
            service (port 3001). All incoming submissions are opened in a
            disposable browser session using this account.
          </p>
        </div>
      </div>
    </div>
  );
}
