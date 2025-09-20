import requests
from bs4 import BeautifulSoup
import json
import re
import os
import sys

# Bu script, dizi verilerini çeker ve gom.html üretir.
# Elle çalıştır: python gom.py
# Otomatik için GitHub Actions ile entegre.

class DiziGom:
    def __init__(self):
        self.main_url = "https://dizigom1.de"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

    def get_main_page(self, page=1, category="Dram"):
        search_url = "/wp-admin/admin-ajax.php"
        url = f"{self.main_url}/tur/{category.lower()}/#p={page}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            if page > 1:
                tax_input = soup.select_one("form.dizigom_advenced_search input[name^='tax_query']")
                tax = tax_input["name"] if tax_input else None
                value = tax_input["value"] if tax_input else None
                data = {
                    "action": "dizigom_advenced_search",
                    "formData": f"{tax}={value}" if tax and value else "",
                    "paged": str(page),
                    "_wpnonce": "18a90a7287"
                }
                headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": url
                }
                response = self.session.post(f"{self.main_url}{search_url}", data=data, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

            items = []
            for element in soup.select("div.episode-box"):
                title = element.select_one("div.serie-name a").text if element.select_one("div.serie-name a") else None
                href = element.select_one("a")["href"] if element.select_one("a") else None
                poster = element.select_one("img")["src"] if element.select_one("img") else None
                score = element.select_one("div.episode-date").text.replace("IMDb:", "").strip() if element.select_one("div.episode-date") else None

                if title and href:
                    item = {
                        "title": title,
                        "url": href,
                        "poster": poster,
                        "score": score,
                        "type": "TvSeries"
                    }
                    items.append(item)

            return items
        except Exception as e:
            print(f"Ana sayfa hatası ({category}, sayfa {page}): {e}")
            return []

    def load(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.select_one("div.serieTitle h1").text.strip() if soup.select_one("div.serieTitle h1") else None
            if not title:
                return None

            poster_style = soup.select_one("div.seriePoster")["style"] if soup.select_one("div.seriePoster") else ""
            poster_match = re.search(r"background-image:url\((.*?)\)", poster_style)
            poster = poster_match.group(1) if poster_match else None

            episodes = []
            for item in soup.select("div.bolumust"):
                ep_href = item.select_one("a")["href"] if item.select_one("a") else ""
                ep_name = item.select_one("div.bolum-ismi").text if item.select_one("div.bolum-ismi") else None
                baslik = item.select_one("div.baslik").text if item.select_one("div.baslik") else ""
                ep_info = baslik.split()
                ep_season = int(ep_info[0].replace(".", "")) if ep_info else None
                ep_episode = int(ep_info[2].replace(".", "")) if len(ep_info) > 2 else None
                episode = {
                    "url": ep_href,
                    "name": ep_name,
                    "season": ep_season,
                    "episode": ep_episode
                }
                episodes.append(episode)

            load_data = {
                "title": title,
                "url": url,
                "poster": poster,
                "episodes": episodes,
                "type": "TvSeries" if episodes else "Movie"
            }

            return load_data
        except Exception as e:
            print(f"Yükleme hatası ({url}): {e}")
            return None

    def load_links(self, data):
        try:
            response = self.session.get(data, headers={"Referer": self.main_url + "/"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Script'leri tara
            scripts = soup.select("script")
            script_data = None
            for script in scripts:
                if script.string and "application/ld+json" in str(script):
                    try:
                        content_json = json.loads(script.string.strip())
                        if "contentUrl" in content_json:
                            script_data = content_json
                            break
                    except json.JSONDecodeError as e:
                        print(f"JSON parse hatası ({data}): {e}")
                        continue

            if not script_data:
                print(f"JSON script bulunamadı: {data}")
                return None

            content_url = script_data.get("contentUrl", "")
            if not content_url:
                print(f"contentUrl bulunamadı: {data}")
                return None

            # Eğer contentUrl doğrudan embed linkiyse
            if "embed" in content_url:
                return content_url
            else:
                print(f"Embed linki bulunamadı: {content_url}")
                return None
        except Exception as e:
            print(f"load_links hatası ({data}): {e}")
            return None

def generate_html(diziler):
    html_template = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <title>TITAN TV YERLİ VOD</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css?family=PT+Sans:700i" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://kit.fontawesome.com/bbe955c5ed.js" crossorigin="anonymous"></script>
    <style>
        *:not(input):not(textarea) {
            -moz-user-select: -moz-none;
            -khtml-user-select: none;
            -webkit-user-select: none;
            -o-user-select: none;
            -o-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
        body {
            margin: 0;
            padding: 0;
            background: #00040d;
            font-family: sans-serif;
            font-size: 15px;
            -webkit-tap-highlight-color: transparent;
            font-style: italic;
            line-height: 20px;
            -webkit-text-size-adjust: 100%;
            text-decoration: none;
            -webkit-text-decoration: none;
            overflow-x: hidden;
        }
        .filmpaneldis {
            background: #15161a;
            width: 100%;
            margin: 20px auto;
            overflow: hidden;
            padding: 10px 5px;
            box-sizing: border-box;
        }
        .baslik {
            width: 96%;
            color: #fff;
            padding: 15px 10px;
            box-sizing: border-box;
        }
        .filmpanel {
            width: 12%;
            height: 200px;
            background: #15161a;
            float: left;
            margin: 1.14%;
            color: #fff;
            border-radius: 15px;
            box-sizing: border-box;
            box-shadow: 1px 5px 10px rgba(0,0,0,0.1);
            border: 1px solid #323442;
            padding: 0px;
            overflow: hidden;
            transition: border 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }
        .filmisimpanel {
            width: 100%;
            height: 200px;
            position: relative;
            margin-top: -200px;
            background: linear-gradient(to bottom, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 1) 100%);
        }
        .filmpanel:hover {
            color: #fff;
            border: 3px solid #572aa7;
            box-shadow: 0 0 10px rgba(87, 42, 167, 0.5);
        }
        .filmresim {
            width: 100%;
            height: 100%;
            margin-bottom: 0px;
            overflow: hidden;
            position: relative;
        }
        .filmresim img {
            width: 100%;
            height: 100%;
            transition: transform 0.4s ease;
        }
        .filmpanel:hover .filmresim img {
            transform: scale(1.1);
        }
        .filmisim {
            width: 100%;
            font-size: 14px;
            text-decoration: none;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding: 0px 5px;
            box-sizing: border-box;
            color: #fff;
            position: absolute;
            bottom: 25px;
        }
        .aramapanel {
            width: 100%;
            height: 60px;
            background: #15161a;
            border-bottom: 1px solid #323442;
            margin: 0px auto;
            padding: 10px;
            box-sizing: border-box;
            overflow: hidden;
            z-index: 11111;
        }
        .aramapanelsag {
            width: auto;
            height: 40px;
            box-sizing: border-box;
            overflow: hidden;
            float: right;
        }
        .aramapanelsol {
            width: 50%;
            height: 40px;
            box-sizing: border-box;
            overflow: hidden;
            float: left;
        }
        .aramapanelyazi {
            height: 40px;
            width: 120px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            padding: 0px 10px;
            background: #fff;
            color: #000;
            margin: 0px 5px;
        }
        .aramapanelbuton {
            height: 40px;
            width: 40px;
            text-align: center;
            background-color: #572aa7;
            border: none;
            color: #fff;
            box-sizing: border-box;
            overflow: hidden;
            float: right;
            transition: .35s;
        }
        .aramapanelbuton:hover {
            background-color: #fff;
            color: #000;
        }
        .logo {
            width: 40px;
            height: 40px;
            float: left;
        }
        .logo img {
            width: 100%;
        }
        .logoisim {
            font-size: 15px;
            width: 70%;
            height: 40px;
            line-height: 40px;
            font-weight: 500;
            color: #fff;
        }
        .hidden {
            display: none;
        }
        .bolum-container {
            background: #15161a;
            padding: 10px;
            margin-top: 10px;
            border-radius: 5px;
        }
        .geri-btn {
            background: #572aa7;
            color: white;
            padding: 10px;
            text-align: center;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
            margin-bottom: 10px;
            display: none;
            width: 100px;
        }
        .geri-btn:hover {
            background: #6b3ec7;
            transition: background 0.3s;
        }
        .playerpanel {
            width: 100vw;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
            background: #000;
            z-index: 9999;
            display: none;
            flex-direction: column;
            overflow: hidden;
            margin: 0;
            padding: 0;
        }
        .player-geri-btn {
            background: #572aa7;
            color: white;
            padding: 10px;
            text-align: center;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
            width: 100px;
            z-index: 10000;
            position: absolute;
            top: 0;
            left: 0;
        }
        .player-geri-btn:hover {
            background: #6b3ec7;
            transition: background 0.3s;
        }
        #iframe-player {
            width: 100%;
            height: 100%;
            border: none;
            position: absolute;
            top: 0;
            left: 0;
        }
        @media(max-width:900px) {
            .filmpanel {
                width: 17%;
                height: 220px;
                margin: 1.5%;
            }
        }
        @media(max-width:550px) {
            .filmisimpanel {
                height: 190px;
                margin-top: -190px;
            }
            .filmpanel {
                width: 31.33%;
                height: 190px;
                margin: 1%;
            }
            .player-geri-btn {
                width: 80px;
                padding: 8px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="aramapanel">
        <div class="aramapanelsol">
            <div class="logo"><img src="https://i.hizliresim.com/t75soiq.png"></div>
            <div class="logoisim">TITAN TV</div>
        </div>
        <div class="aramapanelsag">
            <form action="" name="ara" method="GET" onsubmit="return searchSeries()">
                <input type="text" id="seriesSearch" placeholder="Dizi Adını Giriniz..!" class="aramapanelyazi" oninput="resetSeriesSearch()">
                <input type="submit" value="ARA" class="aramapanelbuton">
            </form>
        </div>
    </div>

    <div class="filmpaneldis">
        <div class="baslik">YERLİ DİZİLER VOD BÖLÜM</div>
        
        {dizi_panelleri}
    </div>

    <div id="bolumler" class="bolum-container hidden">
        <div id="geriBtn" class="geri-btn" onclick="geriDon()">Geri</div>
        <div id="bolumListesi" class="filmpaneldis"></div>
    </div>

    <div id="playerpanel" class="playerpanel">
        <div class="player-geri-btn" onclick="geriPlayer()">Geri</div>
        <iframe id="iframe-player" allowfullscreen></iframe>
    </div>

    <script>
        var diziler = {dizi_json};

        let currentScreen = 'anaSayfa';

        function showBolumler(diziID) {
            sessionStorage.setItem('currentDiziID', diziID);
            var listContainer = document.getElementById("bolumListesi");
            listContainer.innerHTML = "";
            
            if (diziler[diziID]) {
                diziler[diziID].bolumler.forEach(function(bolum) {
                    var item = document.createElement("div");
                    item.className = "filmpanel";
                    item.innerHTML = `
                        <div class="filmresim"><img src="${diziler[diziID].resim}"></div>
                        <div class="filmisimpanel">
                            <div class="filmisim">${bolum.ad}</div>
                        </div>
                    `;
                    item.onclick = function() {
                        showPlayer(bolum.link);
                    };
                    listContainer.appendChild(item);
                });
            } else {
                listContainer.innerHTML = "<p>Bu dizi için bölüm bulunamadı.</p>";
            }
            
            document.querySelector(".filmpaneldis").classList.add("hidden");
            document.getElementById("bolumler").classList.remove("hidden");
            document.getElementById("geriBtn").style.display = "block";
            currentScreen = 'bolumler';
        }

        function showPlayer(videoUrl) {
            document.getElementById("playerpanel").style.display = "flex";
            document.getElementById("bolumler").classList.add("hidden");
            currentScreen = 'player';
            
            // Iframe ile video oynatma
            var iframePlayer = document.getElementById("iframe-player");
            iframePlayer.src = videoUrl;
            
            // Tam ekran desteği için allowfullscreen özelliği eklendi
            iframePlayer.setAttribute('allowfullscreen', 'true');
        }

        function geriPlayer() {
            document.getElementById("playerpanel").style.display = "none";
            document.getElementById("bolumler").classList.remove("hidden");
            currentScreen = 'bolumler';
            
            // Iframe kaynağını sıfırla
            document.getElementById("iframe-player").src = "";
        }

        function geriDon() {
            sessionStorage.removeItem('currentDiziID');
            document.querySelector(".filmpaneldis").classList.remove("hidden");
            document.getElementById("bolumler").classList.add("hidden");
            document.getElementById("geriBtn").style.display = "none";
            currentScreen = 'anaSayfa';
        }

        function checkInitialState() {
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            if (currentDiziID) {
                showBolumler(currentDiziID);
            } else {
                currentScreen = 'anaSayfa';
                document.querySelector(".filmpaneldis").classList.remove("hidden");
                document.getElementById("bolumler").classList.add("hidden");
                document.getElementById("playerpanel").style.display = "none";
                document.getElementById("geriBtn").style.display = "none";
            }
        }

        document.addEventListener('DOMContentLoaded', checkInitialState);

        function searchSeries() {
            var query = document.getElementById('seriesSearch').value.toLowerCase();
            var series = document.querySelectorAll('.filmpanel');
            series.forEach(function(serie) {
                var title = serie.querySelector('.filmisim').textContent.toLowerCase();
                if (title.includes(query)) {
                    serie.style.display = "block";
                } else {
                    serie.style.display = "none";
                }
            });
            return false;
        }

        function resetSeriesSearch() {
            var query = document.getElementById('seriesSearch').value.toLowerCase();
            if (query === "") {
                var series = document.querySelectorAll('.filmpanel');
                series.forEach(function(serie) {
                    serie.style.display = "block";
                });
            }
        }
    </script>
</body>
</html>
    """

    dizi_json = {}
    dizi_panelleri = ""
    dizi_id = 1

    dizi_scraper = DiziGom()
    categories = list(dizi_scraper.main_page_urls.keys())
    all_diziler = []
    for category in categories:
        all_diziler.extend(dizi_scraper.get_main_page(page=1, category=category))

    for dizi in all_diziler:
        dizi_data = dizi_scraper.load(dizi['url'])
        if dizi_data:
            bolumler = []
            for episode in dizi_data['episodes']:
                embed_link = dizi_scraper.load_links(episode['url'])
                if embed_link:
                    bolumler.append({
                        "ad": f"{dizi_data['title']} - S{episode['season']}E{episode['episode']} {episode['name'] or ''}",
                        "link": embed_link
                    })
            if bolumler:
                dizi_json[str(dizi_id)] = {
                    "resim": dizi_data['poster'] or dizi['poster'],
                    "bolumler": bolumler
                }
                dizi_panelleri += f"""
                    <div class="filmpanel" onclick="showBolumler('{dizi_id}')">
                        <div class="filmresim"><img src="{dizi_data['poster'] or dizi['poster']}"></div>
                        <div class="filmisimpanel">
                            <div class="filmisim">{dizi_data['title']}</div>
                        </div>
                    </div>
                """
                dizi_id += 1

    html = html_template.format(dizi_panelleri=dizi_panelleri, dizi_json=json.dumps(dizi_json, ensure_ascii=False))

    with open("gom.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("gom.html oluşturuldu.")

if __name__ == "__main__":
    # GitHub Actions ile çalışıp çalışmadığını kontrol et
    is_github_action = os.getenv("GITHUB_ACTIONS") == "true"

    # Dizi verilerini topla ve gom.html oluştur
    generate_html([])

    # Eğer GitHub Actions içindeyse, gom.html'yi repoya kaydet
    if is_github_action:
        try:
            # GitHub Actions ortamında dosya kaydetme
            import subprocess
            subprocess.run(["git", "config", "--global", "user.email", "action@github.com"])
            subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"])
            subprocess.run(["git", "add", "gom.html"])
            subprocess.run(["git", "commit", "-m", "Update gom.html with latest series data"])
            subprocess.run(["git", "push"])
            print("gom.html GitHub repoya kaydedildi.")
        except Exception as e:
            print(f"GitHub repoya kaydetme hatası: {e}")
