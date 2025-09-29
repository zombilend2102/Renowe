import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def get_embed_link(episode_url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Cloudflare challenge atlatmak için bekleme
        await page.goto(episode_url, timeout=60000)
        await page.wait_for_timeout(8000)  # 8 saniye bekle (doğrulama için)
        
        html = await page.content()
        await browser.close()

        soup = BeautifulSoup(html, "html.parser")
        iframe = soup.find("div", {"id": "vast_new"}).find("iframe")
        return iframe["src"] if iframe else None

if __name__ == "__main__":
    url = "https://dizipal1207.com/dizi/mahsun-j/sezon-2/bolum-8"
    embed = asyncio.run(get_embed_link(url))
    print("Embed Link:", embed if embed else "Bulunamadı.")
