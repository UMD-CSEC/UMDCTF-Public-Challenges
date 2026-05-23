import { useEffect, useRef, useState, useCallback } from "react";

const WS_URL = import.meta.env.VITE_WS_URL ?? "wss://localhost:4443/";

export type RoundMeta = { round: number; total: number; time_ms: number };

export type UiState =
  | { phase: "idle" }
  | { phase: "connecting" }
  | { phase: "awaiting"; round: RoundMeta | null }
  | { phase: "round"; round: RoundMeta; chartUrl: string; deadline: number }
  | { phase: "reject"; reason: string }
  | { phase: "pass"; flag: string }
  | { phase: "lost"; reason: string };

type Answer = "buy" | "sell" | "hold";

export type Keepalive = {
  status: "idle" | "live" | "stale";
  lastAckAt: number | null;
  lastRttMs: number | null;
};

const HEARTBEAT_INTERVAL_MS = 2000;
const STALE_THRESHOLD_MS = 6000;

export function useChoppediver() {
  const wsRef = useRef<WebSocket | null>(null);
  const [state, setState] = useState<UiState>({ phase: "idle" });
  const [total, setTotal] = useState<number | null>(null);
  const [keepalive, setKeepalive] = useState<Keepalive>({
    status: "idle",
    lastAckAt: null,
    lastRttMs: null,
  });

  const start = useCallback(() => {
    if (wsRef.current) return;
    setState({ phase: "connecting" });
    const ws = new WebSocket(WS_URL);
    ws.binaryType = "arraybuffer";
    wsRef.current = ws;

    let pendingRound: RoundMeta | null = null;
    let hbTimer: ReturnType<typeof setInterval> | null = null;
    let staleTimer: ReturnType<typeof setInterval> | null = null;
    let lastHbSentAt: number | null = null;

    const sendHeartbeat = () => {
      if (ws.readyState !== WebSocket.OPEN) return;
      lastHbSentAt = performance.now();
      ws.send(JSON.stringify({ type: "heartbeat" }));
    };

    ws.onopen = () => {
      setState({ phase: "awaiting", round: null });
      setKeepalive({ status: "live", lastAckAt: performance.now(), lastRttMs: null });
      sendHeartbeat();
      hbTimer = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL_MS);
      staleTimer = setInterval(() => {
        setKeepalive((k) =>
          k.lastAckAt !== null && performance.now() - k.lastAckAt > STALE_THRESHOLD_MS
            ? { ...k, status: "stale" }
            : k,
        );
      }, 1000);
    };

    ws.onmessage = (ev) => {
      if (typeof ev.data !== "string") {
        // binary: chart PNG
        const round = pendingRound;
        if (!round) return;
        const blob = new Blob([ev.data], { type: "image/png" });
        const url = URL.createObjectURL(blob);
        setState({
          phase: "round",
          round,
          chartUrl: url,
          deadline: performance.now() + round.time_ms,
        });
        return;
      }
      let data: any;
      try { data = JSON.parse(ev.data); } catch { return; }
      switch (data.type) {
        case "hello":
          setTotal(data.total);
          break;
        case "round":
          pendingRound = { round: data.round, total: data.total, time_ms: data.time_ms };
          setState({ phase: "awaiting", round: pendingRound });
          break;
        case "correct":
          setState({ phase: "awaiting", round: null });
          break;
        case "hb_ack": {
          const now = performance.now();
          const rtt = lastHbSentAt !== null ? Math.round(now - lastHbSentAt) : null;
          setKeepalive({ status: "live", lastAckAt: now, lastRttMs: rtt });
          break;
        }
        case "reject":
          setState({ phase: "reject", reason: data.reason ?? "unspecified" });
          break;
        case "pass":
          setState({ phase: "pass", flag: data.flag });
          break;
      }
    };

    ws.onerror = () => {
      setState({ phase: "lost", reason: "connection error" });
    };

    ws.onclose = () => {
      if (hbTimer !== null) clearInterval(hbTimer);
      if (staleTimer !== null) clearInterval(staleTimer);
      setKeepalive({ status: "idle", lastAckAt: null, lastRttMs: null });
      setState((s) =>
        s.phase === "reject" || s.phase === "pass"
          ? s
          : { phase: "lost", reason: "connection closed" },
      );
      wsRef.current = null;
    };
  }, []);

  const submit = useCallback((value: Answer) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: "answer", value }));
  }, []);

  const ready = useCallback(() => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: "ready" }));
  }, []);

  useEffect(() => {
    return () => {
      wsRef.current?.close();
      if (state.phase === "round") URL.revokeObjectURL(state.chartUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { state, start, submit, ready, total, keepalive };
}
