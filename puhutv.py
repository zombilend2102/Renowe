import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os

main_url = "https://puhutv.com/"
diziler_url = "https://puhutv.com/dizi"
html_file = "puhutv.html"
json_file = "puhutv.json"

def get_series_details(series_id):
    url = f"https://appservice.puhutv.com/service/serie/getSerieInformations?id={series_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()[0]
    return {"title": "", "seasons": []}

def get_stream_urls(season_slug):
    url = urljoin(main_url, season_slug)
    r = requests.get(url)
    if r.status_code != 200:
        return []

    soup = BeautifulSoup(r.content, "html.parser")
    try:
        content = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).string)["props"]["pageProps"]["episodes"]["data"]
    except:
        return []

    episodes = []
    for ep in content["episodes"]:
        episodes.append({
            "id": ep["id"],
            "name": ep["name"],
            "img": ep["image"],
            "url": urljoin(main_url, ep["slug"]),
            "stream_url": f"https://dygvideo.dygdigital.com/api/redirect?PublisherId=29&ReferenceId={ep['video_id']}&SecretKey=NtvApiSecret2014*&.m3u8"
        })
    return episodes

def get_all_content():
    r = requests.get(diziler_url)
    if r.status_code != 200:
        return []

    soup = BeautifulSoup(r.content, "html.parser")
    try:
        container_items = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).string)["props"]["pageProps"]["data"]["data"]["container_items"]
    except:
        return []

    series_list = []
    seen_series = set()  # Aynı dizilerin tekrar çekilmesini önlemek için küme
    for item in container_items:
        for content in item["items"]:
            if content["id"] not in seen_series:  # Aynı ID kontrolü
                seen_series.add(content["id"])
                series_list.append(content)

    all_series = []
    for series in tqdm(series_list, desc="Processing Series"):
        series_id = series["id"]
        series_name = series["name"]
        series_slug = series["meta"]["slug"]
        series_img = series["image"]

        series_details = get_series_details(series_id)
        if not series_details["seasons"]:
            continue

        temp_series = {
            "id": series_id,
            "name": series_name,
            "img": series_img,
            "url": urljoin(main_url, series_slug),
            "episodes": []
        }

        for season in series_details["seasons"]:
            season_slug = season["slug"]
            season_name = season["name"]
            episodes = get_stream_urls(season_slug)
            for ep in episodes:
                temp_name = f"{season_name} - {ep['name']}"
                temp_name = temp_name.replace(". ", ".").replace(" - ", " ")
                ep["full_name"] = f"{series_name} {temp_name}"
                temp_series["episodes"].append(ep)

        all_series.append(temp_series)

    return all_series

def create_json_file(data):
    json_data = {}
    for idx, series in enumerate(data, 1):
        json_data[str(idx)] = {
            "resim": series["img"],
            "bolumler": [
                {"ad": ep["full_name"], "link": ep["stream_url"]}
                for ep in series["episodes"]
            ]
        }
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    print(f"{json_file} başarıyla oluşturuldu!")

def create_html_file(data):
    html_template = """<!DOCTYPE html>
<html lang="tr">
<head>
    <title>TITAN TV YERLİ VOD</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css?family=PT+Sans:700i" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://kit.fontawesome.com/bbe955c5ed.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@splidejs/splide@4.1.4/dist/js/splide.min.js"></script>
    <script src="https://ssl.p.jwpcdn.com/player/v/8.22.0/jwplayer.js"></script>
    <style>
        /* [Buradaki stil kısmı sizin verdiğiniz HTML'deki stil ile aynı kalacak] */
        {css_styles}
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
        {series_html}
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
        jwplayer.key = "cLGMn8T20tGvW+0eXPhq4NNmLB57TrscPjd1IyJF84o=";
        var diziler = {json_data};

        let currentScreen = 'anaSayfa';
        let jwPlayerInstance = null;

        function showBolumler(diziID) {
            sessionStorage.setItem('currentDiziID', diziID);
            var listContainer = document.getElementById("bolumListesi");
            listContainer.innerHTML = "";
            
            if (diziler[diziID]) {
                diziler[diziID].bolumler.forEach(function(bolum) {
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
            if (jwPlayerInstance) {
                jwPlayerInstance.remove();
                jwPlayerInstance = null;
            }
            document.getElementById("main-player").innerHTML = "";
            document.getElementById("main-player").innerHTML = '<div id="jw-player"></div>';
            jwPlayerInstance = jwplayer("jw-player").setup({
                file: streamUrl,
                title: diziler[diziID].bolumler.find(b => b.link === streamUrl).ad,
                image: diziler[diziID].resim,
                width: "100%",
                height: "100%",
                primary: "html5",
                autostart: true,
                playbackRateControls: [0.5, 1, 1.5, 2]
            });
        }

        function geriPlayer() {
            document.getElementById("playerpanel").style.display = "none";
            document.getElementById("bolumler").classList.remove("hidden");
            currentScreen = 'bolumler';
            var currentDiziID = sessionStorage.getItem('currentDiziID');
            history.replaceState({ page: 'bolumler', diziID: currentDiziID }, '', `#bolumler-${currentDiziID}`);
            if (jwPlayerInstance) {
                jwPlayerInstance.remove();
                jwPlayerInstance = null;
            }
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
                if (jwPlayerInstance) {
                    jwPlayerInstance.remove();
                    jwPlayerInstance = null;
                }
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
            if (query === "") {
                var series = document.querySelectorAll('.filmpanel');
                series.forEach(function(serie) {
                    serie.style.display = "block";
                });
            }
        }
    </script>
</body>
</html>"""

    # CSS stil dosyasını sizin verdiğiniz HTML'den alın
    css_styles = """
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
            bottom: 25px;
        }
        .resimust {
            height: 25px;
            width: 100%;
            position: absolute;
            bottom: 0px;
            overflow: hidden;
            box-sizing: border-box;
            padding: 0px 5px;
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
        .dispanel {
            width: 100%;
            height: 100vh;
            display: table;
            margin: 0px auto;
            box-sizing: border-box;
            padding: 0px;
            overflow: hidden;
            position: absolute;
            top: 0;
            left: 0;
            background: #00040d;
        }
        .icpanel {
            display: table-cell;
            vertical-align: middle;
            text-align: center;
        }
        .filmsayfapanel {
            background: #15161a;
            color: #fff;
            width: 70%;
            margin: 20px auto;
            box-sizing: border-box;
            overflow: hidden;
            padding: 10px;
            box-shadow: 1px 5px 10px rgba(0,0,0,0.1);
            border: 1px solid #323442;
            border-radius: 15px;
        }
        .filmbasliklarust {
            width: 100%;
        }
        .filmsayfaresim {
            width: 20%;
            float: left;
            margin-right: 2%;
            height: 230px;
        }
        .filmsayfaresim img {
            width: 100%;
            height: 100%;
            border-radius: 15px;
        }
        .filmbasliklarsag {
            float: left;
            width: 32%;
            margin-left: 2%;
        }
        .ozetpanel {
            float: left;
            width: 42%;
            margin-left: 2%;
            height: 230px;
            overflow-x: hidden;
            box-sizing: border-box;
            background: #15161a;
            border: 1px solid #323442;
            padding: 3px;
            border-radius: 15px;
        }
        .ozetpanel::-webkit-scrollbar {
            width: 0px;
            background-color: #323442;
        }
        .filmsayfabaslik {
            height: 40px;
            line-height: 40px;
            color: #fff;
            font-weight: 700;
            background: #15161a;
            border: 1px solid #323442;
            box-sizing: border-box;
            border-radius: 15px;
        }
        .filsayfafilmisim {
            padding: 10px 0px;
            color: #ccc;
            font-weight: 500;
        }
        .filsayfafilmisim2 {
            padding: 10px 0px;
            color: #ccc;
        }
        a {
            text-decoration: none;
        }
        a .buton {
            height: 40px;
            line-height: 40px;
            width: 200px;
            text-align: center;
            background: #572aa7;
            margin: 10px auto;
            transition: .35s;
            color: #fff;
        }
        .buton:hover {
            background: #fff;
            color: #000;
            transform: scale(1.1);
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
        #main-player {
            width: 100%;
            height: 100%;
            background: #000;
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
            align-self: flex-start;
        }
        .player-geri-btn:hover {
            background: #6b3ec7;
            transition: background 0.3s;
        }
        @media(max-width:900px) {
            .filmpanel {
                width: 17%;
                height: 220px;
                margin: 1.5%;
            }
            .slider-container .slider-slide {
                flex-basis: 20%;
            }
        }
        @media(max-width:550px) {
            .filmisimpanel {
                height: 190px;
                margin-top: -190px;
            }
            .filmpanel {
                width: 31.33%;
                height: 190px;
                margin: 1%;
            }
            .filmsayfaresim {
                width: 48%;
                float: left;
            }
            .filmsayfapanel {
                background: #15161a;
                color: #fff;
                width: 90%;
                height: auto;
            }
            .filmbasliklarsag {
                float: left;
                width: 100%;
                margin-top: 20px;
                margin-left: 0px;
            }
            .ozetpanel {
                float: left;
                width: 48%;
                height: 230px;
            }
            .slider-container .slider-slide {
                flex-basis: 33.33%;
            }
            .playerpanel {
                height: 100vh;
            }
            #main-player {
                height: calc(100% - 60px);
            }
        }
    """

    # Dizi HTML içeriğini oluştur
    series_html = ""
    for idx, series in enumerate(data, 1):
        series_html += f"""
        <div class="filmpanel" onclick="showBolumler('{idx}')">
            <div class="filmresim"><img src="{series['img']}"></div>
            <div class="filmisimpanel">
                <div class="filmisim">{series['name']}</div>
            </div>
        </div>
        """

    # JSON verisini oluştur
    json_data = {}
    for idx, series in enumerate(data, 1):
        json_data[str(idx)] = {
            "resim": series["img"],
            "bolumler": [
                {"ad": ep["full_name"], "link": ep["stream_url"]}
                for ep in series["episodes"]
            ]
        }
    json_data_str = json.dumps(json_data, ensure_ascii=False)

    # HTML dosyasını oluştur
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_template.format(css_styles=css_styles, series_html=series_html, json_data=json_data_str))
    print(f"{html_file} başarıyla oluşturuldu!")

def main():
    data = get_all_content()
    create_json_file(data)  # JSON dosyasını oluştur
    create_html_file(data)  # HTML dosyasını oluştur

if __name__ == "__main__":
    main()
