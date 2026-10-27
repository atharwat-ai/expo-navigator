import asyncio, cv2, base64, numpy as np, io
from PIL import Image
from playwright.async_api import async_playwright
T3=open("node_modules/three/build/three.min.js").read(); OC=open("node_modules/three/examples/js/controls/OrbitControls.js").read(); QRJS=open("node_modules/qrcode-generator/qrcode.js").read()
HTML=open("expo-navigator.html",encoding="utf-8").read()
import glob, os
CHROMIUM=os.environ.get("CHROMIUM") or (sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome")) or [None])[-1]
os.makedirs("r",exist_ok=True)
HOST="https://map.cairoict-expo.test/"
STUB=r"""(function(){const handler={get(t,p){if(p===Symbol.toPrimitive)return ()=>0;if(p==='then')return undefined;if(p in t)return t[p];t[p]=mk();return t[p];},apply(){return mk();},construct(){return mk();},set(t,p,v){t[p]=v;return true;}};function mk(){const f=function(){};return new Proxy(f,handler);} window.THREE=window.THREE||mk();})();"""
import re
PUBLIC=(re.search(r'publicUrl:\s*"([^"]*)"',HTML) or [None,""])[1]  # QR codes point here once the map has a public address
async def route(r):
    u=r.request.url
    if u.startswith(HOST) or (PUBLIC and u.startswith(PUBLIC)): await r.fulfill(body=HTML,content_type="text/html; charset=utf-8")
    elif "three.min.js" in u: await r.fulfill(body=STUB,content_type="application/javascript")
    elif "OrbitControls" in u: await r.fulfill(body="",content_type="application/javascript")
    elif "qrcode" in u: await r.fulfill(body=QRJS,content_type="application/javascript")
    else: await r.abort()
def decode_svg_png(png):
    im=cv2.imdecode(np.frombuffer(png,np.uint8),cv2.IMREAD_COLOR); im=cv2.resize(im,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST)
    im=cv2.copyMakeBorder(im,40,40,40,40,cv2.BORDER_CONSTANT,value=(255,255,255))
    v,_,_=cv2.QRCodeDetector().detectAndDecode(im); return v
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=CHROMIUM)
        kiosk=await b.new_page(viewport={"width":1920,"height":1080}); await kiosk.route("**/*",route)
        await kiosk.goto(HOST+"#kiosk-h1c"); await kiosk.wait_for_timeout(2500)
        cases=[]
        async def grab(sel,label,setup):
            await kiosk.evaluate(setup); await kiosk.wait_for_timeout(900)
            png=await kiosk.locator(sel).first.screenshot(); url=decode_svg_png(png)
            if not url: open("r/fail.png","wb").write(png); print("FAIL html:", (await kiosk.locator(sel).first.inner_html())[:200])
            cases.append((label,url)); print(f"{label:28s} -> {url}")
        await grab("#attractQR .c","idle card","sleep()")
        await grab("#mapQR .mq-code","route to Huawei (zh)","wake();setLang('zh');openDetail('H2-36',{route:true})")
        await grab("#mapQR .mq-code","3-stop plan (ar)","goHomeAll();setLang('ar');PLAN=['H2-07','H1-44','F-CRA'];openPlan()")
        await grab("#lightbox .code.big","my sessions (en)","goHomeAll();setLang('en');document.getElementById('lightbox').hidden=true;REM.clear();toggleRem('S05');toggleRem('S12');openRemQR()")
        # now open each link as a visitor's phone
        for label,url in [c for c in cases if c[1]]:
            ph=await b.new_page(viewport={"width":390,"height":844},is_mobile=True,has_touch=True); await ph.route("**/*",route)
            await ph.goto(url); await ph.wait_for_timeout(2500)
            st=await ph.evaluate("({view:VIEW,lang:LANG,kiosk:KIOSK,phone:ON_PHONE(),sel:SELECTED&&SELECTED.id,route:ROUTE_FOR,plan:PLAN_ORDER.slice(),rem:[...REM],attract:document.getElementById('attract').classList.contains('on'),title:(document.querySelector('.view.on h2')||{}).textContent})")
            print(f"  phone opens {label}: {st}")
            await ph.wait_for_timeout(100); await ph.close()
        await b.close()
asyncio.run(main())
