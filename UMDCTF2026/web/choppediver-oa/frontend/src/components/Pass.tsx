import { useState } from "react";

export function Pass({ flag }: { flag: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(flag);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch { /* ignore */ }
  };

  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
      <div
        className="bg-card fade-up"
        style={{
          width: "min(560px, 100%)",
          borderRadius: "6px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.08), 0 6px 16px rgba(0,0,0,0.04)",
        }}
      >
        <div className="px-10 pt-10 pb-8">
          <div className="flex gap-1.5 mb-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex-1 h-[3px]" style={{ backgroundColor: "var(--color-bid)" }} />
            ))}
          </div>
          <h1 className="text-[26px] font-bold text-ink mb-2">Assessment complete</h1>
          <p className="text-[14px] text-ash leading-[1.6] mb-6">
            Your responses have been recorded. A member of our team will be in
            touch.
          </p>
          <div
            className="bg-canvas rounded-[4px] p-4"
            style={{ border: "1px solid var(--color-rule)" }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] text-ash uppercase tracking-wider font-semibold">
                Reference&nbsp;Code
              </span>
              <button
                onClick={copy}
                className="text-[12px] text-teal hover:text-teal-dark font-semibold"
              >
                {copied ? "Copied ✓" : "Copy"}
              </button>
            </div>
            <code className="block font-mono text-[14px] text-ink break-all select-all">
              {flag}
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}
