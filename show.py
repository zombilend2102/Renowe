import requests
from bs4 import BeautifulSoup
import json
import time
import re

# Web sitesi kök adresi
BASE_URL = "https://www.showtv.com.tr"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"Hata oluştu ({url}): {e}")
        return None

def slugify(text):
    text = text.lower()
    text = text.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def extract_episode_number(name):
    """
    Bölüm adından numarayı çeker (Sıralama için).
    Örn: '131. Bölüm' -> 131 döner.
    Bulamazsa 9999 döndürür ki sona gitsin.
    """
    match = re.search(r'(\d+)\.\s*Bölüm', name)
    if match:
        return int(match.group(1))
    return 9999

def main():
    print("Diziler taranıyor... Lütfen bekleyin.")
    soup = get_soup(f"{BASE_URL}/diziler")
    if not soup:
        return

    diziler_data = {}
    dizi_kutulari = soup.find_all("div", attrs={"data-name": "box-type6"})
    
    print(f"Toplam {len(dizi_kutulari)} adet dizi bulundu.")

    for kutu in dizi_kutulari:
        try:
            link_tag = kutu.find("a", class_="group")
            if not link_tag:
                continue
                
            dizi_link = BASE_URL + link_tag.get("href")
            dizi_adi = link_tag.get("title")
            dizi_id = slugify(dizi_adi)
            
            # Afiş Linki
            img_tag = kutu.find("img")
            poster_url = img_tag.get("src") if img_tag else ""
            if img_tag and img_tag.get("data-src"):
                poster_url = img_tag.get("data-src")
            if "?" in poster_url:
                poster_url = poster_url.split("?")[0]

            print(f"--> İşleniyor: {dizi_adi}")

            # ---------------------------------------------------------
            # ÖNEMLİ: Ana sayfadaki "Son Bölüm" butonunu yakala
            # ---------------------------------------------------------
            son_bolum_url = None
            son_bolum_span = kutu.find("span", string="Son Bölüm")
            if son_bolum_span:
                parent_a = son_bolum_span.find_parent("a")
                if parent_a and parent_a.get("href"):
                    href = parent_a.get("href")
                    if "/tum_bolumler/" in href:
                        son_bolum_url = BASE_URL + href
                        print(f"    [Bilgi] Ana sayfadan son bölüm linki tespit edildi.")

            # Dizi Detay Sayfasına Git
            detail_soup = get_soup(dizi_link)
            if not detail_soup:
                continue

            # Linkleri toplayacağımız geçici liste
            raw_links = []
            seen_urls = set()

            # 1. YÖNTEM: Dropdown (<select> -> <option>)
            options = detail_soup.find_all("option", attrs={"data-href": True})
            for opt in options:
                rel_link = opt.get("data-href")
                bolum_adi = opt.text.strip()
                if "/tum_bolumler/" in rel_link:
                    full = BASE_URL + rel_link
                    if full not in seen_urls:
                        raw_links.append({"ad": bolum_adi, "page_url": full})
                        seen_urls.add(full)

            # 2. YÖNTEM: Eğer ana sayfadan "Son Bölüm" bulduysak ve listede yoksa ekle
            if son_bolum_url and son_bolum_url not in seen_urls:
                raw_links.append({"ad": "Yeni Bölüm (Otomatik Eklendi)", "page_url": son_bolum_url})
                seen_urls.add(son_bolum_url)
                print("    [Kritik] Listede olmayan son bölüm manuel eklendi.")

            print(f"    - {len(raw_links)} adet sayfa linki bulundu. Videolar çekiliyor...")

            final_bolumler = []
            
            # Linkleri gez ve M3U8 çek
            for item in raw_links: 
                video_soup = get_soup(item["page_url"])
                if not video_soup:
                    continue
                
                # Bölüm adını title'dan çekip düzeltelim
                page_title = video_soup.title.string if video_soup.title else item["ad"]
                clean_name = page_title.replace("İzle", "").replace("Show TV", "").strip()
                
                # Eğer temiz isimde "Bölüm" geçiyorsa onu kullan, yoksa listedeki adı kullan
                if "Bölüm" in clean_name:
                    display_name = clean_name
                else:
                    display_name = item["ad"]

                # Video JSON verisi
                video_div = video_soup.find("div", class_="hope-video")
                if video_div and video_div.get("data-hope-video"):
                    try:
                        v_data = json.loads(video_div.get("data-hope-video"))
                        m3u8 = ""
                        if "media" in v_data and "m3u8" in v_data["media"]:
                            m3u8 = v_data["media"]["m3u8"][0]["src"]
                        
                        if m3u8:
                            m3u8 = m3u8.replace("//ht/", "/ht/").replace("com//", "com/")
                            final_bolumler.append({
                                "ad": display_name,
                                "link": m3u8,
                                # Sıralama için bölüm numarasını buluyoruz
                                "episode_num": extract_episode_number(display_name)
                            })
                            print(f"      + {display_name} OK")
                    except:
                        pass
                
                time.sleep(0.05) 

            # ---------------------------------------------------------
            # SIRALAMA: Küçükten Büyüğe (1. Bölüm -> Son Bölüm)
            # ---------------------------------------------------------
            if final_bolumler:
                # Bölüm numarasına göre sırala
                final_bolumler = sorted(final_bolumler, key=lambda x: x['episode_num'])
                
                # JSON'a kaydederken 'episode_num' alanını temizle
                cleaned_final = [{"ad": x["ad"], "link": x["link"]} for x in final_bolumler]

                diziler_data[dizi_id] = {
                    "resim": poster_url,
                    "bolumler": cleaned_final
                }

        except Exception as e:
            print(f"Hata: {e}")

    create_html_file(diziler_data)

def create_html_file(data):
    # JSON verisini HTML içine gömmek için stringe çevir
    json_str = json.dumps(data, ensure_ascii=False)
    
    # CSS'in eksiksiz hali
    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <title>TITAN TV YERLİ VOD</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css?family=PT+Sans:700i" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://kit.fontawesome.com/bbe955c5ed.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@splidejs/splide@4.1.4/dist/js/splide.min.js"></script>
    <style>
        /* CSS: Tamamen Orijinal Yapıya Sadık Kaldı */
        *:not(input):not(textarea) {{
            -moz-user-select: -moz-none;
            -khtml-user-select: none;
            -webkit-user-select: none;
            -o-user-select: none;
            -ms-user-select: none;
            user-select: none
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
        .slider-slide {{
            background: #15161a;
            box-sizing: border-box;
        }}  
        .slidefilmpanel {{
            transition: .35s;
            box-sizing: border-box;
            background: #15161a;
            overflow: hidden;
        }}
        .slidefilmpanel:hover {{
            background-color: #572aa7;
        }}
        .slidefilmpanel:hover .filmresim img {{
            transform: scale(1.2);
        }}
        .slider {{
            position: relative;
            padding-bottom: 0px;
            width: 100%;
            overflow: hidden;
            --tw-shadow: anio0 25px 50px -12px rgb(0 0 0 / 0.25);
            --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color);
            box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
        }}
        .slider-container {{
            display: flex;
            width: 100%;
            scroll-snap-type: x var(--tw-scroll-snap-strictness);
            --tw-scroll-snap-strictness: mandatory;
            align-items: center;
            overflow: auto;
            scroll-behavior: smooth;
        }}
        .slider-container .slider-slide {{
            aspect-ratio: 9/13.5;
            display: flex;
            flex-shrink: 0;
            flex-basis: 14.14%;
            scroll-snap-align: start;
            flex-wrap: nowrap;
            align-items: center;
            justify-content: center;
        }}
        .slider-container::-webkit-scrollbar {{
            width: 0px;
        }}
        .clear {{
            clear: both;
        }}
        .hataekran i {{
            color: #572aa7;
            font-size: 80px;
            text-align: center;
            width: 100%;
        }}
        .hataekran {{
            width: 80%;
            margin: 20px auto;
            color: #fff;
            background: #15161a;
            border: 1px solid #323442;
            padding: 10px;
            box-sizing: border-box;
            border-radius: 10px;
        }}
        .hatayazi {{
            color: #fff;
            font-size: 15px;
            text-align: center;
            width: 100%;
            margin: 20px 0px;
        }}
        .filmpaneldis {{
            background: #15161a;
            width: 100%;
            margin: 20px auto;
            overflow: hidden;
            padding: 10px 5px;
            box-sizing: border-box;
        }}
        .aramafilmpaneldis {{
            background: #15161a;
            width: 100%;
            margin: 20px auto;
            overflow: hidden;
            padding: 10px 5px;
            box-sizing: border-box;
        }}
        .sliderfilmimdb {{
            display: none;
        }}
        .bos {{
            width: 100%;
            height: 60px;
            background: #572aa7;
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
            box-shadow: 0 0 10px rgba(87, 42, 167, 0.5);
        }}
        .filmpanel:focus {{
            outline: none;
            border: 3px solid #572aa7;
            box-shadow: 0 0 10px rgba(87, 42, 167, 0.5);
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
        .filmpanel:focus .filmresim img {{
            transform: none;
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
            bottom: 5px;
        }}
        .filmimdb {{
            display: none;
        }}
        .resimust {{
            display: none;
        }}
        .filmyil {{
            display: none;
        }}
        .filmdil {{
            display: none;
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
            background: ;
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
        #dahafazla {{
            background: #572aa7;
            color: #fff;
            padding: 10px;
            margin: 20px auto;
            width: 200px;
            text-align: center;
            transition: .35s;
        }}
        #dahafazla:hover {{
            background: #fff;
            color: #000;
        }}
        .hidden {{ display: none; }}
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
        /* Player Panel Styles - Tam Ekran Düzeltmesi */
        .playerpanel {{
            width: 100%;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
            background: #0a0e17;
            z-index: 9999;
            display: none;
            flex-direction: column;
            overflow: hidden;
        }}
        
        /* DÜZELTME: main-player artık 100% yüksekliği kullanıyor */
        #main-player {{
            width: 100%;
            height: 100%; 
            background: #000;
        }}
        
        /* Bradmax iframe stili */
        #bradmax-iframe {{
            width: 100%;
            height: 100%;
            border: none;
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
            position: absolute; /* Video alanının üstüne çıkması için mutlak konumlandırma */
            top: 10px;
            left: 10px;
            z-index: 10000;
        }}
        
        @media(max-width:550px) {{
            .filmpanel {{
                width: 31.33%;
                height: 190px;
                margin: 1%;
            }}
            /* DÜZELTME: Mobil görünümde de tam yükseklik kullanılır, böylece ekran tam kaplanır. */
            #main-player {{
                height: 100%; 
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

    <div class="filmpaneldis" id="diziListesiContainer">
        <div class="baslik">YERLİ DİZİLER VOD BÖLÜM</div>
        </div>

    <div id="bolumler" class="bolum-container hidden">
        <div id="geriBtn" class="geri-btn" onclick="geriDon()">Geri</div>
        <div id="bolumListesi" class="filmpaneldis"></div>
    </div>

    <div id="playerpanel" class="playerpanel">
        <div class="player-geri-btn" onclick="geriPlayer()">Geri</div>
        <div id="main-player"></div>
    </div>

    <script>
        
        // Bradmax Player URL'si ve Otomatik Oynatma/Tam Ekran parametreleri
        const BRADMAX_BASE_URL = "https://bradmax.com/client/embed-player/d9decbf0d308f4bb91825c3f3a2beb7b0aaee2f6_8493?mediaUrl=";
        const BRADMAX_PARAMS = "&autoplay=true&fs=true"; 

        // Python tarafından çekilen veri buraya gömülecek
        var diziler = {json_str};

        // Sayfa yüklendiğinde dizileri listele
        document.addEventListener('DOMContentLoaded', function() {{
            var container = document.getElementById("diziListesiContainer");
            
            // Eğer diziler boş değilse listele
            Object.keys(diziler).forEach(function(key) {{
                var dizi = diziler[key];
                var item = document.createElement("div");
                item.className = "filmpanel";
                item.onclick = function() {{ showBolumler(key); }};
                item.innerHTML = `
                    <div class="filmresim"><img src="${{dizi.resim}}"></div>
                    <div class="filmisimpanel">
                        <div class="filmisim">${{key.replace(/-/g, ' ').toUpperCase()}}</div>
                    </div>
                `;
                // Başlık etiketinden sonra eklemek için (Yerli Diziler yazısının altına)
                container.appendChild(item);
            }});

            checkInitialState();
        }});

        let currentScreen = 'anaSayfa';

        function showBolumler(diziID) {{
            sessionStorage.setItem('currentDiziID', diziID);
            var listContainer = document.getElementById("bolumListesi");
            listContainer.innerHTML = "";
            
            if (diziler[diziID]) {{
                // Diziler Python'da sıralandı ama yine de garanti olsun diye burada karışmıyoruz
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
                        showPlayer(bolum.link, diziID);
                    }};
                    listContainer.appendChild(item);
                }});
            }} else {{
                listContainer.innerHTML = "<p>Bu dizi için bölüm bulunamadı.</p>";
            }}
            
            document.querySelector("#diziListesiContainer").classList.add("hidden");
            document.getElementById("bolumler").classList.remove("hidden");
            document.getElementById("geriBtn").style.display = "block";

            currentScreen = 'bolumler';
            history.replaceState({{ page: 'bolumler', diziID: diziID }}, '', `#bolumler-${{diziID}}`);
        }}

        function showPlayer(streamUrl, diziID) {{
            document.getElementById("playerpanel").style.display = "flex"; 
            document.getElementById("bolumler").classList.add("hidden");

            currentScreen = 'player';
            history.pushState({{ page: 'player', diziID: diziID, streamUrl: streamUrl }}, '', `#player-${{diziID}}`);

            document.getElementById("main-player").innerHTML = "";

            // URL oluşturma (Autoplay ve Tam Ekran eklenmiş)
            const fullUrl = BRADMAX_BASE_URL + encodeURIComponent(streamUrl) + BRADMAX_PARAMS;
            
            // Iframe oluşturma (Odaklanmayı sağlamak için tabindex="0" ve autofocus eklendi)
            const iframeHtml = `<iframe id="bradmax-iframe" src="${{fullUrl}}" allowfullscreen tabindex="0" autofocus></iframe>`;
            
            document.getElementById("main-player").innerHTML = iframeHtml;
        }}

        function geriPlayer() {{
            document.getElementById("playerpanel").style.display = "none";
            document.getElementById("bolumler").classList.remove("hidden");

            document.getElementById("main-player").innerHTML = "";

            currentScreen = 'bolumler';
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            history.replaceState({{ page: 'bolumler', diziID: currentDiziID }}, '', `#bolumler-${{currentDiziID}}`);
        }}

        function geriDon() {{
            sessionStorage.removeItem('currentDiziID');
            document.querySelector("#diziListesiContainer").classList.remove("hidden");
            document.getElementById("bolumler").classList.add("hidden");
            document.getElementById("geriBtn").style.display = "none";
            
            currentScreen = 'anaSayfa';
            history.replaceState({{ page: 'anaSayfa' }}, '', '#anaSayfa');
        }}

        window.addEventListener('popstate', function(event) {{
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            
            if (event.state && event.state.page === 'player' && event.state.diziID && event.state.streamUrl) {{
                showBolumler(event.state.diziID);
                showPlayer(event.state.streamUrl, event.state.diziID);
            }} else if (event.state && event.state.page === 'bolumler' && event.state.diziID) {{
                showBolumler(event.state.diziID);
            }} else {{
                sessionStorage.removeItem('currentDiziID');
                document.querySelector("#diziListesiContainer").classList.remove("hidden");
                document.getElementById("bolumler").classList.add("hidden");
                document.getElementById("playerpanel").style.display = "none";
                document.getElementById("geriBtn").style.display = "none";
                currentScreen = 'anaSayfa';
                history.replaceState({{ page: 'anaSayfa' }}, '', '#anaSayfa');

                document.getElementById("main-player").innerHTML = "";
            }}
        }});

        function checkInitialState() {{
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            if (currentDiziID) {{
                showBolumler(currentDiziID);
            }} else {{
                currentScreen = 'anaSayfa';
                document.querySelector("#diziListesiContainer").classList.remove("hidden");
                document.getElementById("bolumler").classList.add("hidden");
                document.getElementById("playerpanel").style.display = "none";
                document.getElementById("geriBtn").style.display = "none";
                history.replaceState({{ page: 'anaSayfa' }}, '', '#anaSayfa');
            }}
        }}

        function searchSeries() {{
            var query = document.getElementById('seriesSearch').value.toLowerCase();
            var series = document.querySelectorAll('#diziListesiContainer .filmpanel');

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
            if (query ===("")) {{
                var series = document.querySelectorAll('#diziListesiContainer .filmpanel');
                series.forEach(function(serie) {{
                    serie.style.display = "block";
                }});
            }}
        }}
    </script>
</body>
</html>"""
    
    with open("show.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("show.html dosyası başarıyla oluşturuldu!")

if __name__ == "__main__":
    main()
