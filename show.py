import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

# --- Sabitler ---
BASE_URL = "https://www.showtv.com.tr"
DIZILER_URL = "https://www.showtv.com.tr/diziler"

# Kazınan veriyi tutacak yapı
dizi_verileri = {}

# --- Fonksiyonlar ---

def get_html_content(url):
    """Belirtilen URL'nin HTML içeriğini çeker."""
    try:
        # User-Agent ekleyerek bazı sunucu engellemelerini aşmayı deneyebiliriz.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # HTTP hatalarını yakala
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Hata: URL çekilemedi {url}: {e}")
        return None

def extract_dizi_list(html_content):
    """Diziler sayfasından dizi adı, afiş linki ve detay linkini çeker."""
    print("1. Adım: Dizi listesi çekiliyor...")
    soup = BeautifulSoup(html_content, 'html.parser')
    diziler = []

    # Dizilerin bulunduğu ana kapsayıcıları bulma (data-name="box-type6")
    # Bu yapının bir <li> içinde olduğunu varsayıyoruz (örneğinizdeki gibi)
    dizi_panelleri = soup.select('li div[data-name="box-type6"]')

    if not dizi_panelleri:
        # Başka bir seçici denemesi, bazen sayfa yapısı değişebilir
        dizi_panelleri = soup.select('.dizi-list-wrapper .group') 
        # Eğer bu da işe yaramazsa, daha genel bir arama yapılabilir.
        # Biz öncelikle kullanıcının verdiği yapıya odaklanıyoruz.

    for panel in dizi_panelleri:
        # Dizi detay linki ve adı (<a title="..." href="...">)
        link_tag = panel.select_one('a.group')
        
        # Afiş resmi (<img src="..."> veya <img data-src="...">)
        img_tag = panel.select_one('img')

        if link_tag and img_tag:
            dizi_title = link_tag.get('title')
            
            # Detay linki (Tam URL yapmak için urljoin kullanıyoruz)
            dizi_detail_path = link_tag.get('href')
            dizi_detail_url = urljoin(BASE_URL, dizi_detail_path)
            
            # Afiş linki (Hem src hem de data-src kontrolü, ?v=... kısmını atıyoruz)
            img_src = img_tag.get('src') if img_tag.get('src') and 'transparent.gif' not in img_tag.get('src') else img_tag.get('data-src')
            if img_src:
                # Afiş linkindeki '?v=...' kısmını at
                img_src_cleaned = re.sub(r'\?v=\d+', '', img_src)
            else:
                img_src_cleaned = None

            if dizi_title and dizi_detail_url and img_src_cleaned:
                diziler.append({
                    'ad': dizi_title.strip(),
                    'id': re.sub(r'[^a-z0-9]', '', dizi_title.lower()), # HTML için basitleştirilmiş ID
                    'detail_url': dizi_detail_url,
                    'poster_url': img_src_cleaned
                })
    return diziler

def extract_bolum_links(dizi_detail_html):
    """Dizi detay sayfasından bölüm linklerini çeker."""
    soup = BeautifulSoup(dizi_detail_html, 'html.parser')
    bolumler = []

    # Bölüm listesinin olduğu JSON verisini içeren script etiketini bulma
    # '<script type="application/ld+json">{"@context":"http:\/\/schema.org","@type":"ItemList", ... </script>'
    # Bu etiket genelde sayfanın ilk ItemList JSON-LD verisi oluyor.
    script_tags = soup.find_all('script', {'type': 'application/ld+json'})
    
    for tag in script_tags:
        try:
            data = json.loads(tag.string)
            # ItemList tipinde ve itemListElement içeren yapıyı kontrol et
            if data.get('@type') == 'ItemList' and 'itemListElement' in data:
                for element in data['itemListElement']:
                    if element.get('@type') == 'ListItem' and 'url' in element:
                        # URL'yi temizle ve tam URL yap
                        bolum_path = element['url'].replace('\\/', '/')
                        bolum_url = urljoin(BASE_URL, bolum_path)
                        # Bölüm adını URL'den çekmeye çalış (ör: /.../ruya-gibi-sezon-1-bolum-2-izle/...)
                        match = re.search(r'/(.*?)-sezon-(\d+)-bolum-(\d+)-izle/', bolum_path)
                        if match:
                            bolum_ad = f"S{match.group(2)} B{match.group(3)} - {match.group(1).replace('-', ' ').title()}"
                        else:
                            bolum_ad = f"Bölüm {element.get('position', len(bolumler) + 1)}" # Bir ad bulunamazsa yedek

                        bolumler.append({
                            'ad': bolum_ad,
                            'url': bolum_url
                        })
                # İlk bulunan geçerli ItemList'i kullan ve döngüyü sonlandır
                return bolumler[::-1] # Bölüm listesini genelde tersten alırız (eskiden yeniye)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"Bölüm linkleri JSON ayrıştırma hatası: {e}")
            continue

    return bolumler

def extract_m3u8_link(bolum_html):
    """Bölüm sayfasından m3u8 stream linkini çeker."""
    soup = BeautifulSoup(bolum_html, 'html.parser')
    
    # m3u8 linki genellikle data-hope-video özniteliği içinde JSON formatında bulunur
    video_tag = soup.find(lambda tag: tag.has_attr('data-hope-video'))

    if video_tag:
        try:
            # data-hope-video içindeki JSON verisini çek
            data_hope_video_str = video_tag['data-hope-video']
            # data-hope-video içindeki tek tırnakları çift tırnağa çevir (geçerli JSON için)
            # JSON içinde kaçan çift tırnaklar (\") sorun yaratabilir, bu yüzden dikkatli olmalıyız
            data_hope_video_str = data_hope_video_str.replace("'", '"')
            data = json.loads(data_hope_video_str)

            # JSON yapısı: media -> m3u8 -> src
            m3u8_list = data.get('media', {}).get('m3u8', [])
            if m3u8_list:
                # İlk m3u8 linkini al
                m3u8_path = m3u8_list[0].get('src')
                if m3u8_path:
                    # m3u8 path'i bazen /ht ile başlar, tam URL yapısını sağlamak gerekiyor
                    # Örneğin: //vmcdn.ciner.com.tr/ht/2025/12/02/128FF40E56A11F01031840CDCFCAEB4F.m3u8
                    # Bazen de tam link gelir.
                    
                    # Eğer // ile başlıyorsa, http: ekle
                    if m3u8_path.startswith('//'):
                        return "https:" + m3u8_path
                    
                    # Eğer /ht/ veya tam link değilse, ana domaini ekle
                    # Not: Örnekte //vmcdn.ciner.com.tr/ht... yapısı var.
                    # Eğer sadece /ht/... gelirse, tam URL'yi bulmak zorlaşır.
                    # Ancak örnek çıktıdaki gibi tam pathi döndüreceğiz.
                    
                    # Kullanıcının örneğine göre tam URL'yi yeniden oluşturma
                    # 'https:\/\/vmcdn.ciner.com.tr\/ht\/2025\/12\/02\/128FF40E56A11F01031840CDCFCAEB4F.m3u8'
                    # Bu genellikle '/' ile başlar ve tam domain gerekebilir.
                    # Path'i temizleyip birleştiriyoruz.
                    m3u8_path_cleaned = m3u8_path.replace('\\/', '/')
                    if m3u8_path_cleaned.startswith('/'):
                        # m3u8 linki genellikle farklı bir sub-domainden gelir (vmcdn.ciner.com.tr)
                        # Burada sabit bir yapıya göre döndürelim:
                        # https://vmcdn.ciner.com.tr/ht/2025/12/02/128FF40E56A11F01031840CDCFCAEB4F.m3u8
                        # Ancak bunu dinamik olarak çekmek daha iyi.
                        
                        # Eğer path tam domain içermiyorsa, örnekteki domaini kullanalım:
                        # 'https://vmcdn.ciner.com.tr' baz alınarak daha güvenli birleşim
                        
                        # JSON'dan gelen src genellikle tam path içeriyor:
                        return m3u8_path_cleaned
                    
                    return m3u8_path_cleaned

        except json.JSONDecodeError as e:
            print(f"data-hope-video JSON ayrıştırma hatası: {e}")
        except Exception as e:
            print(f"data-hope-video genel hata: {e}")
            
    # Alternatif olarak <source src="..."> etiketi de aranabilir (daha az olası)
    source_tag = soup.select_one('source[type="application/x-mpegURL"]')
    if source_tag and source_tag.get('src'):
        return source_tag.get('src')
        
    return None

def main_scraper():
    """Ana kazıma işlemini yürütür."""
    # 1. Dizi listesini çek
    diziler_html = get_html_content(DIZILER_URL)
    if not diziler_html:
        print("Dizi listesi çekilemedi, program sonlanıyor.")
        return

    dizi_listesi = extract_dizi_list(diziler_html)
    if not dizi_listesi:
        print("Dizi bulunamadı, program sonlanıyor.")
        return
        
    print(f"Toplam {len(dizi_listesi)} dizi bulundu.")

    # 2. Her dizi için bölüm linklerini ve m3u8'leri çek
    for i, dizi in enumerate(dizi_listesi):
        dizi_ad = dizi['ad']
        dizi_id = dizi['id']
        print(f"\n--- {i+1}/{len(dizi_listesi)}: '{dizi_ad}' dizisi işleniyor... ---")
        
        # Dizi detay sayfasını çek
        dizi_detail_html = get_html_content(dizi['detail_url'])
        if not dizi_detail_html:
            print(f"'{dizi_ad}' detay sayfası çekilemedi, atlanıyor.")
            continue
            
        # Bölüm linklerini çek
        bolumler = extract_bolum_links(dizi_detail_html)
        print(f"  -> {len(bolumler)} bölüm linki bulundu.")
        
        # Dizi verisini hazırla
        dizi_verileri[dizi_id] = {
            'resim': dizi['poster_url'],
            'bolumler': []
        }
        
        # Her bölüm için m3u8 linkini çek
        for j, bolum in enumerate(bolumler):
            # 3. Bölüm sayfasını çek
            bolum_url = bolum['url']
            print(f"    -> {j+1}/{len(bolumler)}: Bölüm HTML'i çekiliyor: {bolum_url}")
            bolum_html = get_html_content(bolum_url)
            
            if bolum_html:
                # 4. m3u8 linkini çek
                m3u8_link = extract_m3u8_link(bolum_html)
                
                if m3u8_link:
                    print(f"      -> m3u8 linki bulundu: {m3u8_link}")
                    dizi_verileri[dizi_id]['bolumler'].append({
                        'ad': bolum['ad'],
                        'link': m3u8_link
                    })
                else:
                    print(f"      -> UYARI: '{bolum['ad']}' için m3u8 linki bulunamadı, atlanıyor.")
            else:
                print(f"      -> HATA: '{bolum['ad']}' bölüm HTML'i çekilemedi, atlanıyor.")

    print("\n--- Kazıma Tamamlandı ---")

# --- HTML Oluşturma Fonksiyonu ---

def generate_output_html(dizi_data, template_html_path="template.html", output_file="show.html"):
    """Kazınan veriyi HTML şablonuna gömer ve çıktı dosyasını oluşturur."""
    print(f"\n5. Adım: HTML şablonu güncelleniyor ve '{output_file}' oluşturuluyor...")
    
    # 1. Şablon HTML'i oku
    try:
        with open(template_html_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        # Kullanıcının sağladığı HTML'i bir değişkene kopyalamak daha güvenlidir
        # Şablon HTML'i, kodun altındaki bir değişkende tutulduğunu varsayıyoruz
        template_content = HTML_TEMPLATE

    # 2. Python'dan gelen veriyi (dizi_data) JavaScript formatına çevir
    diziler_js_data = json.dumps(dizi_data, indent=1, ensure_ascii=False)
    
    # 3. JS verisini şablonun içine göm (diziler objesi yerine)
    # Şablonda varolan örnek diziler objesinin yerini bulup değiştiriyoruz
    # 'var diziler = {' ile başlayan bloğu arayacağız
    
    # Regex ile diziler objesini bul ve değiştir
    # 'diziler' objesi başlangıcı: var diziler = {
    # 'diziler' objesi bitişi: };
    
    # Not: Regex kullanmak risklidir. En iyisi placeholder kullanmaktır.
    # Şablonda bir placeholder (`// DIZILER_VERISI_BURAYA`) olduğunu varsayalım.
    # Şablonu değiştiremeyeceğimiz için, mevcut `var diziler = { ... };` bloğunu değiştireceğiz.
    
    pattern = re.compile(r'var diziler = \{.*?\}', re.DOTALL)
    
    # Yeni JS bloğu
    new_js_block = f"var diziler = {diziler_js_data};"

    # Şablonu güncelle (Eğer şablonda varsa değiştir, yoksa sadece ekle)
    updated_content = pattern.sub(new_js_block, template_content, count=1)

    # 4. Ana sayfadaki dizi panellerini oluştur
    dizi_panelleri_html = ""
    for dizi_id, data in dizi_data.items():
        dizi_ad = data.get('ad', dizi_id.replace('-', ' ').title()) # 'ad' anahtarını data yapısına eklemedik, ID'den türetelim
        dizi_panelleri_html += f"""
        <div class="filmpanel" onclick="showBolumler('{dizi_id}')">
            <div class="filmresim"><img src="{data['resim']}"></div>
            <div class="filmisimpanel">
                <div class="filmisim">{dizi_id.replace('-', ' ').title()}</div>
            </div>
        </div>
        """
        
    # Şablonda varolan örnek dizi panellerini bul ve değiştir
    # <div class="filmpanel" onclick="showBolumler('ruyagibi')">...</div>
    # <div class="filmpanel" onclick="showBolumler('veliaht')">...</div>
    
    # Bu kısmı bulmak için örnekteki iki div'i içeren en dıştaki .filmpaneldis div'i içinde arama yapacağız.
    
    # '</div><div class="filmpanel" onclick="showBolumler('ruyagibi')">'
    # pattern_panel = re.compile(r'<div class="filmpanel" onclick="showBolumler\(\'ruyagibi\'\)">.*?veliaht\'\)">.*?</div>\s*', re.DOTALL | re.MULTILINE)
    
    # En güvenli yol, mevcut HTML'deki örnek panelleri içeren bloğu bulmaktır:
    start_anchor = '<div class="filmpaneldis">'
    end_anchor = '</div>' # Bu div'in bitişi
    
    if start_anchor in updated_content:
        # Başlangıç ve bitiş noktalarını bul
        start_index = updated_content.find(start_anchor)
        
        # Baslik div'i sonrası tüm panelleri bulmaya çalışalım
        baslik_anchor = '<div class="baslik">YERLİ DİZİLER VOD BÖLÜM</div>'
        baslik_index = updated_content.find(baslik_anchor)
        
        if baslik_index != -1:
            # İlk örnek panelin başlangıcını bul
            filmpanel_start = updated_content.find('<div class="filmpanel"', baslik_index)
            if filmpanel_start != -1:
                # İkinci örnek panelin bitişini bul
                veliaht_end = updated_content.find('</div>\n        \n    </div>', filmpanel_start)
                
                if veliaht_end != -1:
                    # Yeni panelleri bu aralığa ekle
                    # '</div>' kısmı, yani .filmpaneldis bitişinin hemen öncesine
                    end_of_panels = veliaht_end + len('</div>\n        \n    ')
                    
                    # Baslik div'i ile ilk panel arasına yeni içeriği yerleştir
                    # Yani varolan panelleri komple silip yenisini koy
                    
                    # Varolan paneller:
                    # <div class="filmpanel" onclick="showBolumler('ruyagibi')">...</div>
                    # <div class="filmpanel" onclick="showBolumler('veliaht')">...</div>
                    
                    # Daha basit bir yol: Sadece varolan panelleri temizleyip, hemen <div class="baslik"> altına ekle:
                    
                    # Regex ile sadece dizi panellerini bulup değiştireceğiz
                    # <div class="filmpaneldis">... <div class="baslik">...</div> **burası** <div class="filmpanel"...
                    
                    # Sadece ruyagibi ve veliaht panellerini silip yerini alıyoruz
                    updated_content = updated_content.replace("""
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
        """, dizi_panelleri_html) # Yeni HTML panellerini buraya koy

    # 5. Dosyayı kaydet
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Başarılı: '{output_file}' dosyası oluşturuldu ve veri başarıyla gömüldü.")
    except IOError as e:
        print(f"Hata: Dosya yazma hatası: {e}")

# --- HTML Şablonu (Kullanıcının sağladığı tam şablon) ---

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
    main_scraper()
    
    # Not: Dizi verileri kazındıktan sonra, HTML şablonu güncellenir.
    # Burada, kazıma işlemi bittikten sonra `dizi_verileri` değişkeni dolu olacaktır.
    
    if dizi_verileri:
        # Dizi ID'lerine, adlarını da ekleyelim (HTML panelini oluşturmak için)
        for dizi_id, data in dizi_verileri.items():
            # İlk başta dizi listesinden gelen adı bulup eklememiz lazım.
            # Şimdilik ID'den title'ı türetiyoruz (daha güvenli olurdu).
            pass
            
        # Dizi listesindeki adı bulup dizi_verileri'ne ekleyelim (daha doğru olması için)
        diziler_html_for_ad = get_html_content(DIZILER_URL)
        if diziler_html_for_ad:
             dizi_listesi_ad = extract_dizi_list(diziler_html_for_ad)
             for dizi in dizi_listesi_ad:
                 if dizi['id'] in dizi_verileri:
                     dizi_verileri[dizi['id']]['ad'] = dizi['ad']
        
        # HTML dosyasını oluştur
        generate_output_html(dizi_verileri, output_file="show.html")
    else:
        print("Kazınan veri boş olduğu için HTML dosyası oluşturulamadı.")
