import init, { FmOsc } from "./pkg/wasm_test.js";

const runWasm = async () => {
  // Instantiate our wasm module
  const rust_module = await init("./pkg/wasm_test_bg.wasm");

  let fm = null;

    const play_button = document.getElementById("play");
    play_button.addEventListener("click", event => {
      if (fm === null) {
        fm = new FmOsc();
        console.log(fm);
        fm.set_note(50);
        fm.set_fm_frequency(0);
        fm.set_fm_amount(0);
        fm.set_gain(0.8);
      } else {
        fm.free();
        fm = null;
      }
    });

    const primary_slider = document.getElementById("primary_input");
    primary_slider.addEventListener("input", event => {
      if (fm) {
        fm.set_note(parseInt(event.target.value));
      }
    });

    const fm_freq = document.getElementById("fm_freq");
    fm_freq.addEventListener("input", event => {
      if (fm) {
        fm.set_fm_frequency(parseFloat(event.target.value));
      }
    });

    const fm_amount = document.getElementById("fm_amount");
    fm_amount.addEventListener("input", event => {
      if (fm) {
        fm.set_fm_amount(parseFloat(event.target.value));
      }
    });
};
runWasm();