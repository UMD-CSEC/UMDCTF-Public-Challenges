const puppeteer = require("puppeteer");

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const frontendUrl = process.env.FRONTEND_URL || "http://localhost:5173";

const timeout = 8000;

async function visit(postId) {
  const USERNAME = "admin";
  const PASSWORD = "1ca937afd336064ffc5b6106d3a6d49a";
  const TARGET_URL = `${frontendUrl}/post?postId=${postId}`;  

  const args = ["--js-flags=--jitless,--no-expose-wasm", "--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
  const browser = await puppeteer.launch({
    headless: "new",
    args
  });

  const context = await browser.createBrowserContext();
  const page = await context.newPage();

  await page.goto(`${frontendUrl}/login`, { waitUntil: "networkidle2" });
  await sleep(1000);

  await page.waitForSelector("#username", {
    visible: true,
    timeout: timeout
  });
  await page.type("#username", USERNAME);
  await sleep(500);

  await page.waitForSelector("#password", {
    visible: true,
    timeout: timeout
  });
  await page.type("#password", PASSWORD);
  await sleep(500);

  await page.keyboard.press("Enter");
  await page.waitForNavigation({ waitUntil: "networkidle2" });
  await sleep(3000);

  await page.goto(TARGET_URL, { waitUntil: "networkidle2" });
  await sleep(1000);

  await page.waitForSelector("#dislike-button", {
    visible: true,
    timeout: timeout
  });
  await page.click("#dislike-button");
  await sleep(2000);

  await browser.close();
};

if (require.main === module) {
	visit(process.argv[2])
}
