import requests
import re
import sys
import json
import os

# API URL'ini statik olarak tanımlıyoruz, çünkü dinamik çekim sürekli başarısız oluyor.
API_URL = "https://maqrizi.com/domain.php" 
LOGO_URL = "https://i.hizliresim.com/ska5t9e.jpg"
GROUP_TITLE = "DENGE-SPORTS"
OUTPUT_FILE = "Denge-iptv.m3u"

# Kanal ID'leri ve İsimleri Sözlüğü
CHANNEL_LIST = {
    "yayinzirve": "beIN Sports 1", "yayininat": "beIN Sports 1 (Inat)", "yayin1": "beIN Sports 1 (Yayin1)",
    "yayinb2": "beIN Sports 2", "yayinb3": "beIN Sports 3", "yayinb4": "beIN Sports 4", 
    "yayinb5": "beIN Sports 5", "yayinbm1": "beIN Sports 1 Max", "yayinbm2": "beIN Sports 2 Max",
    "yayinss": "Saran Sports 1", "yayinss2": "Saran Sports 2", "yayint1": "Tivibu Sports 1", 
    "yayint2": "Tivibu Sports 2", "yayint3": "Tivibu Sports 3", "yayint4": "Tivibu Sports 4", 
    "yayinsmarts": "Smart Sports", "yayinsms2": "Smart Sports 2", "yayintrtspor": "TRT Spor", 
    "yayintrtspor2": "TRT Spor 2", "yayinas": "A Spor", "yayinatv": "ATV", "yayintv8": "TV8", 
    "yayintv85": "TV8.5", "yayinnbatv": "NBA TV", "yayinex1": "Tâbii 1", "yayinex2": "Tâbii 2", 
    "yayinex3": "Tâbii 3", "yayinex4": "Tâbii 4", "yayinex5": "Tâbii 5", "yayinex6": "Tâbii 6", 
    "yayinex7": "Tâbii 7", "yayinex8": "Tâbii 8"
}

# --- FONKSİYONLAR ---

def find_active_domain(base_url_prefix, tld):
    """Aktif domaini bulur (67-199 aralığı)."""
    print("🚀 Aktif Alan Adı Aranıyor (67 - 199)...")
    for i in range(67, 200):
        url = f"{base_url_prefix}{i}{tld}"
        try:
            response = requests.head(url, timeout=3)
            if 200 <= response.status_code < 400:
                print(f"✅ Aktif Domain Bulundu: {url}")
                return url
        except requests.exceptions.RequestException:
            continue
    print("❌ 67'den 199'a kadar aktif domain bulunamadı.")
    return None

def fetch_base_url():
    """Statik API URL'i üzerinden Base URL'i çeker."""
    print(f"🔍 Base URL JSON API'den Çekiliyor: {API_URL}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'
    }
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status() 
        data = response.json()
        
        if "baseurl" in data:
            baseurl = data["baseurl"]
            print(f"✅ Base URL Çekildi: {baseurl}")
            return baseurl
        else:
            print("❌ API yanıtında 'baseurl' anahtarı bulunamadı.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API Çekme Hatası: {e}")
        return None
    except json.JSONDecodeError:
        print("❌ API yanıtı geçerli bir JSON formatında değil.")
        return None

def generate_m3u_playlist(active_domain, base_url):
    """M3U8 linklerini birleştirip M3U dosyasını oluşturur."""
    m3u_content = ["#EXTM3U"]

    print("\n📝 Tüm Kanallar İçin M3U8 Linkleri Oluşturuluyor...")

    for channel_id, channel_name in CHANNEL_LIST.items():
        stream_file = f"{channel_id}.m3u8"
        final_m3u8_link = base_url + stream_file
        
        # M3U Başlık Satırı (Logo ve Grup Başlığı)
        header_line = f'#EXTINF:-1 tvg-logo="{LOGO_URL}" group-title="{GROUP_TITLE}", {channel_name}'
        
        # VLC/Oynatıcı İçin Referer Bilgisi
        referer_line = f'#EXTVLCOPT:http-referrer={active_domain}'
        
        # Linkin Kendisi
        link_line = final_m3u8_link
        
        m3u_content.append(header_line)
        m3u_content.append(referer_line)
        m3u_content.append(link_line)
        
        print(f"   -> Eklendi: {channel_name}")
    
    # Dosyaya Yazma
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(m3u_content))
        print(f"\n✨ BAŞARILI: {len(CHANNEL_LIST)} kanal için M3U dosyası oluşturuldu: {OUTPUT_FILE}")
        print(f"Dosyayı Pydroid'in klasöründe bulabilirsiniz.")
    except IOError as e:
        print(f"\n❌ DOSYA YAZMA HATASI: {e}")

# --- ANA ÇALIŞMA BLOĞU ---

def run_all():
    base_url_prefix = "https://dengetv"
    tld = ".live"

    # 1. Aktif Domaini Bul
    active_domain = find_active_domain(base_url_prefix, tld)
    if not active_domain:
        return

    print("-" * 30)

    # 2. Base URL'i Çek
    base_url = fetch_base_url()
    if not base_url:
        return

    print("-" * 30)

    # 3. M3U Playlistini Oluştur
    generate_m3u_playlist(active_domain, base_url)

if __name__ == "__main__":
    run_all()
      
