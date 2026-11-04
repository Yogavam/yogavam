#!/usr/bin/env python3
"""Иконки и og.jpg в фирменных цветах. Нужен playwright: pip install playwright && playwright install chromium"""
import asyncio, os, tempfile
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = "file:///" + os.path.join(ROOT, "assets", "fonts", "geologica-cyrillic.woff2").replace("\\", "/")
FONT_L = "file:///" + os.path.join(ROOT, "assets", "fonts", "geologica-latin.woff2").replace("\\", "/")

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="18" fill="#0a4442"/>'
       '<path d="M11 41c8-23 16 14 24-7s11-13 18-7" fill="none" stroke="#d6e7e2" stroke-width="4.5" stroke-linecap="round"/>'
       '<circle cx="35" cy="34" r="3.6" fill="#d6e7e2"/></svg>')
open(os.path.join(ROOT, "favicon.svg"), "w").write(SVG)

OG = f"""<html><head><style>
@font-face{{font-family:G;font-weight:100 900;src:url('{FONT}');unicode-range:U+0400-04FF}}
@font-face{{font-family:G;font-weight:100 900;src:url('{FONT_L}');unicode-range:U+0000-00FF,U+2000-206F}}
body{{margin:0;width:1200px;height:630px;background:#f1f4f2;font-family:G,sans-serif;color:#14211f;position:relative;overflow:hidden}}
.in{{position:absolute;left:84px;top:0;bottom:0;right:84px;display:flex;flex-direction:column;justify-content:center}}
.b{{display:flex;align-items:center;gap:20px;font-size:40px;font-weight:600;letter-spacing:-1px}}
.b svg{{width:68px;height:68px}}
h1{{margin:44px 0 0;font-weight:300;font-size:84px;line-height:1.04;letter-spacing:-3px}}
p{{margin:30px 0 0;font-size:32px;font-weight:300;color:#536561}}
.u{{position:absolute;right:84px;bottom:56px;font-size:26px;color:#536561}}
svg.t{{position:absolute;inset:0}}
</style></head><body>
<svg class="t" viewBox="0 0 1200 630"><path d="M-30 560C190 330 340 700 560 470S860 190 1040 400s150 130 200-40" fill="none" stroke="#0d5956" stroke-opacity=".35" stroke-width="2" stroke-linecap="round"/></svg>
<div class="in"><div class="b">{SVG.replace('<svg ', '<svg ')}Yogavam</div>
<h1>Йогатерапия и<br>метод Фельденкрайза</h1><p>Наталья Умнова. Онлайн и в Батуми</p></div><div class="u">yogavam.com</div></body></html>"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        tmp = os.path.join(ROOT, "tools", "_og.html")
        open(tmp, "w", encoding="utf-8").write(OG)
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.goto("file:///" + tmp.replace("\\", "/"))
        await pg.evaluate("document.fonts.ready")
        await pg.wait_for_timeout(400)
        os.makedirs(os.path.join(ROOT, "assets", "img"), exist_ok=True)
        await pg.screenshot(path=os.path.join(ROOT, "assets", "img", "og.jpg"), type="jpeg", quality=88)
        os.remove(tmp)
        for name, size in [("apple-touch-icon.png", 180), ("favicon-48.png", 48), ("icon-192.png", 192), ("icon-512.png", 512)]:
            pg2 = await b.new_page(viewport={"width": size, "height": size})
            await pg2.set_content(f'<html><body style="margin:0">{SVG.replace("<svg ", f"<svg width={size} height={size} ")}</body></html>')
            await pg2.screenshot(path=os.path.join(ROOT, name), omit_background=True)
        await b.close()

asyncio.run(main())
