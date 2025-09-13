import requests
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

CHANNELS = [
    {"id": "bein1", "source_id": "selcukbeinsports1", "name": "BeIN Sports 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/5rhmw31628798883.png", "group": "Spor"},
    {"id": "bein1", "source_id": "selcukobs1", "name": "BeIN Sports 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/5rhmw31628798883.png", "group": "Spor"},
    {"id": "bein2", "source_id": "selcukbeinsports2", "name": "BeIN Sports 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/7uv6x71628799003.png", "group": "Spor"},
    {"id": "bein3", "source_id": "selcukbeinsports3", "name": "BeIN Sports 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/u3117i1628798857.png", "group": "Spor"},
    {"id": "bein4", "source_id": "selcukbeinsports4", "name": "BeIN Sports 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/2ktmcp1628798841.png", "group": "Spor"},
    {"id": "bein5", "source_id": "selcukbeinsports5", "name": "BeIN Sports 5", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/BeIn_Sports_5_US.png", "group": "Spor"},
    {"id": "beinmax1", "source_id": "selcukbeinsportsmax1", "name": "BeIN Sports Max 1", "logo": "https://assets.bein.com/mena/sites/3/2015/06/beIN_SPORTS_MAX1_DIGITAL_Mono.png", "group": "Spor"},
    {"id": "beinmax2", "source_id": "selcukbeinsportsmax2", "name": "BeIN Sports Max 2", "logo": "http://tvprofil.com/img/kanali-logo/beIN_Sports_MAX_2_TR_logo_v2.png?1734011568", "group": "Spor"},
    {"id": "tivibu1", "source_id": "selcuktivibuspor1", "name": "Tivibu Spor 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/qadnsi1642604437.png", "group": "Spor"},
    {"id": "tivibu2", "source_id": "selcuktivibuspor2", "name": "Tivibu Spor 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/kuasdm1642604455.png", "group": "Spor"},
    {"id": "tivibu3", "source_id": "selcuktivibuspor3", "name": "Tivibu Spor 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/slwrz41642604502.png", "group": "Spor"},
    {"id": "tivibu4", "source_id": "selcuktivibuspor4", "name": "Tivibu Spor 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/59bqi81642604517.png", "group": "Spor"},
    {"id": "ssport1", "source_id": "selcukssport", "name": "S Sport 1", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923239.png", "group": "Spor"},
    {"id": "ssport2", "source_id": "selcukssport2", "name": "S Sport 2", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923321.png", "group": "Spor"},
    {"id": "smart1", "source_id": "selcuksmartspor", "name": "Smart Spor 1", "logo": "https://dsmart-static-v2.ercdn.net//resize-width/1920/content/p/el/11909/Thumbnail.png", "group": "Spor"},
    {"id": "smart2", "source_id": "selcuksmartspor2", "name": "Smart Spor 2", "logo": "https://www.dsmart.com.tr/api/v1/public/images/kanallar/SPORSMART2-gri.png", "group": "Spor"},
    {"id": "aspor", "source_id": "selcukaspor", "name": "A Spor", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/9d28401f-2d4e-4862-85e2-69773f6f45f4.png", "group": "Spor"},
    {"id": "eurosport1", "source_id": "selcukeurosport1", "name": "Eurosport 1", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/54cad412-5f3a-4184-b5fc-d567a5de7160.png", "group": "Spor"},
    {"id": "eurosport2", "source_id": "selcukeurosport2", "name": "Eurosport 2", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/a4cbdd15-1509-408f-a108-65b8f88f2066.png", "group": "Spor"},
]

def get_active_site():
    entry_url = "https://www.selcuksportshd78.is/"
    try:
        entry_source = requests.get(entry_url, headers=HEADERS, timeout=5).text
        match = re.search(r'url=(https:\/\/[^"]+)', entry_source)
        if match:
            print(f"Aktif site: {match.group(1)}")
            return match.group(1)
        else:
            print("Aktif site bulunamadı.")
            return None
    except:
        print("Giriş URL'sine erişilemedi.")
        return None

def get_base_url(active_site):
    try:
        source = requests.get(active_site, headers=HEADERS, timeout=5).text
        match = re.search(r'https:\/\/[^"]+\/index\.php\?id=selcukbeinsports1', source)
        if match:
            base_url = match.group(0).replace("selcukbeinsports1", "")
            print(f"Base URL: {base_url}")
            return base_url
        else:
            print("Base URL bulunamadı.")
            return None
    except:
        print("Aktif siteye erişilemedi.")
        return None

def fetch_streams(base_url):
    result = []
    for ch in CHANNELS:
        url = f"{base_url}{ch['source_id']}"
        try:
            source = requests.get(url, headers=HEADERS, timeout=5).text
            match = re.search(r'(https:\/\/[^\'"]+\/live\/[^\'"]+\/playlist\.m3u8)', source)
            if match:
                stream_url = match.group(1)
            else:
                match = re.search(r'(https:\/\/[^\'"]+\/live\/)', source)
                if match:
                    stream_url = f"{match.group(1)}{ch['source_id']}/playlist.m3u8"
                else:
                    continue
            stream_url = re.sub(r'[\'";].*$', '', stream_url).strip()
            if stream_url and re.match(r'^https?://', stream_url):
                print(f"{ch['name']} → {stream_url}")
                result.append((ch, stream_url))
        except:
            continue
    return result

def generate_html(streams, filename="sadom.html"):
    print(f"\nHTML dosyası yazılıyor: {filename}")
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TITAN TV</title>
    <script src="https://cdn.jsdelivr.net/npm/clappr@latest/dist/clappr.min.js"></script>
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
            background-color: #000000;
            color: white;
            font-family: sans-serif;
            font-weight: 500;
            -webkit-tap-highlight-color: transparent;
            line-height: 20px;
            -webkit-text-size-adjust: 100%;
            text-decoration: none;
        }

        a {
            text-decoration: none;
            color: white;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background-color: rgba(23, 43, 67, 0.8);
            backdrop-filter: blur(5px);
            border-bottom: 1px solid #000;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 99999;
        }

        .logo {
            width: 55px;
            height: 55px;
            margin-right: 5px;
        }

        .title {
            font-size: 16px;
            margin-right: auto;
            color: #e1e1e1;
        }

        .subtitle {
            font-size: 16px;
        }

        .channel-list {
            padding: 0;
            margin: 0;
            margin-top: 76px;
        }

        .channel-item {
            display: flex;
            align-items: center;
            background-color: #16202a;
            transition: background-color 0.3s;
            cursor: pointer;
            border-bottom: 2px solid #9400d3;
        }

        .channel-item:last-child {
            border-bottom: none;
        }

        .channel-item a {
            text-decoration: none;
            color: #e1e1e1;
            padding: 10px;
            display: flex;
            align-items: center;
            width: 100%;
        }

        .channel-item img {
            width: 55px;
            height: 55px;
            border-radius: 0px;
            margin-right: 10px;
        }

        .channel-item:hover {
            background-color: rgba(136, 141, 147, 0.9);
            outline: none;
        }

        #player-container {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: #000;
            z-index: 100000;
        }

        #player {
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="https://i.hizliresim.com/t75soiq.png" alt="Logo" class="logo">
        <div class="title">
            TITAN TV
            <div class="subtitle"></div>
        </div>
    </div>
    <div class="channel-list">
"""

    for ch, url in streams:
        html_template += f"""        <div class='channel-item' data-channel='{ch["name"]}' data-href='{url}'>
            <a><img src='{ch["logo"]}' alt='Logo'><span>{ch["name"]}</span></a>
        </div>
"""

    html_template += """    </div>

    <div id="player-container">
        <div id="player"></div>
    </div>

    <script>
        let player = null;
        document.querySelectorAll('.channel-item').forEach(item => {
            item.addEventListener('click', function() {
                const channelName = this.getAttribute('data-channel');
                const channelUrl = this.getAttribute('data-href');
                
                document.querySelector('.subtitle').textContent = channelName;
                document.getElementById('player-container').style.display = 'block';
                
                if (player) {
                    player.destroy();
                }
                
                player = new Clappr.Player({
                    source: channelUrl,
                    parentId: '#player',
                    autoPlay: false,
                    mute: false,
                    height: '100%',
                    width: '100%'
                });
            });
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                if (player) {
                    player.destroy();
                    player = null;
                }
                document.getElementById('player-container').style.display = 'none';
                document.querySelector('.subtitle').textContent = '';
            }
        });
    </script>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    print("Tamamlandı. Kanal sayısı:", len(streams))

def main():
    active_site = get_active_site()
    if not active_site:
        return
    base_url = get_base_url(active_site)
    if not base_url:
        return
    streams = fetch_streams(base_url)
    if streams:
        generate_html(streams)
    else:
        print("Hiçbir yayın alınamadı.")

if __name__ == "__main__":
    main()
