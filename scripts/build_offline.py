#!/usr/bin/env python3
"""Build dist/kiosk-offline.html: the kiosk map as one file that runs with no internet.

The libraries (three.js r128, OrbitControls, qrcode-generator, jsPDF) come from node_modules
(npm install), the fonts from offline/fonts (Latin and Arabic subsets; Chinese uses the PC's
own font, e.g. Microsoft YaHei). QR codes still point phones to the website in CFG.publicUrl.

    python3 scripts/build_offline.py
"""
import base64, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
html = (ROOT / "expo-navigator.html").read_text(encoding="utf-8")

def lib(path):
    code = (ROOT / "node_modules" / path).read_text(encoding="utf-8")
    return "<script>\n" + code.replace("</script", "<\\/script") + "\n</script>"

SCRIPTS = {
    "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js": "three/build/three.min.js",
    "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js": "three/examples/js/controls/OrbitControls.js",
    "https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js": "qrcode-generator/qrcode.js",
}
for url, path in SCRIPTS.items():
    tag = f'<script src="{url}"></script>'
    if html.count(tag) != 1:
        sys.exit(f"expected one {tag}")
    inline = lib(path)
    if "qrcode" in path:                      # jsPDF too, so the route PDF never has to download it
        inline += "\n" + lib("jspdf/dist/jspdf.umd.min.js")
    html = html.replace(tag, inline)

# fonts: drop the Google Fonts links, embed the saved Latin and Arabic files
html = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"( crossorigin)?>\s*', "", html)
link = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">', html)
if not link:
    sys.exit("Google Fonts link not found")
fdir = ROOT / "offline" / "fonts"
css = (fdir / "fonts.css").read_text(encoding="utf-8")
css = re.sub(r"url\(([^)]+\.woff2)\)",
             lambda m: "url(data:font/woff2;base64," + base64.b64encode((fdir / m.group(1)).read_bytes()).decode() + ")", css)
html = html[:link.start()] + "<style>\n" + css + "</style>" + html[link.end():]

left = re.findall(r'<(?:script|link)[^>]*(?:src|href)="(https://[^"]+)"', html)
if left:
    sys.exit("still loads from the internet: " + ", ".join(left))

out = ROOT / "dist" / "kiosk-offline.html"
out.parent.mkdir(exist_ok=True)
out.write_text('<!DOCTYPE html>\n<html lang="en">\n<head>\n' + html + "\n</html>\n", encoding="utf-8")
print(f"{out.relative_to(ROOT)}: {out.stat().st_size / 1e6:.1f} MB")
