/* tslint:disable */
/* eslint-disable */
/**
*/
export class FmOsc {
  free(): void;
/**
*/
  constructor();
/**
* Sets the gain for this oscillator, between 0.0 and 1.0.
* @param {number} gain
*/
  set_gain(gain: number): void;
/**
* @param {number} freq
*/
  set_primary_frequency(freq: number): void;
/**
* @param {number} note
*/
  set_note(note: number): void;
/**
* This should be between 0 and 1, though higher values are accepted.
* @param {number} amt
*/
  set_fm_amount(amt: number): void;
/**
* This should be between 0 and 1, though higher values are accepted.
* @param {number} amt
*/
  set_fm_frequency(amt: number): void;
}

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
  readonly memory: WebAssembly.Memory;
  readonly __wbg_fmosc_free: (a: number) => void;
  readonly fmosc_new: (a: number) => void;
  readonly fmosc_set_gain: (a: number, b: number) => void;
  readonly fmosc_set_primary_frequency: (a: number, b: number) => void;
  readonly fmosc_set_note: (a: number, b: number) => void;
  readonly fmosc_set_fm_amount: (a: number, b: number) => void;
  readonly fmosc_set_fm_frequency: (a: number, b: number) => void;
  readonly __wbindgen_add_to_stack_pointer: (a: number) => number;
  readonly __wbindgen_exn_store: (a: number) => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;
/**
* Instantiates the given `module`, which can either be bytes or
* a precompiled `WebAssembly.Module`.
*
* @param {SyncInitInput} module
*
* @returns {InitOutput}
*/
export function initSync(module: SyncInitInput): InitOutput;

/**
* If `module_or_path` is {RequestInfo} or {URL}, makes a request and
* for everything else, calls `WebAssembly.instantiate` directly.
*
* @param {InitInput | Promise<InitInput>} module_or_path
*
* @returns {Promise<InitOutput>}
*/
export default function init (module_or_path?: InitInput | Promise<InitInput>): Promise<InitOutput>;
