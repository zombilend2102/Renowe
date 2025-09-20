import requests
import json
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import time
from datetime import datetime

class DiziGomScraper:
    def __init__(self):
        self.main_url = "https://dizigom1.plus"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_main_categories(self):
        categories = {
            f"{self.main_url}/tur/aile/": "Aile",
            f"{self.main_url}/tur/aksiyon/": "Aksiyon",
            f"{self.main_url}/tur/animasyon/": "Animasyon",
            f"{self.main_url}/tur/belgesel/": "Belgesel",
            f"{self.main_url}/tur/bilim-kurgu/": "Bilim Kurgu",
            f"{self.main_url}/tur/dram/": "Dram",
            f"{self.main_url}/tur/fantastik/": "Fantastik",
            f"{self.main_url}/tur/gerilim/": "Gerilim",
            f"{self.main_url}/tur/komedi/": "Komedi",
            f"{self.main_url}/tur/korku/": "Korku",
            f"{self.main_url}/tur/macera/": "Macera",
            f"{self.main_url}/tur/polisiye/": "Polisiye",
            f"{self.main_url}/tur/romantik/": "Romantik",
            f"{self.main_url}/tur/savas/": "Savaş",
            f"{self.main_url}/tur/suc/": "Suç",
            f"{self.main_url}/tur/tarih/": "Tarih",
        }
        return categories
    
    def scrape_series_from_category(self, category_url, max_pages=3):
        series_list = []
        
        for page in range(1, max_pages + 1):
            try:
                if page == 1:
                    response = self.session.get(f"{category_url}")
                else:
                    # AJAX isteği simüle etmek için
                    form_data = {
                        "action": "dizigom_search_action",
                        "formData": "category=your_category",
                        "paged": str(page),
                        "_wpnonce": "18a90a7287"
                    }
                    response = self.session.post(
                        f"{self.main_url}/wp-admin/admin-ajax.php",
                        data=form_data,
                        headers={
                            "X-Requested-With": "XMLHttpRequest",
                            "Referer": category_url
                        }
                    )
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Dizi kutularını bul
                series_boxes = soup.select('div.episode-box')
                
                for box in series_boxes:
                    try:
                        title_elem = box.select_one('div.serie-name a')
                        if not title_elem:
                            continue
                            
                        title = title_elem.text.strip()
                        href = title_elem.get('href')
                        if href and not href.startswith('http'):
                            href = urljoin(self.main_url, href)
                            
                        poster_elem = box.select_one('img')
                        poster_url = poster_elem.get('src') if poster_elem else None
                        if poster_url and not poster_url.startswith('http'):
                            poster_url = urljoin(self.main_url, poster_url)
                            
                        score_elem = box.select_one('div.episode-date')
                        score = score_elem.text.replace('IMDb:', '').strip() if score_elem else None
                        
                        series_list.append({
                            'title': title,
                            'url': href,
                            'poster': poster_url,
                            'score': score
                        })
                    except Exception as e:
                        print(f"Error parsing series box: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue
                
        return series_list
    
    def search_series(self, query):
        search_url = f"{self.main_url}/?s={quote(query)}"
        series_list = []
        
        try:
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            series_items = soup.select('div.single-item')
            
            for item in series_items:
                try:
                    title_elem = item.select_one('div.categorytitle a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    href = title_elem.get('href')
                    if href and not href.startswith('http'):
                        href = urljoin(self.main_url, href)
                        
                    poster_elem = item.select_one('img')
                    poster_url = poster_elem.get('src') if poster_elem else None
                    if poster_url and not poster_url.startswith('http'):
                        poster_url = urljoin(self.main_url, poster_url)
                        
                    series_list.append({
                        'title': title,
                        'url': href,
                        'poster': poster_url
                    })
                except Exception as e:
                    print(f"Error parsing search result: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error searching: {e}")
            
        return series_list
    
    def get_series_details(self, series_url):
        try:
            response = self.session.get(series_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Başlık
            title_elem = soup.select_one('div.serieTitle h1')
            title = title_elem.text.strip() if title_elem else None
            
            # Poster
            poster_elem = soup.select_one('div.seriePoster')
            poster_style = poster_elem.get('style') if poster_elem else ''
            poster_url = None
            if 'background-image:url(' in poster_style:
                poster_url = poster_style.split('background-image:url(')[1].split(')')[0]
                if poster_url and not poster_url.startswith('http'):
                    poster_url = urljoin(self.main_url, poster_url)
            
            # Açıklama
            desc_elem = soup.select_one('div.serieDescription p')
            description = desc_elem.text.strip() if desc_elem else None
            
            # Bölümler
            episodes = []
            episode_containers = soup.select('div.bolumust')
            
            for container in episode_containers:
                try:
                    ep_link_elem = container.select_one('a')
                    ep_href = ep_link_elem.get('href') if ep_link_elem else ''
                    
                    ep_name_elem = container.select_one('div.bolum-ismi')
                    ep_name = ep_name_elem.text.strip() if ep_name_elem else ''
                    
                    ep_title_elem = container.select_one('div.baslik')
                    ep_title = ep_title_elem.text.strip() if ep_title_elem else ''
                    
                    # Sezon ve bölüm numaralarını çıkar
                    season_num = None
                    episode_num = None
                    
                    if ep_title:
                        parts = ep_title.split()
                        if len(parts) >= 3:
                            season_part = parts[0].replace('.', '')
                            episode_part = parts[2].replace('.', '')
                            
                            if season_part.isdigit():
                                season_num = int(season_part)
                            if episode_part.isdigit():
                                episode_num = int(episode_part)
                    
                    episodes.append({
                        'name': ep_name,
                        'url': ep_href,
                        'season': season_num,
                        'episode': episode_num,
                        'title': ep_title
                    })
                except Exception as e:
                    print(f"Error parsing episode: {e}")
                    continue
            
            return {
                'title': title,
                'poster': poster_url,
                'description': description,
                'episodes': episodes
            }
            
        except Exception as e:
            print(f"Error getting series details: {e}")
            return None
    
    def get_episode_video_url(self, episode_url):
        try:
            response = self.session.get(episode_url, headers={'Referer': f'{self.main_url}/'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Script içindeki JSON verisini bul
            script_content = None
            scripts = soup.select('div#content script')
            
            for script in scripts:
                if script.string and 'contentUrl' in script.string:
                    script_content = script.string
                    break
            
            if not script_content:
                return None
            
            # JSON verisini çıkar
            json_match = re.search(r'({.*})', script_content)
            if not json_match:
                return None
            
            json_data = json.loads(json_match.group(1))
            content_url = json_data.get('contentUrl', '')
            
            if not content_url:
                return None
            
            # Iframe içeriğini al
            iframe_url = content_url.replace('https://', 'https://play.')
            response = self.session.get(iframe_url, headers={'Referer': f'{self.main_url}/'})
            
            # JavaScript unpack işlemi
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.select('script')
            
            for script in scripts:
                if script.string and 'eval(function(p,a,c,k,e' in script.string:
                    # Basit bir unpack işlemi
                    js_code = script.string
                    # sources kısmını bul
                    sources_match = re.search(r'sources:\s*\[(.*?)\]', js_code, re.DOTALL)
                    if sources_match:
                        sources_text = sources_match.group(1)
                        # file ve label değerlerini bul
                        file_match = re.search(r'file:\s*["\'](.*?)["\']', sources_text)
                        if file_match:
                            return file_match.group(1)
            
            return None
            
        except Exception as e:
            print(f"Error getting video URL: {e}")
            return None
    
    def generate_html(self, series_data, output_file='gom.html'):
        # HTML şablonu
        html_template = '''<!DOCTYPE html>
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
        ${SERIES_LIST}
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
        var diziler = ${DIZILER_JSON};
        
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
</html>'''
        
        # Dizileri HTML formatına dönüştür
        series_html = ""
        for i, (series_id, series_info) in enumerate(series_data.items(), 1):
            series_html += f'''
            <div class="filmpanel" onclick="showBolumler('{i}')">
                <div class="filmresim"><img src="{series_info['resim']}"></div>
                <div class="filmisimpanel">
                    <div class="filmisim">{series_info['isim']}</div>
                </div>
            </div>'''
        
        # JSON verisini hazırla
        diziler_json = {}
        for i, (series_id, series_info) in enumerate(series_data.items(), 1):
            diziler_json[str(i)] = {
                "resim": series_info['resim'],
                "bolumler": series_info['bolumler']
            }
        
        # HTML'i oluştur ve kaydet
        html_content = html_template\
            .replace('${SERIES_LIST}', series_html)\
            .replace('${DIZILER_JSON}', json.dumps(diziler_json, ensure_ascii=False))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML dosyası oluşturuldu: {output_file}")
        return output_file

def main():
    scraper = DiziGomScraper()
    
    # Tüm kategorilerden dizileri çek
    all_series = {}
    categories = scraper.get_main_categories()
    
    print("Diziler çekiliyor...")
    
    for category_url, category_name in list(categories.items())[:3]:  # İlk 3 kategori
        print(f"{category_name} kategorisi işleniyor...")
        series_list = scraper.scrape_series_from_category(category_url, max_pages=1)
        
        for series in series_list[:5]:  # Her kategoriden ilk 5 dizi
            print(f"  {series['title']} işleniyor...")
            
            # Dizi detaylarını al
            series_details = scraper.get_series_details(series['url'])
            if not series_details:
                continue
            
            # Bölüm video linklerini al
            episodes_with_links = []
            for episode in series_details['episodes'][:4]:  # İlk 4 bölüm
                print(f"    {episode['title']} bölümü işleniyor...")
                video_url = scraper.get_episode_video_url(episode['url'])
                
                if video_url:
                    episodes_with_links.append({
                        'ad': episode['title'],
                        'link': video_url
                    })
                time.sleep(1)  # Sunucu yükünü azaltmak için
            
            if episodes_with_links:
                series_id = f"series_{len(all_series) + 1}"
                all_series[series_id] = {
                    'isim': series_details['title'],
                    'resim': series_details['poster'] or series['poster'],
                    'bolumler': episodes_with_links
                }
            
            time.sleep(2)  # Sunucu yükünü azaltmak için
    
    # HTML oluştur
    if all_series:
        scraper.generate_html(all_series, 'gom.html')
        print("İşlem tamamlandı!")
    else:
        print("Hiç dizi bulunamadı!")

if __name__ == "__main__":
    main()
