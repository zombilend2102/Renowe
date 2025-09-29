import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def get_embed_link(episode_url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Sayfaya git
        await page.goto(episode_url, timeout=60000)

        # Cloudflare doğrulama + iframe yüklenmesi için bekle
        await page.wait_for_selector("div#vast_new iframe", timeout=20000)

        # Kaynağı al
        html = await page.content()
        await browser.close()

        # HTML parse et
        soup = BeautifulSoup(html, "html.parser")
        iframe = soup.select_one("div#vast_new iframe")
        return iframe["src"] if iframe else None

if __name__ == "__main__":
    url = "https://dizipal1207.com/dizi/mahsun-j/sezon-2/bolum-8"
    embed = asyncio.run(get_embed_link(url))
    print("Embed Link:", embed if embed else "Bulunamadı.")
