import requests
import re
import os
import warnings

# --- AYARLAR ---
warnings.filterwarnings('ignore')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/"
}

# --- LOGO HARİTASI (SENİN LİSTEN) ---
CHANNEL_LOGOS = {
    "Canlı Maç İzle": "https://i.hizliresim.com/lkl7u2r.png",
    "beIN Sports 1": "https://i.hizliresim.com/lkl7u2r.png",
    "beIN Sports 2": "https://i.hizliresim.com/pvr9h26.png",
    "beIN Sports 3": "https://i.hizliresim.com/ozrfqya.png",
    "beIN Sports 4": "https://i.hizliresim.com/kbhvyeh.png",
    "beIN Sports 5": "https://i.hizliresim.com/l5huh73.png",
    "beIN Sports Max 1": "https://i.hizliresim.com/a6kdghr.png",
    "beIN Sports Max 2": "https://i.hizliresim.com/hp2j3mg.png",
    "S Sport 1": "https://i.hizliresim.com/35ndyy0.png",
    "S Sport 2": "https://i.imgur.com/mbF7SLI.png",
    "Smart Spor 1": "https://i.hizliresim.com/aa4pe3w.png",
    "Smart Spor 2": "https://i.hizliresim.com/ce1qms5.png",
    "NBA TV": "https://i.ibb.co/VSSByY9/NBA-TV.png",
    "Tivibu Spor 1": "https://i.hizliresim.com/nyyqh1f.png",
    "Tivibu Spor 2": "https://i.hizliresim.com/mr3sv0j.png",
    "Tivibu Spor 3": "https://i.hizliresim.com/rcz77hb.png",
    "Tivibu Spor 4": "https://i.hizliresim.com/185gwih.png",
    "Tabii": "https://i.hizliresim.com/ojqbhcx.png",
    "Tabii 1": "https://i.ibb.co/0cYJYvB/tabi1.png",
    "Tabii 2": "https://i.ibb.co/VNpTh0J/tabi2.png",
    "Tabii 3": "https://i.ibb.co/D7NwYrT/tabi3.png",
    "Tabii 4": "https://i.ibb.co/2h6yJJt/tabi4.png",
    "Tabii 5": "https://i.ibb.co/QFZnFHg/tabi5.png",
    "Tabii 6": "https://i.ibb.co/s386Cn7/tabi6.png"
}

DEFAULT_LOGO = "https://i.hizliresim.com/t75soiq.png"

def get_logo(channel_name):
    return CHANNEL_LOGOS.get(channel_name, DEFAULT_LOGO)

# --- DEATHLESS / BİRAZCIKSPOR TARAMA MANTIĞI ---
def fetch_deathless():
    print("--- DeaTHLesS Bot (Birazcıkspor) Çalışıyor ---")
    
    # 1. ADIM: Aktif Domaini Bul
    print("🔍 Aktif domain aranıyor (44-200)...")
    active_domain = None
    
    for i in range(44, 200):
        url = f"https://birazcikspor{i}.xyz/"
        try:
            # Proxy kullanmıyoruz, direkt istek (hızlı olması için)
            response = requests.head(url, headers=HEADERS, timeout=2)
            if response.status_code == 200:
                active_domain = url
                print(f"✅ Aktif Domain Bulundu: {active_domain}")
                break
        except:
            continue
    
    if not active_domain:
        print("❌ Hiçbir domain aktif değil.")
        return []

    # 2. ADIM: Ana Sayfadan ID'yi Çek
    found_id = None
    HEADERS['Referer'] = active_domain # Referer güncelle

    try:
        response = requests.get(active_domain, headers=HEADERS, timeout=10)
        html = response.text
        
        # event.html?id= sonrasını yakalar
        id_match = re.search(r'event\.html\?id=([a-zA-Z0-9_]+)', html)
        if id_match:
            found_id = id_match.group(1)
            print(f"🆔 Referans ID Bulundu: {found_id}")
        else:
            print("❌ ID kalıbı bulunamadı, manuel ID kullanılacak.")
            found_id = "androstreamlivebiraz1"
            
    except Exception as e:
        print(f"❌ Ana sayfa hatası: {e}")
        return []

    # 3. ADIM: Base URL'yi Kaynak Koddan Çek
    base_url = ""
    if found_id:
        try:
            event_url = f"{active_domain}event.html?id={found_id}"
            print(f"🔗 Kaynak taranıyor: {event_url}")
            
            event_response = requests.get(event_url, headers=HEADERS, timeout=10)
            event_source = event_response.text
            
            # Kaynak kod: const baseurls = [ "URL", ...
            base_url_match = re.search(r'const\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
            
            if base_url_match:
                base_url = base_url_match.group(1)
                print(f"📡 Yayın Sunucusu (Base URL): {base_url}")
            else:
                print("❌ 'const baseurls' satırı bulunamadı.")
                
        except Exception as e:
            print(f"❌ Event sayfası okuma hatası: {e}")

    if not base_url:
        print("⚠️ Base URL bulunamadı, varsayılan deneniyor...")
        base_url = "https://andro.226503.xyz/checklist/"

    # 4. ADIM: Kanal Listesini Oluştur
    deathless_channels = [
        ["Canlı Maç İzle", "androstreamlivebiraz1"],
        ["beIN Sports 1", "androstreamlivebs1"],
        ["beIN Sports 2", "androstreamlivebs2"],
        ["beIN Sports 3", "androstreamlivebs3"],
        ["beIN Sports 4", "androstreamlivebs4"],
        ["beIN Sports 5", "androstreamlivebs5"],
        ["beIN Sports Max 1", "androstreamlivebsm1"],
        ["beIN Sports Max 2", "androstreamlivebsm2"],
        ["S Sport 1", "androstreamlivess1"],
        ["S Sport 2", "androstreamlivess2"],
        ["Tivibu Spor 1", "androstreamlivets1"],
        ["Tivibu Spor 2", "androstreamlivets2"],
        ["Tivibu Spor 3", "androstreamlivets3"],
        ["Tivibu Spor 4", "androstreamlivets4"],
        ["Smart Spor 1", "androstreamlivesm1"],
        ["Smart Spor 2", "androstreamlivesm2"],
        ["Euro Sport 1", "androstreamlivees1"],
        ["Euro Sport 2", "androstreamlivees2"],
        ["Tabii", "androstreamlivetb"],
        ["Tabii 1", "androstreamlivetb1"],
        ["Tabii 2", "androstreamlivetb2"],
        ["Tabii 3", "androstreamlivetb3"],
        ["Tabii 4", "androstreamlivetb4"],
        ["Tabii 5", "androstreamlivetb5"],
        ["Tabii 6", "androstreamlivetb6"],
        ["Tabii 7", "androstreamlivetb7"],
        ["Tabii 8", "androstreamlivetb8"],
        ["Exxen 1", "androstreamliveexn1"],
        ["Exxen 2", "androstreamliveexn2"],
        ["Exxen 3", "androstreamliveexn3"],
        ["Exxen 4", "androstreamliveexn4"],
        ["Exxen 5", "androstreamliveexn5"],
        ["Exxen 6", "androstreamliveexn6"],
        ["Exxen 7", "androstreamliveexn7"],
        ["Exxen 8", "androstreamliveexn8"],
    ]

    results = []
    print("⚡ Linkler oluşturuluyor...")
    
    for item in deathless_channels:
        name = item[0]
        stream_id = item[1]
        
        logo_url = get_logo(name)
        stream_url = f"{base_url}{stream_id}.m3u8"
        
        # HTML içine gömülecek format: #EXTINF... \n URL
        entry = f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="TURKIYE DEATHLESS", {name}\n{stream_url}'
        results.append(entry)

    print(f"✅ DeaTHLesS: {len(results)} kanal hazırlandı.")
    return results

# --- STATİK KANALLAR (DOKUNULMADI) ---
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

# --- HTML ŞABLONU ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#000000">
    <title>Ultimate Pro Player - DeaTHLesS Edition</title>
    
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
                var config = {
                    startFragPrefetch: true,
                    enableWorker: true,
                    lowLatencyMode: true,
                    backBufferLength: 30,
                    maxMaxBufferLength: 10,
                    liveSyncDurationCount: 2,
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
    # 1. DeaTHLesS Botu Çalıştır (Linkleri Al)
    dynamic_list = fetch_deathless()

    # 2. String Haline Getir
    dynamic_m3u_content = "\n".join(dynamic_list)
    
    # 3. Statik Kanallarla Birleştir
    final_m3u_content = dynamic_m3u_content + "\n" + STATIC_CHANNELS

    # 4. HTML Şablonuna Göm
    final_html = HTML_TEMPLATE.replace("__M3U_CONTENT__", final_m3u_content)

    # 5. Dosyayı Kaydet
    with open("andro.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    
    total_channels = len(dynamic_list) + 17 # 17 Statik kanal
    print(f"🎯 İŞLEM TAMAMLANDI! 'andro.html' dosyası oluşturuldu.")
    print(f"📊 Toplam Kanal Sayısı: {total_channels}")

if __name__ == "__main__":
    main()

