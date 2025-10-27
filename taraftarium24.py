import requests, re, os

site = "https://taraftarium24amp2.xyz/"
output_path = "taraftarium24_channels.html"

print("[+] Connecting to main site:", site)
try:
    html = requests.get(site, timeout=10).text
except:
    print("[-] Unable to reach the site!")
    exit()

links = re.findall(r'https:\/\/[a-zA-Z0-9\.\-\/]+player-[a-zA-Z0-9]+', html)
links = list(dict.fromkeys(links))

if not links:
    print("[-] No player links found.")
    exit()

print(f"[+] Found {len(links)} channels.")

channels = []
for link in links:
    referrer = re.match(r'(https:\/\/[^\/]+)', link).group(1)
    short = re.search(r'player\-([a-zA-Z0-9]+)', link).group(1).lower()

    name = short.upper()
    if re.match(r'bsn(\d+)', short):
        num = re.findall(r'\d+', short)[0]
        name = f"Bein {num}"
    elif re.match(r'mx(\d+)', short):
        num = re.findall(r'\d+', short)[0]
        name = f"Bein Max {num}"
    elif re.match(r's(\d+)', short):
        num = re.findall(r'\d+', short)[0]
        name = f"S-Sport {num}"
    elif re.match(r'tvb(\d+)', short):
        num = re.findall(r'\d+', short)[0]
        name = f"Tivibu {num}"

    print(f"[*] Scanning: {name}")

    try:
        headers = {"Referer": referrer, "User-Agent": "Mozilla/5.0"}
        page = requests.get(link, headers=headers, timeout=10).text
    except:
        print(f"[-] Failed to fetch page for {name}")
        continue

    m3u8 = re.findall(r'https?:\/\/[^\s\'"]+\.m3u8[^\s\'"]*', page)
    if not m3u8:
        print(f"[-] Stream not found for {name}")
        continue

    stream = m3u8[0]
    channels.append((name, stream))
    print(f"[+] Stream found: {name}")

# HTML dosyasını oluştur
html_content = '''<!DOCTYPE html>
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
    <div class="channel-list">'''

# Kanal listesini ekle
for name, stream_url in channels:
    html_content += f'''
        <div class='channel-item' data-channel='{name}' data-href='{stream_url}'>
            <a><img src='https://i.hizliresim.com/t75soiq.png' alt='Logo'><span>{name}</span></a>
        </div>'''

html_content += '''
    </div>

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
</html>'''

# HTML dosyasını kaydet
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n✅ HTML file saved to: {output_path}")
print(f"📺 Total channels: {len(channels)}")
