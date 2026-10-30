# Cairo ICT Expo Navigator

3D wayfinding map for EIEC, New Cairo: Cairo ICT (Halls 1 & 2), Pafix (Hall 1), AIDC² Expo (Hall 3) and Connecta (Hall 4). It runs as a touch kiosk, and visitors carry it to their phone by QR.
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
| Hall 4 · Connecta stands, zones, Cairo Khayal walls (from the Connecta 26 plan) | `CONNECTA_BOOTHS`, `CONNECTA_FAC`, `KHAYAL_WALLS` |
| Venue footprint: walkable areas and walls with door gaps | `WALKS`, `WALLS` |
| Exhibitor stand renders | `const DESIGNS` |
| Exhibitor contacts (still empty) | `const CONTACTS` |
| Conference agenda (**sample data**, `sample:true`) | `const AGENDA`, `TRACKS` |
| Kiosk positions, opening hours, public URL, app links | `const CFG` |
| Halls, categories, facilities, entrances | `HALLS`, `CATS`, `FAC`, `ENTR` |
| Routing (walk graph + Dijkstra; walls block everywhere except doors) | `buildGrid`, `dijkstra`, `pathTo`, `directions` |
| Visitor-chosen starting point (picker, tap on map, drag the marker) | `setOrigin`, `openStartPicker`, `startDragYou` |
| Round tables (real) appended to the agenda | `AGENDA.sessions.push` (`RT1`–`RT6`) |
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
- `AGENDA` conference sessions are sample data (the round tables are real); `CONTACTS` is empty.
- Hall 3 (AIDC²) has no floor plan yet: the hall is walkable but empty. The pavement in front of all four halls is walkable.
- Only the two central doors of each hall are open (`DOORS_Y`, `DOORS_W`, Hall 2 west, Hall 1 east, Hall 4 west); no hall has front doors onto the pavement. Halls 3 & 4 are placed from the EIEC site map,
  so their position relative to Halls 1 & 2 is approximate; Hall 4's interior comes from the Connecta plan.
- Round table RT6 (Day 4) only says "Hall 3", so it routes to Hall 3's east entrance. RT3 (Day 2) has no location
  and is shown in the Round Tables & VIP Lounge (Hall 2). RT4 and RT5 overlap (both Mon 9 Nov 11:00–14:00, Hall 2).
- The conference-room render can be added as the rooms' roof texture and hero image once supplied as a file.
