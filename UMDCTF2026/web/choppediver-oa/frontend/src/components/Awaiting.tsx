import type { RoundMeta, Keepalive as KeepaliveState } from "../lib/ws";
import { Keepalive } from "./Keepalive";

export function Awaiting({
  round,
  total,
  keepalive,
}: {
  round: RoundMeta | null;
  total: number | null;
  keepalive: KeepaliveState;
}) {
  return (
    <div className="min-h-screen bg-canvas flex flex-col">
      <div className="px-8 pt-4 flex justify-end">
        <Keepalive keepalive={keepalive} />
      </div>
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-teal text-[13px] font-semibold tracking-wide uppercase">
            <span className="inline-block w-2 h-2 rounded-full bg-teal pulse-dot" />
            {round ? "Preparing chart" : "Connecting"}
          </div>
          <div className="mt-4 text-ash text-[13px]">
            {round
              ? `Round ${round.round} of ${round.total}`
              : total
              ? `${total} rounds · ${total * 2}s average`
              : " "}
          </div>
        </div>
      </div>
    </div>
  );
}
