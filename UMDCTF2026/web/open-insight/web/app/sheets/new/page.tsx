import { redirect } from "next/navigation";
import { createSheetAction } from "@/app/actions/create-sheet";
import { getSessionUser } from "@/lib/session";

export default async function NewSheetPage() {
  const user = await getSessionUser();
  if (!user) redirect("/login");
  return (
    <div className="mx-auto max-w-[520px] px-6 pt-24 pb-24">
      <p className="eyebrow">Research Desk · New workbook</p>
      <h1 className="display mt-3 text-5xl">Start a model.</h1>
      <p className="mt-4 text-sm text-[color:var(--color-paper-dim)]">
        Give it a name. You can change it later.
      </p>
      <form action={createSheetAction} className="mt-10 space-y-6">
        <div>
          <label htmlFor="title" className="eyebrow mb-2 block">
            Workbook title
          </label>
          <input
            id="title"
            name="title"
            required
            placeholder="e.g. Fed rate cut Dec 2026 — my model"
            className="w-full border-0 border-b border-[color:var(--color-rule-strong)] bg-transparent px-0 py-2 font-mono text-sm text-[color:var(--color-paper)] outline-none transition-colors placeholder:text-[color:var(--color-paper-faint)] focus:border-[color:var(--color-signal)]"
          />
        </div>
        <button
          type="submit"
          className="inline-flex items-center gap-2 bg-[color:var(--color-signal)] px-5 py-2.5 text-sm font-medium text-[#0b0c0e] hover:brightness-110"
        >
          Create workbook
          <span aria-hidden>→</span>
        </button>
      </form>
    </div>
  );
}
