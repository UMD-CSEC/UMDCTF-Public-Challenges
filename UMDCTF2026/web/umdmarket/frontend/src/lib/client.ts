import {
  REQ_REGISTER,
  REQ_LOGIN,
  REQ_SUBSCRIBE,
  REQ_UNSUBSCRIBE,
  REQ_FETCH_TICKERS,
  REQ_FETCH_HISTORY,
  REQ_RESEND,
  REQ_TRADE,
  REQ_PORTFOLIO,
  REQ_BUY_FLAG,
  STATUS_OK,
  DATAGRAM_QUOTE,
  DATAGRAM_RESOLVED,
  QUOTE_HMAC_SIZE,
  QUOTE_DATAGRAM_SIZE,
  RESOLVED_DATAGRAM_SIZE,
  encodeU8,
  encodeU16,
  encodeU32,
  encodeLenPrefixedString,
  concat,
  readU16,
  readU32,
  readU64,
  readLenPrefixedString,
  readU16LenPrefixedString,
  statusToError,
} from "./protocol.ts";

export interface Ticker {
  id: number;
  name: string;
  description: string;
}

export interface HistoryRecord {
  timestamp: number; // unix seconds
  price: number; // yes price in units (0-10000)
}

export interface Position {
  tickerId: number;
  yesQty: number;
  noQty: number;
}

export interface Portfolio {
  balance: bigint;
  positions: Position[];
}

export interface TradeResult {
  fillPrice: number;
  newBalance: bigint;
}

export interface QuoteUpdate {
  seq: number;
  tickerId: number;
  yesPrice: number;
  hmac: Uint8Array;
}

// QuoteToken is the same shape as QuoteUpdate; the client echoes a received
// or resent quote back to the server on TRADE.
export type QuoteToken = QuoteUpdate;

export interface ResolutionEvent {
  tickerId: number;
  outcome: number; // 0 = YES, 1 = NO
}

type QuoteCallback = (quote: QuoteUpdate) => void;
type ResolutionCallback = (event: ResolutionEvent) => void;
type DisconnectCallback = () => void;

export class PredictionMarketClient {
  private wt: WebTransport | null = null;
  private quoteCallbacks: Set<QuoteCallback> = new Set();
  private resolutionCallbacks: Set<ResolutionCallback> = new Set();
  private disconnectCallbacks: Set<DisconnectCallback> = new Set();
  private _connected = false;

  get connected(): boolean {
    return this._connected;
  }

  async connect(url: string, certHash?: Uint8Array): Promise<void> {
    const opts: any = {};
    if (certHash) {
      // Must pass the raw ArrayBuffer of the exact 32-byte hash
      const hashBuffer = new ArrayBuffer(certHash.length);
      new Uint8Array(hashBuffer).set(certHash);
      opts.serverCertificateHashes = [
        { algorithm: "sha-256", value: hashBuffer },
      ];
      console.log("[UMDMarket] Connecting with serverCertificateHashes, hash length:", certHash.length);
    } else {
      console.log("[UMDMarket] Connecting without cert hash");
    }
    this.wt = new WebTransport(url, opts);
    await this.wt.ready;
    this._connected = true;
    this.startDatagramReader();

    this.wt.closed.then(() => {
      this._connected = false;
      this.disconnectCallbacks.forEach((cb) => cb());
    }).catch(() => {
      this._connected = false;
      this.disconnectCallbacks.forEach((cb) => cb());
    });
  }

  close(): void {
    if (this.wt) {
      this.wt.close();
      this.wt = null;
      this._connected = false;
    }
  }

  onQuote(cb: QuoteCallback): () => void {
    this.quoteCallbacks.add(cb);
    return () => this.quoteCallbacks.delete(cb);
  }

  onResolution(cb: ResolutionCallback): () => void {
    this.resolutionCallbacks.add(cb);
    return () => this.resolutionCallbacks.delete(cb);
  }

  onDisconnect(cb: DisconnectCallback): () => void {
    this.disconnectCallbacks.add(cb);
    return () => this.disconnectCallbacks.delete(cb);
  }

  private async startDatagramReader(): Promise<void> {
    if (!this.wt) return;
    const reader = this.wt.datagrams.readable.getReader();
    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        if (!value || value.length < 1) continue;

        const dv = new DataView(
          value.buffer,
          value.byteOffset,
          value.byteLength,
        );

        if (value[0] === DATAGRAM_QUOTE && value.length >= QUOTE_DATAGRAM_SIZE) {
          const seq = dv.getUint16(1, true);
          const tickerId = dv.getUint16(3, true);
          const yesPrice = dv.getUint16(5, true);
          const hmac = new Uint8Array(QUOTE_HMAC_SIZE);
          hmac.set(value.subarray(7, 7 + QUOTE_HMAC_SIZE));

          const quote: QuoteUpdate = { seq, tickerId, yesPrice, hmac };
          this.quoteCallbacks.forEach((cb) => cb(quote));
        } else if (
          value[0] === DATAGRAM_RESOLVED &&
          value.length >= RESOLVED_DATAGRAM_SIZE
        ) {
          const tickerId = dv.getUint16(1, true);
          const outcome = dv.getUint8(3);
          const event: ResolutionEvent = { tickerId, outcome };
          this.resolutionCallbacks.forEach((cb) => cb(event));
        }
      }
    } catch {
      // Connection closed
    }
  }

  private async sendRequest(payload: Uint8Array): Promise<DataView> {
    if (!this.wt) throw new Error("Not connected");

    const stream = await this.wt.createBidirectionalStream();
    const writer = stream.writable.getWriter();
    await writer.write(payload);
    await writer.close();

    const reader = stream.readable.getReader();
    const chunks: Uint8Array[] = [];
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      if (value) chunks.push(value);
    }

    const totalLen = chunks.reduce((s, c) => s + c.length, 0);
    const combined = new Uint8Array(totalLen);
    let off = 0;
    for (const c of chunks) {
      combined.set(c, off);
      off += c.length;
    }

    return new DataView(combined.buffer);
  }

  private checkStatus(dv: DataView): void {
    const status = dv.getUint8(0);
    if (status !== STATUS_OK) {
      throw new Error(statusToError(status));
    }
  }

  async register(
    username: string,
    password: string,
  ): Promise<{ balance: bigint }> {
    const payload = concat(
      encodeU8(REQ_REGISTER),
      encodeLenPrefixedString(username),
      encodeLenPrefixedString(password),
    );
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);
    const [balance] = readU64(resp, 1);
    return { balance };
  }

  async login(
    username: string,
    password: string,
  ): Promise<{ balance: bigint }> {
    const payload = concat(
      encodeU8(REQ_LOGIN),
      encodeLenPrefixedString(username),
      encodeLenPrefixedString(password),
    );
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);
    const [balance] = readU64(resp, 1);
    return { balance };
  }

  async subscribe(tickerId: number): Promise<void> {
    const payload = concat(encodeU8(REQ_SUBSCRIBE), encodeU16(tickerId));
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);
  }

  async unsubscribe(tickerId: number): Promise<void> {
    const payload = concat(encodeU8(REQ_UNSUBSCRIBE), encodeU16(tickerId));
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);
  }

  async fetchTickers(): Promise<Ticker[]> {
    const payload = encodeU8(REQ_FETCH_TICKERS);
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);

    let offset = 1;
    const [count, off1] = readU16(resp, offset);
    offset = off1;

    const tickers: Ticker[] = [];
    for (let i = 0; i < count; i++) {
      const [id, off2] = readU16(resp, offset);
      offset = off2;
      const [name, off3] = readLenPrefixedString(resp, offset);
      offset = off3;
      const [description, off4] = readU16LenPrefixedString(resp, offset);
      offset = off4;
      tickers.push({ id, name, description });
    }
    return tickers;
  }

  async fetchHistory(
    tickerId: number,
    minutes: number,
  ): Promise<HistoryRecord[]> {
    const payload = concat(
      encodeU8(REQ_FETCH_HISTORY),
      encodeU16(tickerId),
      encodeU16(minutes),
    );
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);

    let offset = 1;
    const [count, off1] = readU16(resp, offset);
    offset = off1;

    const records: HistoryRecord[] = [];
    for (let i = 0; i < count; i++) {
      const [tsBig, off2] = readU64(resp, offset);
      offset = off2;
      const [price, off3] = readU16(resp, offset);
      offset = off3;
      records.push({ timestamp: Number(tsBig), price });
    }
    return records;
  }

  async trade(
    token: QuoteToken,
    side: number,
    qty: number,
  ): Promise<TradeResult> {
    if (token.hmac.length !== QUOTE_HMAC_SIZE) {
      throw new Error(
        `Quote HMAC must be ${QUOTE_HMAC_SIZE} bytes, got ${token.hmac.length}`,
      );
    }
    const payload = concat(
      encodeU8(REQ_TRADE),
      encodeU16(token.seq),
      encodeU16(token.tickerId),
      encodeU16(token.yesPrice),
      token.hmac,
      encodeU8(side),
      encodeU32(qty),
    );
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);

    const [fillPrice, off1] = readU16(resp, 1);
    const [newBalance] = readU64(resp, off1);
    return { fillPrice, newBalance };
  }

  async resend(seq: number, tickerId: number): Promise<QuoteToken> {
    const payload = concat(
      encodeU8(REQ_RESEND),
      encodeU16(seq),
      encodeU16(tickerId),
    );
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);

    // Response payload: [seq:2][ticker:2][price:2][hmac:QUOTE_HMAC_SIZE]
    const [rSeq, off1] = readU16(resp, 1);
    const [rTickerId, off2] = readU16(resp, off1);
    const [yesPrice, off3] = readU16(resp, off2);
    const hmacBytes = new Uint8Array(
      resp.buffer,
      resp.byteOffset + off3,
      QUOTE_HMAC_SIZE,
    );
    const hmac = new Uint8Array(QUOTE_HMAC_SIZE);
    hmac.set(hmacBytes);
    return { seq: rSeq, tickerId: rTickerId, yesPrice, hmac };
  }

  async portfolio(): Promise<Portfolio> {
    const payload = encodeU8(REQ_PORTFOLIO);
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);

    let offset = 1;
    const [balance, off1] = readU64(resp, offset);
    offset = off1;
    const [count, off2] = readU16(resp, offset);
    offset = off2;

    const positions: Position[] = [];
    for (let i = 0; i < count; i++) {
      const [tickerId, off3] = readU16(resp, offset);
      offset = off3;
      const [yesQty, off4] = readU32(resp, offset);
      offset = off4;
      const [noQty, off5] = readU32(resp, offset);
      offset = off5;
      positions.push({ tickerId, yesQty, noQty });
    }
    return { balance, positions };
  }

  async buyFlag(): Promise<string> {
    const payload = encodeU8(REQ_BUY_FLAG);
    const resp = await this.sendRequest(payload);
    this.checkStatus(resp);

    const flagLen = resp.getUint16(1, true);
    const flagBytes = new Uint8Array(resp.buffer, 3, flagLen);
    return new TextDecoder().decode(flagBytes);
  }
}
