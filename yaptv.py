import requests

def check_domain_availability(domain):
    """Domain'in gerçekten erişilebilir olup olmadığını kontrol et"""
    test_urls = [
        f"{domain}/wp-content/themes/ikisifirbirdokuz/match-center.php?id=5062",
        domain  # Ana sayfayı da kontrol et
    ]
    
    for test_url in test_urls:
        try:
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200:
                print(f"✓ {test_url} erişilebilir")
                return True
        except requests.exceptions.RequestException as e:
            print(f"✗ {test_url} erişilemez: {e}")
    
    return False

def find_highest_active_domain():
    """En yüksek numaralı erişilebilir domain'i bul"""
    potential_domains = []
    
    # Önce tüm domain'leri tarıyoruz
    for num in range(132, 151):
        domain = f"https://betyaptv{num}.live"
        test_url = f"{domain}/wp-content/themes/ikisifirbirdokuz/match-center.php?id=5062"
        
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                print(f"[POTANSİYEL] {domain} - HTTP 200")
                potential_domains.append(domain)
            else:
                print(f"[PASİF] {domain} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[PASİF] {domain} - Hata: {e}")
    
    if not potential_domains:
        raise Exception("Hiç potansiyel domain bulunamadı")
    
    # Potansiyel domain'leri numaraya göre sırala (büyükten küçüğe)
    potential_domains.sort(reverse=True, key=lambda x: int(x.split('betyaptv')[1].split('.')[0]))
    
    print(f"\n{len(potential_domains)} potansiyel domain bulundu. En yüksek numaralıyı kontrol ediyorum...")
    print(f"Sıralama: {potential_domains}")
    
    # En yüksek numaralıdan başlayarak kontrol et
    for domain in potential_domains:
        print(f"\nDetaylı kontrol: {domain}")
        if check_domain_availability(domain):
            domain_num = domain.split('betyaptv')[1].split('.')[0]
            print(f"🎯 EN YÜKSEK AKTİF DOMAIN: {domain} (No: {domain_num})")
            return domain
    
    raise Exception("Hiçbir domain erişilebilir değil")

def generate_html(active_domain):
    channels = [
        ('beIN SPORTS 1 HD', 5062),
        ('beIN SPORTS 2 HD', 5063),
        ('beIN SPORTS 3 HD', 5064),
        ('beIN SPORTS 4 HD', 5065),
        ('beIN SPORTS 5 HD', 5066),
        ('beIN SPORTS MAX 1 HD', 5067),
        ('beIN SPORTS MAX 2 HD', 5068),
        ('SMART SPORTS 1 HD', 5091),
        ('SMART SPORTS 2 HD', 5092),
        ('TİVİBU SPORTS HD', 5081),
        ('TİVİBU SPORTS 1 HD', 5082),
        ('TİVİBU SPORTS 2 HD', 5083),
        ('TİVİBU SPORTS 3 HD', 5084),
        ('TİVİBU SPORTS 4 HD', 5085),
        ('S SPORTS 1 HD', 5101),
        ('S SPORTS 2 HD', 5102),
        ('EURO SPORTS 1 HD', 5111),
        ('EURO SPORTS 2 HD', 5112),
        ('NBA HD', 5121),
        ('TABİİ SPORTS HD', 5071),
        ('TABİİ SPORTS 1 HD', 5072),
        ('TABİİ SPORTS 2 HD', 5073),
        ('TABİİ SPORTS 3 HD', 5074),
        ('TABİİ SPORTS 4 HD', 5075),
        ('TABİİ SPORTS 5 HD', 5076),
        ('TABİİ SPORTS 6 HD', 5077)
    ]

    channel_items = ''
    for name, channel_id in channels:
        href = f"{active_domain}/wp-content/themes/ikisifirbirdokuz/match-center.php?id={channel_id}"
        channel_items += f'<div class=\'channel-item\' data-channel=\'{name}\' data-href=\'{href}\'><a><img src=\'https://i.hizliresim.com/t75soiq.png\' alt=\'Logo\'><span>{name}</span></a></div>\n'

    html_template = f"""<!DOCTYPE html>
<html lang="en">
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
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function() {{
            $('.channel-item').on('click', function() {{
                const href = $(this).data('href');
                window.location.href = href;
            }});
        }});
    </script>
</body>
</html>"""

    return html_template

if __name__ == "__main__":
    active_domain = find_highest_active_domain()
    html_content = generate_html(active_domain)
    with open('yaptv.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("yaptv.html başarıyla oluşturuldu.")
