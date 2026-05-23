import type { Keepalive as KeepaliveState } from "../lib/ws";

type Props = { keepalive: KeepaliveState };

export function Keepalive({ keepalive }: Props) {
  if (keepalive.status === "idle") return null;
  const { status, lastRttMs } = keepalive;
  const label =
    status === "live"
      ? lastRttMs !== null
        ? `ping ${lastRttMs}ms`
        : "ping"
      : "ping stale";
  return (
    <div className="inline-flex items-center gap-1.5 text-[11px] text-ash font-mono">
      <span
        className={`inline-block w-1.5 h-1.5 rounded-full ${
          status === "live" ? "keepalive-live" : ""
        }`}
        style={{
          backgroundColor: status === "live" ? "var(--color-teal)" : "#f5b400",
        }}
      />
      <span className="tabular-nums">{label}</span>
    </div>
  );
}
