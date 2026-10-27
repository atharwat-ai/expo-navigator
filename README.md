# Cairo ICT Expo Navigator

3D wayfinding map for Cairo ICT 2026 (Halls 1 & 2, plus Pafix). It runs as a touch kiosk, and visitors carry it to their phone by QR.
Everything lives in **one file**, `expo-navigator.html`. It holds the three.js scene, the UI, the i18n strings (EN / AR / ZH) and the data.
Logos and stand renders are embedded as data URIs.

## Run

```bash
npm install          # three@0.128.0 + qrcode-generator@1.4.4, used by the offline tests only
npm run serve        # http://localhost:8080/expo-navigator.html  (page loads libs/fonts from CDNs)
```

URL hash tokens are joined by dots: `#kiosk-h1c`, `#look-day` (midnight | day | graphite), `#lang-ar`, `#phone`,
`#go_H2-36_main` (route to a stand from a kiosk), `#plan_H2-07_H1-44_F-CRA` (multi-stop), `#rem_S05_S12` (saved sessions).
Staff menu: press and hold the event logo for 2 s.

## Tests

```bash
npm test             # both suites below
npm run test:smoke   # real three.js render: kiosk landscape/portrait + phone route; screenshots in r/
npm run test:qr      # kiosk QR codes -> decode with OpenCV -> open each link as a phone, check the state it lands in
```

The QR test needs `pip install opencv-python-headless numpy pillow playwright`. Set `CHROMIUM=/path/to/chrome` if
Python Playwright's own browser isn't installed.

## Where things are in `expo-navigator.html`

| What | Look for |
|---|---|
| Stands, from the official plan (1:100, 28.35 pt = 1 m) | `const BOOTHS` |
| Exhibitor stand renders | `const DESIGNS` |
| Exhibitor contacts (still empty) | `const CONTACTS` |
| Conference agenda (**sample data**, `sample:true`) | `const AGENDA`, `TRACKS` |
| Kiosk positions, opening hours, public URL, app links | `const CFG` |
| Halls, categories, facilities, entrances | `HALLS`, `CATS`, `FAC`, `ENTR` |
| Routing (walk graph + Dijkstra) | `buildGrid`, `dijkstra`, `pathTo`, `directions` |
| Native-app bridge for live indoor positioning | `window.ExpoMap` (`setPosition`, `open`, `route`, `places`) |
| Boot and URL hash parsing | `boot()` at the end of the file |

## Source assets (not in this repo)

The original uploads live in Google Drive under `expo-navigator-src`. `lg/` holds about 100 logo PNGs, already embedded in the
HTML. `bd/` holds the exhibitor PDFs (`fedis.pdf`, `fortinet.pdf`). `libs/` holds copies of three.js and qrcode-generator,
which are now replaced by npm.

## Open items noticed in config

- `CFG.publicUrl` points at the claude.ai artifact https://claude.ai/artifact/VpUe9qimNPX1Nnv3pmVDbg. Set it to the real hosted address (e.g. `https://map.cairoict.com/`)
  or leave it blank so the page uses its own address.
- `CFG.previewUrl` is a temporary placeholder (`example.com`).
- `CFG.apps` / `CFG.appLink` are empty until the iOS/Android apps ship.
- `AGENDA` is sample data and `CONTACTS` is empty.
