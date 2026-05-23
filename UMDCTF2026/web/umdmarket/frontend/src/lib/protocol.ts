// Wire protocol constants matching the Go server
export const REQ_REGISTER = 0x20;
export const REQ_LOGIN = 0x21;
export const REQ_SUBSCRIBE = 0x22;
export const REQ_UNSUBSCRIBE = 0x23;
export const REQ_FETCH_TICKERS = 0x24;
export const REQ_FETCH_HISTORY = 0x25;
export const REQ_RESEND = 0x26;
export const REQ_TRADE = 0x30;
export const REQ_PORTFOLIO = 0x40;
export const REQ_BUY_FLAG = 0x50;

export const STATUS_OK = 0x00;
export const STATUS_ERR_INVALID_REQUEST = 0x01;
export const STATUS_ERR_NOT_AUTHENTICATED = 0x02;
export const STATUS_ERR_COOLDOWN = 0x03;
export const STATUS_ERR_STALE = 0x04;
export const STATUS_ERR_INSUFFICIENT_FUNDS = 0x05;
export const STATUS_ERR_INSUFFICIENT_POS = 0x06;
export const STATUS_ERR_INVALID_QTY = 0x07;
export const STATUS_ERR_MARKET_WARMUP = 0x08;
export const STATUS_ERR_TICKER_NOT_FOUND = 0x09;
export const STATUS_ERR_INVALID_CREDENTIALS = 0x0a;
export const STATUS_ERR_USERNAME_TAKEN = 0x0b;
export const STATUS_ERR_WEAK_PASSWORD = 0x0c;
export const STATUS_ERR_ALREADY_LOGGED_IN = 0x0d;
export const STATUS_ERR_INVALID_QUOTE = 0x0e;
export const STATUS_ERR_RESEND_UNAVAILABLE = 0x0f;
export const STATUS_ERR_TICKER_RESOLVED = 0x10;

export const SIDE_BUY_YES = 0x00;
export const SIDE_BUY_NO = 0x01;
export const SIDE_SELL_YES = 0x02;
export const SIDE_SELL_NO = 0x03;

export const DATAGRAM_QUOTE = 0x01;
export const DATAGRAM_RESOLVED = 0x02;

// Signed-quote wire format: [tag:1][seq:2][ticker:2][price:2][hmac:QUOTE_HMAC_SIZE].
export const QUOTE_HMAC_SIZE = 8;
export const QUOTE_DATAGRAM_SIZE = 7 + QUOTE_HMAC_SIZE;

// RESOLVED datagram wire format: [tag:1][ticker:2][outcome:1]. outcome 0=YES, 1=NO.
export const RESOLVED_DATAGRAM_SIZE = 4;
export const OUTCOME_YES = 0;
export const OUTCOME_NO = 1;

export const PRICE_UNIT = 10000;

// Encode helpers - all little-endian
export function encodeU8(v: number): Uint8Array {
  return new Uint8Array([v & 0xff]);
}

export function encodeU16(v: number): Uint8Array {
  const buf = new Uint8Array(2);
  new DataView(buf.buffer).setUint16(0, v, true);
  return buf;
}

export function encodeU32(v: number): Uint8Array {
  const buf = new Uint8Array(4);
  new DataView(buf.buffer).setUint32(0, v, true);
  return buf;
}

export function encodeLenPrefixedString(s: string): Uint8Array {
  const bytes = new TextEncoder().encode(s);
  const buf = new Uint8Array(1 + bytes.length);
  buf[0] = bytes.length;
  buf.set(bytes, 1);
  return buf;
}

export function concat(...arrays: Uint8Array[]): Uint8Array {
  const total = arrays.reduce((sum, a) => sum + a.length, 0);
  const result = new Uint8Array(total);
  let offset = 0;
  for (const a of arrays) {
    result.set(a, offset);
    offset += a.length;
  }
  return result;
}

// Decode helpers
export function readU8(data: DataView, offset: number): [number, number] {
  return [data.getUint8(offset), offset + 1];
}

export function readU16(data: DataView, offset: number): [number, number] {
  return [data.getUint16(offset, true), offset + 2];
}

export function readU32(data: DataView, offset: number): [number, number] {
  return [data.getUint32(offset, true), offset + 4];
}

export function readU64(data: DataView, offset: number): [bigint, number] {
  return [data.getBigUint64(offset, true), offset + 8];
}

export function readLenPrefixedString(
  data: DataView,
  offset: number,
): [string, number] {
  const len = data.getUint8(offset);
  offset += 1;
  const bytes = new Uint8Array(data.buffer, data.byteOffset + offset, len);
  return [new TextDecoder().decode(bytes), offset + len];
}

export function readU16LenPrefixedString(
  data: DataView,
  offset: number,
): [string, number] {
  const len = data.getUint16(offset, true);
  offset += 2;
  const bytes = new Uint8Array(data.buffer, data.byteOffset + offset, len);
  return [new TextDecoder().decode(bytes), offset + len];
}

// Price conversion: price units (0-10000) to percentage string
export function priceToPercent(price: number): number {
  return (price / PRICE_UNIT) * 100;
}

// Balance conversion: units to dollar string
export function balanceToDollars(units: number | bigint): string {
  const n = typeof units === "bigint" ? Number(units) : units;
  return (n / PRICE_UNIT).toFixed(2);
}

// Status code to human-readable error
export function statusToError(status: number): string {
  const map: Record<number, string> = {
    [STATUS_ERR_INVALID_REQUEST]: "Invalid request: the server couldn't understand that",
    [STATUS_ERR_NOT_AUTHENTICATED]: "You need to sign in first",
    [STATUS_ERR_COOLDOWN]: "Trade cooldown: wait 5 seconds between trades",
    [STATUS_ERR_STALE]: "Quote expired: prices update every 100ms, try again",
    [STATUS_ERR_INSUFFICIENT_FUNDS]: "Not enough balance to cover this trade",
    [STATUS_ERR_INSUFFICIENT_POS]: "You don't hold enough contracts to sell that many",
    [STATUS_ERR_INVALID_QTY]: "Quantity must be at least 1",
    [STATUS_ERR_MARKET_WARMUP]: "Market is still warming up, please wait",
    [STATUS_ERR_TICKER_NOT_FOUND]: "Ticker not found: make sure you're subscribed to this market",
    [STATUS_ERR_INVALID_CREDENTIALS]: "Wrong username or password",
    [STATUS_ERR_USERNAME_TAKEN]: "That username is already taken: try another",
    [STATUS_ERR_WEAK_PASSWORD]: "Password must be 12+ characters with uppercase, lowercase, digit, and special character",
    [STATUS_ERR_ALREADY_LOGGED_IN]: "You're already logged in somewhere else",
    [STATUS_ERR_INVALID_QUOTE]: "Quote signature invalid: this quote didn't come from the server",
    [STATUS_ERR_RESEND_UNAVAILABLE]: "That seq is outside the server's resend window",
    [STATUS_ERR_TICKER_RESOLVED]: "Market closed: price is inside the resolution band",
  };
  return map[status] || `Something went wrong (error 0x${status.toString(16)})`;
}
