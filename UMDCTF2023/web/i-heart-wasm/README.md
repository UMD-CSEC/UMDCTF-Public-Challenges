# i-heart-wasm

I've been messing around with WASM lately. Turns out, there's a ton of cool things you can do with it! Time to rewrite everything in Rust.

## Writeup

This challenge makes use of the lovely Rust + WebAssembly documentation available on the web. The challenge itself initially
appears to have something to do with oscillators or audio but it is simply just [a wasm-bindgen demo](https://rustwasm.github.io/wasm-bindgen/examples/web-audio.html) and acts as a red herring.

This [same documentation](https://rustwasm.github.io/docs/book/reference/js-ffi.html#custom-sections) tells us that we are able to embed custom sections within a wasm binary and access them from JavaScript.

To reveal the flag:

```js
WebAssembly.compileStreaming(fetch("./pkg/wasm_test_bg.wasm"))
    .then(mod => {
        let flag = "";
        for(let i = 42; i >= 0; i--) {
            const sections = WebAssembly.Module.customSections(mod, i.toString());

            const decoder = new TextDecoder();
            const text = decoder.decode(sections[0]);

            flag += text;
        }
        console.log(flag);
    });
```

## Files for CTFd

User should be able to access from the web

## Flag

`UMDCTF{4ll_y0ur_53c710n5_4r3_b3l0n6_70_u5}`
