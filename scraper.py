import requests
from bs4 import BeautifulSoup

def get_embed_link(episode_url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36"
    }
    
    response = requests.get(episode_url, headers=headers, timeout=15)
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
