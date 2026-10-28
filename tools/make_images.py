import asyncio, os, sys
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(ROOT)  # корень репозитория
svg = open(os.path.join(S, "favicon.svg")).read()
OG = """<html><body style="margin:0;width:1200px;height:630px;background:#2f5d50;color:#faf7f2;font-family:Georgia,'DejaVu Serif',serif;display:flex;flex-direction:column;justify-content:center;padding:0 90px;box-sizing:border-box">
<div style="display:flex;align-items:center;gap:22px;margin-bottom:46px"><div style="width:84px;height:84px">%s</div><div style="font-size:44px;letter-spacing:1px">Yogavam</div></div>
<div style="font-size:66px;font-weight:bold;line-height:1.12">Йогатерапия и метод<br>Фельденкрайза</div>
<div style="font-size:34px;margin-top:30px;color:#e8d6c6;font-family:'DejaVu Sans',sans-serif">Наталья Умнова · онлайн и в Батуми</div>
<div style="position:absolute;right:90px;bottom:60px;font-size:28px;font-family:'DejaVu Sans',sans-serif;opacity:.8">yogavam.com</div>
</body></html>""" % svg.replace('<svg ', '<svg width="84" height="84" ')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":1200,"height":630})
        await pg.set_content(OG); os.makedirs(os.path.join(S,"assets/img"), exist_ok=True)
        await pg.screenshot(path=os.path.join(S,"assets/img/og.jpg"), type="jpeg", quality=88)
        for name, size in [("apple-touch-icon.png",180),("favicon-48.png",48),("icon-192.png",192),("icon-512.png",512)]:
            pg2 = await b.new_page(viewport={"width":size,"height":size})
            await pg2.set_content(f'<html><body style="margin:0">{svg.replace("<svg ", f"<svg width={size} height={size} ")}</body></html>')
            await pg2.screenshot(path=os.path.join(S,name), omit_background=True)
        await b.close()
asyncio.run(main())
