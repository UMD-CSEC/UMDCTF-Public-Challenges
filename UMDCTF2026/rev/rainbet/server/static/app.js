"use strict";

const $ = (id) => document.getElementById(id);

const state = {
  sid: null,
  secret: null,
  streak: 0,
  target: 25,
  game: null,
  progress: { revealed: [], crossed: 0 },
};
let ws = null;
let pending = false;

// ---- crypto ---------------------------------------------------------------

async function hmacHex(secretHex, msg) {
  const key = new Uint8Array(secretHex.match(/../g).map((b) => parseInt(b, 16)));
  const ck = await crypto.subtle.importKey(
    "raw", key, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", ck, new TextEncoder().encode(msg));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function canonView() {
  const g = state.game;
  if (g.type === "mines") {
    const rev = [...state.progress.revealed].sort((a, b) => a - b).join(",");
    return `mines:${state.streak}:${g.grid_size}:${g.num_mines}:${rev}`;
  }
  return `chicken:${state.streak}:${g.steps}:${state.progress.crossed}`;
}

async function sendMove(action, extra = {}) {
  if (pending || !ws || ws.readyState !== WebSocket.OPEN) return;
  pending = true;
  const view = canonView();
  const sig = await hmacHex(state.secret, view);
  ws.send(JSON.stringify({ action, view, sig, ...extra }));
}

// ---- UI -------------------------------------------------------------------

function toast(msg, ms = 2000) {
  const el = $("toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.add("hidden"), ms);
}

function setStreak(n, target) {
  state.streak = n;
  state.target = target;
  $("streak-n").textContent = n;
  $("streak-t").textContent = target;
}

function showSection(id) {
  for (const s of ["mines", "chicken", "finished"]) {
    $(s).classList.toggle("hidden", s !== id);
  }
}

function updateMinesSidebar() {
  const g = state.game;
  if (!g || g.type !== "mines") return;
  const total = g.grid_size * g.grid_size;
  const safe = total - g.num_mines;
  const remaining = safe - state.progress.revealed.length;
  $("mines-gem-count").textContent = remaining;
  $("mines-bomb-count").textContent = g.num_mines;

  // Grid Size tabs: highlight the active one
  const tabs = $("mines-grid-tabs");
  if (tabs) {
    for (const tab of tabs.children) {
      tab.classList.toggle("active", Number(tab.dataset.size) === total);
    }
  }

  // Slider: position thumb based on mines / (total - 1)
  const pct = (g.num_mines / (total - 1)) * 100;
  const thumb = $("mines-slider-thumb");
  const range = $("mines-slider-range");
  if (thumb) thumb.style.left = `${pct}%`;
  if (range) range.style.width = `${pct}%`;
}

function renderMines() {
  const g = state.game;
  const grid = $("mines-grid");
  grid.innerHTML = "";
  grid.style.setProperty("--grid-size", g.grid_size);
  const total = g.grid_size * g.grid_size;
  const revealed = new Set(state.progress.revealed);
  const tpl = $("tile-template");
  for (let i = 0; i < total; i++) {
    const node = tpl.content.firstElementChild.cloneNode(true);
    node.dataset.tile = i;
    if (revealed.has(i)) {
      node.classList.add("revealed");
      node.disabled = true;
    }
    node.addEventListener("click", () => {
      if (node.disabled) return;
      sendMove("reveal", { tile: i });
    });
    grid.appendChild(node);
  }
  updateMinesSidebar();
}

const LANE_WIDTH_PX = 52;
const LANE_GAP_PX = 4;
const LANE_STEP_PX = LANE_WIDTH_PX + LANE_GAP_PX;
const CHICKEN_TRACK_PAD_PX = 28;

function positionChickenMarker() {
  const marker = $("chicken-marker");
  if (!marker) return;
  const crossed = state.progress.crossed;
  let x;
  if (crossed === 0) x = CHICKEN_TRACK_PAD_PX / 2;
  else x = CHICKEN_TRACK_PAD_PX + (crossed - 1) * LANE_STEP_PX + LANE_WIDTH_PX / 2;
  marker.style.left = `${x}px`;

  const track = $("chicken-track");
  if (track) {
    const tw = track.clientWidth;
    const sl = track.scrollLeft;
    if (x > sl + tw - 120 || x < sl + 60) {
      track.scrollTo({ left: Math.max(0, x - tw / 2), behavior: "smooth" });
    }
  }
}

function updateChickenPayout() {
  const g = state.game;
  if (!g || g.type !== "chicken") return;
  const cur = state.progress.crossed;
  const m = cur > 0 ? g.multipliers[cur - 1] : 1.0;
  const el = $("chicken-multiplier");
  if (el) el.textContent = m.toFixed(2) + "x";
}

function renderChicken() {
  const g = state.game;
  const riskEl = $("chicken-risk-name");
  if (riskEl && g.risk) riskEl.textContent = g.risk;
  const row = $("chicken-row");
  row.innerHTML = "";
  for (let i = 0; i < g.steps; i++) {
    const lane = document.createElement("div");
    lane.className = "lane" + (i < state.progress.crossed ? " crossed" : "");
    lane.dataset.step = i;
    const mult = document.createElement("div");
    mult.className = "mult";
    mult.textContent = g.multipliers[i].toLocaleString();
    lane.appendChild(mult);
    const stepNum = document.createElement("div");
    stepNum.className = "step-num";
    stepNum.textContent = i + 1;
    lane.appendChild(stepNum);
    const car = document.createElement("div");
    car.className = "car-icon";
    car.textContent = "🚗";
    lane.appendChild(car);
    row.appendChild(lane);
  }
  positionChickenMarker();
  updateChickenPayout();
}

function renderGame() {
  if (state.game.type === "mines") {
    showSection("mines");
    renderMines();
  } else {
    showSection("chicken");
    renderChicken();
  }
}

function flashTile(tile, cls) {
  const grid = $("mines-grid");
  const node = grid.children[tile];
  if (!node) return;
  node.classList.add("flash");
  setTimeout(() => node.classList.remove("flash"), 220);
  if (cls) node.classList.add(cls);
  node.disabled = true;
}

function showReveal(reveal) {
  if (reveal.type === "mines") {
    const grid = $("mines-grid");
    for (const m of reveal.mines) grid.children[m]?.classList.add("mine");
  } else {
    const row = $("chicken-row");
    for (const c of reveal.cars) row.children[c]?.classList.add("car");
  }
}

function showFlag(flag) {
  $("flag").textContent = flag;
  showSection("finished");
}

// ---- WS handling ----------------------------------------------------------

function applyNextGame(ng) {
  state.streak = ng.streak;
  state.target = ng.target;
  if (ng.complete) { showFlag("already complete — POST /api/reset for a new run"); return; }
  state.game = ng.game;
  state.progress = {
    revealed: [...(ng.game.revealed || [])],
    crossed: ng.game.crossed || 0,
  };
  setStreak(state.streak, state.target);
  renderGame();
}

function handleMessage(m) {
  switch (m.kind) {
    case "hello":
      state.sid = m.session_id;
      state.target = m.target;
      setStreak(m.streak, m.target);
      if (m.complete) { showFlag("already complete — POST /api/reset for a new run"); return; }
      state.game = m.game;
      state.progress = {
        revealed: [...(m.game.revealed || [])],
        crossed: m.game.crossed || 0,
      };
      renderGame();
      break;
    case "state":
      setStreak(m.streak, state.target);
      if ("revealed" in m) {
        const newly = m.revealed.filter((x) => !state.progress.revealed.includes(x));
        state.progress.revealed = m.revealed;
        for (const t of newly) flashTile(t, "revealed");
        updateMinesSidebar();
      }
      if ("crossed" in m) {
        const prev = state.progress.crossed;
        state.progress.crossed = m.crossed;
        const row = $("chicken-row");
        for (let i = prev; i < m.crossed; i++) {
          row.children[i]?.classList.add("crossed");
        }
        positionChickenMarker();
        updateChickenPayout();
      }
      break;
    case "result":
      if (m.reveal) showReveal(m.reveal);
      if (m.session_id && m.secret) {
        state.sid = m.session_id;
        state.secret = m.secret;
      }
      if (m.result === "win" && m.complete) { setStreak(m.streak, m.target); showFlag(m.flag); return; }
      if (m.result === "complete") { showFlag(m.flag); return; }
      if (m.next_game) {
        const delay = m.result === "lose" ? 1600 : 600;
        if (m.result === "lose") toast("streak reset", 2200);
        setTimeout(() => applyNextGame(m.next_game), delay);
      }
      break;
    case "error":
      toast(m.error + (m.expected_view ? ` (expected: ${m.expected_view})` : ""), 3200);
      break;
  }
  pending = false;
}

// ---- bootstrap ------------------------------------------------------------

async function init() {
  $("mines-cashout").addEventListener("click", () => sendMove("cashout"));
  const cx = $("chicken-cross");
  if (cx) cx.addEventListener("click", () => sendMove("cross"));
  const cc = $("chicken-cashout");
  if (cc) cc.addEventListener("click", () => sendMove("cashout"));

  const info = await fetch("/api/sessioninfo", { credentials: "same-origin" }).then((r) => r.json());
  state.sid = info.session_id;
  state.secret = info.secret;

  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.addEventListener("message", (e) => handleMessage(JSON.parse(e.data)));
  ws.addEventListener("close", () => toast("connection closed — refresh to reconnect", 5000));
  ws.addEventListener("error", () => toast("ws error", 3000));
}

init();
