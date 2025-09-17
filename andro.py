import requests
import re
import os
import urllib.parse

# Proxy prefix
PROXY = "https://api.codetabs.com/v1/proxy/?quest="

# Domain aralığı (25–99)
active_domain = None
for i in range(25, 100):
    url = f"https://birazcikspor{i}.xyz/"
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200:
            active_domain = url
            break
    except:
        continue

if not active_domain:
    raise SystemExit("Aktif domain bulunamadı.")

# İlk kanal ID'si al
html = requests.get(active_domain, timeout=10).text
m = re.search(r'<iframe[^>]+id="matchPlayer"[^>]+src="event\.html\?id=([^"]+)"', html)
if not m:
    raise SystemExit("Kanal ID bulunamadı.")
first_id = m.group(1)

# Base URL çek
event_source = requests.get(active_domain + "event.html?id=" + first_id, timeout=10).text
b = re.search(r'var\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
if not b:
    raise SystemExit("Base URL bulunamadı.")
base_url = b.group(1)

# Kanal listesi
channels = [
    ("beIN Sport 1 HD","androstreamlivebs1","https://i.hizliresim.com/t75soiq.png"),
    ("beIN Sport 2 HD","androstreamlivebs2","https://i.hizliresim.com/t75soiq.png"),
    ("beIN Sport 3 HD","androstreamlivebs3","https://i.hizliresim.com/t75soiq.png"),
    ("beIN Sport 4 HD","androstreamlivebs4","https://i.hizliresim.com/t75soiq.png"),
    ("beIN Sport 5 HD","androstreamlivebs5","https://i.hizliresim.com/t75soiq.png"),
    ("beIN Sport Max 1 HD","androstreamlivebsm1","https://i.hizliresim.com/t75soiq.png"),
    ("beIN Sport Max 2 HD","androstreamlivebsm2","https://i.hizliresim.com/t75soiq.png"),
    ("S Sport 1 HD","androstreamlivess1","https://i.hizliresim.com/t75soiq.png"),
    ("S Sport 2 HD","androstreamlivess2","https://i.hizliresim.com/t75soiq.png"),
    ("Tivibu Sport HD","androstreamlivets","https://i.hizliresim.com/t75soiq.png"),
    ("Tivibu Sport 1 HD","androstreamlivets1","https://i.hizliresim.com/t75soiq.png"),
    ("Tivibu Sport 2 HD","androstreamlivets2","https://i.hizliresim.com/t75soiq.png"),
    ("Tivibu Sport 3 HD","androstreamlivets3","https://i.hizliresim.com/t75soiq.png"),
    ("Tivibu Sport 4 HD","androstreamlivets4","https://i.hizliresim.com/t75soiq.png"),
    ("Smart Sport 1 HD","androstreamlivesm1","https://i.hizliresim.com/t75soiq.png"),
    ("Smart Sport 2 HD","androstreamlivesm2","https://i.hizliresim.com/t75soiq.png"),
    ("Euro Sport 1 HD","androstreamlivees1","https://i.hizliresim.com/t75soiq.png"),
    ("Euro Sport 2 HD","androstreamlivees2","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii HD","androstreamlivetb","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii 1 HD","androstreamlivetb1","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii 2 HD","androstreamlivetb2","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii 3 HD","androstreamlivetb3","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii 4 HD","androstreamlivetb4","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii 5 HD","androstreamlivetb5","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii 6 HD","androstreamlivetb6","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii 7 HD","androstreamlivetb7","https://i.hizliresim.com/t75soiq.png"),
    ("Tabii 8 HD","androstreamlivetb8","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen HD","androstreamliveexn","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen 1 HD","androstreamliveexn1","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen 2 HD","androstreamliveexn2","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen 3 HD","androstreamliveexn3","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen 4 HD","androstreamliveexn4","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen 5 HD","androstreamliveexn5","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen 6 HD","androstreamliveexn6","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen 7 HD","androstreamliveexn7","https://i.hizliresim.com/t75soiq.png"),
    ("Exxen 8 HD","androstreamliveexn8","https://i.hizliresim.com/t75soiq.png"),
]

# HTML şablonu - THEOplayer iframe ile
html_template = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TITAN TV</title>
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
            background-color: #000000;
            color: white;
            font-family: sans-serif;
            font-weight: 500;
            -webkit-tap-highlight-color: transparent;
            line-height: 20px;
            -webkit-text-size-adjust: 100%;
            text-decoration: none;
        }}

        a {{
            text-decoration: none;
            color: white;
        }}

        .header {{
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
        }}

        .logo {{
            width: 55px;
            height: 55px;
            margin-right: 5px;
        }}

        .title {{
            font-size: 16px;
            margin-right: auto;
            color: #e1e1e1;
        }}

        .subtitle {{
            font-size: 16px;
        }}

        .channel-list {{
            padding: 0;
            margin: 0;
            margin-top: 76px;
            padding-bottom: 10px;
        }}

        .channel-item {{
            display: flex;
            align-items: center;
            background-color: #16202a;
            transition: background-color 0.3s;
            cursor: pointer;
            border-bottom: 2px solid #9400d3;
        }}

        .channel-item:last-child {{
            border-bottom: none;
        }}

        .channel-item a {{
            text-decoration: none;
            color: #e1e1e1;
            padding: 10px;
            display: flex;
            align-items: center;
            width: 100%;
        }}

        .channel-item img {{
            width: 55px;
            height: 55px;
            border-radius: 0px;
            margin-right: 10px;
        }}

        .channel-item:hover {{
            background-color: rgba(136, 141, 147, 0.9);
            outline: none;
        }}

        #player-container {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: #000;
            z-index: 100000;
        }}

        #player-wrapper {{
            width: 100%;
            height: 100%;
            position: relative;
        }}
        
        #theoplayer-iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .back-button {{
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 100001;
            background-color: rgba(0, 0, 0, 0.5);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
        }}
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
        {channel_items}
    </div>

    <div id="player-container">
        <div id="player-wrapper">
            <iframe id="theoplayer-iframe" frameborder="0" allowfullscreen allow="autoplay; encrypted-media"></iframe>
        </div>
        <button class="back-button" onclick="closePlayer()">✖ Kapat</button>
    </div>

    <script>
        function playChannel(channelUrl, channelName) {{
            document.querySelector('.subtitle').textContent = channelName;
            document.getElementById('player-container').style.display = 'block';
            
            // THEOplayer iframe URL'sini oluştur
            const encodedUrl = encodeURIComponent(channelUrl);
            const theoUrl = `https://cdn.theoplayer.com/demos/iframe/theoplayer.html?autoplay=true&muted=false&preload=none&src=${{encodedUrl}}`;
            
            // IFrame source'unu ayarla
            document.getElementById('theoplayer-iframe').src = theoUrl;
        }}
        
        function closePlayer() {{
            // IFrame source'unu temizle (player'ı durdur)
            document.getElementById('theoplayer-iframe').src = '';
            document.getElementById('player-container').style.display = 'none';
            document.querySelector('.subtitle').textContent = '';
        }}

        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closePlayer();
            }}
        }});
    </script>
</body>
</html>'''

# Kanal HTML öğelerini oluştur
channel_items = ""
for name, cid, logo in channels:
    full_url = f"{base_url}{cid}.m3u8"
    proxy_url = PROXY + full_url
    # URL'yi encode et
    encoded_url = urllib.parse.quote(proxy_url, safe='')
    channel_items += f"<div class='channel-item' onclick=\"playChannel('{proxy_url}', '{name}')\">\n"
    channel_items += f"    <a><img src='{logo}' alt='Logo'><span>{name}</span></a>\n"
    channel_items += "</div>\n"

# HTML dosyasını oluştur
html_output = html_template.format(channel_items=channel_items)

with open("andro.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("✅ andro.html THEOplayer iframe ile oluşturuldu.")
