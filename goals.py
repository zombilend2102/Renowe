import requests
import re
import time

# --- AYARLAR ---
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
TIMEOUT_VAL = 10 # Bağlantı süresini uzattık, hemen hata vermesin

# --- LOGO HARİTASI (Tüm botlar için ortak) ---
LOGO_MAP = {
    "beIN Sports 1": "https://i.hizliresim.com/lkl7u2r.png",
    "beIN Sports 2": "https://i.hizliresim.com/pvr9h26.png",
    "beIN Sports 3": "https://i.hizliresim.com/ozrfqya.png",
    "beIN Sports 4": "https://i.hizliresim.com/kbhvyeh.png",
    "beIN Sports 5": "https://i.hizliresim.com/lkl7u2r.png",
    "beIN Sports Max 1": "https://i.hizliresim.com/a6kdghr.png",
    "beIN Sports Max 2": "https://i.hizliresim.com/hp2j3mg.png",
    "Saran Sports 1": "https://i.hizliresim.com/35ndyy0.png",
    "S Sports 1": "https://i.hizliresim.com/35ndyy0.png",
    "S Sport 1": "https://i.hizliresim.com/35ndyy0.png",
    "Saran Sports 2": "https://i.imgur.com/mbF7SLI.png",
    "S Sports 2": "https://i.imgur.com/mbF7SLI.png",
    "S Sport 2": "https://i.imgur.com/mbF7SLI.png",
    "Smart Spor 1": "https://i.hizliresim.com/aa4pe3w.png",
    "Smart Sports 1": "https://i.hizliresim.com/aa4pe3w.png",
    "Smart Spor 2": "https://i.hizliresim.com/ce1qms5.png",
    "Smart Sports 2": "https://i.hizliresim.com/ce1qms5.png",
    "NBA TV": "https://i.ibb.co/VSSByY9/NBA-TV.png",
    "Tivibu Sports 1": "https://i.hizliresim.com/nyyqh1f.png",
    "Tivibu Spor 1": "https://i.hizliresim.com/nyyqh1f.png",
    "Tivibu Sports 2": "https://i.hizliresim.com/mr3sv0j.png",
    "Tivibu Spor 2": "https://i.hizliresim.com/mr3sv0j.png",
    "Tivibu Sports 3": "https://i.hizliresim.com/rcz77hb.png",
    "Tivibu Spor 3": "https://i.hizliresim.com/rcz77hb.png",
    "Tivibu Sports 4": "https://i.hizliresim.com/185gwih.png",
    "Tivibu Spor 4": "https://i.hizliresim.com/185gwih.png",
    "Tâbii": "https://i.hizliresim.com/ojqbhcx.png",
    "Tabii": "https://i.hizliresim.com/ojqbhcx.png",
    "BeIN Sports Haber": "https://i.ibb.co/XZmhFDn/Bein-HABER-HD.png",
    "A Spor": "https://i.ibb.co/NVcr0ST/A-SPOR.png",
    "TRT Spor": "https://i.ibb.co/H4k7r31/TRT-SPOR.png",
    "Eurosport 1": "https://i.hizliresim.com/t75soiq.png",
    "Eurosport 2": "https://i.hizliresim.com/t75soiq.png",
    "Exxen": "https://i.hizliresim.com/t75soiq.png",
}

def get_logo(channel_name):
    # İsim içinde geçen anahtar kelimeye göre logo bul
    # Önce tam eşleşme veya içerik kontrolü
    for key, url in LOGO_MAP.items():
        if key.lower() in channel_name.lower():
            return url
    # Tâbii kanalları için özel dinamik kontrol (Tabii 1, Tabii 2...)
    if "tabii" in channel_name.lower():
        num = re.search(r'\d+', channel_name)
        if num:
            n = num.group(0)
            # Senin verdiğin listeye göre Tabii 1-6 arası logolar
            tabii_logos = {
                "1": "https://i.ibb.co/0cYJYvB/tabi1.png",
                "2": "https://i.ibb.co/VNpTh0J/tabi2.png",
                "3": "https://i.ibb.co/D7NwYrT/tabi3.png",
                "4": "https://i.ibb.co/2h6yJJt/tabi4.png",
                "5": "https://i.ibb.co/QFZnFHg/tabi5.png",
                "6": "https://i.ibb.co/s386Cn7/tabi6.png"
            }
            return tabii_logos.get(n, "https://i.hizliresim.com/ojqbhcx.png")
            
    return "https://i.hizliresim.com/ska5t9e.jpg" # Varsayılan Logo

# --- STATİK KANALLAR ---
STATIC_CHANNELS = """
#EXTINF:-1 tvg-id="" tvg-name="HT SPOR HD" tvg-logo="https://i.hizliresim.com/mmazkt2.png" group-title="TURKIYE DEATHLESS",HT SPOR HD
https://ciner.daioncdn.net/ht-spor/ht-spor.m3u8?app=web
#EXTINF:-1 tvg-id="" tvg-name="NBA SPORTS HD" tvg-logo="https://i.ibb.co/VSSByY9/NBA-TV.png" group-title="TURKIYE DEATHLESS",NBA SPORTS HD
https://ww.dooballfree.vip/live/nba/playlist.m3u8
#EXTINF:-1 tvg-id="" tvg-name="A SPOR HD" tvg-logo="https://i.ibb.co/NVcr0ST/A-SPOR.png" group-title="TURKIYE DEATHLESS",A SPOR HD
https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/aspor/aspor.m3u8
#EXTINF:-1 tvg-id="" tvg-name="TRT SPOR HD" tvg-logo="https://i.ibb.co/H4k7r31/TRT-SPOR.png" group-title="TURKIYE DEATHLESS",TRT SPOR HD
https://tv-trtspor1.medya.trt.com.tr/master.m3u8
#EXTINF:-1 tvg-id="" tvg-name="TRT SPOR ★ HD" tvg-logo="https://i.ibb.co/rH9TkLx/TRT-SPOR-YILDIZ.png" group-title="TURKIYE DEATHLESS",TRT SPOR ★ HD
https://tv-trtspor2.medya.trt.com.tr/master.m3u8
#EXTINF:-1 tvg-id="" tvg-name="TJK SPOR HD" tvg-logo="https://i.ibb.co/WVwxNCY/TJK-TV.png" group-title="TURKIYE DEATHLESS",TJK SPOR HD
https://tjktv-live.tjk.org/tjktv_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="FB SPOR HD" tvg-logo="https://i.ibb.co/5kTcBJM/FB-TV.png" group-title="TURKIYE DEATHLESS",FB SPOR HD
https://fbtv.fenerbahce.org/fenerbahcetv.stream_720p/playlist.m3u8
#EXTINF:-1 tvg-id="" tvg-name="SPORTS HD" tvg-logo="https://i.ibb.co/VxHMGyp/SportsTV.png" group-title="TURKIYE DEATHLESS",SPORTS HD
https://live.sportstv.com.tr/hls/low/sportstv_fhd/index.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport HD" tvg-logo="https://i.hizliresim.com/ojqbhcx.png" group-title="TURKIYE DEATHLESS",Tabii Sport HD
https://beert7sqimrk0bfdupfgn6qew.medya.trt.com.tr/master.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 1 HD" tvg-logo="https://i.ibb.co/0cYJYvB/tabi1.png" group-title="TURKIYE DEATHLESS",Tabii Sport 1 HD
https://iaqzu4szhtzeqd0edpsayinle.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 2 HD" tvg-logo="https://i.ibb.co/VNpTh0J/tabi2.png" group-title="TURKIYE DEATHLESS",Tabii Sport 2 HD
https://klublsslubcgyiz7zqt5bz8il.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 3 HD" tvg-logo="https://i.ibb.co/D7NwYrT/tabi3.png" group-title="TURKIYE DEATHLESS",Tabii Sport 3 HD
https://ujnf69op16x2fiiywxcnx41q8.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 4 HD" tvg-logo="https://i.ibb.co/2h6yJJt/tabi4.png" group-title="TURKIYE DEATHLESS",Tabii Sport 4 HD
https://bfxy3jgeydpbphtk8qfqwm3hr.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 5 HD" tvg-logo="https://i.ibb.co/QFZnFHg/tabi5.png" group-title="TURKIYE DEATHLESS",Tabii Sport 5 HD
https://z3mmimwz148csv0vaxtphqspf.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 6 HD" tvg-logo="https://i.ibb.co/s386Cn7/tabi6.png" group-title="TURKIYE DEATHLESS",Tabii Sport 6 HD
https://vbtob9hyq58eiophct5qctxr2.medya.trt.com.tr/master_1080p.m3u8
"""

# --- 1. KAYNAK: TRGOALS (Proxy ile) ---
def fetch_trgoals():
    print("--- 1. TrGoals Taranıyor ---")
    base = "https://trgoals"
    domain = ""
    # Aralığı daralttım ki hızlı bulsun, bulamazsa devam etsin
    for i in range(1478, 1600): 
        test_domain = f"{base}{i}.xyz"
        try:
            response = requests.head(test_domain, headers=HEADERS, timeout=2)
            if response.status_code == 200:
                domain = test_domain
                print(f"✅ TrGoals Domain Bulundu: {domain}")
                break
        except:
            continue
    
    # Eğer yukarıda bulamazsa bir de 2080'den geriye tarasın (yedek)
    if not domain:
        for i in range(2101, 2080, -1):
             test_domain = f"{base}{i}.xyz"
             try:
                response = requests.head(test_domain, headers=HEADERS, timeout=2)
                if response.status_code == 200:
                    domain = test_domain
                    print(f"✅ TrGoals Domain Bulundu (Yedek): {domain}")
                    break
             except:
                continue

    if not domain:
        print("❌ TrGoals domain bulunamadı.")
        return []

    channel_ids = {
        "yayinzirve":"beIN Sports 1","yayininat":"beIN Sports 1","yayin1":"beIN Sports 1",
        "yayinb2":"beIN Sports 2","yayinb3":"beIN Sports 3","yayinb4":"beIN Sports 4",
        "yayinb5":"beIN Sports 5","yayinbm1":"beIN Sports 1 Max","yayinbm2":"beIN Sports 2 Max",
        "yayinss":"Saran Sports 1","yayinss2":"Saran Sports 2","yayint1":"Tivibu Sports 1",
        "yayint2":"Tivibu Sports 2","yayint3":"Tivibu Sports 3","yayint4":"Tivibu Sports 4",
        "yayinsmarts":"Smart Sports 1","yayinsms2":"Smart Sports 2","yayinnbatv":"NBA TV",
        "yayinex1":"Tâbii 1","yayinex2":"Tâbii 2","yayinex3":"Tâbii 3",
        "yayinex4":"Tâbii 4","yayinex5":"Tâbii 5","yayinex6":"Tâbii 6"
    }

    results = []
    for channel_id, channel_name in channel_ids.items():
        channel_url = f"{domain}/channel.html?id={channel_id}"
        try:
            r = requests.get(channel_url, headers=HEADERS, timeout=5)
            match = re.search(r'const baseurl = "(.*?)"', r.text)
            if match:
                baseurl = match.group(1)
                full_url = f"http://palxlendimgaliba1010.mywire.org/proxy.php?url={baseurl}{channel_id}.m3u8"
                logo = get_logo(channel_name)
                # İsim karışmasın diye sonuna (G) ekleyebilirsin veya olduğu gibi bırakabilirsin
                results.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="TURKIYE DEATHLESS", {channel_name}\n{full_url}')
        except:
            continue
    print(f"TrGoals'den {len(results)} kanal eklendi.")
    return results

# --- 2. KAYNAK: ANDRO/BIRAZCIK ---
def fetch_andro():
    print("--- 2. Andro/Birazcik Taranıyor ---")
    active_domain = None
    # 25'ten 100'e kadar tara
    for i in range(25, 100):
        url = f"https://birazcikspor{i}.xyz/"
        try:
            r = requests.head(url, headers=HEADERS, timeout=2)
            if r.status_code == 200:
                active_domain = url
                print(f"✅ Andro Domain: {active_domain}")
                break
        except:
            continue

    if not active_domain:
        print("❌ Andro domain bulunamadı.")
        return []

    try:
        html = requests.get(active_domain, headers=HEADERS, timeout=TIMEOUT_VAL).text
        m = re.search(r'<iframe[^>]+id="matchPlayer"[^>]+src="event\.html\?id=([^"]+)"', html)
        if not m: 
            print("Andro iframe ID bulunamadı.")
            return []
        first_id = m.group(1)

        event_source = requests.get(active_domain + "event.html?id=" + first_id, headers=HEADERS, timeout=TIMEOUT_VAL).text
        b = re.search(r'var\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
        if not b: 
            print("Andro BaseURL bulunamadı.")
            return []
        base_url = b.group(1)
    except Exception as e:
        print(f"Andro Hata: {e}")
        return []

    channels_data = [
        ("beIN Sports 1", "androstreamlivebs1"), ("beIN Sports 2", "androstreamlivebs2"),
        ("beIN Sports 3", "androstreamlivebs3"), ("beIN Sports 4", "androstreamlivebs4"),
        ("beIN Sports 5", "androstreamlivebs5"), ("beIN Sports Max 1", "androstreamlivebsm1"),
        ("beIN Sports Max 2", "androstreamlivebsm2"), ("Saran Sports 1", "androstreamlivess1"),
        ("Saran Sports 2", "androstreamlivess2"), ("Tivibu Sports 1", "androstreamlivets1"),
        ("Tivibu Sports 2", "androstreamlivets2"), ("Tivibu Sports 3", "androstreamlivets3"),
        ("Tivibu Sports 4", "androstreamlivets4"), ("Smart Sports 1", "androstreamlivesm1"),
        ("Smart Sports 2", "androstreamlivesm2"), ("Tâbii 1", "androstreamlivetb1"),
        ("Tâbii 2", "androstreamlivetb2"), ("Tâbii 3", "androstreamlivetb3"),
        ("Tâbii 4", "androstreamlivetb4"), ("Tâbii 5", "androstreamlivetb5"),
        ("Tâbii 6", "androstreamlivetb6")
    ]

    results = []
    for name, cid in channels_data:
        # Andro direkt link veriyor, proxy eklemiyoruz hızlı çalışsın diye.
        full_url = f"{base_url}{cid}.m3u8"
        logo = get_logo(name)
        results.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="TURKIYE DEATHLESS", {name}\n{full_url}')
    
    print(f"Andro'dan {len(results)} kanal eklendi.")
    return results

# --- 3. KAYNAK: SELÇUK (Senin Py3 Kodun) ---
def fetch_selcuk():
    print("--- 3. Selçuk Taranıyor ---")
    CHANNELS = [
        {"id": "bein1", "source_id": "selcukbeinsports1", "name": "beIN Sports 1"},
        {"id": "bein2", "source_id": "selcukbeinsports2", "name": "beIN Sports 2"},
        {"id": "bein3", "source_id": "selcukbeinsports3", "name": "beIN Sports 3"},
        {"id": "bein4", "source_id": "selcukbeinsports4", "name": "beIN Sports 4"},
        {"id": "beinmax1", "source_id": "selcukbeinsportsmax1", "name": "beIN Sports Max 1"},
        {"id": "beinmax2", "source_id": "selcukbeinsportsmax2", "name": "beIN Sports Max 2"},
        {"id": "tivibu1", "source_id": "selcuktivibuspor1", "name": "Tivibu Sports 1"},
        {"id": "tivibu2", "source_id": "selcuktivibuspor2", "name": "Tivibu Sports 2"},
        {"id": "ssport1", "source_id": "selcukssport", "name": "S Sport 1"},
        {"id": "ssport2", "source_id": "selcukssport2", "name": "S Sport 2"},
        {"id": "smart1", "source_id": "selcuksmartspor", "name": "Smart Sports 1"},
        {"id": "smart2", "source_id": "selcuksmartspor2", "name": "Smart Sports 2"},
    ]

    base_url = None
    try:
        # 1. Adım: Giriş sayfasından aktif siteyi bul
        entry_url = "https://www.selcuksportshd78.is/"
        entry_source = requests.get(entry_url, headers=HEADERS, timeout=TIMEOUT_VAL).text
        match = re.search(r'url=(https:\/\/[^"]+)', entry_source)
        if match:
            active_site = match.group(1)
            print(f"✅ Selçuk Aktif Site: {active_site}")
            
            # 2. Adım: Aktif siteden Base URL'yi bul
            source = requests.get(active_site, headers=HEADERS, timeout=TIMEOUT_VAL).text
            match_base = re.search(r'https:\/\/[^"]+\/index\.php\?id=selcukbeinsports1', source)
            if match_base:
                base_url = match_base.group(0).replace("selcukbeinsports1", "")
            else:
                print("❌ Selçuk Base URL Regex uymadı.")
        else:
             print("❌ Selçuk Giriş URL Regex uymadı.")
    except Exception as e:
        print(f"Selçuk Bağlantı Hatası: {e}")
        return []

    if not base_url:
        return []

    results = []
    for ch in CHANNELS:
        url = f"{base_url}{ch['source_id']}"
        try:
            source = requests.get(url, headers=HEADERS, timeout=5).text
            stream_url = ""
            # Senin Py3'teki regex mantığı
            match = re.search(r'(https:\/\/[^\'"]+\/live\/[^\'"]+\/playlist\.m3u8)', source)
            if match:
                stream_url = match.group(1)
            else:
                match = re.search(r'(https:\/\/[^\'"]+\/live\/)', source)
                if match:
                    stream_url = f"{match.group(1)}{ch['source_id']}/playlist.m3u8"
            
            if stream_url:
                stream_url = re.sub(r'[\'";].*$', '', stream_url).strip()
                if stream_url.startswith("http"):
                    logo = get_logo(ch['name'])
                    results.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="TURKIYE DEATHLESS", {ch["name"]}\n{stream_url}')
        except:
            continue
    
    print(f"Selçuk'tan {len(results)} kanal eklendi.")
    return results

# --- HTML ŞABLONU (HIZLANDIRILMIŞ PLAYER) ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#000000">
    <title>Ultimate Pro Player - Fast Mode</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@1.5.0"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* --- TEMEL --- */
        body {
            background-color: #000;
            margin: 0; padding: 0;
            width: 100vw; height: 100dvh;
            overflow: hidden;
            font-family: 'Inter', sans-serif;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }

        #video-container {
            position: fixed; inset: 0;
            background: #000; z-index: 0;
            display: flex; align-items: center; justify-content: center;
        }

        video {
            display: block;
            transition: all 0.3s ease;
        }
        video.mode-contain { width: 100%; height: 100%; object-fit: contain; }
        video.mode-stretch { position: absolute; top: 0; left: 0; width: 100vw !important; height: 100dvh !important; object-fit: fill !important; }

        /* --- ARAYÜZ KATMANI --- */
        #ui-layer {
            position: fixed; inset: 0; z-index: 20;
            display: flex; flex-direction: column; justify-content: space-between;
            background: linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, transparent 25%, transparent 65%, rgba(0,0,0,0.95) 100%);
            opacity: 0; transition: opacity 0.3s ease;
            pointer-events: none; 
        }
        #ui-layer.visible { opacity: 1; pointer-events: auto; }

        .top-bar { padding: 20px; margin-top: env(safe-area-inset-top); color: white; pointer-events: none; }
        .channel-title { font-size: 20px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.8); padding-left: 20px; }

        .center-controls {
            position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            display: flex; align-items: center; gap: 40px; color: white;
            pointer-events: auto; 
        }
        .ctrl-btn { 
            cursor: pointer; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.6)); 
            transition: transform 0.2s, color 0.2s; 
            border-radius: 50%; padding: 5px;
            border: 3px solid transparent; 
        }
        .ctrl-btn:active { transform: scale(0.9); }
        .play-btn svg { width: 80px; height: 80px; }
        .skip-btn svg { width: 45px; height: 45px; opacity: 0.9; }

        .focused {
            transform: scale(1.15);
            border-color: #ff5200 !important;
            background: rgba(255, 82, 0, 0.2);
            box-shadow: 0 0 15px rgba(255, 82, 0, 0.5);
        }

        .bottom-section {
            padding: 20px; padding-bottom: calc(20px + env(safe-area-inset-bottom));
            display: flex; flex-direction: column; gap: 15px;
            pointer-events: auto;
        }

        #channel-carousel {
            display: flex; overflow-x: auto; gap: 15px; padding: 10px;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
        }
        #channel-carousel::-webkit-scrollbar { display: none; }

        .channel-card {
            flex: 0 0 auto; width: 150px; height: 80px;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px); border-radius: 12px;
            display: flex; align-items: center; padding: 10px; gap: 10px;
            border: 3px solid transparent; 
            transition: all 0.2s; cursor: pointer;
        }
        
        .channel-card.playing {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .channel-card.focused {
            background: rgba(255, 82, 0, 0.8);
            border-color: #fff !important;
            transform: scale(1.1);
            z-index: 10;
        }

        .channel-card img { width: 40px; height: 40px; object-fit: contain; }
        .channel-card .c-name { font-size: 13px; color: white; font-weight: 600; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }

        .controls-row { display: flex; align-items: center; gap: 15px; color: white; padding: 0 10px; }
        .time-text { font-size: 14px; font-weight: 600; }
        
        #info-toast {
            position: absolute; top: 30px; right: 30px;
            background: #ff5200; color: white; padding: 10px 20px;
            border-radius: 8px; font-weight: bold; opacity: 0; transition: opacity 0.5s; z-index: 50;
        }
    </style>
</head>
<body>

    <div id="video-container">
        <video id="player" class="mode-contain" playsinline autoplay></video>
    </div>

    <div id="ui-layer">
        <div id="info-toast">Bilgi</div>

        <div class="top-bar">
            <div class="channel-title" id="current-title">Yükleniyor...</div>
        </div>

        <div class="center-controls">
            <div class="ctrl-btn skip-btn" id="btn-rewind" onclick="event.stopPropagation(); seek(-10)">
                <svg viewBox="0 0 24 24" fill="white"><path d="M11 14.17L8.83 12 11 9.83V6L5 12l6 6v-3.83zM19 14.17L16.83 12 19 9.83V6l-6 6 6 6v-3.83z"></path></svg>
            </div>
            <div class="ctrl-btn play-btn" id="btn-play" onclick="event.stopPropagation(); togglePlay()">
                <svg id="icon-play" class="hidden" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"></path></svg>
                <svg id="icon-pause" viewBox="0 0 24 24" fill="white"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"></path></svg>
            </div>
            <div class="ctrl-btn skip-btn" id="btn-forward" onclick="event.stopPropagation(); seek(10)">
                <svg viewBox="0 0 24 24" fill="white"><path d="M5 14.17L7.17 12 5 9.83V6l6 6-6 6v-3.83zM13 14.17L15.17 12 13 9.83V6l6 6-6 6v-3.83z"></path></svg>
            </div>
        </div>

        <div class="bottom-section">
            <div id="channel-carousel"></div>

            <div class="controls-row">
                <span class="time-text">CANLI YAYIN</span>
                <div style="flex-grow:1"></div>
                <div class="ctrl-btn" id="btn-fit" onclick="event.stopPropagation(); toggleFit()" style="padding: 5px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"></path></svg>
                </div>
            </div>
        </div>
    </div>

    <script>
        const video = document.getElementById('player');
        const uiLayer = document.getElementById('ui-layer');
        const carousel = document.getElementById('channel-carousel');
        const titleEl = document.getElementById('current-title');
        const iconPlay = document.getElementById('icon-play');
        const iconPause = document.getElementById('icon-pause');
        const infoToast = document.getElementById('info-toast');
        
        let hls = null;
        let channels = [];
        let currentChannelIndex = 0;
        let isStretched = false;
        let uiTimeout;

        let focusArea = 'none'; 
        let focusedControlIndex = 1;
        let focusedChannelIndex = 0;

        document.addEventListener('click', (e) => {
            if(e.target.closest('.ctrl-btn') || e.target.closest('.channel-card')) {
                resetUITimer();
                return;
            }
            if(uiLayer.classList.contains('visible')) {
                hideUI();
            } else {
                showUI();
                focusArea = 'none'; 
                document.querySelectorAll('.focused').forEach(el => el.classList.remove('focused'));
            }
        });

        function togglePlay() {
            if (video.paused) { video.play(); iconPlay.classList.add('hidden'); iconPause.classList.remove('hidden'); }
            else { video.pause(); iconPlay.classList.remove('hidden'); iconPause.classList.add('hidden'); }
        }

        window.seek = function(sec) {
            video.currentTime += sec;
            resetUITimer();
        }

        function toggleFit() {
            isStretched = !isStretched;
            video.className = isStretched ? 'mode-stretch' : 'mode-contain';
            showToast(isStretched ? "Tam Ekran" : "Orijinal");
        }

        function playChannel(index) {
            if (index < 0 || index >= channels.length) return;
            currentChannelIndex = index;
            renderList();
            
            const ch = channels[index];
            titleEl.textContent = ch.name;

            if (hls) { hls.destroy(); hls = null; }
            
            if (Hls.isSupported()) {
                // --- HIZLANDIRMA AYARLARI BURADA ---
                var config = {
                    startFragPrefetch: true,        // Başlangıç parçasını hemen çek
                    enableWorker: true,             // Arka plan işçisini aç
                    lowLatencyMode: true,           // Düşük gecikme modu
                    backBufferLength: 30,
                    maxMaxBufferLength: 10,         // Çok fazla tampon yapma, canlı yayın bu
                    liveSyncDurationCount: 2,       // Canlı yayına daha yakın başla
                };
                
                hls = new Hls(config);
                hls.loadSource(ch.url);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    video.play().catch(e => {
                        console.log("Oto oynatma bekleniyor...");
                    });
                });
                hls.on(Hls.Events.ERROR, function (event, data) {
                     if (data.fatal) {
                        switch (data.type) {
                        case Hls.ErrorTypes.NETWORK_ERROR:
                            console.log("Ağ hatası, yeniden deneniyor...");
                            hls.startLoad();
                            break;
                        case Hls.ErrorTypes.MEDIA_ERROR:
                            console.log("Medya hatası, kurtarılıyor...");
                            hls.recoverMediaError();
                            break;
                        default:
                            hls.destroy();
                            break;
                        }
                    }
                });

            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = ch.url;
                video.addEventListener('loadedmetadata', () => {
                    video.play().catch(e => {});
                });
            }
            iconPlay.classList.add('hidden'); iconPause.classList.remove('hidden');
        }

        function showUI() {
            uiLayer.classList.add('visible');
            resetUITimer();
        }

        function hideUI() {
            uiLayer.classList.remove('visible');
            focusArea = 'none';
            document.querySelectorAll('.focused').forEach(el => el.classList.remove('focused'));
        }

        function resetUITimer() {
            clearTimeout(uiTimeout);
            uiTimeout = setTimeout(hideUI, 5000);
        }

        function showToast(msg) {
            infoToast.textContent = msg;
            infoToast.style.opacity = '1';
            setTimeout(() => infoToast.style.opacity = '0', 3000);
        }

        function renderList() {
            carousel.innerHTML = '';
            channels.forEach((ch, idx) => {
                const card = document.createElement('div');
                card.className = 'channel-card';
                if(idx === currentChannelIndex) card.classList.add('playing'); 
                card.id = `ch-card-${idx}`;
                card.innerHTML = `<img src="${ch.logo}" onerror="this.style.display='none'"><div class="c-name">${ch.name}</div>`;
                card.onclick = (e) => { 
                    e.stopPropagation(); 
                    playChannel(idx); 
                    resetUITimer();
                };
                carousel.appendChild(card);
            });
        }

        function updateFocusVisuals() {
            document.querySelectorAll('.focused').forEach(el => el.classList.remove('focused'));
            if (focusArea === 'controls') {
                if (focusedControlIndex === 0) document.getElementById('btn-rewind').classList.add('focused');
                if (focusedControlIndex === 1) document.getElementById('btn-play').classList.add('focused');
                if (focusedControlIndex === 2) document.getElementById('btn-forward').classList.add('focused');
                if (focusedControlIndex === 3) document.getElementById('btn-fit').classList.add('focused');
            } 
            else if (focusArea === 'channels') {
                const card = document.getElementById(`ch-card-${focusedChannelIndex}`);
                if (card) {
                    card.classList.add('focused');
                    card.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
                }
            }
        }

        document.addEventListener('keydown', (e) => {
            if (focusArea !== 'none') resetUITimer();

            switch(e.key) {
                case 'ArrowUp':
                case 'ChannelUp':
                    if (focusArea === 'none') {
                        playChannel(currentChannelIndex - 1); 
                    } else if (focusArea === 'channels') {
                        focusArea = 'controls';
                        focusedControlIndex = 1; 
                        updateFocusVisuals();
                    }
                    break;
                case 'ArrowDown':
                case 'ChannelDown':
                    if (focusArea === 'none') {
                        playChannel(currentChannelIndex + 1); 
                    } else if (focusArea === 'controls') {
                        focusArea = 'channels';
                        focusedChannelIndex = currentChannelIndex; 
                        updateFocusVisuals();
                    }
                    break;
                case 'ArrowLeft':
                    if (focusArea === 'channels') {
                        if (focusedChannelIndex > 0) focusedChannelIndex--;
                        updateFocusVisuals();
                    } else if (focusArea === 'controls') {
                        if (focusedControlIndex > 0) focusedControlIndex--;
                        updateFocusVisuals();
                    }
                    break;
                case 'ArrowRight':
                    if (focusArea === 'channels') {
                        if (focusedChannelIndex < channels.length - 1) focusedChannelIndex++;
                        updateFocusVisuals();
                    } else if (focusArea === 'controls') {
                        if (focusedControlIndex < 3) focusedControlIndex++;
                        updateFocusVisuals();
                    }
                    break;
                case 'Enter':
                case 'Ok':
                    if (focusArea === 'none') {
                        showUI();
                        focusArea = 'channels';
                        focusedChannelIndex = currentChannelIndex;
                        updateFocusVisuals();
                    } else {
                        if (focusArea === 'channels') playChannel(focusedChannelIndex);
                        else if (focusArea === 'controls') {
                            if (focusedControlIndex === 0) seek(-10);
                            if (focusedControlIndex === 1) togglePlay();
                            if (focusedControlIndex === 2) seek(10);
                            if (focusedControlIndex === 3) toggleFit();
                        }
                    }
                    break;
                case 'Escape':
                case 'Backspace':
                    hideUI();
                    break;
            }
        });

        // --- VERİ ENJEKSİYONU ---
        const m3uList = `
__M3U_CONTENT__
`;

        window.onload = () => {
            const lines = m3uList.split('\\n');
            let t = {};
            lines.forEach(l => {
                l=l.trim();
                if(l.startsWith('#EXTINF')) {
                    const nameMatch = l.match(/tvg-name="([^"]+)"/);
                    const logoMatch = l.match(/tvg-logo="([^"]+)"/);
                    let name = "Kanal";
                    
                    if (nameMatch) name = nameMatch[1];
                    else {
                        const commaSplit = l.split(',');
                        if (commaSplit.length > 1) name = commaSplit[1].trim();
                    }
                    
                    t = { name: name, logo: logoMatch ? logoMatch[1] : "" };
                } else if(l.startsWith('http')) {
                    channels.push({...t, url: l});
                }
            });
            if(channels.length) { 
                renderList(); 
                playChannel(0); 
            }
        };
    </script>
</body>
</html>
"""

def main():
    print("Kanallar taranıyor...")
    
    # 3 Kaynağı tara ve listeleri al
    list1 = fetch_trgoals() # Proxy'li
    list2 = fetch_andro()   # Proxy'siz (Direkt Link)
    list3 = fetch_selcuk()  # Proxy'siz (Direkt Link)

    all_channels = list1 + list2 + list3
    
    # Python listesini tek bir string haline getir
    dynamic_m3u_content = "\n".join(all_channels)
    
    # Sabit kanalları da ekle
    final_m3u_content = dynamic_m3u_content + "\n" + STATIC_CHANNELS

    # HTML şablonundaki yer tutucuyu değiştir
    final_html = HTML_TEMPLATE.replace("__M3U_CONTENT__", final_m3u_content)

    with open("goals.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"✅ goals.html oluşturuldu. Toplam Kanal: {len(all_channels)}")

if __name__ == "__main__":
    main()
