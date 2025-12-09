import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import unidecode # Türkçe karakterleri dönüştürmek için

# --- Sabitler ---
SITE_URL = "https://www.showtv.com.tr"
DIZILER_URL = "https://www.showtv.com.tr/diziler"
PLAYER_TYPE = "2" # JW Player kullanılacak
OUTPUT_FILE = "showtv_vod_player.html"

# Regex: Video verilerini yakalamak için (data-hope-video)
VIDEO_DATA_PATTERN = r'data-hope-video=\'(.*?)\''

# --- Oturum ve Hata Tekrarı Stratejisi ---
def create_session():
    """Hata durumunda tekrar deneme (Retry) stratejisi ile bir oturum oluşturur."""
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

session = create_session()
# --- Yardımcı Fonksiyonlar ---

def normalize_dizi_ad(dizi_adi):
    """
    Dizi adını JS anahtarı olarak kullanılabilecek, küçük harf ve boşluksuz bir ID'ye dönüştürür.
    ID'de sadece harf ve rakam kalır.
    """
    normalized = unidecode.unidecode(dizi_adi).lower()
    return re.sub(r'[^a-z0-9]', '', normalized)

def parse_bolum_page(url):
    """Bölüm sayfasından .m3u8 stream URL'sini çeker."""
    try:
        # Rate-limiting'den kaçınmak için bekleme
        time.sleep(0.5) 
        r = session.get(url, timeout=15)
        r.raise_for_status()
        
        # data-hope-video içeriğini bul
        match = re.search(VIDEO_DATA_PATTERN, r.text)
        if match:
            # HTML entitilerini düzelt ve JSON olarak yükle
            video_data_str = match.group(1).replace('&quot;', '"')
            video_data = json.loads(video_data_str)
            
            # m3u8 listesini kontrol et
            m3u8_list = video_data.get("media", {}).get("m3u8", [])
            for item in m3u8_list:
                if "src" in item and item["src"].endswith(".m3u8"):
                    return item["src"]
        
        return None
            
    except requests.exceptions.RequestException as e:
        print(f"    [Hata] Bölüm sayfası çekilemedi: {url} - {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"    [Hata] Video verisi JSON hatası: {url} - {e}")
        return None
    except Exception as e:
        print(f"    [Hata] Bölüm sayfası işlenirken beklenmedik hata: {url} - {e}")
        return None

def parse_episodes_page(url):
    """Show TV'nin JSON API'sinden bir sayfalık bölüm listesini çeker."""
    try:
        time.sleep(0.3)
        r = session.get(url, timeout=15)
        r.raise_for_status()
        
        # JSON yanıtından 'episodes' listesini al
        data = r.json().get("episodes", [])
        
        item_list = []
        for item in data:
            item_name = item.get("title", "Bölüm Adı Yok").strip().replace("-", " ") 
            item_img = item.get("image")
            item_url = SITE_URL + item.get("link", "")
            
            if item_img and item_url.startswith(SITE_URL):
                 item_list.append({"name": item_name, "img": item_img, "url": item_url})
                 
        return item_list
    except Exception as e:
        # Boş bir JSON yanıtı döndürebilir, bu da son sayfa demektir
        print(f"    [Uyarı] Bölümler API'si çağrısında hata/son sayfa: {url} - {str(e)}")
        return []

def get_episodes_page(serie_url):
    """Tüm sayfaları dolaşarak bir dizinin tüm bölümlerini eksiksiz çeker."""
    all_items = []
    
    # Dizi ID'sini URL'den çekiyoruz
    serie_id_match = re.search(r'/dizi/(.*?)/(\d+)$', serie_url)
    if not serie_id_match:
        print(f"    [KRİTİK HATA] Dizi ID'si bulunamadı: {serie_url}")
        return []
        
    serie_id = serie_id_match.group(2)
    base_url = f"{SITE_URL}/dizi/pagination/{serie_id}/2/"
    
    flag = True
    page_no = 0
    while flag:
        page_url = base_url + str(page_no)
        print(f"    -> Sayfa {page_no + 1} kontrol ediliyor...")
        page_items = parse_episodes_page(page_url)
        
        if not page_items:
            flag = False # Bölüm yoksa veya API hatası
        else:
            # Show TV API'si en yeni bölümü önce veriyor.
            # Sayfalandırmanın her çağrısı genellikle yeni bölümleri baştan getirir,
            # ancak genellikle bölümler ters sırada (eskiden yeniye) eklenmelidir.
            # parse_episodes_page zaten en yeniyi en başa eklediği için, 
            # buradaki mantıkta, yeni gelen sayfayı listenin başına ekliyoruz.
            all_items = page_items + all_items 
        
        page_no += 1
        # Aşırı istek atmamak için güvenli sayfa sınırı
        if page_no > 50: 
            print("    [UYARI] Çok fazla sayfa bulundu, maksimum sayfa sayısına ulaşıldı (50).")
            flag = False

    # Bölümleri addan sıralayıp tekrarları temizliyoruz.
    unique_episodes = {}
    for ep in all_items:
        # Bölüm adı ve URL'yi birleştirerek tekillik kontrolü yap
        key = f"{ep['name']}_{ep['url']}"
        if key not in unique_episodes:
            unique_episodes[key] = ep
            
    # Bölümleri adına göre (örn: 1, 2, 3...) sıralamak genellikle en doğrusudur, 
    # ancak API'den gelen sırayı koruyalım (en eski en başta).
    return list(unique_episodes.values())

def get_arsiv_page(url):
    """Tüm dizi listesini arşiv sayfasından çeker."""
    item_list = []
    try:
        time.sleep(0.3)
        r = session.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        
        # Dizi kartlarını bul
        items = soup.find_all("div", {"data-name": "box-type6"})
        
        for item in items:
            link_tag = item.find("a")
            img_tag = item.find("img")
            name_tag = item.find("span", {"class": "line-clamp-3"})
            
            if link_tag and img_tag and name_tag:
                item_url = SITE_URL + link_tag.get("href", "")
                item_img = img_tag.get("src", "")
                # Dizi adını temizle ve boşlukları koru (ileride normalize edilecek)
                item_name = name_tag.get_text().strip().replace("-", " ") 
                item_id = normalize_dizi_ad(item_name) # JS ID'si için normalize et
                
                # Sadece geçerli URL'leri ve resimleri kontrol et
                if item_url.startswith(SITE_URL) and item_img:
                    item_list.append({"name": item_name, "img": item_img, "url": item_url, "id": item_id})
                
    except Exception as e:
        print(f"[KRİTİK HATA] Arşiv sayfası hatası: {url} - {str(e)}")
        
    return item_list

# --- Ana İşlem Fonksiyonu ---

def main():
    
    print("🎬 Show TV Dizi VOD Verileri Çekiliyor...")
    
    # 1. Dizi Listesini Çek
    series_list = get_arsiv_page(DIZILER_URL)
    
    if not series_list:
        print("❌ Dizi listesi çekilemedi. Program sonlandırılıyor.")
        return
        
    diziler_data = {} # Final JSON verisi için
    total_series = len(series_list)
    print(f"✅ Toplam {total_series} dizi bulundu. Bölüm verileri çekiliyor...")

    # 2. Her Dizi İçin Bölümleri ve Stream URL'lerini Çek
    for i, serie in enumerate(tqdm(series_list, desc="Diziler İşleniyor", unit="dizi")):
        
        dizi_adi = serie['name']
        dizi_id = serie['id']
        dizi_url = serie['url']
        dizi_logo = serie['img']
        
        # print(f"\n[{i+1}/{total_series}] -> Dizi: {dizi_adi}")
        
        try:
            # Tüm bölümleri çek (sayfalandırma kontrolü dahil)
            episodes = get_episodes_page(dizi_url)
            
            if episodes:
                # print(f"  Toplam {len(episodes)} bölüm bulundu.")
                
                temp_bolumler = []
                
                # Stream URL'lerini çek
                for j, episode in enumerate(tqdm(episodes, desc=f"  {dizi_adi} Bölümleri", unit="bölüm", leave=False)):
                    stream_url = parse_bolum_page(episode["url"])
                    
                    if stream_url:
                        # Bölüm adı formatını düzelt (örn: 1. Sezon 1. Bölüm)
                        # Show TV genelde Bölüm Adı olarak sadece "1. Bölüm" vb. kullanıyor.
                        bolum_ad_match = re.search(r'(\d+)\.\s*Bölüm', episode["name"], re.IGNORECASE)
                        bolum_numarasi = bolum_ad_match.group(1) if bolum_ad_match else f"{j+1}"
                        
                        # Bölüm adını standartlaştıralım. Yıl bilgisi olmadığı için IMDb'den yılı çekmiyoruz.
                        final_bolum_ad = f"1. Sezon {bolum_numarasi}. Bölüm" 
                        
                        temp_bolumler.append({
                            "ad": final_bolum_ad,
                            "link": stream_url
                        })
                
                if temp_bolumler:
                    # Yeni dizi objesini oluştur ve 'diziler_data'ya ekle
                    # Yıl ve IMDb bilgisi Show TV'den çekilmediği için sabit değerler eklendi
                    diziler_data[dizi_id] = {
                        "ad": dizi_adi,
                        "resim": dizi_logo,
                        "imdb": "-",
                        "dil": "Yerli",
                        "yil": "VOD",
                        "player": PLAYER_TYPE,
                        "bolumler": temp_bolumler
                    }
                    # print(f"  ✅ {dizi_adi} için TOPLAM {len(temp_bolumler)} stream URL'si çekildi.")
                # else:
                    # print(f"  [ATLANDI] {dizi_adi} için stream URL'si bulunamadı.")
            # else:
                # print(f"  [ATLANDI] {dizi_adi} için hiç bölüm bulunamadı.")
                
        except Exception as e:
            print(f"\n  [KRİTİK HATA] {dizi_adi} işlenirken beklenmedik hata: {e}")
            continue

    print(f"\n--- Veri Çekimi Tamamlandı. Toplam {len(diziler_data)} dizi işlendi. ---")
    
    # 3. HTML ve JavaScript Kodu Oluşturma
    generate_html_output(diziler_data)

# --- HTML/JS Çıktısı Oluşturma ---

def generate_html_output(diziler_data):
    """Çekilen verileri kullanarak HTML çıktısını oluşturur ve kaydeder."""
    
    if not diziler_data:
        print("❌ HTML dosyası oluşturulamadı: İşlenecek dizi verisi yok.")
        return

    # JSON'u sıkıştır ve JS güvenli hale getir
    js_diziler_data = json.dumps(diziler_data, indent=None, ensure_ascii=False)
    # Tırnak işaretlerini kaçış karakteri ile düzelt (Python'da '\\"' yerine '\'')
    js_diziler_data = js_diziler_data.replace('"', '\\"') 

    # Ana sayfa üzerindeki dizileri oluşturmak için HTML dizeleri
    dizi_paneller_html = ""
    for id, data in diziler_data.items():
        # IMDb ve YIL bilgileri yoksa bile yeri dursun diye boş string gönderdim
        imdb_rating = data.get("imdb", "-")
        year = data.get("yil", "VOD")
        
        dizi_paneller_html += f"""
    <div class="filmpanel" onclick="showBolumler('{id}')">
        <div class="filmresim"><img src="{data['resim']}"></div>
        <div class="filmisimpanel">
            <div class="filmimdb">{imdb_rating}</div>
            <div class="filmisim">{data['ad']}</div>
            <div class="resimust">
                <div class="filmdil">{data['dil']}</div>
                <div class="filmyil">{year}</div>
            </div>
        </div>
    </div>
"""

    # HTML Şablonu (Player entegrasyonlu ve tarihçe yönetimli)
    html_template = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <title>TITAN TV YERLİ VOD - Show TV</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css?family=PT+Sans:700i" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://kit.fontawesome.com/bbe955c5ed.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@splidejs/splide@4.1.4/dist/js/splide.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/clappr@latest/dist/clappr.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/clappr/clappr-level-selector-plugin@latest/dist/level-selector.min.js"></script>
    <script src="https://ssl.p.jwpcdn.com/player/v/8.22.0/jwplayer.js"></script>
    <style>
        /* CSS KODLARI BURADA */
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
        .slider-slide {{ background: #15161a; box-sizing: border-box; }}  
        .slidefilmpanel {{ transition: .35s; box-sizing: border-box; background: #15161a; overflow: hidden; }}
        .slidefilmpanel:hover {{ background-color: #572aa7; }}
        .slidefilmpanel:hover .filmresim img {{ transform: scale(1.2); }}
        .slider {{ position: relative; padding-bottom: 0px; width: 100%; overflow: hidden; --tw-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25); --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color); box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow); }}
        .slider-container {{ display: flex; width: 100%; scroll-snap-type: x var(--tw-scroll-snap-strictness); --tw-scroll-snap-strictness: mandatory; align-items: center; overflow: auto; scroll-behavior: smooth; }}
        .slider-container .slider-slide {{ aspect-ratio: 9/13.5; display: flex; flex-shrink: 0; flex-basis: 14.14%; scroll-snap-align: start; flex-wrap: nowrap; align-items: center; justify-content: center; }}
        .slider-container::-webkit-scrollbar {{ width: 0px; }}
        .clear {{ clear: both; }}
        .hataekran i {{ color: #572aa7; font-size: 80px; text-align: center; width: 100%; }}
        .hataekran {{ width: 80%; margin: 20px auto; color: #fff; background: #15161a; border: 1px solid #323442; padding: 10px; box-sizing: border-box; border-radius: 10px; }}
        .hatayazi {{ color: #fff; font-size: 15px; text-align: center; width: 100%; margin: 20px 0px; }}
        .filmpaneldis {{ background: #15161a; width: 100%; margin: 20px auto; overflow: hidden; padding: 10px 5px; box-sizing: border-box; }}
        .aramafilmpaneldis {{ background: #15161a; width: 100%; margin: 20px auto; overflow: hidden; padding: 10px 5px; box-sizing: border-box; }}
        .sliderfilmimdb {{ width: 20px; height: 20px; background-color: #572aa7; padding: 5px; text-align: center; border-radius: 50%; position: absolute; display: block; color: #fff; box-shadow: 1px 5px 10px rgba(0,0,0,0.8); margin: 5px; }}
        .bos {{ width: 100%; height: 60px; background: #572aa7; }}
        .baslik {{ width: 96%; color: #fff; padding: 15px 10px; box-sizing: border-box; }}
        .filmpanel {{ width: 12%; height: 200px; background: #15161a; float: left; margin: 1.14%; color: #fff; border-radius: 15px; box-sizing: border-box; box-shadow: 1px 5px 10px rgba(0,0,0,0.1); border: 1px solid #323442; padding: 0px; overflow: hidden; transition: border 0.3s ease, box-shadow 0.3s ease; }}
        .filmisimpanel {{ width: 100%; height: 200px; position: relative; margin-top: -200px; background: linear-gradient(to bottom, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 1) 100%); }}
        .filmpanel:hover {{ color: #fff; border: 3px solid #572aa7; box-shadow: 0 0 10px rgba(87, 42, 167, 0.5); }}
        .filmpanel:focus {{ outline: none; border: 3px solid #572aa7; box-shadow: 0 0 10px rgba(87, 42, 167, 0.5); }}
        .filmresim {{ width: 100%; height: 100%; margin-bottom: 0px; overflow: hidden; position: relative; }}
        .filmresim img {{ width: 100%; height: 100%; transition: transform 0.4s ease; }}
        .filmpanel:hover .filmresim img {{ transform: scale(1.1); }}
        .filmpanel:focus .filmresim img {{ transform: none; }}
        .filmisim {{ width: 100%; font-size: 14px; text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0px 5px; box-sizing: border-box; color: #fff; position: absolute; bottom: 25px; }}
        .filmimdb {{ width: 20px; height: 20px; background-color: #572aa7; padding: 5px; text-align: center; border-radius: 50%; position: absolute; display: block; color: #fff; top: 0; box-shadow: 1px 5px 10px rgba(0,0,0,0.8); margin: 10px; }}
        .resimust {{ height: 25px; width: 100%; position: absolute; bottom: 0px; overflow: hidden; box-sizing: border-box; padding: 0px 5px; }}
        .filmyil {{ width: 30%; font-size: 13px; font-weight: 500; color: #ccc; float: right; text-align: right; }}
        .filmdil {{ transition: .35s; width: 70%; float: left; box-sizing: border-box; padding: 0px; font-size: 13px; color: #ccc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .aramapanel {{ width: 100%; height: 60px; background: #15161a; border-bottom: 1px solid #323442; margin: 0px auto; padding: 10px; box-sizing: border-box; overflow: hidden; z-index: 11111; }}
        .aramapanelsag {{ width: auto; height: 40px; box-sizing: border-box; overflow: hidden; float: right; }}
        .aramapanelsol {{ width: 50%; height: 40px; box-sizing: border-box; overflow: hidden; float: left; }}
        .aramapanelyazi {{ height: 40px; width: 120px; border: 1px solid #ccc; box-sizing: border-box; padding: 0px 10px; background: ; color: #000; margin: 0px 5px; }}
        .aramapanelbuton {{ height: 40px; width: 40px; text-align: center; background-color: #572aa7; border: none; color: #fff; box-sizing: border-box; overflow: hidden; float: right; transition: .35s; }}
        .aramapanelbuton:hover {{ background-color: #fff; color: #000; }}
        .logo {{ width: 40px; height: 40px; float: left; }}
        .logo img {{ width: 100%; }}
        .logoisim {{ font-size: 15px; width: 70%; height: 40px; line-height: 40px; font-weight: 500; color: #fff; }}
        #dahafazla {{ background: #572aa7; color: #fff; padding: 10px; margin: 20px auto; width: 200px; text-align: center; transition: .35s; }}
        #dahafazla:hover {{ background: #fff; color: #000; }}
        .hidden {{ display: none; }}
        .bolum-container {{ background: #15161a; padding: 10px; margin-top: 10px; border-radius: 5px; }}
        .geri-btn {{ background: #572aa7; color: white; padding: 10px; text-align: center; border-radius: 5px; cursor: pointer; margin-top: 10px; margin-bottom: 10px; display: none; width: 100px; }}
        .geri-btn:hover {{ background: #6b3ec7; transition: background 0.3s; }}
        /* Player Panel Styles */
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
        #main-player {{
            width: 100%;
            height: 100%;
            background: #000;
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
            align-self: flex-start;
        }}
        .player-geri-btn:hover {{
            background: #6b3ec7;
            transition: background 0.3s;
        }}
        @media(max-width:900px) {{ .filmpanel {{ width: 17%; height: 220px; margin: 1.5%; }} .slider-container .slider-slide {{ flex-basis: 20%; }} }}
        @media(max-width:550px) {{ 
            .filmisimpanel {{ height: 190px; margin-top: -190px; }} 
            .filmpanel {{ width: 31.33%; height: 190px; margin: 1%; }} 
            .filmsayfaresim {{ width: 48%; float: left; }} 
            .filmsayfapanel {{ background: #15161a; color: #fff; width: 90%; height: auto; }} 
            .filmbasliklarsag {{ float: left; width: 100%; margin-top: 20px; margin-left: 0px; }} 
            .ozetpanel {{ float: left; width: 48%; height: 230px; }} 
            .slider-container .slider-slide {{ flex-basis: 33.33%; }} 
            .playerpanel {{ height: 100vh; }}
            #main-player {{ height: calc(100% - 60px); }}
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

    <div class="filmpaneldis" id="anaDiziler">
        <div class="baslik">YERLİ DİZİLER VOD BÖLÜM (Show TV)</div>
        
        {dizi_paneller_html}

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
        // JW Player anahtarı
        jwplayer.key = "cLGMn8T20tGvW+0eXPhq4NNmLB57TrscPjd1IyJF84o=";

        // PYTHON TARAFINDAN ÇEKİLEN VE DÜZENLENEN VERİ BURAYA EKLENİR
        var diziler = JSON.parse('{js_diziler_data}'); 

        // Mevcut ekranı takip etmek için bir değişken
        let currentScreen = 'anaSayfa';
        let playerInstance = null; // Clappr için
        let jwPlayerInstance = null; // JW Player için

        function showBolumler(diziID) {{
            // Daha önce açılmış bir player varsa kapat
            if (jwPlayerInstance) {{ jwPlayerInstance.remove(); jwPlayerInstance = null; }}
            if (playerInstance) {{ playerInstance.destroy(); playerInstance = null; }}
            document.getElementById("playerpanel").style.display = "none";

            sessionStorage.setItem('currentDiziID', diziID);
            var listContainer = document.getElementById("bolumListesi");
            listContainer.innerHTML = "";
            
            if (diziler[diziID]) {{
                var diziData = diziler[diziID];
                
                diziData.bolumler.forEach(function(bolum) {{
                    var item = document.createElement("div");
                    item.className = "filmpanel";
                    item.innerHTML = `
                        <div class="filmresim"><img src="${{diziData.resim}}"></div>
                        <div class="filmisimpanel">
                            <div class="filmimdb">${{diziData.imdb}}</div>
                            <div class="filmisim">${{bolum.ad}}</div>
                            <div class="resimust">
                                <div class="filmdil">${{diziData.dil}}</div>
                                <div class="filmyil">${{diziData.yil}}</div>
                            </div>
                        </div>
                    `;
                    item.onclick = function() {{
                        showPlayer(bolum.link, diziID, bolum.ad);
                    }};
                    listContainer.appendChild(item);
                }});
            }} else {{
                listContainer.innerHTML = `<div class="hataekran"><i class="fas fa-exclamation-triangle"></i><div class="hatayazi">Bu dizi için bölüm bulunamadı veya veri çekilemedi.</div></div>`;
            }}
            
            document.getElementById("anaDiziler").classList.add("hidden"); 
            document.getElementById("bolumler").classList.remove("hidden");
            document.getElementById("geriBtn").style.display = "block";

            currentScreen = 'bolumler';
            // URL hash'i güncelle
            history.pushState({{ page: 'bolumler', diziID: diziID }}, '', `#bolumler-${{diziID}}`);
        }}

        function showPlayer(streamUrl, diziID, bolumAd) {{
            document.getElementById("playerpanel").style.display = "flex";
            document.getElementById("bolumler").classList.add("hidden");

            currentScreen = 'player';
            // URL hash'i player durumuna güncelle
            history.pushState({{ page: 'player', diziID: diziID, streamUrl: streamUrl }}, '', `#player-${{diziID}}`);

            // Varolan player'ları temizle
            if (playerInstance) {{
                playerInstance.destroy();
                playerInstance = null;
            }}
            if (jwPlayerInstance) {{
                jwPlayerInstance.remove();
                jwPlayerInstance = null;
            }}

            document.getElementById("main-player").innerHTML = "";

            var diziData = diziler[diziID];
            var playerType = diziData.player;

            if (playerType === "1") {{
                // Clappr Player
                playerInstance = new Clappr.Player({{
                    source: streamUrl,
                    parentId: "#main-player",
                    autoPlay: true,
                    height: "100%",
                    width: "100%",
                    plugins: [LevelSelector],
                    mediacontrol: {{ buttons: "#00c3ff", seekbar: "#00c3ff" }},
                    playbackNotSupportedMessage: "Bu yayın desteklenmiyor",
                    hlsjsConfig: {{
                        enableWorker: true,
                        liveSyncDuration: 30
                    }}
                }});
            }} else if (playerType === "2") {{
                // JW Player
                document.getElementById("main-player").innerHTML = '<div id="jw-player"></div>';
                jwPlayerInstance = jwplayer("jw-player").setup({{
                    file: streamUrl,
                    title: bolumAd,
                    image: diziData.resim,
                    width: "100%",
                    height: "100%",
                    primary: "html5",
                    autostart: true,
                    playbackRateControls: [0.5, 1, 1.5, 2]
                }});
            }}
        }}

        function geriPlayer() {{
            document.getElementById("playerpanel").style.display = "none";
            document.getElementById("bolumler").classList.remove("hidden");

            // Player'ı temizle
            if (playerInstance) {{
                playerInstance.destroy();
                playerInstance = null;
            }}
            if (jwPlayerInstance) {{
                jwPlayerInstance.remove();
                jwPlayerInstance = null;
            }}

            currentScreen = 'bolumler';
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            // Geri dönünce URL hash'i bölüm listesine geri al
            history.pushState({{ page: 'bolumler', diziID: currentDiziID }}, '', `#bolumler-${{currentDiziID}}`);
        }}

        function geriDon() {{
            sessionStorage.removeItem('currentDiziID');
            document.getElementById("anaDiziler").classList.remove("hidden"); 
            document.getElementById("bolumler").classList.add("hidden");
            document.getElementById("geriBtn").style.display = "none";
            document.getElementById("playerpanel").style.display = "none";

            // Player'ı temizle
            if (jwPlayerInstance) {{
                jwPlayerInstance.remove();
                jwPlayerInstance = null;
            }}
            if (playerInstance) {{
                playerInstance.destroy();
                playerInstance = null;
            }}
            
            currentScreen = 'anaSayfa';
            history.pushState({{ page: 'anaSayfa' }}, '', '#anaSayfa');
        }}

        window.addEventListener('popstate', function(event) {{
            const hash = window.location.hash;
            const diziMatch = hash.match(/^#bolumler-(.*)$/);
            const playerMatch = hash.match(/^#player-(.*)$/);
            
            if (playerMatch) {{
                // Tarayıcı Geri/İleri butonu ile player'a gidilirse
                // Bu durumda sadece player'ı kapatıp bölüm listesine dönülmeli
                geriPlayer(); 
            }} else if (diziMatch) {{
                // Tarayıcı Geri/İleri butonu ile bölüm listesine gidilirse
                const diziID = diziMatch[1];
                if (diziler[diziID]) {{
                    showBolumler(diziID);
                }} else {{
                     geriDon();
                }}
            }} else {{
                // Ana sayfaya dönülürse
                geriDon();
            }}
        }});


        function checkInitialState() {{
            const hash = window.location.hash;
            const diziMatch = hash.match(/^#bolumler-(.*)$/);
            
            if (diziMatch) {{
                const diziID = diziMatch[1];
                if (diziler[diziID]) {{
                    showBolumler(diziID);
                }} else {{
                    geriDon();
                }}
            }} else {{
                document.getElementById("anaDiziler").classList.remove("hidden");
                document.getElementById("bolumler").classList.add("hidden");
                document.getElementById("playerpanel").style.display = "none";
                document.getElementById("geriBtn").style.display = "none";
                currentScreen = 'anaSayfa';
                // Başlangıç durumunda URL'yi temizle
                history.replaceState({{ page: 'anaSayfa' }}, '', '#anaSayfa');
            }}
        }}

        document.addEventListener('DOMContentLoaded', checkInitialState);


        function searchSeries() {{
            var query = document.getElementById('seriesSearch').value.toLowerCase();
            var mainSeriesPanels = document.getElementById('anaDiziler').querySelectorAll('.filmpanel');

            mainSeriesPanels.forEach(function(serie) {{
                var title = serie.querySelector('.filmisim').textContent.toLowerCase();
                
                if (query.length > 0) {{
                    // Dizi adını normalize etmeden arama yap
                    if (title.includes(query)) {{
                        serie.style.display = "block";
                    }} else {{
                        serie.style.display = "none";
                    }}
                }} else {{
                    serie.style.display = "block";
                }}
            }});
            
            return false; 
        }}

        function resetSeriesSearch() {{
            var query = document.getElementById('seriesSearch').value;
            if (query === "") {{
                var mainSeriesPanels = document.getElementById('anaDiziler').querySelectorAll('.filmpanel');
                mainSeriesPanels.forEach(function(serie) {{
                    serie.style.display = "block";
                }});
            }}
        }}
    </script>
</body>
</html>
"""

    # HTML dosyasını kaydet
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        print(f"\n✅ BAŞARILI: Tüm veriler çekildi ve '{OUTPUT_FILE}' dosyasına kaydedildi.")
        print("Oluşturulan HTML dosyasını tarayıcınızda açarak sonucu görebilirsiniz.")

    except Exception as e:
        print(f"\n[KRİTİK HATA] HTML dosyası yazılırken bir sorun oluştu: {e}")

# Betiği Çalıştır
if __name__ == "__main__":
    # unidecode modülünün yüklü olduğundan emin olun.
    try:
        import unidecode
    except ImportError:
        print("\n❌ unidecode modülü yüklü değil. 'pip install unidecode' ile yükleyin.")
        exit()
        
    main()
