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
# AtomSporTV kanallarıyla eşleşecek şekilde genişletildi/ayıklandı.
CHANNEL_LOGOS = {
    "BEIN SPORTS 1": "https://i.hizliresim.com/lkl7u2r.png",
    "BEIN SPORTS 2": "https://i.hizliresim.com/pvr9h26.png",
    "BEIN SPORTS 3": "https://i.hizliresim.com/ozrfqya.png",
    "BEIN SPORTS 4": "https://i.hizliresim.com/kbhvyeh.png",
    "S SPORT": "https://i.hizliresim.com/35ndyy0.png",
    "S SPORT 2": "https://i.imgur.com/mbF7SLI.png",
    "TİVİBU SPOR 1": "https://i.hizliresim.com/nyyqh1f.png",
    "TİVİBU SPOR 2": "https://i.hizliresim.com/mr3sv0j.png",
    "TİVİBU SPOR 3": "https://i.hizliresim.com/rcz77hb.png",
    # Statik kanallar için olanlar da tutuluyor:
    "NBA TV": "https://i.ibb.co/VSSByY9/NBA-TV.png",
    "Tabii": "https://i.hizliresim.com/ojqbhcx.png",
    "Tabii 1": "https://i.ibb.co/0cYJYvB/tabi1.png",
    "Tabii 2": "https://i.ibb.co/VNpTh0J/tabi2.png",
    "Tabii 3": "https://i.ibb.co/D7NwYrT/tabi3.png",
    "Tabii 4": "https://i.ibb.co/2h6yJJt/tabi4.png",
    "Tabii 5": "https://i.ibb.co/QFZnFHg/tabi5.png",
    "Tabii 6": "https://i.ibb.co/s386Cn7/tabi6.png",
}

DEFAULT_LOGO = "https://i.hizliresim.com/t75soiq.png"

def get_logo(channel_name):
    # İsim eşleştirmesi yaparken büyük/küçük harf duyarlılığını azaltmak için.
    # AtomSporTV isimleri hep BÜYÜK harfli geldiği için bu önemli.
    normalized_name = channel_name.upper().strip()
    return CHANNEL_LOGOS.get(normalized_name, DEFAULT_LOGO)


# --- ATOMSPOR TV TARAMA MANTIĞI ---

START_URL = "https://url24.link/AtomSporTV"

def get_base_domain():
    """Ana domain'i bul"""
    print("🔍 AtomSporTV için aktif domain aranıyor...")
    
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://url24.link/'
    
    try:
        # 1. Adım: İlk Yönlendirmeyi Yakala
        response = requests.get(START_URL, headers=local_headers, allow_redirects=False, timeout=10)
        
        if 'location' in response.headers:
            location1 = response.headers['location']
            print(f"   -> İlk Konum: {location1}")
            
            # 2. Adım: İkinci Yönlendirmeyi Yakala (Asıl Domain)
            response2 = requests.get(location1, headers=local_headers, allow_redirects=False, timeout=10)
            
            if 'location' in response2.headers:
                base_domain = response2.headers['location'].strip().rstrip('/')
                print(f"✅ Ana Domain Bulundu: {base_domain}")
                return base_domain
        
        # Varsayılan (yedek) domain
        fallback_domain = "https://www.atomsportv480.top"
        print(f"⚠️ Domain bulunamadı, varsayılan kullanılıyor: {fallback_domain}")
        return fallback_domain
        
    except Exception as e:
        fallback_domain = "https://www.atomsportv480.top"
        print(f"❌ Domain hatası: {e}. Varsayılan kullanılıyor: {fallback_domain}")
        return fallback_domain

def get_channel_m3u8(channel_id, base_domain):
    """PHP mantığı ile m3u8 linkini al"""
    local_headers = HEADERS.copy()
    local_headers['Referer'] = base_domain # Referer güncellendi
    
    try:
        # 1. matches?id= endpoint
        matches_url = f"{base_domain}/matches?id={channel_id}"
        response = requests.get(matches_url, headers=local_headers, timeout=10)
        html = response.text
        
        # 2. fetch URL'sini bul
        fetch_match = re.search(r'fetch\("(.*?)"', html)
        if not fetch_match:
            fetch_match = re.search(r'fetch\(\s*["\'](.*?)["\']', html)
        
        if fetch_match:
            fetch_url = fetch_match.group(1).strip()
            
            # 3. fetch URL'sine istek yap
            custom_headers = local_headers.copy()
            custom_headers['Origin'] = base_domain
            
            if not fetch_url.endswith(channel_id):
                # Bazı siteler fetch url'ye id'yi otomatik ekler, eklemeyenler için birleştirme
                fetch_url = f"{base_domain}{fetch_url}{channel_id}" 
            
            response2 = requests.get(fetch_url, headers=custom_headers, timeout=10)
            fetch_data = response2.text
            
            # 4. m3u8 linkini bul
            # Öncelikli Pattern (deismackanal)
            m3u8_match = re.search(r'"deismackanal":"(.*?)"', fetch_data)
            
            # İkinci Pattern (stream/url/source)
            if not m3u8_match:
                m3u8_match = re.search(r'"(?:stream|url|source)":\s*"(.*?\.m3u8)"', fetch_data)
                
            if m3u8_match:
                m3u8_url = m3u8_match.group(1).replace('\\', '')
                return m3u8_url
        
        return None
        
    except Exception as e:
        return None

def fetch_atomsportv():
    print("--- AtomSporTV Bot Çalışıyor ---")
    
    # 1. ADIM: Aktif Domaini Bul
    base_domain = get_base_domain()
    
    # Sadece TV Kanalları listesi
    tv_channels = [
        ("bein-sports-1", "BEIN SPORTS 1"),
        ("bein-sports-2", "BEIN SPORTS 2"),
        ("bein-sports-3", "BEIN SPORTS 3"),
        ("bein-sports-4", "BEIN SPORTS 4"),
        ("s-sport", "S SPORT"),
        ("s-sport-2", "S SPORT 2"),
        ("tivibu-spor-1", "TİVİBU SPOR 1"),
        ("tivibu-spor-2", "TİVİBU SPOR 2"),
        ("tivibu-spor-3", "TİVİBU SPOR 3"),
        ("tivibu-spor-4", "TİVİBU SPOR 4"), # Bu da eklenebilir
    ]
    
    results = []
    working_count = 0
    print("\n⚡ Kanal Linkleri Çekiliyor...")
    
    for channel_id, name in tv_channels:
        m3u8_url = get_channel_m3u8(channel_id, base_domain)
        
        if m3u8_url:
            logo_url = get_logo(name)
            
            # HTML içine gömülecek format: #EXTINF... \n #EXTVLCOPT... \n URL
            entry = (
                f'#EXTINF:-1 tvg-logo="{logo_url}" group-title="TURKIYE ATOMSPOR", {name}\n'
                f'#EXTVLCOPT:http-referrer={base_domain}\n'
                f'#EXTVLCOPT:http-user-agent={HEADERS["User-Agent"]}\n'
                f'{m3u8_url}'
            )
            results.append(entry)
            print(f"   [✓] {name} eklendi.")
            working_count += 1
        else:
            print(f"   [✗] {name} çekilemedi.")

    print(f"\n✅ AtomSporTV: {working_count} çalışan kanal hazırlandı.")
    return results

# --- STATİK KANALLAR (DOKUNULMADI) ---
# group-title değiştirildi (ATOMSPOR için)
STATIC_CHANNELS = """
#EXTINF:-1 tvg-id="" tvg-name="HT SPOR HD" tvg-logo="https://i.hizliresim.com/mmazkt2.png" group-title="TURKIYE ATOMSPOR",HT SPOR HD
https://ciner.daioncdn.net/ht-spor/ht-spor.m3u8?app=web
#EXTINF:-1 tvg-id="" tvg-name="NBA SPORTS HD" tvg-logo="https://i.ibb.co/VSSByY9/NBA-TV.png" group-title="TURKIYE ATOMSPOR",NBA SPORTS HD
https://ww.dooballfree.vip/live/nba/playlist.m3u8
#EXTINF:-1 tvg-id="" tvg-name="A SPOR HD" tvg-logo="https://i.ibb.co/NVcr0ST/A-SPOR.png" group-title="TURKIYE ATOMSPOR",A SPOR HD
https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/aspor/aspor.m3u8
#EXTINF:-1 tvg-id="" tvg-name="TRT SPOR HD" tvg-logo="https://i.ibb.co/H4k7r31/TRT-SPOR.png" group-title="TURKIYE ATOMSPOR",TRT SPOR HD
https://tv-trtspor1.medya.trt.com.tr/master.m3u8
#EXTINF:-1 tvg-id="" tvg-name="TRT SPOR ★ HD" tvg-logo="https://i.ibb.co/rH9TkLx/TRT-SPOR-YILDIZ.png" group-title="TURKIYE ATOMSPOR",TRT SPOR ★ HD
https://tv-trtspor2.medya.trt.com.tr/master.m3u8
#EXTINF:-1 tvg-id="" tvg-name="TJK SPOR HD" tvg-logo="https://i.ibb.co/WVwxNCY/TJK-TV.png" group-title="TURKIYE ATOMSPOR",TJK SPOR HD
https://tjktv-live.tjk.org/tjktv_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="FB SPOR HD" tvg-logo="https://i.ibb.co/5kTcBJM/FB-TV.png" group-title="TURKIYE ATOMSPOR",FB SPOR HD
https://fbtv.fenerbahce.org/fenerbahcetv.stream_720p/playlist.m3u8
#EXTINF:-1 tvg-id="" tvg-name="SPORTS HD" tvg-logo="https://i.ibb.co/VxHMGyp/SportsTV.png" group-title="TURKIYE ATOMSPOR",SPORTS HD
https://live.sportstv.com.tr/hls/low/sportstv_fhd/index.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport HD" tvg-logo="https://i.hizliresim.com/ojqbhcx.png" group-title="TURKIYE ATOMSPOR",Tabii Sport HD
https://beert7sqimrk0bfdupfgn6qew.medya.trt.com.tr/master.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 1 HD" tvg-logo="https://i.ibb.co/0cYJYvB/tabi1.png" group-title="TURKIYE ATOMSPOR",Tabii Sport 1 HD
https://iaqzu4szhtzeqd0edpsayinle.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 2 HD" tvg-logo="https://i.ibb.co/VNpTh0J/tabi2.png" group-title="TURKIYE ATOMSPOR",Tabii Sport 2 HD
https://klublsslubcgyiz7zqt5bz8il.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 3 HD" tvg-logo="https://i.ibb.co/D7NwYrT/tabi3.png" group-title="TURKIYE ATOMSPOR",Tabii Sport 3 HD
https://ujnf69op16x2fiiywxcnx41q8.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 4 HD" tvg-logo="https://i.ibb.co/2h6yJJt/tabi4.png" group-title="TURKIYE ATOMSPOR",Tabii Sport 4 HD
https://bfxy3jgeydpbphtk8qfqwm3hr.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 5 HD" tvg-logo="https://i.ibb.co/QFZnFHg/tabi5.png" group-title="TURKIYE ATOMSPOR",Tabii Sport 5 HD
https://z3mmimwz148csv0vaxtphqspf.medya.trt.com.tr/master_1080p.m3u8
#EXTINF:-1 tvg-id="" tvg-name="Tabii Sport 6 HD" tvg-logo="https://i.ibb.co/s386Cn7/tabi6.png" group-title="TURKIYE ATOMSPOR",Tabii Sport 6 HD
https://vbtob9hyq58eiophct5qctxr2.medya.trt.com.tr/master_1080p.m3u8
"""

# --- HTML ŞABLONU (AYNEN KORUNDU) ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#000000">
    <title>Ultimate Pro Player - AtomSporTV Edition</title>
    
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
                hls.config.pLoader = (context) => new HlsPlayerLoader(context, ch.referrer, ch.userAgent);
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

        // Custom HLS Loader for Referrer/User-Agent Support
        function HlsPlayerLoader(context, referrer, userAgent) {
            this.context = context;
            this.stats = { trequest: performance.now(), tfirst: 0, tload: 0, tabort: 0, loaded: 0, total: 0 };
            this.xhr = null;
            this.referrer = referrer;
            this.userAgent = userAgent;
        }

        HlsPlayerLoader.prototype.load = function(context, config, callbacks) {
            this.context = context;
            this.callbacks = callbacks;
            this.stats.trequest = performance.now();
            const xhr = this.xhr = new XMLHttpRequest();
            xhr.onreadystatechange = this.onreadystatechange.bind(this);
            xhr.onprogress = this.onprogress.bind(this);
            xhr.responseType = context.responseType || '';
            xhr.open('GET', context.url, true);
            
            // Custom Headers ekleniyor
            if (this.referrer) xhr.setRequestHeader('Referer', this.referrer);
            if (this.userAgent) xhr.setRequestHeader('User-Agent', this.userAgent);

            xhr.send();
        };

        HlsPlayerLoader.prototype.onreadystatechange = function(event) {
            const xhr = event.currentTarget;
            if (xhr.readyState === 4) {
                this.stats.tload = performance.now();
                if (xhr.status >= 200 && xhr.status < 300) {
                    this.stats.loaded = this.stats.total = xhr.response.length || xhr.responseText.length || 0;
                    this.callbacks.onSuccess(this.context, this.stats, { code: xhr.status, data: xhr.response || xhr.responseText });
                } else {
                    this.callbacks.onError(this.context, this.stats, { code: xhr.status, text: xhr.statusText });
                }
            }
        };

        HlsPlayerLoader.prototype.onprogress = function(event) {
            if (event.lengthComputable) {
                this.stats.loaded = event.loaded;
                this.stats.total = event.total;
                this.callbacks.onProgress(this.context, this.stats, event.loaded / event.total);
            }
        };

        HlsPlayerLoader.prototype.abort = function() {
            const xhr = this.xhr;
            if (xhr && xhr.readyState !== 4) {
                this.stats.tabort = performance.now();
                xhr.abort();
            }
        };

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
                // Kontroller 0: Rewind, 1: Play/Pause, 2: Forward, 3: Fit
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
            
            // Eğer arayüz görünmüyorsa, sadece Ok/Enter gösterir, yukarı/aşağı kanal değiştirir.
            if (!uiLayer.classList.contains('visible') && e.key !== 'Enter' && e.key !== 'Ok') {
                if (e.key === 'ArrowUp' || e.key === 'ChannelUp') {
                    playChannel(currentChannelIndex - 1); 
                    return;
                }
                if (e.key === 'ArrowDown' || e.key === 'ChannelDown') {
                    playChannel(currentChannelIndex + 1); 
                    return;
                }
            }


            switch(e.key) {
                case 'ArrowUp':
                case 'ChannelUp':
                    if (focusArea === 'none') {
                        // Eğer UI yoksa, sadece kanal değiştirme
                        playChannel(currentChannelIndex - 1); 
                    } else if (focusArea === 'channels') {
                        focusArea = 'controls';
                        focusedControlIndex = 1; // Ortadaki Play tuşuna odaklan
                        updateFocusVisuals();
                    }
                    break;
                case 'ArrowDown':
                case 'ChannelDown':
                    if (focusArea === 'none') {
                        // Eğer UI yoksa, sadece kanal değiştirme
                        playChannel(currentChannelIndex + 1); 
                    } else if (focusArea === 'controls') {
                        focusArea = 'channels';
                        focusedChannelIndex = currentChannelIndex; // Oynatılan kanala odaklan
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
                        focusArea = 'channels'; // Default olarak kanallara odaklan
                        focusedChannelIndex = currentChannelIndex;
                        updateFocusVisuals();
                    } else {
                        if (focusArea === 'channels') {
                            playChannel(focusedChannelIndex);
                            hideUI(); // Kanal seçildikten sonra arayüzü gizle
                        }
                        else if (focusArea === 'controls') {
                            if (focusedControlIndex === 0) seek(-10);
                            if (focusedControlIndex === 1) togglePlay();
                            if (focusedControlIndex === 2) seek(10);
                            if (focusedControlIndex === 3) toggleFit();
                            updateFocusVisuals();
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
            let currentReferrer = "";
            let currentUserAgent = "";

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
                    
                    t = { name: name, logo: logoMatch ? logoMatch[1] : "", referrer: "", userAgent: "" };
                    currentReferrer = "";
                    currentUserAgent = "";
                } else if (l.startsWith('#EXTVLCOPT:http-referrer=')) {
                    currentReferrer = l.split('=')[1].trim();
                } else if (l.startsWith('#EXTVLCOPT:http-user-agent=')) {
                    currentUserAgent = l.split('=')[1].trim();
                } else if(l.startsWith('http')) {
                    channels.push({...t, url: l, referrer: currentReferrer, userAgent: currentUserAgent});
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
    # 1. AtomSporTV Botu Çalıştır (Linkleri Al)
    dynamic_list = fetch_atomsportv()

    # 2. String Haline Getir
    dynamic_m3u_content = "\n".join(dynamic_list)
    
    # 3. Statik Kanallarla Birleştir
    final_m3u_content = dynamic_m3u_content + "\n" + STATIC_CHANNELS

    # 4. HTML Şablonuna Göm
    # HTML kodundaki HLS.js Loader kısmı, #EXTVLCOPT referer/user-agent değerlerini okuyacak şekilde güncellendi.
    final_html = HTML_TEMPLATE.replace("__M3U_CONTENT__", final_m3u_content)

    # 5. Dosyayı Kaydet
    output_filename = "atom.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    # Statik kanalların sayısı (elle sayıldı)
    static_channel_count = STATIC_CHANNELS.count('#EXTINF')
    total_channels = len(dynamic_list) + static_channel_count 
    
    print(f"🎯 İŞLEM TAMAMLANDI! '{output_filename}' dosyası oluşturuldu.")
    print(f"📊 Toplam Kanal Sayısı: {total_channels}")

if __name__ == "__main__":
    main()
