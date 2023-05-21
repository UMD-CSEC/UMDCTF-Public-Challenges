const lAudioContext = (typeof AudioContext !== 'undefined' ? AudioContext : (typeof webkitAudioContext !== 'undefined' ? webkitAudioContext : undefined));
let wasm;
export function __wbg_set_wasm(val) {
    wasm = val;
}


const heap = new Array(128).fill(undefined);

heap.push(undefined, null, true, false);

function getObject(idx) { return heap[idx]; }

let heap_next = heap.length;

function dropObject(idx) {
    if (idx < 132) return;
    heap[idx] = heap_next;
    heap_next = idx;
}

function takeObject(idx) {
    const ret = getObject(idx);
    dropObject(idx);
    return ret;
}

const lTextDecoder = typeof TextDecoder === 'undefined' ? (0, module.require)('util').TextDecoder : TextDecoder;

let cachedTextDecoder = new lTextDecoder('utf-8', { ignoreBOM: true, fatal: true });

cachedTextDecoder.decode();

let cachedUint8Memory0 = null;

function getUint8Memory0() {
    if (cachedUint8Memory0 === null || cachedUint8Memory0.byteLength === 0) {
        cachedUint8Memory0 = new Uint8Array(wasm.memory.buffer);
    }
    return cachedUint8Memory0;
}

function getStringFromWasm0(ptr, len) {
    return cachedTextDecoder.decode(getUint8Memory0().subarray(ptr, ptr + len));
}

function addHeapObject(obj) {
    if (heap_next === heap.length) heap.push(heap.length + 1);
    const idx = heap_next;
    heap_next = heap[idx];

    heap[idx] = obj;
    return idx;
}

let cachedInt32Memory0 = null;

function getInt32Memory0() {
    if (cachedInt32Memory0 === null || cachedInt32Memory0.byteLength === 0) {
        cachedInt32Memory0 = new Int32Array(wasm.memory.buffer);
    }
    return cachedInt32Memory0;
}

function handleError(f, args) {
    try {
        return f.apply(this, args);
    } catch (e) {
        wasm.__wbindgen_exn_store(addHeapObject(e));
    }
}
/**
*/
export class FmOsc {

    static __wrap(ptr) {
        const obj = Object.create(FmOsc.prototype);
        obj.ptr = ptr;

        return obj;
    }

    __destroy_into_raw() {
        const ptr = this.ptr;
        this.ptr = 0;

        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_fmosc_free(ptr);
    }
    /**
    */
    constructor() {
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.fmosc_new(retptr);
            var r0 = getInt32Memory0()[retptr / 4 + 0];
            var r1 = getInt32Memory0()[retptr / 4 + 1];
            var r2 = getInt32Memory0()[retptr / 4 + 2];
            if (r2) {
                throw takeObject(r1);
            }
            return FmOsc.__wrap(r0);
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
    }
    /**
    * Sets the gain for this oscillator, between 0.0 and 1.0.
    * @param {number} gain
    */
    set_gain(gain) {
        wasm.fmosc_set_gain(this.ptr, gain);
    }
    /**
    * @param {number} freq
    */
    set_primary_frequency(freq) {
        wasm.fmosc_set_primary_frequency(this.ptr, freq);
    }
    /**
    * @param {number} note
    */
    set_note(note) {
        wasm.fmosc_set_note(this.ptr, note);
    }
    /**
    * This should be between 0 and 1, though higher values are accepted.
    * @param {number} amt
    */
    set_fm_amount(amt) {
        wasm.fmosc_set_fm_amount(this.ptr, amt);
    }
    /**
    * This should be between 0 and 1, though higher values are accepted.
    * @param {number} amt
    */
    set_fm_frequency(amt) {
        wasm.fmosc_set_fm_frequency(this.ptr, amt);
    }
}

export function __wbindgen_object_drop_ref(arg0) {
    takeObject(arg0);
};

export function __wbg_connect_77f2f818a74097e1() { return handleError(function (arg0, arg1) {
    const ret = getObject(arg0).connect(getObject(arg1));
    return addHeapObject(ret);
}, arguments) };

export function __wbg_connect_20516fb9960e9ddd() { return handleError(function (arg0, arg1) {
    getObject(arg0).connect(getObject(arg1));
}, arguments) };

export function __wbg_destination_5dfc354bcf2eb941(arg0) {
    const ret = getObject(arg0).destination;
    return addHeapObject(ret);
};

export function __wbg_new_80c6bdc66ebfa0b7() { return handleError(function () {
    const ret = new lAudioContext();
    return addHeapObject(ret);
}, arguments) };

export function __wbg_close_82409a9d656a7c26() { return handleError(function (arg0) {
    const ret = getObject(arg0).close();
    return addHeapObject(ret);
}, arguments) };

export function __wbg_createGain_b1696583b33776a1() { return handleError(function (arg0) {
    const ret = getObject(arg0).createGain();
    return addHeapObject(ret);
}, arguments) };

export function __wbg_createOscillator_10f5fec75718e0e7() { return handleError(function (arg0) {
    const ret = getObject(arg0).createOscillator();
    return addHeapObject(ret);
}, arguments) };

export function __wbg_value_7294289b65409498(arg0) {
    const ret = getObject(arg0).value;
    return ret;
};

export function __wbg_setvalue_68c7d71b30468aa0(arg0, arg1) {
    getObject(arg0).value = arg1;
};

export function __wbindgen_string_new(arg0, arg1) {
    const ret = getStringFromWasm0(arg0, arg1);
    return addHeapObject(ret);
};

export function __wbg_settype_b2e33217df9f0dd2(arg0, arg1) {
    getObject(arg0).type = takeObject(arg1);
};

export function __wbg_frequency_b6ac1defd170d551(arg0) {
    const ret = getObject(arg0).frequency;
    return addHeapObject(ret);
};

export function __wbg_start_76dacec3db013a6d() { return handleError(function (arg0) {
    getObject(arg0).start();
}, arguments) };

export function __wbg_gain_37232ff852f65f78(arg0) {
    const ret = getObject(arg0).gain;
    return addHeapObject(ret);
};

export function __wbindgen_throw(arg0, arg1) {
    throw new Error(getStringFromWasm0(arg0, arg1));
};

