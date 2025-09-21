import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
import os
import time

class DiziGom:
    def __init__(self):
        self.main_url = "https://dizipod.com"
        self.session = requests.Session()
        self.kategoriler = {
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
            f"{self.main_url}/dizi-arsivi-hd1/": "Dizi Arşivi",
        }
        self.zaten_eklenenler = set()

    def _fix_url(self, url):
        if not url:
            return None
        return urljoin(self.main_url, url)

    def get_main_page(self, page, category_url):
        search_url = "/wp-admin/admin-ajax.php"
        if page > 1:
            response = self.session.post(
                f"{self.main_url}{search_url}",
                headers={"X-Requested-With": "XMLHttpRequest", "Referer": category_url},
                data={
                    "action": "dizigom_search_action",
                    "formData": self._get_form_data(category_url),
                    "paged": str(page),
                    "_wpnonce": "18a90a7287"
                }
            )
        else:
            response = self.session.get(category_url)
            time.sleep(1)

        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select("div.episode-box")
        return [self._parse_item(item) for item in items if self._parse_item(item)]

    def _get_form_data(self, url):
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        form_input = soup.select_one("form.dizigom_advenced_search input")
        if form_input:
            name = form_input.get("name")
            value = form_input.get("value")
            return f"{name}={value}"
        return ""

    def _parse_item(self, item):
        title = item.select_one("div.serie-name a")
        href = item.select_one("a")
        poster = item.select_one("img")
        if not title or not href:
            return None
        return {
            "baslik": title.text.strip(),
            "afis_url": self._fix_url(poster.get("src") if poster else None),
            "url": self._fix_url(href.get("href"))
        }

    def kac_sayfa_var(self, category_url):
        try:
            response = self.session.get(category_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            sayfa_linkleri = soup.select("a.page-numbers")
            if sayfa_linkleri:
                sayfa_nolar = []
                for link in sayfa_linkleri:
                    try:
                        sayfa_nolar.append(int(link.text))
                    except ValueError:
                        continue
                return max(sayfa_nolar) if sayfa_nolar else 1
            return 1
        except:
            return 1

    def tum_sayfalari_cek(self, category_url):
        tum_icerik = []
        try:
            toplam_sayfa = self.kac_sayfa_var(category_url)
            print(f"Toplam {toplam_sayfa} sayfa bulundu.")
            
            for sayfa in range(1, toplam_sayfa + 1):
                print(f"Sayfa {sayfa}/{toplam_sayfa} çekiliyor...")
                icerikler = self.get_main_page(sayfa, category_url)
                tum_icerik.extend(icerikler)
                time.sleep(0.5)
        except Exception as e:
            print(f"Hata oluştu: {e}")
        return tum_icerik

    def search(self, query):
        response = self.session.get(f"{self.main_url}/?s={query}")
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select("div.single-item")
        return [self._parse_search_item(item) for item in items if self._parse_search_item(item)]

    def _parse_search_item(self, item):
        title = item.select_one("div.categorytitle a")
        poster = item.select_one("img")
        if not title:
            return None
        return {
            "baslik": title.text.strip(),
            "afis_url": self._fix_url(poster.get("src") if poster else None),
            "url": self._fix_url(title.get("href"))
        }

    def load(self, url):
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.select_one("div.serieTitle h1")
        poster_style = soup.select_one("div.seriePoster")
        if not title:
            return None

        afis_url = None
        if poster_style and poster_style.get("style"):
            match = re.search(r'background-image:url\((.*?)\)', poster_style.get("style"))
            if match:
                afis_url = self._fix_url(match.group(1))

        bolumler = []
        for item in soup.select("div.bolumust"):
            ep_href = item.select_one("a")
            ep_name = item.select_one("div.bolum-ismi")
            ep_baslik = item.select_one("div.baslik")
            if not ep_href:
                continue

            sezon = bolum = None
            if ep_baslik:
                baslik_text = ep_baslik.text.split()
                if len(baslik_text) >= 3:
                    sezon = int(baslik_text[0].replace(".", "")) if baslik_text[0].replace(".", "").isdigit() else None
                    bolum = int(baslik_text[2].replace(".", "")) if baslik_text[2].replace(".", "").isdigit() else None

            bolumler.append({
                "bolum_url": self._fix_url(ep_href.get("href")),
                "bolum_adi": ep_name.text.strip() if ep_name else None,
                "sezon": sezon,
                "bolum": bolum
            })

        return {
            "baslik": title.text.strip(),
            "afis_url": afis_url,
            "bolumler": bolumler
        }

    def load_links(self, bolum_url):
        try:
            response = self.session.get(bolum_url, headers={"Referer": self.main_url + "/"})
            soup = BeautifulSoup(response.text, 'html.parser')
            script = soup.select_one("div#content script")
            if not script or not script.string:
                return None

            json_data = json.loads(script.string)
            embed_url = json_data.get("contentUrl")
            if not embed_url:
                return None

            embed_url = embed_url.replace("https://", "https://play.")
            return embed_url
        except Exception as e:
            print(f"Embed link alınırken hata: {e}")
            return None

    def tum_icerik_cek(self, kategori_url=None, arama_query=None):
        tum_icerikler = []
        
        if arama_query:
            print(f"Arama yapılıyor: {arama_query}")
            arama_sonuclari = self.search(arama_query)
            for item in arama_sonuclari:
                if item["baslik"] in self.zaten_eklenenler:
                    continue
                    
                icerik = self.load(item["url"])
                if not icerik:
                    continue
                
                bolumler_embed = []
                for bolum in icerik.get("bolumler", []):
                    embed_link = self.load_links(bolum["bolum_url"])
                    if embed_link:
                        bolumler_embed.append({
                            "sezon": bolum["sezon"],
                            "bolum": bolum["bolum"],
                            "bolum_adi": bolum["bolum_adi"],
                            "embed_link": embed_link
                        })
                
                tum_icerikler.append({
                    "baslik": icerik["baslik"],
                    "afis_url": icerik["afis_url"],
                    "bolumler": bolumler_embed,
                    "kategori": "Arama Sonucu"
                })
                self.zaten_eklenenler.add(icerik["baslik"])
        elif kategori_url:
            kategori_adi = self.kategoriler.get(kategori_url, "Bilinmeyen Kategori")
            print(f"{kategori_adi} kategorisinden içerik çekiliyor...")
            
            items = self.tum_sayfalari_cek(kategori_url)
            
            for item in items:
                if item["baslik"] in self.zaten_eklenenler:
                    continue
                    
                icerik = self.load(item["url"])
                if not icerik:
                    continue
                
                bolumler_embed = []
                for bolum in icerik.get("bolumler", []):
                    embed_link = self.load_links(bolum["bolum_url"])
                    if embed_link:
                        bolumler_embed.append({
                            "sezon": bolum["sezon"],
                            "bolum": bolum["bolum"],
                            "bolum_adi": bolum["bolum_adi"],
                            "embed_link": embed_link
                        })
                
                tum_icerikler.append({
                    "baslik": icerik["baslik"],
                    "afis_url": icerik["afis_url"],
                    "bolumler": bolumler_embed,
                    "kategori": kategori_adi
                })
                self.zaten_eklenenler.add(icerik["baslik"])
        else:
            for kategori_url, kategori_adi in self.kategoriler.items():
                print(f"{kategori_adi} kategorisinden içerik çekiliyor...")
                
                items = self.tum_sayfalari_cek(kategori_url)
                
                for item in items:
                    if item["baslik"] in self.zaten_eklenenler:
                        continue
                        
                    icerik = self.load(item["url"])
                    if not icerik:
                        continue
                    
                    bolumler_embed = []
                    for bolum in icerik.get("bolumler", []):
                        embed_link = self.load_links(bolum["bolum_url"])
                        if embed_link:
                            bolumler_embed.append({
                                "sezon": bolum["sezon"],
                                "bolum": bolum["bolum"],
                                "bolum_adi": bolum["bolum_adi"],
                                "embed_link": embed_link
                            })
                    
                    tum_icerikler.append({
                        "baslik": icerik["baslik"],
                        "afis_url": icerik["afis_url"],
                        "bolumler": bolumler_embed,
                        "kategori": kategori_adi
                    })
                    self.zaten_eklenenler.add(icerik["baslik"])
        
        return tum_icerikler

    def _dizi_kartlari_olustur(self, icerikler):
        kart_html = ""
        for i, icerik in enumerate(icerikler):
            kart_html += f"""
        <div class="filmpanel" onclick="showBolumler('{i}')" data-kategori="{icerik['kategori']}">
            <div class="filmresim"><img src="{icerik['afis_url']}"></div>
            <div class="filmisimpanel">
                <div class="filmisim">{icerik['baslik']}</div>
            </div>
        </div>"""
        return kart_html

    def _js_veri_olustur(self, icerikler):
        js_veri = {}
        for i, icerik in enumerate(icerikler):
            bolumler = []
            for bolum in icerik['bolumler']:
                bolum_adi = f"{icerik['baslik']} {bolum['sezon']}.Sezon {bolum['bolum']}.Bölüm"
                if bolum['bolum_adi']:
                    bolum_adi += f" - {bolum['bolum_adi']}"
                
                bolumler.append({
                    "ad": bolum_adi,
                    "link": bolum['embed_link']
                })
            
            js_veri[str(i)] = {
                "resim": icerik['afis_url'],
                "bolumler": bolumler
            }
        
        return json.dumps(js_veri, ensure_ascii=False)

    def html_olustur(self, icerikler, dosya_adi="gom.html"):
        dizi_kartlari = self._dizi_kartlari_olustur(icerikler)
        js_veri = self._js_veri_olustur(icerikler)
        
        tum_kategoriler = list(set([icerik["kategori"] for icerik in icerikler]))
        kategori_butonlari = "".join([f'<div class="kategori-btn" onclick="showKategori(\'{kategori}\')">{kategori}</div>' for kategori in tum_kategoriler])
        
        html_template = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <title>TITAN TV YERLİ VOD</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css?family=PT+Sans:700i" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://kit.fontawesome.com/bbe955c5ed.js" crossorigin="anonymous"></script>
    <style>
        *:not(input):not(textarea) {{
            -moz-user-select: -moz-none;
            -khtml-user-select: none;
            -webkit-user-select: none;
            -o-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }}
        body {{
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
        }}
        .filmpaneldis {{
            background: #15161a;
            width: 100%;
            margin: 20px auto;
            overflow: hidden;
            padding: 10px 5px;
            box-sizing: border-box;
        }}
        .baslik {{
            width: 96%;
            color: #fff;
            padding: 15px 10px;
            box-sizing: border-box;
        }}
        .filmpanel {{
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
        }}
        .filmisimpanel {{
            width: 100%;
            height: 200px;
            position: relative;
            margin-top: -200px;
            background: linear-gradient(to bottom, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 1) 100%);
        }}
        .filmpanel:hover {{
            color: #fff;
            border: 3px solid #572aa7;
            box-shadow: 0 0 10px rgba(87,42,167,0.5);
        }}
        .filmresim {{
            width: 100%;
            height: 100%;
            margin-bottom: 0px;
            overflow: hidden;
            position: relative;
        }}
        .filmresim img {{
            width: 100%;
            height: 100%;
            transition: transform 0.4s ease;
        }}
        .filmpanel:hover .filmresim img {{
            transform: scale(1.1);
        }}
        .filmisim {{
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
        }}
        .aramapanel {{
            width: 100%;
            height: 60px;
            background: #15161a;
            border-bottom: 1px solid #323442;
            margin: 0px auto;
            padding: 10px;
            box-sizing: border-box;
            overflow: hidden;
            z-index: 11111;
        }}
        .aramapanelsag {{
            width: auto;
            height: 40px;
            box-sizing: border-box;
            overflow: hidden;
            float: right;
        }}
        .aramapanelsol {{
            width: 50%;
            height: 40px;
            box-sizing: border-box;
            overflow: hidden;
            float: left;
        }}
        .aramapanelyazi {{
            height: 40px;
            width: 120px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            padding: 0px 10px;
            background: #fff;
            color: #000;
            margin: 0px 5px;
        }}
        .aramapanelbuton {{
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
        }}
        .aramapanelbuton:hover {{
            background-color: #fff;
            color: #000;
        }}
        .logo {{
            width: 40px;
            height: 40px;
            float: left;
        }}
        .logo img {{
            width: 100%;
        }}
        .logoisim {{
            font-size: 15px;
            width: 70%;
            height: 40px;
            line-height: 40px;
            font-weight: 500;
            color: #fff;
        }}
        .hidden {{
            display: none;
        }}
        .bolum-container {{
            background: #15161a;
            padding: 10px;
            margin-top: 10px;
            border-radius: 5px;
        }}
        .geri-btn {{
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
        }}
        .geri-btn:hover {{
            background: #6b3ec7;
            transition: background 0.3s;
        }}
        .playerpanel {{
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
        }}
        .player-geri-btn {{
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
        }}
        .player-geri-btn:hover {{
            background: #6b3ec7;
            transition: background 0.3s;
        }}
        #iframe-player {{
            width: 100%;
            height: 100%;
            border: none;
            position: absolute;
            top: 0;
            left: 0;
        }}
        .kategori-secim {{
            width: 100%;
            padding: 10px;
            background: #15161a;
            margin-bottom: 10px;
            border-bottom: 1px solid #323442;
        }}
        .kategori-btn {{
            background: #572aa7;
            color: white;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            display: inline-block;
        }}
        .kategori-btn:hover {{
            background: #6b3ec7;
        }}
        @media(max-width:900px) {{
            .filmpanel {{
                width: 17%;
                height: 220px;
                margin: 1.5%;
            }}
        }}
        @media(max-width:550px) {{
            .filmisimpanel {{
                height: 190px;
                margin-top: -190px;
            }}
            .filmpanel {{
                width: 31.33%;
                height: 190px;
                margin: 1%;
            }}
            .player-geri-btn {{
                width: 80px;
                padding: 8px;
                font-size: 14px;
            }}
            .kategori-btn {{
                padding: 6px 10px;
                font-size: 12px;
            }}
        }}
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

    <div class="kategori-secim">
        <div class="kategori-btn" onclick="showKategori('all')">Tümü</div>
        {kategori_butonlari}
    </div>

    <div class="filmpaneldis">
        <div class="baslik">DİZİLER VOD BÖLÜM</div>
        
        {dizi_kartlari}
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
        var diziler = {js_veri};
        var kategoriler = {json.dumps({icerik["baslik"]: icerik["kategori"] for icerik in icerikler}, ensure_ascii=False)};
        
        let currentScreen = 'anaSayfa';

        function showBolumler(diziID) {{
            sessionStorage.setItem('currentDiziID', diziID);
            var listContainer = document.getElementById("bolumListesi");
            listContainer.innerHTML = "";
            
            if (diziler[diziID]) {{
                diziler[diziID].bolumler.forEach(function(bolum) {{
                    var item = document.createElement("div");
                    item.className = "filmpanel";
                    item.innerHTML = `
                        <div class="filmresim"><img src="${{diziler[diziID].resim}}"></div>
                        <div class="filmisimpanel">
                            <div class="filmisim">${{bolum.ad}}</div>
                        </div>
                    `;
                    item.onclick = function() {{
                        showPlayer(bolum.link);
                    }};
                    listContainer.appendChild(item);
                }});
            }} else {{
                listContainer.innerHTML = "<p>Bu dizi için bölüm bulunamadı.</p>";
            }}
            
            document.querySelector(".filmpaneldis").classList.add("hidden");
            document.getElementById("bolumler").classList.remove("hidden");
            document.getElementById("geriBtn").style.display = "block";
            currentScreen = 'bolumler';
        }}

        function showPlayer(videoUrl) {{
            document.getElementById("playerpanel").style.display = "flex";
            document.getElementById("bolumler").classList.add("hidden");
            currentScreen = 'player';
            
            var iframePlayer = document.getElementById("iframe-player");
            iframePlayer.src = videoUrl;
            iframePlayer.setAttribute('allowfullscreen', 'true');
        }}

        function geriPlayer() {{
            document.getElementById("playerpanel").style.display = "none";
            document.getElementById("bolumler").classList.remove("hidden");
            currentScreen = 'bolumler';
            document.getElementById("iframe-player").src = "";
        }}

        function geriDon() {{
            sessionStorage.removeItem('currentDiziID');
            document.querySelector(".filmpaneldis").classList.remove("hidden");
            document.getElementById("bolumler").classList.add("hidden");
            document.getElementById("geriBtn").style.display = "none";
            currentScreen = 'anaSayfa';
        }}

        function checkInitialState() {{
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            if (currentDiziID) {{
                showBolumler(currentDiziID);
            }} else {{
                currentScreen = 'anaSayfa';
                document.querySelector(".filmpaneldis").classList.remove("hidden");
                document.getElementById("bolumler").classList.add("hidden");
                document.getElementById("playerpanel").style.display = "none";
                document.getElementById("geriBtn").style.display = "none";
            }}
        }}

        document.addEventListener('DOMContentLoaded', checkInitialState);

        function searchSeries() {{
            var query = document.getElementById('seriesSearch').value.toLowerCase();
            var series = document.querySelectorAll('.filmpanel');
            series.forEach(function(serie) {{
                var title = serie.querySelector('.filmisim').textContent.toLowerCase();
                if (title.includes(query)) {{
                    serie.style.display = "block";
                }} else {{
                    serie.style.display = "none";
                }}
            }});
            return false;
        }}

        function resetSeriesSearch() {{
            var query = document.getElementById('seriesSearch').value.toLowerCase();
            if (query === "") {{
                var series = document.querySelectorAll('.filmpanel');
                series.forEach(function(serie) {{
                    serie.style.display = "block";
                }});
            }}
        }}

        function showKategori(kategori) {{
            var series = document.querySelectorAll('.filmpanel');
            series.forEach(function(serie, index) {{
                var diziBaslik = serie.querySelector('.filmisim').textContent;
                if (kategori === 'all' || kategoriler[diziBaslik] === kategori) {{
                    serie.style.display = "block";
                }} else {{
                    serie.style.display = "none";
                }}
            }});
        }}
    </script>
</body>
</html>"""

        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        print(f"HTML dosyası '{dosya_adi}' olarak kaydedildi.")
        return dosya_adi

# Kodu çalıştır
if __name__ == "__main__":
    dizigom = DiziGom()
    
    # Tüm kategorilerden içerik çek
    print("Tüm kategorilerden içerik çekiliyor...")
    icerikler = dizigom.tum_icerik_cek()
    
    # HTML oluştur ve kaydet
    print("HTML oluşturuluyor...")
    dizigom.html_olustur(icerikler, "gom.html")
    
    print("İşlem tamamlandı! gom.html dosyası oluşturuldu.")
    print(f"Toplam {len(icerikler)} dizi eklendi.")
