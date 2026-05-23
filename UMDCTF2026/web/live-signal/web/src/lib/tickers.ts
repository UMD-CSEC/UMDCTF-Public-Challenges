export const TICKER_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-";

export function formatTicker(t: string) {
  return t.toUpperCase();
}
