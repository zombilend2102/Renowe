import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
from unidecode import unidecode 

# --- Sabitler ---
BASE_URL = "https://www.showtv.com.tr"
DIZILER_URL = "https://www.showtv.com.tr/diziler"

# Kazınan veriyi tutacak yapı
dizi_verileri = {}

# --- Yardımcı Fonksiyonlar ---

def slugify_turkish(text):
    """Türkçe karakterleri Latin alfabesine dönüştürerek URL dostu bir slug/ID oluşturur."""
    if not text:
        return ""
    text = unidecode(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text).replace(' ', '-')
    return re.sub(r'-+', '-', text).strip('-')

def get_html_content(url):
    """Belirtilen URL'nin HTML içeriğini çeker."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        # Yüksek zaman aşımı ve hata kontrolü
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() 
        return response.text
    except requests.exceptions.RequestException as e:
        # print(f"Hata: URL çekilemedi {url}: {e}") # Çok fazla loglamamak için devre dışı
        return None

# --- Ana Kazıma Fonksiyonları ---

def extract_dizi_list(html_content):
    """Diziler sayfasından dizi adı, afiş linki ve detay linkini çeker."""
    print("1. Adım: Dizi listesi çekiliyor...")
    soup = BeautifulSoup(html_content, 'html.parser')
    diziler = []

    # Tüm dizi listelerini kapsayan ana etiketleri arama
    dizi_panelleri = soup.select('li div[data-name="box-type6"]')
    
    # Yedek arama (eğer site yapısı değişirse)
    if not dizi_panelleri:
        dizi_panelleri = soup.select('ul.w-full > li') 

    for panel in dizi_panelleri:
        link_tag = panel.select_one('a.group')
        img_tag = panel.select_one('img')

        if link_tag and img_tag:
            dizi_title = link_tag.get('title')
            dizi_detail_path = link_tag.get('href')
            dizi_detail_url = urljoin(BASE_URL, dizi_detail_path)
            
            # Afiş linkini çekme (src veya data-src kontrolü ve temizleme)
            img_src = img_tag.get('data-src') or img_tag.get('src')
            if img_src and 'transparent.gif' not in img_src:
                img_src_cleaned = re.sub(r'\?v=\d+', '', img_src)
            else:
                img_src_cleaned = None

            if dizi_title and dizi_detail_url and img_src_cleaned:
                diziler.append({
                    'ad': dizi_title.strip(), 
                    # --- DÜZELTME 1: slugify ile benzersiz, temiz ID ---
                    'id': slugify_turkish(dizi_title.strip()), 
                    'detail_url': dizi_detail_url,
                    'poster_url': img_src_cleaned
                })
    return diziler

def extract_bolum_links(dizi_detail_html):
    """Dizi detay sayfasından bölüm linklerini çeker ve temiz adlar oluşturur."""
    soup = BeautifulSoup(dizi_detail_html, 'html.parser')
    all_bolumler = []

    # Tüm JSON-LD script etiketlerini al
    script_tags = soup.find_all('script', {'type': 'application/ld+json'})
    
    for tag in script_tags:
        try:
            data = json.loads(tag.string)
            
            # 'ItemList' tipindeki JSON bloğunu buluyoruz
            if data.get('@type') == 'ItemList' and 'itemListElement' in data:
                
                # Bu blokta birden fazla sezonun tüm bölümleri listelenmiş olabilir.
                for element in data['itemListElement']:
                    if element.get('@type') == 'ListItem' and 'url' in element:
                        bolum_path = element['url'].replace('\\/', '/')
                        bolum_url = urljoin(BASE_URL, bolum_path)
                        
                        # --- DÜZELTME 2 & 3: Temiz Bölüm Adı Çıkarma ---
                        # Link yapısı: /dizi/tum_bolumler/dizi-adi-sezon-X-bolum-Y-izle/ID
                        match = re.search(r'sezon-(\d+)-bolum-(\d+)-izle', bolum_path, re.IGNORECASE)
                        
                        if match:
                            sezon = match.group(1)
                            bolum_num = match.group(2)
                            bolum_ad = f"S{sezon} B{bolum_num}"
                        else:
                            # Eğer Sezon/Bölüm bilgisi bulunamazsa, pozisyon bilgisini kullan
                            position = element.get('position', len(all_bolumler) + 1)
                            bolum_ad = f"Bölüm {position}" 

                        all_bolumler.append({
                            'ad': bolum_ad, 
                            'url': bolum_url
                        })
                        
                # Bir 'ItemList' bloğu bulduğumuzda, genellikle o dizinin tüm bölümlerini içerir.
                # En yeni bölümün en başta olması için listeyi ters çeviriyoruz.
                return all_bolumler[::-1]
                
        except json.JSONDecodeError:
            continue
        except Exception:
            continue

    return all_bolumler # Boş liste dönerse, sorun yok demektir.

# ... extract_m3u8_link ve main_scraper aynı kalır ...

def extract_m3u8_link(bolum_html):
    """Bölüm sayfasından m3u8 stream linkini çeker."""
    soup = BeautifulSoup(bolum_html, 'html.parser')
    video_tag = soup.find(lambda tag: tag.has_attr('data-hope-video'))

    if video_tag:
        try:
            data_hope_video_str = video_tag['data-hope-video']
            data_hope_video_str = data_hope_video_str.replace("'", '"')
            data = json.loads(data_hope_video_str)

            m3u8_list = data.get('media', {}).get('m3u8', [])
            if m3u8_list:
                m3u8_path = m3u8_list[0].get('src')
                if m3u8_path:
                    m3u8_path_cleaned = m3u8_path.replace('\\/', '/')
                    if m3u8_path_cleaned.startswith('//'):
                        return "https:" + m3u8_path_cleaned
                    return m3u8_path_cleaned
        except Exception:
            pass
            
    return None

def main_scraper():
    """Ana kazıma işlemini yürütür."""
    global dizi_verileri
    dizi_verileri = {}
    
    diziler_html = get_html_content(DIZILER_URL)
    if not diziler_html:
        return

    dizi_listesi = extract_dizi_list(diziler_html)
    if not dizi_listesi:
        return
        
    print(f"Toplam {len(dizi_listesi)} dizi bulundu.")

    for i, dizi in enumerate(dizi_listesi):
        dizi_ad = dizi['ad']
        dizi_id = dizi['id']
        print(f"\n--- {i+1}/{len(dizi_listesi)}: '{dizi_ad}' ({dizi_id}) dizisi işleniyor... ---")
        
        dizi_detail_html = get_html_content(dizi['detail_url'])
        if not dizi_detail_html:
            print(f"'{dizi_ad}' detay sayfası çekilemedi, atlanıyor.")
            continue
            
        # Düzeltilmiş Bölüm Çıkarma fonksiyonu çağrısı
        bolumler = extract_bolum_links(dizi_detail_html)
        print(f"  -> {len(bolumler)} bölüm linki bulundu.")
        
        dizi_verileri[dizi_id] = {
            'ad': dizi_ad, 
            'resim': dizi['poster_url'],
            'bolumler': []
        }
        
        for j, bolum in enumerate(bolumler):
            bolum_url = bolum['url']
            
            if j < 3: 
                print(f"    -> {j+1}/{len(bolumler)}: Bölüm HTML'i çekiliyor: {bolum_url}")
            elif j == 3:
                 print(f"    -> ... kalan {len(bolumler) - 3} bölüm taranıyor ...")

            bolum_html = get_html_content(bolum_url)
            
            if bolum_html:
                m3u8_link = extract_m3u8_link(bolum_html)
                
                if m3u8_link:
                    dizi_verileri[dizi_id]['bolumler'].append({
                        'ad': bolum['ad'],
                        'link': m3u8_link
                    })
    
    # Boş bölümlü dizileri listeden çıkaralım mı? Hayır, yine de listede dursunlar.
    
    print("\n--- Kazıma Tamamlandı ---")

def generate_output_html(dizi_data, output_file="show.html"):
    """Kazınan veriyi HTML şablonuna gömer ve çıktı dosyasını oluşturur."""
    print(f"\n5. Adım: HTML şablonu güncelleniyor ve '{output_file}' oluşturuluyor...")
    
    template_content = HTML_TEMPLATE

    # 1. JS Dizi Verisini Oluşturma ve Gömme (Kesin Yerleştirme)
    diziler_js_data = json.dumps(dizi_data, indent=1, ensure_ascii=False)
    
    js_start_marker = 'var diziler = {'
    js_end_marker = '};'
    
    start_idx = template_content.find(js_start_marker)
    # Örnek objenin bittiği yeri bul
    end_idx = template_content.find(js_end_marker, start_idx)

    # Diziler objesinin tamamını yeni veriyle değiştir
    new_js_block_content = f"var diziler = {diziler_js_data}"
    updated_content = template_content[:start_idx] + new_js_block_content + template_content[end_idx:]

    # 2. Ana Sayfa Dizi Panellerini Oluşturma (Türkçe isimlerle)
    dizi_panelleri_html = ""
    for dizi_id, data in dizi_data.items():
        dizi_ad_gorunen = data.get('ad', dizi_id.replace('-', ' ').title()) 
        
        # Sadece bölümleri olan dizileri göster
        # if data['bolumler']: 
        dizi_panelleri_html += f"""
        <div class="filmpanel" onclick="showBolumler('{dizi_id}')">
            <div class="filmresim"><img src="{data['resim']}"></div>
            <div class="filmisimpanel">
                <div class="filmisim">{dizi_ad_gorunen}</div>
            </div>
        </div>
        """
        
    # 3. HTML Panellerini Şablona Entegre Etme (Fazlalığı Temizleme Garantili)
    
    # Panellerin başlangıç ve bitiş noktalarını bulalım (orijinal şablondaki gibi)
    html_start_anchor = '<div class="baslik">YERLİ DİZİLER VOD BÖLÜM</div>'
    html_end_anchor = '</div>\n\n    <div id="bolumler" class="bolum-container hidden">'

    start_index = updated_content.find(html_start_anchor)
    end_index = updated_content.find(html_end_anchor)

    if start_index != -1 and end_index != -1:
        # Yeni içeriği oluştur: Başlangıç anchor'ı + yeni paneller + bitiş anchor'ı
        new_html_content = f'{html_start_anchor}\n\n{dizi_panelleri_html}\n    {html_end_anchor}'
        
        # Eski ve hatalı panelleri içeren bloğu, yeni temiz blokla değiştir
        # Panellerin başlangıç noktasından alıp, hemen #bolumler div'inin başlangıcına kadar değiştiriyoruz.
        
        # Panellerin başlangıcı: <div class="baslik">...</div> den sonra
        start_replace = updated_content.find(html_start_anchor) + len(html_start_anchor)
        # Panellerin bitişi: <div id="bolumler" ...> den önce
        end_replace = updated_content.find('    <div id="bolumler" class="bolum-container hidden">')

        if start_replace != -1 and end_replace != -1:
            # Sadece panel kısmını değiştir
            content_before = updated_content[:start_replace] + '\n'
            content_after = updated_content[end_replace:]
            
            # Yeni panelleri yerleştir
            new_panels = f"""{dizi_panelleri_html}
        
    """
            updated_content = content_before + new_panels + content_after
    
    # 4. Dosyayı kaydet
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Başarılı: '{output_file}' dosyası oluşturuldu ve hatalar düzeltildi.")
        print("\nŞimdi 'show.html' dosyasını tarayıcınızda açıp deneyebilirsiniz.")
    except IOError as e:
        print(f"Hata: Dosya yazma hatası: {e}")

# --- HTML Şablonu (Orijinal hali, içindeki örnek paneller temizlenecek) ---

HTML_TEMPLATE = """<!DOCTYPE html>
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
        *:not(input):not(textarea) {
            -moz-user-select: -moz-none;
            -khtml-user-select: none;
            -webkit-user-select: none;
            -o-user-select: none;
            -ms-user-select: none;
            user-select: none
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
        .slider-slide {
            background: #15161a;
            box-sizing: border-box;
        }  
        .slidefilmpanel {
            transition: .35s;
            box-sizing: border-box;
            background: #15161a;
            overflow: hidden;
        }
        .slidefilmpanel:hover {
            background-color: #572aa7;
        }
        .slidefilmpanel:hover .filmresim img {
            transform: scale(1.2);
        }
        .slider {
            position: relative;
            padding-bottom: 0px;
            width: 100%;
            overflow: hidden;
            --tw-shadow: anio0 25px 50px -12px rgb(0 0 0 / 0.25);
            --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color);
            box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
        }
        .slider-container {
            display: flex;
            width: 100%;
            scroll-snap-type: x var(--tw-scroll-snap-strictness);
            --tw-scroll-snap-strictness: mandatory;
            align-items: center;
            overflow: auto;
            scroll-behavior: smooth;
        }
        .slider-container .slider-slide {
            aspect-ratio: 9/13.5;
            display: flex;
            flex-shrink: 0;
            flex-basis: 14.14%;
            scroll-snap-align: start;
            flex-wrap: nowrap;
            align-items: center;
            justify-content: center;
        }
        .slider-container::-webkit-scrollbar {
            width: 0px;
        }
        .clear {
            clear: both;
        }
        .hataekran i {
            color: #572aa7;
            font-size: 80px;
            text-align: center;
            width: 100%;
        }
        .hataekran {
            width: 80%;
            margin: 20px auto;
            color: #fff;
            background: #15161a;
            border: 1px solid #323442;
            padding: 10px;
            box-sizing: border-box;
            border-radius: 10px;
        }
        .hatayazi {
            color: #fff;
            font-size: 15px;
            text-align: center;
            width: 100%;
            margin: 20px 0px;
        }
        .filmpaneldis {
            background: #15161a;
            width: 100%;
            margin: 20px auto;
            overflow: hidden;
            padding: 10px 5px;
            box-sizing: border-box;
        }
        .aramafilmpaneldis {
            background: #15161a;
            width: 100%;
            margin: 20px auto;
            overflow: hidden;
            padding: 10px 5px;
            box-sizing: border-box;
        }
        .sliderfilmimdb {
            display: none;
        }
        .bos {
            width: 100%;
            height: 60px;
            background: #572aa7;
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
        .filmpanel:focus {
            outline: none;
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
        .filmpanel:focus .filmresim img {
            transform: none;
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
            bottom: 5px;
        }
        .filmimdb {
            display: none;
        }
        .resimust {
            display: none;
        }
        .filmyil {
            display: none;
        }
        .filmdil {
            display: none;
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
            background: ;
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
        #dahafazla {
            background: #572aa7;
            color: #fff;
            padding: 10px;
            margin: 20px auto;
            width: 200px;
            text-align: center;
            transition: .35s;
        }
        #dahafazla:hover {
            background: #fff;
            color: #000;
        }
        .hidden { display: none; }
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
        /* Player Panel Styles - Tam Ekran Düzeltmesi */
        .playerpanel {
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
        }
        
        /* DÜZELTME: main-player artık 100% yüksekliği kullanıyor */
        #main-player {
            width: 100%;
            height: 100%; 
            background: #000;
        }
        
        /* Bradmax iframe stili */
        #bradmax-iframe {
            width: 100%;
            height: 100%;
            border: none;
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
            /* Flexbox'a göre hizalanır, ancak #main-player tam alanı kapladığı için bu düğme üstte görünecektir */
            position: absolute; /* Video alanının üstüne çıkması için mutlak konumlandırma */
            top: 10px;
            left: 10px;
            z-index: 10000;
        }
        
        @media(max-width:550px) {
            .filmpanel {
                width: 31.33%;
                height: 190px;
                margin: 1%;
            }
            /* DÜZELTME: Mobil görünümde de tam yükseklik kullanılır, böylece ekran tam kaplanır. */
            #main-player {
                height: 100%; 
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

        <div class="filmpanel" onclick="showBolumler('ruyagibi')">
            <div class="filmresim"><img src="https://mo.ciner.com.tr/showtv/iu/300x300/ruya-gibi.jpg"></div>
            <div class="filmisimpanel">
                <div class="filmisim">Rüya Gibi</div>
            </div>
        </div>

        <div class="filmpanel" onclick="showBolumler('veliaht')">
            <div class="filmresim"><img src="https://mo.ciner.com.tr/showtv/iu/300x300/veliaht.jpg"></div>
            <div class="filmisimpanel">
                <div class="filmisim">Veliaht</div>
            </div>
        </div>
        
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

        var diziler = {
            "ruyagibi": {
                "resim": "https://mo.ciner.com.tr/showtv/iu/300x300/ruya-gibi.jpg",
                "bolumler": [
                    {"ad":"1. Sezon 1. Bölüm","link":"https://vmcdn.ciner.com.tr/ht/2025/12/02/128FF40E56A11F01031840CDCFCAEB4F.m3u8"},
                    {"ad":"1. Sezon 2. Bölüm","link":"https://vmcdn.ciner.com.tr/ht/2025/12/09/3882B62ABBED735B704C81460395E859.m3u8"}
                ]
            },
            "veliaht": {
                "resim": "https://mo.ciner.com.tr/showtv/iu/300x300/veliaht.jpg",
                "bolumler": [
                    {"ad":"1. Sezon 1. Bölüm","link":"https://vmcdn.ciner.com.tr/ht/2025/09/11/C6437C080D5CFEB117D142CC82CD60CF.m3u8"},
                    {"ad":"1. Sezon 2. Bölüm","link":"https://vmcdn.ciner.com.tr/ht/2025/09/18/FAB6DADCE6659DD196BD04A1228F1109.m3u8"}
                ]
            }
        };

        let currentScreen = 'anaSayfa';

        function showBolumler(diziID) {
            sessionStorage.setItem('currentDiziID', diziID);
            var listContainer = document.getElementById("bolumListesi");
            listContainer.innerHTML = "";
            
            if (diziler[diziID]) {
                // Bölüm listesini tersten göster (yeni bölümler başta olsun)
                diziler[diziID].bolumler.slice().reverse().forEach(function(bolum) {
                    var item = document.createElement("div");
                    item.className = "filmpanel";
                    item.innerHTML = `
                        <div class="filmresim"><img src="${diziler[diziID].resim}"></div>
                        <div class="filmisimpanel">
                            <div class="filmisim">${bolum.ad}</div>
                        </div>
                    `;
                    item.onclick = function() {
                        showPlayer(bolum.link, diziID);
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
            history.replaceState({ page: 'bolumler', diziID: diziID }, '', `#bolumler-${diziID}`);
        }

        function showPlayer(streamUrl, diziID) {
            document.getElementById("playerpanel").style.display = "flex"; 
            document.getElementById("bolumler").classList.add("hidden");

            currentScreen = 'player';
            history.pushState({ page: 'player', diziID: diziID, streamUrl: streamUrl }, '', `#player-${diziID}`);

            document.getElementById("main-player").innerHTML = "";

            // URL oluşturma (Autoplay ve Tam Ekran eklenmiş)
            const fullUrl = BRADMAX_BASE_URL + encodeURIComponent(streamUrl) + BRADMAX_PARAMS;
            
            // Iframe oluşturma (Odaklanmayı sağlamak için tabindex="0" ve autofocus eklendi)
            const iframeHtml = `<iframe id="bradmax-iframe" src="${fullUrl}" allowfullscreen tabindex="0" autofocus></iframe>`;
            
            document.getElementById("main-player").innerHTML = iframeHtml;
        }

        function geriPlayer() {
            document.getElementById("playerpanel").style.display = "none";
            document.getElementById("bolumler").classList.remove("hidden");

            document.getElementById("main-player").innerHTML = "";

            currentScreen = 'bolumler';
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            history.replaceState({ page: 'bolumler', diziID: currentDiziID }, '', `#bolumler-${currentDiziID}`);
        }

        function geriDon() {
            sessionStorage.removeItem('currentDiziID');
            document.querySelector(".filmpaneldis").classList.remove("hidden");
            document.getElementById("bolumler").classList.add("hidden");
            document.getElementById("geriBtn").style.display = "none";
            
            currentScreen = 'anaSayfa';
            history.replaceState({ page: 'anaSayfa' }, '', '#anaSayfa');
        }

        window.addEventListener('popstate', function(event) {
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            
            if (event.state && event.state.page === 'player' && event.state.diziID && event.state.streamUrl) {
                showBolumler(event.state.diziID);
                showPlayer(event.state.streamUrl, event.state.diziID);
            } else if (event.state && event.state.page === 'bolumler' && event.state.diziID) {
                showBolumler(event.state.diziID);
            } else {
                sessionStorage.removeItem('currentDiziID');
                document.querySelector(".filmpaneldis").classList.remove("hidden");
                document.getElementById("bolumler").classList.add("hidden");
                document.getElementById("playerpanel").style.display = "none";
                document.getElementById("geriBtn").style.display = "none";
                currentScreen = 'anaSayfa';
                history.replaceState({ page: 'anaSayfa' }, '', '#anaSayfa');

                document.getElementById("main-player").innerHTML = "";
            }
        });

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
                history.replaceState({ page: 'anaSayfa' }, '', '#anaSayfa');
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
            if (query ===("")) {
                var series = document.querySelectorAll('.filmpanel');
                series.forEach(function(serie) {
                    serie.style.display = "block";
                });
            }
        }
    </script>
</body>
</html>"""

# --- Çalıştırma ---

if __name__ == "__main__":
    try:
        from unidecode import unidecode
        # unidecode kütüphanesi yoksa, slugify_turkish fonksiyonu hata verir.
        # Bu yüzden, eğer kütüphane kurulmamışsa, kullanıcıya uyarı vermemiz gerekir.
    except ImportError:
        print("HATA: 'unidecode' kütüphanesi kurulu değil.")
        print("Lütfen komut satırında 'pip install unidecode' çalıştırın.")
        exit()
        
    main_scraper()
    
    if dizi_verileri:
        # Son çıktı dosyasını oluştur
        generate_output_html(dizi_verileri, output_file="show.html")
    else:
        print("Kazınan veri boş olduğu için HTML dosyası oluşturulamadı.")
