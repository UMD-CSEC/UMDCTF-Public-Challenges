type Props = {
  onContinue: () => void;
  totalRounds: number | null;
};

export function Instructions({ onContinue, totalRounds }: Props) {
  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
      <div
        className="bg-card fade-up"
        style={{
          width: "min(520px, 100%)",
          borderRadius: "6px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.08), 0 6px 16px rgba(0,0,0,0.04)",
        }}
      >
        <div className="px-8 pt-8 pb-6">
          {/* Progress segments */}
          <div className="flex gap-1.5 mb-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="flex-1 h-[3px]"
                style={{
                  backgroundColor: i <= 4 ? "var(--color-teal)" : "var(--color-rule)",
                }}
              />
            ))}
          </div>

          <h2 className="text-[22px] font-bold text-ink mb-3">Instruction</h2>
          <div className="text-[13.5px] text-ink/80 leading-[1.6] space-y-3">
            <p>
              You will be shown a series of stock price charts.
              {totalRounds ? ` There are ${totalRounds} rounds in total.` : ""}
              &nbsp;For each chart, decide whether to <strong>BUY</strong>,{" "}
              <strong>HOLD</strong>, or <strong>SELL</strong>.
            </p>
            <p>
              Response time decreases each round. A missed or incorrect response
              ends the assessment immediately. Guessing is not recommended.
            </p>
            <p className="text-ash">
              Keyboard shortcuts: <kbd className="kbd">B</kbd>{" "}
              <kbd className="kbd">H</kbd> <kbd className="kbd">S</kbd>
            </p>
          </div>

          <div className="mt-8 flex justify-end">
            <button
              onClick={onContinue}
              className="bg-teal hover:bg-teal-dark text-white text-[13px] font-semibold tracking-wide uppercase
                         px-6 py-2.5 rounded-[4px] transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <style>{`
        .kbd {
          display: inline-block;
          padding: 1px 6px;
          margin: 0 2px;
          font-family: var(--font-mono);
          font-size: 11px;
          color: var(--color-ink);
          background: var(--color-canvas);
          border: 1px solid var(--color-rule);
          border-radius: 3px;
          box-shadow: inset 0 -1px 0 rgba(0,0,0,0.08);
        }
      `}</style>
    </div>
  );
}
