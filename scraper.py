import cloudscraper
from bs4 import BeautifulSoup

def get_embed_link(episode_url: str) -> str:
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "mobile": False})
    
    response = scraper.get(episode_url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    iframe = soup.find("div", {"id": "vast_new"}).find("iframe")
    
    return iframe["src"] if iframe else None

if __name__ == "__main__":
    url = "https://dizipal1207.com/dizi/mahsun-j/sezon-2/bolum-8"
    embed = get_embed_link(url)
    if embed:
        print("Embed Link:", embed)
    else:
        print("Embed link bulunamadı.")
