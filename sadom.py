from flask import Flask, render_template_string, jsonify
import requests
import re
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Global variables for caching
streams = []
last_update = None
update_lock = threading.Lock()

# Entry URL
ENTRY_URL = "https://www.selcuksportshd78.is/"

# Channels dictionary
CHANNELS = {
    "selcukbeinsports1": "beIN Sports 1",
    "selcukobs1": "beIN Sports 1",
    "selcukbeinsports2": "beIN Sports 2",
    "selcukbeinsports3": "beIN Sports 3",
    "selcukbeinsports4": "beIN Sports 4",
    "selcukbeinsports5": "beIN Sports 5",
    "selcukbeinsportsmax1": "beIN Sports Max 1",
    "selcukbeinsportsmax2": "beIN Sports Max 2",
    "selcukssport": "Saran Sports",
    "selcukssport2": "Saran Sports 2",
    "selcuksmartspor": "Smart Spor",
    "selcuksmartspor2": "Smart Spor 2",
    "selcuktivibuspor1": "Tivibu Spor 1",
    "selcuktivibuspor2": "Tivibu Spor 2",
    "selcuktivibuspor3": "Tivibu Spor 3",
    "selcuktivibuspor4": "Tivibu Spor 4"
}

def get_active_site():
    try:
        response = requests.get(ENTRY_URL, timeout=10)
        if response.status_code == 200:
            match = re.search(r'url[](https://[^"]+)', response.text, re.IGNORECASE)
            if match:
                return match.group(1)
    except Exception:
        pass
    return None

def get_stream_links(active_site):
    if not active_site:
        return []
    
    try:
        response = requests.get(active_site, timeout=10)
        if response.status_code != 200:
            return []
        
        iframe_match = re.search(r'https://[^"]+/index\.php\?id=selcukbeinsports1', response.text)
        if not iframe_match:
            return []
        
        base_url = re.sub(r'selcukbeinsports1', '', iframe_match.group(0))
        
        stream_links = []
        for channel_id, channel_name in CHANNELS.items():
            url = base_url + channel_id
            try:
                source = requests.get(url, timeout=10).text
                # Find m3u8 URL
                m3u8_match = re.search(r[](https://[^'"]+/live/[^'"]+/playlist\.m3u8)', source)
                if m3u8_match:
                    stream_url = m3u8_match.group(1)
                else:
                    base_match = re.search(r[](https://[^'"]+/live/)', source)
                    if base_match:
                        stream_url = base_match.group(1) + f"{channel_id}/playlist.m3u8"
                    else:
                        continue
                
                stream_url = re.sub(r'[\'";].*$', '', stream_url).strip()
                if stream_url and 'http' in stream_url:  # Basic URL check
                    stream_links.append({
                        'url': stream_url,  # No base64, direct URL
                        'name': channel_name
                    })
            except Exception:
                continue
        
        return stream_links
    except Exception:
        return []

def update_streams():
    global streams, last_update
    with update_lock:
        active_site = get_active_site()
        if active_site:
            streams = get_stream_links(active_site)
            last_update = datetime.now().isoformat()
        else:
            streams = []

# Initial update
update_streams()

# Auto-update every 3 minutes
def auto_update():
    while True:
        time.sleep(180)  # 3 minutes
        update_streams()

threading.Thread(target=auto_update, daemon=True).start()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TITAN TV</title>
    <style>
        *:not(input):not(textarea) {
            user-select: none;
        }
        body {
            margin: 0;
            padding: 0;
            background-color: #000000;
            color: white;
            font-family: sans-serif;
            font-weight: 500;
            line-height: 20px;
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
        .refresh-btn {
            background: #9400d3;
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
            margin-left: 10px;
        }
        .status {
            font-size: 12px;
            color: #888;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="https://i.hizliresim.com/t75soiq.png" alt="Logo" class="logo">
        <div class="title">
            TITAN TV
            <div class="subtitle">
                <button class="refresh-btn" onclick="location.reload()">Yenile</button>
                <span class="status">Son Güncelleme: {{ last_update or 'Hiç' }}</span>
            </div>
        </div>
    </div>
    <div class="channel-list">
        {% if streams %}
            {% for stream in streams %}
            <div class="channel-item" data-href="{{ stream.url }}">
                <a>
                    <img src="https://i.hizliresim.com/t75soiq.png" alt="Logo">
                    <span>{{ stream.name }}</span>
                </a>
            </div>
            {% endfor %}
        {% else %}
            <div class="channel-item">
                <a>
                    <span>Yayın bulunamadı. Lütfen yenileyin.</span>
                </a>
            </div>
        {% endif %}
    </div>
    <div id="player-container">
        <div id="player"></div>
    </div>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/clappr/latest/clappr.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <script>
        let player = null;
        $(document).ready(function() {
            $('.channel-item').on('click', function() {
                const href = $(this).data('href');
                if (!href) return;
                $('#player-container').show();
                if (player) {
                    player.destroy();
                }
                player = new Clappr.Player({
                    source: href,
                    parentId: "#player",
                    mimeType: "application/x-mpegURL",
                    mediacontrol: { seekbar: "#181929" },
                    poster: "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnNzcXA1eHhyNzNvc3U4Z3NmdXE5amFiNWFuNjNocWR3ZXpjcXNyYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/z013AJDZs99eUWszPa/giphy.gif",
                    width: '100%',
                    height: '100%',
                    autoPlay: true,
                    hlsjsConfig: {
                        enableWorker: true,
                        debug: false
                    }
                });
                const playerElement = document.getElementById('player-container');
                if (playerElement.requestFullscreen) {
                    playerElement.requestFullscreen();
                } else if (playerElement.mozRequestFullScreen) {
                    playerElement.mozRequestFullScreen();
                } else if (playerElement.webkitRequestFullscreen) {
                    playerElement.webkitRequestFullscreen();
                } else if (playerElement.msRequestFullscreen) {
                    playerElement.msRequestFullscreen();
                }
            });
            document.addEventListener('fullscreenchange', function() {
                if (!document.fullscreenElement) {
                    $('#player-container').hide();
                    if (player) {
                        player.destroy();
                        player = null;
                    }
                }
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    global streams, last_update
    with update_lock:
        return render_template_string(HTML_TEMPLATE, streams=streams, last_update=last_update)

@app.route('/refresh')
def refresh():
    update_streams()
    return jsonify({"status": "updated", "streams_count": len(streams), "last_update": last_update})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
