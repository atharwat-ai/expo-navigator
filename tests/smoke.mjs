// Smoke test: boots the real page (real three.js from node_modules, no network),
// fails on any page error, and saves screenshots to r/ for a quick visual check.
//   node tests/smoke.mjs
import { createRequire } from "node:module";
const { chromium } = createRequire(import.meta.url)("playwright"); // global install in the dev container, or npm i -D playwright
import { readFileSync, mkdirSync } from "node:fs";

const HOST = "https://map.cairoict-expo.test/";
const FILES = {
  "three.min.js": "node_modules/three/build/three.min.js",
  "OrbitControls.js": "node_modules/three/examples/js/controls/OrbitControls.js",
  "qrcode": "node_modules/qrcode-generator/qrcode.js",
};
const HTML = readFileSync("expo-navigator.html", "utf8");
mkdirSync("r", { recursive: true });

async function route(r) {
  const u = r.request().url();
  if (u.startsWith(HOST)) return r.fulfill({ body: HTML, contentType: "text/html; charset=utf-8" });
  for (const [k, f] of Object.entries(FILES))
    if (u.includes(k)) return r.fulfill({ body: readFileSync(f, "utf8"), contentType: "application/javascript" });
  return r.abort(); // fonts etc.: the page must cope offline
}

const CASES = [
  { name: "kiosk-landscape", hash: "#kiosk-h1c", viewport: { width: 1920, height: 1080 } },
  { name: "kiosk-portrait", hash: "#kiosk-main.look-day", viewport: { width: 1080, height: 1920 } },
  { name: "phone-route", hash: "#go_H2-36_main.phone", viewport: { width: 390, height: 844 }, mobile: true },
];

const browser = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"] });
let failed = 0;
for (const c of CASES) {
  const page = await browser.newPage({ viewport: c.viewport, isMobile: !!c.mobile, hasTouch: !!c.mobile });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => m.type() === "error" && !/net::ERR_FAILED|Failed to load resource/.test(m.text()) && errors.push(m.text()));
  await page.route("**/*", route);
  await page.goto(HOST + c.hash);
  await page.waitForTimeout(4000);
  const state = await page.evaluate(() => ({ view: VIEW, kiosk: KIOSK, sel: SELECTED && SELECTED.id, loading: !!document.getElementById("loading") }));
  await page.screenshot({ path: `r/${c.name}.png` });
  const ok = errors.length === 0 && !state.loading;
  if (!ok) failed++;
  console.log(`${ok ? "PASS" : "FAIL"} ${c.name}`, JSON.stringify(state), errors.length ? errors : "");
  await page.close();
}
await browser.close();
process.exit(failed ? 1 : 0);
