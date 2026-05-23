import { useEffect, useRef, useState } from "react";
import type { RoundMeta, Keepalive as KeepaliveState } from "../lib/ws";
import { Keepalive } from "./Keepalive";

type Props = {
  round: RoundMeta;
  chartUrl: string;
  deadline: number;
  onAnswer: (v: "buy" | "sell" | "hold") => void;
  keepalive: KeepaliveState;
};

export function Round({ round, chartUrl, deadline, onAnswer, keepalive }: Props) {
  const [submitted, setSubmitted] = useState<null | "buy" | "sell" | "hold">(null);
  const [displayRemaining, setDisplayRemaining] = useState(round.time_ms);
  const rafRef = useRef(0);

  useEffect(() => {
    setSubmitted(null);
  }, [round.round]);

  // Lightweight RAF only for the text countdown readout.
  useEffect(() => {
    const loop = () => {
      setDisplayRemaining(Math.max(0, deadline - performance.now()));
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
  }, [deadline]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (submitted) return;
      const k = e.key.toLowerCase();
      if (k === "b") submit("buy");
      else if (k === "s") submit("sell");
      else if (k === "h") submit("hold");
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [submitted]);

  const submit = (v: "buy" | "sell" | "hold") => {
    if (submitted) return;
    setSubmitted(v);
    onAnswer(v);
  };

  const label =
    displayRemaining >= 1000
      ? `${(displayRemaining / 1000).toFixed(2)}s`
      : `${displayRemaining.toFixed(0)}ms`;

  return (
    <div className="h-screen bg-canvas flex flex-col overflow-hidden">
      {/* Top meta */}
      <div className="px-8 pt-4 pb-2 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <div className="text-[12px] text-ash tabular-nums">
            {round.round}/{round.total}
          </div>
          <Keepalive keepalive={keepalive} />
        </div>
        <div className="text-[12px] text-ash">
          Time left:&nbsp;<span className="text-ink tabular-nums">{label}</span>
        </div>
      </div>

      {/* Progress dots (rounds completed) */}
      <div className="px-8 mb-3 shrink-0">
        <div className="flex gap-1">
          {Array.from({ length: round.total }).map((_, i) => (
            <div
              key={i}
              className="flex-1 h-[3px]"
              style={{
                backgroundColor:
                  i + 1 < round.round
                    ? "var(--color-teal)"
                    : i + 1 === round.round
                    ? "var(--color-teal-pale)"
                    : "var(--color-rule)",
              }}
            />
          ))}
        </div>
      </div>

      {/* Main — viewport-constrained */}
      <main className="flex-1 min-h-0 flex flex-col items-center justify-center px-4 pb-6 gap-3">
        <div
          className="w-full flex flex-col min-h-0 flex-1 gap-3"
          style={{ maxWidth: "960px" }}
        >
          {/* Chart card fills available space; image contains within */}
          <div
            className="bg-card overflow-hidden fade-up flex-1 min-h-0 flex items-center justify-center"
            style={{
              borderRadius: "6px",
              boxShadow: "0 1px 3px rgba(0,0,0,0.08), 0 6px 16px rgba(0,0,0,0.04)",
            }}
          >
            <img
              src={chartUrl}
              alt=""
              className="max-w-full max-h-full object-contain block"
              draggable={false}
            />
          </div>

          {/* Smooth time bar */}
          <div className="h-1.5 bg-rule rounded-sm overflow-hidden shrink-0">
            <div
              key={round.round}
              className="timebar-fill h-full"
              style={{
                animationDuration: `${round.time_ms}ms`,
                backgroundColor: "var(--color-teal)",
              }}
            />
          </div>

          {/* Answer buttons — fixed compact height */}
          <div className="grid grid-cols-3 gap-3 shrink-0">
            <AnswerButton
              color="bid"
              label="Buy"
              hint="B"
              active={submitted === "buy"}
              disabled={!!submitted}
              onClick={() => submit("buy")}
            />
            <AnswerButton
              color="hold"
              label="Hold"
              hint="H"
              active={submitted === "hold"}
              disabled={!!submitted}
              onClick={() => submit("hold")}
            />
            <AnswerButton
              color="ask"
              label="Sell"
              hint="S"
              active={submitted === "sell"}
              disabled={!!submitted}
              onClick={() => submit("sell")}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

function AnswerButton({
  color,
  label,
  hint,
  active,
  disabled,
  onClick,
}: {
  color: "bid" | "ask" | "hold";
  label: string;
  hint: string;
  active: boolean;
  disabled: boolean;
  onClick: () => void;
}) {
  const base =
    color === "bid"
      ? "bg-bid hover:bg-bid-dark"
      : color === "ask"
      ? "bg-ask hover:bg-ask-dark"
      : "bg-hold hover:bg-hold-dark";

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`relative ${base} text-white rounded-[4px] py-6 transition-colors
                  disabled:cursor-not-allowed
                  ${active ? "ring-4 ring-offset-2 ring-teal ring-offset-canvas" : ""}
                  ${disabled && !active ? "opacity-50" : ""}`}
      style={{ boxShadow: "0 1px 2px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04)" }}
    >
      <span className="text-[28px] font-bold uppercase tracking-wider">{label}</span>
      <span
        className="absolute top-2 right-3 font-mono text-[11px] text-white/75"
      >
        [{hint}]
      </span>
    </button>
  );
}
