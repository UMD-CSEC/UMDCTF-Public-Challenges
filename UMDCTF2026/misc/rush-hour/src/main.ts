import { Renderer } from './renderer';

interface StateMsg {
  type: 'state';
  t: number;
  x: number;
  z: number;
  heading: number;
  speed: number;
  obs: number[];
  obsDelta: number[];
  attack: 'none' | 'active' | 'error';
  attackError: string | null;
  goalReached: boolean;
  timedOut: boolean;
  flag: string | null;
}

interface AckMsg {
  type: 'submit_ack';
  ok: boolean;
  error?: string;
  cleared?: boolean;
}

function bufferToBase64(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk) as unknown as number[]);
  }
  return btoa(binary);
}

async function main() {
  const canvas = document.getElementById('canvas') as HTMLCanvasElement;
  const loading = document.getElementById('loading')!;
  const status = document.getElementById('status')!;
  const flagEl = document.getElementById('flag')!;
  const attackStatus = document.getElementById('attackStatus')!;
  const fileInput = document.getElementById('fileInput') as HTMLInputElement;
  const btnChoose = document.getElementById('btnChoose') as HTMLButtonElement;
  const btnClear = document.getElementById('btnClear') as HTMLButtonElement;
  const btnReset = document.getElementById('btnReset') as HTMLButtonElement;
  const fileName = document.getElementById('fileName')!;

  let renderer: Renderer;
  let nativeW: number;
  let nativeH: number;
  try {
    renderer = new Renderer(canvas);
    const dims = await renderer.load('/snapshot.jpg', '/model.glb', '/texture.jpg');
    nativeW = dims.width;
    nativeH = dims.height;
    renderer.eyeX = 0; renderer.eyeY = 10; renderer.eyeZ = 60;
    renderer.lookX = 0; renderer.lookZ = 0;
    renderer.fov = 15;
    renderer.carScale = 0.75;
    loading.style.display = 'none';
  } catch (e) {
    loading.textContent = 'Error: ' + (e instanceof Error ? e.message : String(e));
    return;
  }

  function fitCanvas() {
    const imgAspect = nativeW / nativeH;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    let cw: number, ch: number;
    if (vw / vh > imgAspect) { ch = vh; cw = vh * imgAspect; }
    else { cw = vw; ch = vw / imgAspect; }
    canvas.style.width = cw + 'px';
    canvas.style.height = ch + 'px';
  }
  fitCanvas();
  window.addEventListener('resize', fitCanvas);

  let ws: WebSocket | null = null;
  let lastState: StateMsg | null = null;
  const wsUrl = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`;

  function wsSend(obj: unknown) {
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj));
  }

  function connect() {
    status.textContent = 'connecting…';
    status.className = '';
    ws = new WebSocket(wsUrl);
    ws.onopen = () => { status.textContent = 'connected'; status.className = 'connected'; };
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data) as StateMsg | AckMsg;
        if (msg.type === 'state') {
          lastState = msg;
        } else if (msg.type === 'submit_ack') {
          if (!msg.ok) {
            attackStatus.className = 'error';
            attackStatus.textContent = 'attack: error — ' + (msg.error ?? 'unknown');
          }
        }
      } catch {}
    };
    ws.onclose = () => {
      status.textContent = 'disconnected — retrying…';
      status.className = 'disconnected';
      ws = null;
      setTimeout(connect, 1000);
    };
    ws.onerror = () => {};
  }
  connect();

  btnChoose.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', async () => {
    const f = fileInput.files?.[0];
    if (!f) return;
    fileName.textContent = `${f.name} (${f.size} bytes)`;
    if (f.size > 100_000) {
      attackStatus.className = 'error';
      attackStatus.textContent = 'attack: error — file > 100KB';
      return;
    }
    const buf = await f.arrayBuffer();
    wsSend({ type: 'submit', npz_b64: bufferToBase64(buf) });
  });
  btnClear.addEventListener('click', () => {
    wsSend({ type: 'clear_attack' });
    fileInput.value = '';
    fileName.textContent = '';
  });
  btnReset.addEventListener('click', () => wsSend({ type: 'reset' }));

  function frame() {
    if (lastState) {
      renderer.carX = lastState.x;
      renderer.carZ = lastState.z;
      renderer.carRotation = -(lastState.heading * 180 / Math.PI) + 90;

      if (lastState.attack === 'active') {
        attackStatus.className = 'active';
        attackStatus.textContent = 'attack: active';
      } else if (lastState.attack === 'error') {
        attackStatus.className = 'error';
        attackStatus.textContent = 'attack: error — ' + (lastState.attackError ?? '');
      } else if (attackStatus.className !== 'error') {
        attackStatus.className = 'none';
        attackStatus.textContent = 'attack: none';
      }

      if (lastState.goalReached && lastState.flag) {
        flagEl.style.display = 'flex';
        flagEl.innerHTML = `<div>GOAL REACHED</div><div style="color:#4f4;font-size:22px">${lastState.flag}</div>`;
      } else if (lastState.timedOut) {
        flagEl.style.display = 'flex';
        flagEl.innerHTML = `<div style="color:#f88">episode timed out</div>`;
      } else {
        flagEl.style.display = 'none';
      }
    }
    renderer.render();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

main();
