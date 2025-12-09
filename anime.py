import requests
from bs4 import BeautifulSoup
import re
import json

# --- 1. Dizi Verileri (Sadece Karma 2025 ve Hükümsüz) ---
dizi_listesi = [
    {"ad": "Mirage", "logo": "https://www.themoviedb.org/t/p/w500/pKh8bJNn4bJvlNsHNmScmKeAu1R.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9taXJhZ2U="},
    {"ad": "Sorgu", "logo": "https://www.themoviedb.org/t/p/w500/otj4Mo8HS7ypBpt33MOngBHUNgB.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zb3JndQ=="},
    {"ad": "Zamanın Kapıları", "logo": "https://www.themoviedb.org/t/p/w500/lc5Auyq4F8QK6yeMCCpvdwJIIve.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS96YW1hbmluLWthcGlsYXJp"},
    {"ad": "Sarmaşık Zamanı", "logo": "https://www.themoviedb.org/t/p/w500/bs3lq3yzuuKXoDtDo22d2qRZXUR.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zYXJtYXNpay16YW1hbmk="},
    {"ad": "Var Bunlar", "logo": "https://www.themoviedb.org/t/p/w500/iWKG3UKXVSCZ0VkqjEGfTk7MD4C.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS92YXItYnVubGFy"},
    {"ad": "Fandom", "logo": "https://www.themoviedb.org/t/p/w500//bk6af4kwnnPCMa5wzWieS6vP3rv.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9mYW5kb20="},
    {"ad": "Nasıl Fenomen Oldum", "logo": "https://www.themoviedb.org/t/p/w500//1CsppyAoBANBAdgFtawDMySwMuQ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9uYXNpbC1mZW5vbWVuLW9sZHVt"},
    {"ad": "Hayaller ve Hayatlar", "logo": "https://www.themoviedb.org/t/p/w500//iebnEt6dLqmq63nkqNRyKIAGIRS.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9oYXlhbGxlci12ZS1oYXlhdGxhcg=="},
    {"ad": "Erkek Severse", "logo": "https://www.themoviedb.org/t/p/w500//bUvf4WjKHFzFfZkemo4TrTHV0Mo.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9lcmtlay1zZXZlcnNl"}
]

# Ana diziler objesi, JavaScript'te kullanılacak.
diziler_data = {}

def normalize_dizi_ad(dizi_adi):
    """Dizi adını JS anahtarı olarak kullanılabilecek, küçük harf ve boşluksuz bir ID'ye dönüştürür."""
    dizi_adi = dizi_adi.lower().replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i').replace('ö', 'o').replace('ş', 's').replace('ü', 'u').replace('?', '')
    return re.sub(r'[^a-z0-9]', '', dizi_adi)

def get_iframe_src(bolum_link):
    """Bölüm sayfasından gömülü video (iframe) URL'sini çeker."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(bolum_link, headers=headers, timeout=10)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        iframe = soup.find('iframe', id='iframe-player')
        
        if iframe and 'src' in iframe.attrs:
            return iframe['src']
        return None
            
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None

def process_dizi(dizi):
    """Bir dizinin tüm bölümlerini çeker ve iframe linklerini bulur."""
    dizi_adi = dizi["ad"]
    dizi_link = dizi["link"]
    dizi_id = normalize_dizi_ad(dizi_adi)
    bolumler = []

    try:
        print(f"\n--- {dizi_adi} Bölüm Listesi Çekiliyor ---")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(dizi_link, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        bolum_butonlari = soup.find_all('button', class_='list-group-item izle')
        
        if not bolum_butonlari:
            print(f"  [UYARI] {dizi_adi} için bölüm butonu bulunamadı.")
            return

        for i, button in enumerate(bolum_butonlari):
            p_tag = button.find('p', class_='menu70')
            bolum_ad = p_tag.text.strip().replace('\n', ' ').strip() if p_tag else f"Bölüm {i+1}"
            
            onclick_attr = button.get('onclick', '')
            match = re.search(r"location\.href='(.*?)'", onclick_attr)
            
            if match:
                watch_link = match.group(1).strip()
                iframe_link = get_iframe_src(watch_link)
                
                if iframe_link:
                    bolumler.append({
                        "ad": bolum_ad,
                        "link": iframe_link
                    })
                    print(f"  -> Eklendi: {bolum_ad}")
                else:
                    print(f"  [ATLANDI] {bolum_ad} için iframe linki ÇEKİLEMEDİ.")
        
        if bolumler:
            diziler_data[dizi_id] = {
                "ad": dizi_adi, 
                "resim": dizi["logo"],
                "dil": "Yerli",
                "bolumler": bolumler
            }
            print(f"--- {dizi_adi} için TOPLAM {len(bolumler)} bölüm başarıyla çekildi. ---")

    except requests.exceptions.RequestException as e:
        print(f"\n[KRİTİK HATA] {dizi_adi} ana sayfasını çekerken bir sorun oluştu: {e}")
    except Exception as e:
        print(f"\n[KRİTİK HATA] {dizi_adi} işlenirken beklenmedik hata: {e}")


# Tüm dizileri işle
for dizi in dizi_listesi:
    process_dizi(dizi)

# --- 2. HTML ve JavaScript Kodu Oluşturma ---

# JSON'u sıkıştır ve güvenli hale getir
js_diziler_data = json.dumps(diziler_data, indent=None, ensure_ascii=False).replace('"', '\\"').replace("'", "\\'")

# Ana sayfa üzerindeki dizileri oluşturmak için HTML dizeleri
dizi_paneller_html = ""
for id, data in diziler_data.items():
    dizi_paneller_html += f"""
    <div class="filmpanel" onclick="showBolumler('{id}')">
        <div class="filmresim"><img src="{data['resim']}"></div>
        <div class="filmisimpanel">
            <div class="filmisim">{data['ad']}</div>
            <div class="resimust">
                <div class="filmdil">{data['dil']}</div>
            </div>
        </div>
    </div>
"""

# HTML şablonu (showBolumler fonksiyonu orijinal çalışan kodun mantığına göre yeniden yazıldı)
html_template = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
<title>TITAN TV YERLI VOD</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css?family=PT+Sans:700i" rel="stylesheet">
<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
<script src="https://kit.fontawesome.com/bbe955c5ed.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@splidejs/splide@4.1.4/dist/js/splide.min.js"></script>
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
    .resimust {{ height: 25px; width: 100%; position: absolute; bottom: 0px; overflow: hidden; box-sizing: border-box; padding: 0px 5px; }}
    .filmdil {{ transition: .35s; width: 100%; float: left; box-sizing: border-box; padding: 0px; font-size: 13px; color: #ccc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; }}
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
    @media(max-width:900px) {{ .filmpanel {{ width: 17%; height: 220px; margin: 1.5%; }} .slider-container .slider-slide {{ flex-basis: 20%; }} }}
    @media(max-width:550px) {{ 
        .filmisimpanel {{ height: 190px; margin-top: -190px; }} 
        .filmpanel {{ width: 31.33%; height: 190px; margin: 1%; }} 
        .filmsayfaresim {{ width: 48%; float: left; }} 
        .filmsayfapanel {{ background: #15161a; color: #fff; width: 90%; height: auto; }} 
        .filmbasliklarsag {{ float: left; width: 100%; margin-top: 20px; margin-left: 0px; }} 
        .ozetpanel {{ float: left; width: 48%; height: 230px; }} 
        .slider-container .slider-slide {{ flex-basis: 33.33%; }} 
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
    <div class="baslik">YERLİ DİZİLER VOD BÖLÜM</div>
    
    {dizi_paneller_html}

</div>

<div id="bolumler" class="bolum-container hidden">
    <div id="geriBtn" class="geri-btn" onclick="geriDon()">Geri</div>
    <div id="bolumListesi" class="filmpaneldis"></div>
</div>

<script>
// PYTHON TARAFINDAN ÇEKİLEN VE DÜZENLENEN VERİ BURAYA EKLENİR
var diziler = JSON.parse('{js_diziler_data}'); 

// Mevcut ekranı takip etmek için bir değişken
let currentScreen = 'anaSayfa';

function showBolumler(diziID) {{
    sessionStorage.setItem('currentDiziID', diziID);
    
    var listContainer = document.getElementById("bolumListesi");
    listContainer.innerHTML = "";
    
    if (diziler[diziID]) {{
        var diziData = diziler[diziID];
        
        diziData.bolumler.forEach(function(bolum) {{
            // Orijinal kodunuzdaki gibi DIV oluşturuluyor ve onclick ile yönlendiriliyor.
            var item = document.createElement("div"); 
            item.className = "filmpanel";
            
            item.onclick = function() {{
                // Bölüm linkine giderken tarihçeye bölümler durumunu kaydet
                history.replaceState({{ page: 'bolumler', diziID: diziID }}, '', `#bolumler-${{diziID}}`);
                window.location.href = bolum.link;
            }};
            
            // Temiz HTML yapısı (IMDb ve YIL olmadan)
            item.innerHTML = '<div class="filmresim"><img src="' + diziData.resim + '"></div>' +
                             '<div class="filmisimpanel">' +
                                 '<div class="filmisim">' + bolum.ad + '</div>' +
                                 '<div class="resimust">' +
                                     '<div class="filmdil">' + diziData.dil + '</div>' +
                                 '</div>' +
                             '</div>';

            listContainer.appendChild(item);
        }});
    }} else {{
        listContainer.innerHTML = `<div class="hataekran"><i class="fas fa-exclamation-triangle"></i><div class="hatayazi">Bu dizi için bölüm bulunamadı veya veri çekilemedi.</div></div>`;
    }}
    
    document.getElementById("anaDiziler").classList.add("hidden"); 
    document.getElementById("bolumler").classList.remove("hidden");
    document.getElementById("geriBtn").style.display = "block";

    currentScreen = 'bolumler';
    history.pushState({{ page: 'bolumler', diziID: diziID }}, '', `#bolumler-${{diziID}}`);
}}

function geriDon() {{
    sessionStorage.removeItem('currentDiziID');
    document.getElementById("anaDiziler").classList.remove("hidden"); 
    document.getElementById("bolumler").classList.add("hidden");
    document.getElementById("geriBtn").style.display = "none";
    
    currentScreen = 'anaSayfa';
    history.pushState({{ page: 'anaSayfa' }}, '', '#anaSayfa');
}}

window.addEventListener('popstate', function(event) {{
    const hash = window.location.hash;
    const match = hash.match(/^#bolumler-(.*)$/);
    
    if (match) {{
        const diziID = match[1];
        if (diziler[diziID]) {{
            showBolumler(diziID);
        }} else {{
             geriDon();
        }}
    }} else {{
        geriDon();
    }}
}});


function checkInitialState() {{
    const hash = window.location.hash;
    const match = hash.match(/^#bolumler-(.*)$/);
    
    if (match) {{
        const diziID = match[1];
        if (diziler[diziID]) {{
            showBolumler(diziID);
        }} else {{
            geriDon();
        }}
    }} else {{
        document.getElementById("anaDiziler").classList.remove("hidden");
        document.getElementById("bolumler").classList.add("hidden");
        document.getElementById("geriBtn").style.display = "none";
        currentScreen = 'anaSayfa';
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
    dosya_adi = "anime.html"
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"\n✅ BAŞARILI: Tüm veriler çekildi ve '{dosya_adi}' dosyasına kaydedildi.")
    print("Oluşturulan HTML dosyasını tarayıcınızda açarak sonucu görebilirsiniz.")

except Exception as e:
    print(f"\n[KRİTİK HATA] HTML dosyası yazılırken bir sorun oluştu: {e}")
