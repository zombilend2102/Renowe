import requests
from bs4 import BeautifulSoup
import re
import json

# --- 1. Dizi Verileri (Sadece Karma 2025 ve Hükümsüz) ---
dizi_listesi = [
    {"ad": "Prens", "logo": "https://www.themoviedb.org/t/p/w500/b5YfJKBKD5lRCunqeKB3alpgusQ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9wcmVucw=="},
    {"ad": "Magarsus!", "logo": "https://www.themoviedb.org/t/p/w500/nqkgWcS7jIsGebMJP0YEBAqEUbS.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9tYWdhcnN1cw=="},
    {"ad": "Doğu", "logo": "https://www.themoviedb.org/t/p/w500/16TlWbNcmpyRaXt0IVmWOx8xtBl.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kb2d1"},
    {"ad": "Eko Eko Eko", "logo": "https://www.themoviedb.org/t/p/w500/1dMldtEmNEtltZEWEOcXFLx8Va5.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9la28tZWtvLWVrbw=="},
    {"ad": "İlk ve Son", "logo": "https://www.themoviedb.org/t/p/w500/epARLyo8ctJr4xVdS2DObuRiie8.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9pbGstdmUtc29u"},
    {"ad": "Yalnızım Mesut Bey", "logo": "https://www.themoviedb.org/t/p/w500/j9QevI1ZF2tExVASNexx231G4gV.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95YWxuaXppbS1tZXN1dC1iZXk="},
    {"ad": "Kıyma", "logo": "https://www.themoviedb.org/t/p/w500/zXjIMMQklJQOWhJiY2siFzpabyH.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9raXltYQ=="},
    {"ad": "Adil Yıldırım ile Kutu", "logo": "https://www.themoviedb.org/t/p/w500/bFcCjo6EooQiEGXZDerNFhnZtbO.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hZGlsLXlpbGRpcmltLWlsZS1rdXR1"},
    {"ad": "Sokağın Çocukları", "logo": "https://www.themoviedb.org/t/p/w500/lwbVDkrrnDeXwWBhbaikfaZumhm.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zb2thZ2luLWNvY3VrbGFyaQ=="},
    {"ad": "Deprem", "logo": "https://www.moviedb.org/t/p/w500/e9x0zceUorXnMqa5yr6CJ97LlmW.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kZXByZW0="},
    {"ad": "Mesut Süre İle İlişki Testi", "logo": "https://www.themoviedb.org/t/p/w500/lZS9Tp7E99ixNcfZULLoruruooq.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9tZXN1dC1zdXJlLWlsZS1pbGlza2ktdGVzdGk="},
    {"ad": "Deneme Çekimi", "logo": "https://www.themoviedb.org/t/p/w500/spzb00xxRAxDSqhLS1kZXzj0igc.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kZW5lbWUtY2VraW1p"},
    {"ad": "Bozkır", "logo": "https://www.themoviedb.org/t/p/w500/rvSI23gERFpXfJwxTeayXHVr4o6.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9ib3praXI="},
    {"ad": "Ben Bu Boşluğu Nasıl?", "logo": "https://www.themoviedb.org/t/p/w500/2vr2JwKdGTwb6b0I4FHk5eCTO9J.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iZW4tYnUtYm9zbHVndS1uYXNpbA=="},
    {"ad": "Sen, Ben, O!", "logo": "https://www.themoviedb.org/t/p/w500/j45r6C5LVN3kwbcQyoHTRXxNG5U.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zZW4tYmVuLW8="},
    {"ad": "Çimen Talkshow", "logo": "https://www.themoviedb.org/t/p/w500/9i3eiXWacihxxoLSLYPUwimJyb7.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9jaW1lbi10YWxrc2hvdw=="},
    {"ad": "Meta Aşk", "logo": "https://www.themoviedb.org/t/p/w500/scP2SMIBLM5KwxAqkFoUE56mrFU.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9tZXRhLWFzaw=="},
    {"ad": "Ultrastories", "logo": "https://www.themoviedb.org/t/p/w500/fe0EtaeHd7kQTrKRPh9bllpYwO3.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS91bHRyYXN0b3JpZXM="},
    {"ad": "Hayaller Bizim İki Gözüm", "logo": "https://www.themoviedb.org/t/p/w500/zTqkqIVSntVXKRh0Qp21xMweKDi.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9oYXlhbGxlci1iaXppbS1pa2ktZ296dW0="},
    {"ad": "Bizden Olur Mu?", "logo": "https://www.themoviedb.org/t/p/w500/l7ixfp1p5XWDruErlfaoXUJok8k.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iaXpkZW4tb2x1ci1tdQ=="},
    {"ad": "Operasyon", "logo": "https://www.themoviedb.org/t/p/w500/elBPvukKx21q2Umcwr7mqBlCK99.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9vcGVyYXN5b24="},
    {"ad": "Cansu Canan Özgen ile 40", "logo": "https://www.themoviedb.org/t/p/w500/6t4mxX7Zx7xjz6ZbHbz56wMni3V.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9jYW5zdS1jYW5hbi1vemdlbi1pbGUtNDA="},
    {"ad": "Saklı", "logo": "https://www.themoviedb.org/t/p/w500/17X5zOsCG8yE7zawYkMwk0U7ZdT.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zYWtsaQ=="},
    {"ad": "Şamanın Yolunda", "logo": "https://www.themoviedb.org/t/p/w500/kiTepihv7YtP9qbPDiLd8QS6rsM.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zYW1hbmluLXlvbHVuZGE="},
    {"ad": "Karsu'nun Odası", "logo": "https://www.themoviedb.org/t/p/w500/hEihck3vPgwCinns5NgtY4Bu7RL.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9rYXJzdW51bi1vZGFzaQ=="},
    {"ad": "Bunu Bi Düşünün", "logo": "https://www.themoviedb.org/t/p/w500/4GSAvfo2sT5F6tCG30pGFmv3OC1.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9idW51LWJpLWR1c3VudW4="},
    {"ad": "Renkli Rüyalar Oteli", "logo": "https://www.themoviedb.org/t/p/w500/ndgo3bx0AnbTCUyYz7lFNNromC6.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9yZW5rbGktcnV5YWxhci1vdGVsaQ=="},
    {"ad": "Aslı Gibidir", "logo": "https://www.themoviedb.org/t/p/w500/1ZUuZytQ2toiz5ro832L8JjnYuM.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hc2xpLWdpYmlkaXI="},
    {"ad": "Şokopop Yeşilçam 101", "logo": "https://www.themoviedb.org/t/p/w500/uVf3jCMerWMCb2qizxsCYFS9ido.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zb2tvcG9wLXllc2lsY2FtLTEwMQ=="},
    {"ad": "Dün Dündür", "logo": "https://www.themoviedb.org/t/p/w500/2AQkEI0b27d9ilgnteumsAaCDRx.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kdW4tZHVuZHVy"},
    {"ad": "Masal Şatosu: Peri Hırsızı", "logo": "https://www.themoviedb.org/t/p/w500/qi60C0ZrG9L86H7x45uUL034l1Q.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9tYXNhbC1zYXRvc3UtcGVyaS1oaXJzaXpp"},
    {"ad": "Yeşilçam", "logo": "https://www.themoviedb.org/t/p/w500/iRSOQLrvVw0ZvrX5JDUrZFjPPNb.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95ZXNpbGNhbQ=="},
    {"ad": "We Are Who We Are", "logo": "https://www.themoviedb.org/t/p/w500/33btSKKmjmc24hK9Vj1sRWQGfyh.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS93ZS1hcmUtd2hvLXdlLWFyZQ=="},
    {"ad": "BOOM by İbrahim Selim", "logo": "https://www.themoviedb.org/t/p/w500/r5VL2MnBMMRfm2P6BCSwZ0aLiD3.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9ib29tLWJ5LWlicmFoaW0tc2VsaW0="},
    {"ad": "Gürkan Şef ile Ateş Oyunları", "logo": "https://www.themoviedb.org/t/p/w500/qtmoy51jkBmYvITt8vVlxRU1HFj.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9ndXJrYW4tc2VmLWlsZS1hdGVzLW95dW5sYXJp"},
    {"ad": "Acans", "logo": "https://www.themoviedb.org/t/p/w500/jFBcC9ZclKUD36HZgZPAssrTBaL.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hY2Fucw=="},
    {"ad": "Dövüşçü", "logo": "https://www.themoviedb.org/t/p/w500/9m3OE0CwrgoAWB0lN2SBJyQW7RL.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kb3Z1c2N1"},
    {"ad": "Ganyan", "logo": "https://www.themoviedb.org/t/p/w500/jVJwB0OcUxCqz0nRqnCyLah9Btr.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9nYW55YW4="},
    {"ad": "Ankara Havası", "logo": "https://www.themoviedb.org/t/p/w500/7y4XlTwpy7aIBjGmVBZwoVfIOL9.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hbmthcmEtaGF2YXNp"},
    {"ad": "Hiç", "logo": "https://www.themoviedb.org/t/p/w500/3yVxMwGTSZU3YC3NvTgiiXvXCa5.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9oaWM="},
    {"ad": "Efsane T", "logo": "https://www.themoviedb.org/t/p/w500/k5suSzjpfDL1ENGUyqxSPZ4tXtz.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9lZnNhbmUtdA=="},
    {"ad": "Dijital Flörtleşme", "logo": "https://www.themoviedb.org/t/p/w500/j3jycOMemX0xF0VpQVv8WJe7jP2.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kaWppdGFsLWZsb3J0bGVzbWU="},
    {"ad": "Saygı", "logo": "https://www.themoviedb.org/t/p/w500/2lD7iegVJ7ZQSiRHqFqE8tQ3PKV.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zYXlnaQ=="},
    {"ad": "Yarım Kalan Aşklar", "logo": "https://www.themoviedb.org/t/p/w500/af3EDd9AElTOuyG2BF1LnCYbQQ1.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95YXJpbS1rYWxhbi1hc2tsYXI="},
    {"ad": "Parayı Vuranlar", "logo": "https://www.themoviedb.org/t/p/w500/hj9nIZUnQoNuWLjzF2o0Eq587ow.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9wYXJheWktdnVyYW5sYXI="},
    {"ad": "Sahipli", "logo": "https://www.themoviedb.org/t/p/w500/3nI3lzhYyTmWeUKvJdxFhcvzxK4.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zYWhpcGxp"},
    {"ad": "Çalınmış Hayatlar", "logo": "https://www.themoviedb.org/t/p/w500/jCsPVQJPyM38YiS0P9MSvGsGl3w.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9jYWxpbm1pcy1oYXlhdGxhcg=="},
    {"ad": "Bize Gezmek Olsun", "logo": "https://www.themoviedb.org/t/p/w500/t52TqVFA3FzGkFuAv0OqCSjHq7x.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iaXplLWdlem1lay1vbHN1bg=="},
    {"ad": "Kafalarına Göre", "logo": "https://www.themoviedb.org/t/p/w500/nzN4bUt1HjM4Vx27kh8Kgv6cmbZ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9rYWZhbGFyaW5hLWdvcmU="},
    {"ad": "Alef", "logo": "https://www.themoviedb.org/t/p/w500/6CyNjKgbgs6dTBKNkUJsEfMnX1B.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hbGVm"},
    {"ad": "Çıplak", "logo": "https://www.themoviedb.org/t/p/w500/3Yq5dXQFheq1iH8uIPjc2kb3qxc.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9jaXBsYWs="},
    {"ad": "Behzat Ç Bir Ankara Polisiyesi", "logo": "https://www.moviedb.org/t/p/w500//m5NHEg7GcHgjzxPy6EAMs7BtU1C.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iZWh6YXQtYy1iaXItYW5rYXJhLXBvbGlzaXllc2k="},
    {"ad": "Yaşamayanlar", "logo": "https://www.themoviedb.org/t/p/w500//Vntk70iZz58EmUTETdtsDP04T3.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95YXNhbWF5YW5sYXI="},
    {"ad": "Sıfır Bir: Bir Zamanlar Adana’da", "logo": "https://www.themoviedb.org/t/p/w500//ftOG1UNX7POB5hLMk3sMRiroJRQ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zaWZpci1iaXItYmlyLXphbWFubGFyLWFkYW5hLWRh"},
    {"ad": "Pavyon", "logo": "https://www.moviedb.org/t/p/w500//379zkovxRTO2m0YYtOt7A4n0NxH.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9wYXZ5b24="},
    {"ad": "Masum", "logo": "https://www.themoviedb.org/t/p/w500//6FG5YgmQpD5f1TfTzKWznRBBoBv.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9tYXN1bQ=="},
    {"ad": "Dudullu Postası", "logo": "https://www.themoviedb.org/t/p/w500//uKsFVdRDzwC6G34hl0x9E8r3mtS.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kdWR1bGx1LXBvc3Rhc2k="},
    {"ad": "Bartu Ben", "logo": "https://www.themoviedb.org/t/p/w500//bFCM1bCWdgTy8QNxG0fR2HDnuXo.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iYXJ0dS1iZW4="},
    {"ad": "Aynen Aynen", "logo": "https://www.themoviedb.org/t/p/w500//fiki0zbFwJJoR6QH9Ubphyc8zbp.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9heW5lbi1heW5lbg=="},
    {"ad": "7YÜZ", "logo": "https://www.themoviedb.org/t/p/w500//gpSBmZUKpAmfzEBlpmiv06dgIoT.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS83eXV6"},
    {"ad": "Bonkis", "logo": "https://www.themoviedb.org/t/p/w500//imTaJg7HHt0b0HhmxIVhvep3Ibf.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9ib25raXM="}
]

# Ana diziler objesi, JavaScript'te kullanılacak.
diziler_data = {}

def normalize_dizi_ad(dizi_adi):
    """Dizi adını JS anahtarı olarak kullanılabilecek, küçük harf ve boşluksuz bir ID'ye dönüştürür."""
    dizi_adi = dizi_adi.lower().replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i').replace('ö', 'o').replace('ş', 's').replace('ü', 'u').replace('?', '')
    return re.sub(r'[^a-z0-9]', '', dizi_adi)

def get_iframe_src(bolum_link):
    """Bölüm sayfasından gömülü video (iframe) URL'sini çeker."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(bolum_link, headers=headers, timeout=10)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        iframe = soup.find('iframe', id='iframe-player')
        
        if iframe and 'src' in iframe.attrs:
            return iframe['src']
        return None
            
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None

def process_dizi(dizi):
    """Bir dizinin tüm bölümlerini çeker ve iframe linklerini bulur."""
    dizi_adi = dizi["ad"]
    dizi_link = dizi["link"]
    dizi_id = normalize_dizi_ad(dizi_adi)
    bolumler = []

    try:
        print(f"\n--- {dizi_adi} Bölüm Listesi Çekiliyor ---")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(dizi_link, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        bolum_butonlari = soup.find_all('button', class_='list-group-item izle')
        
        if not bolum_butonlari:
            print(f"  [UYARI] {dizi_adi} için bölüm butonu bulunamadı.")
            return

        for i, button in enumerate(bolum_butonlari):
            p_tag = button.find('p', class_='menu70')
            bolum_ad = p_tag.text.strip().replace('\n', ' ').strip() if p_tag else f"Bölüm {i+1}"
            
            onclick_attr = button.get('onclick', '')
            match = re.search(r"location\.href='(.*?)'", onclick_attr)
            
            if match:
                watch_link = match.group(1).strip()
                iframe_link = get_iframe_src(watch_link)
                
                if iframe_link:
                    bolumler.append({
                        "ad": bolum_ad,
                        "link": iframe_link
                    })
                    print(f"  -> Eklendi: {bolum_ad}")
                else:
                    print(f"  [ATLANDI] {bolum_ad} için iframe linki ÇEKİLEMEDİ.")
        
        if bolumler:
            diziler_data[dizi_id] = {
                "ad": dizi_adi, 
                "resim": dizi["logo"],
                "dil": "Yerli",
                "bolumler": bolumler
            }
            print(f"--- {dizi_adi} için TOPLAM {len(bolumler)} bölüm başarıyla çekildi. ---")

    except requests.exceptions.RequestException as e:
        print(f"\n[KRİTİK HATA] {dizi_adi} ana sayfasını çekerken bir sorun oluştu: {e}")
    except Exception as e:
        print(f"\n[KRİTİK HATA] {dizi_adi} işlenirken beklenmedik hata: {e}")


# Tüm dizileri işle
for dizi in dizi_listesi:
    process_dizi(dizi)

# --- 2. HTML ve JavaScript Kodu Oluşturma ---

# JSON'u sıkıştır ve güvenli hale getir
js_diziler_data = json.dumps(diziler_data, indent=None, ensure_ascii=False).replace('"', '\\"').replace("'", "\\'")

# Ana sayfa üzerindeki dizileri oluşturmak için HTML dizeleri
dizi_paneller_html = ""
for id, data in diziler_data.items():
    dizi_paneller_html += f"""
    <div class="filmpanel" onclick="showBolumler('{id}')">
        <div class="filmresim"><img src="{data['resim']}"></div>
        <div class="filmisimpanel">
            <div class="filmisim">{data['ad']}</div>
            <div class="resimust">
                <div class="filmdil">{data['dil']}</div>
            </div>
        </div>
    </div>
"""

# HTML şablonu (showBolumler fonksiyonu orijinal çalışan kodun mantığına göre yeniden yazıldı)
html_template = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
<title>TITAN TV YERLI VOD</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css?family=PT+Sans:700i" rel="stylesheet">
<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
<script src="https://kit.fontawesome.com/bbe955c5ed.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@splidejs/splide@4.1.4/dist/js/splide.min.js"></script>
<style>
    /* CSS KODLARI BURADA */
    *:not(input):not(textarea) {{
        -moz-user-select: -moz-none;
        -khtml-user-select: none;
        -webkit-user-select: none;
        -o-user-select: none;
        -ms-user-select: none;
        user-select: none
    }}
    body {{
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
    }}
    .slider-slide {{ background: #15161a; box-sizing: border-box; }}  
    .slidefilmpanel {{ transition: .35s; box-sizing: border-box; background: #15161a; overflow: hidden; }}
    .slidefilmpanel:hover {{ background-color: #572aa7; }}
    .slidefilmpanel:hover .filmresim img {{ transform: scale(1.2); }}
    .slider {{ position: relative; padding-bottom: 0px; width: 100%; overflow: hidden; --tw-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25); --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color); box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow); }}
    .slider-container {{ display: flex; width: 100%; scroll-snap-type: x var(--tw-scroll-snap-strictness); --tw-scroll-snap-strictness: mandatory; align-items: center; overflow: auto; scroll-behavior: smooth; }}
    .slider-container .slider-slide {{ aspect-ratio: 9/13.5; display: flex; flex-shrink: 0; flex-basis: 14.14%; scroll-snap-align: start; flex-wrap: nowrap; align-items: center; justify-content: center; }}
    .slider-container::-webkit-scrollbar {{ width: 0px; }}
    .clear {{ clear: both; }}
    .hataekran i {{ color: #572aa7; font-size: 80px; text-align: center; width: 100%; }}
    .hataekran {{ width: 80%; margin: 20px auto; color: #fff; background: #15161a; border: 1px solid #323442; padding: 10px; box-sizing: border-box; border-radius: 10px; }}
    .hatayazi {{ color: #fff; font-size: 15px; text-align: center; width: 100%; margin: 20px 0px; }}
    .filmpaneldis {{ background: #15161a; width: 100%; margin: 20px auto; overflow: hidden; padding: 10px 5px; box-sizing: border-box; }}
    .aramafilmpaneldis {{ background: #15161a; width: 100%; margin: 20px auto; overflow: hidden; padding: 10px 5px; box-sizing: border-box; }}
    .bos {{ width: 100%; height: 60px; background: #572aa7; }}
    .baslik {{ width: 96%; color: #fff; padding: 15px 10px; box-sizing: border-box; }}
    .filmpanel {{ width: 12%; height: 200px; background: #15161a; float: left; margin: 1.14%; color: #fff; border-radius: 15px; box-sizing: border-box; box-shadow: 1px 5px 10px rgba(0,0,0,0.1); border: 1px solid #323442; padding: 0px; overflow: hidden; transition: border 0.3s ease, box-shadow 0.3s ease; }}
    .filmisimpanel {{ width: 100%; height: 200px; position: relative; margin-top: -200px; background: linear-gradient(to bottom, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 1) 100%); }}
    .filmpanel:hover {{ color: #fff; border: 3px solid #572aa7; box-shadow: 0 0 10px rgba(87, 42, 167, 0.5); }}
    .filmpanel:focus {{ outline: none; border: 3px solid #572aa7; box-shadow: 0 0 10px rgba(87, 42, 167, 0.5); }}
    .filmresim {{ width: 100%; height: 100%; margin-bottom: 0px; overflow: hidden; position: relative; }}
    .filmresim img {{ width: 100%; height: 100%; transition: transform 0.4s ease; }}
    .filmpanel:hover .filmresim img {{ transform: scale(1.1); }}
    .filmpanel:focus .filmresim img {{ transform: none; }}
    .filmisim {{ width: 100%; font-size: 14px; text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0px 5px; box-sizing: border-box; color: #fff; position: absolute; bottom: 25px; }}
    .resimust {{ height: 25px; width: 100%; position: absolute; bottom: 0px; overflow: hidden; box-sizing: border-box; padding: 0px 5px; }}
    .filmdil {{ transition: .35s; width: 100%; float: left; box-sizing: border-box; padding: 0px; font-size: 13px; color: #ccc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; }}
    .aramapanel {{ width: 100%; height: 60px; background: #15161a; border-bottom: 1px solid #323442; margin: 0px auto; padding: 10px; box-sizing: border-box; overflow: hidden; z-index: 11111; }}
    .aramapanelsag {{ width: auto; height: 40px; box-sizing: border-box; overflow: hidden; float: right; }}
    .aramapanelsol {{ width: 50%; height: 40px; box-sizing: border-box; overflow: hidden; float: left; }}
    .aramapanelyazi {{ height: 40px; width: 120px; border: 1px solid #ccc; box-sizing: border-box; padding: 0px 10px; background: ; color: #000; margin: 0px 5px; }}
    .aramapanelbuton {{ height: 40px; width: 40px; text-align: center; background-color: #572aa7; border: none; color: #fff; box-sizing: border-box; overflow: hidden; float: right; transition: .35s; }}
    .aramapanelbuton:hover {{ background-color: #fff; color: #000; }}
    .logo {{ width: 40px; height: 40px; float: left; }}
    .logo img {{ width: 100%; }}
    .logoisim {{ font-size: 15px; width: 70%; height: 40px; line-height: 40px; font-weight: 500; color: #fff; }}
    #dahafazla {{ background: #572aa7; color: #fff; padding: 10px; margin: 20px auto; width: 200px; text-align: center; transition: .35s; }}
    #dahafazla:hover {{ background: #fff; color: #000; }}
    .hidden {{ display: none; }}
    .bolum-container {{ background: #15161a; padding: 10px; margin-top: 10px; border-radius: 5px; }}
    .geri-btn {{ background: #572aa7; color: white; padding: 10px; text-align: center; border-radius: 5px; cursor: pointer; margin-top: 10px; margin-bottom: 10px; display: none; width: 100px; }}
    .geri-btn:hover {{ background: #6b3ec7; transition: background 0.3s; }}
    @media(max-width:900px) {{ .filmpanel {{ width: 17%; height: 220px; margin: 1.5%; }} .slider-container .slider-slide {{ flex-basis: 20%; }} }}
    @media(max-width:550px) {{ 
        .filmisimpanel {{ height: 190px; margin-top: -190px; }} 
        .filmpanel {{ width: 31.33%; height: 190px; margin: 1%; }} 
        .filmsayfaresim {{ width: 48%; float: left; }} 
        .filmsayfapanel {{ background: #15161a; color: #fff; width: 90%; height: auto; }} 
        .filmbasliklarsag {{ float: left; width: 100%; margin-top: 20px; margin-left: 0px; }} 
        .ozetpanel {{ float: left; width: 48%; height: 230px; }} 
        .slider-container .slider-slide {{ flex-basis: 33.33%; }} 
    }}
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

<div class="filmpaneldis" id="anaDiziler">
    <div class="baslik">YERLİ DİZİLER VOD BÖLÜM</div>
    
    {dizi_paneller_html}

</div>

<div id="bolumler" class="bolum-container hidden">
    <div id="geriBtn" class="geri-btn" onclick="geriDon()">Geri</div>
    <div id="bolumListesi" class="filmpaneldis"></div>
</div>

<script>
// PYTHON TARAFINDAN ÇEKİLEN VE DÜZENLENEN VERİ BURAYA EKLENİR
var diziler = JSON.parse('{js_diziler_data}'); 

// Mevcut ekranı takip etmek için bir değişken
let currentScreen = 'anaSayfa';

function showBolumler(diziID) {{
    sessionStorage.setItem('currentDiziID', diziID);
    
    var listContainer = document.getElementById("bolumListesi");
    listContainer.innerHTML = "";
    
    if (diziler[diziID]) {{
        var diziData = diziler[diziID];
        
        diziData.bolumler.forEach(function(bolum) {{
            // Orijinal kodunuzdaki gibi DIV oluşturuluyor ve onclick ile yönlendiriliyor.
            var item = document.createElement("div"); 
            item.className = "filmpanel";
            
            item.onclick = function() {{
                // Bölüm linkine giderken tarihçeye bölümler durumunu kaydet
                history.replaceState({{ page: 'bolumler', diziID: diziID }}, '', `#bolumler-${{diziID}}`);
                window.location.href = bolum.link;
            }};
            
            // Temiz HTML yapısı (IMDb ve YIL olmadan)
            item.innerHTML = '<div class="filmresim"><img src="' + diziData.resim + '"></div>' +
                             '<div class="filmisimpanel">' +
                                 '<div class="filmisim">' + bolum.ad + '</div>' +
                                 '<div class="resimust">' +
                                     '<div class="filmdil">' + diziData.dil + '</div>' +
                                 '</div>' +
                             '</div>';

            listContainer.appendChild(item);
        }});
    }} else {{
        listContainer.innerHTML = `<div class="hataekran"><i class="fas fa-exclamation-triangle"></i><div class="hatayazi">Bu dizi için bölüm bulunamadı veya veri çekilemedi.</div></div>`;
    }}
    
    document.getElementById("anaDiziler").classList.add("hidden"); 
    document.getElementById("bolumler").classList.remove("hidden");
    document.getElementById("geriBtn").style.display = "block";

    currentScreen = 'bolumler';
    history.pushState({{ page: 'bolumler', diziID: diziID }}, '', `#bolumler-${{diziID}}`);
}}

function geriDon() {{
    sessionStorage.removeItem('currentDiziID');
    document.getElementById("anaDiziler").classList.remove("hidden"); 
    document.getElementById("bolumler").classList.add("hidden");
    document.getElementById("geriBtn").style.display = "none";
    
    currentScreen = 'anaSayfa';
    history.pushState({{ page: 'anaSayfa' }}, '', '#anaSayfa');
}}

window.addEventListener('popstate', function(event) {{
    const hash = window.location.hash;
    const match = hash.match(/^#bolumler-(.*)$/);
    
    if (match) {{
        const diziID = match[1];
        if (diziler[diziID]) {{
            showBolumler(diziID);
        }} else {{
             geriDon();
        }}
    }} else {{
        geriDon();
    }}
}});


function checkInitialState() {{
    const hash = window.location.hash;
    const match = hash.match(/^#bolumler-(.*)$/);
    
    if (match) {{
        const diziID = match[1];
        if (diziler[diziID]) {{
            showBolumler(diziID);
        }} else {{
            geriDon();
        }}
    }} else {{
        document.getElementById("anaDiziler").classList.remove("hidden");
        document.getElementById("bolumler").classList.add("hidden");
        document.getElementById("geriBtn").style.display = "none";
        currentScreen = 'anaSayfa';
        history.replaceState({{ page: 'anaSayfa' }}, '', '#anaSayfa');
    }}
}}

document.addEventListener('DOMContentLoaded', checkInitialState);


function searchSeries() {{
    var query = document.getElementById('seriesSearch').value.toLowerCase();
    var mainSeriesPanels = document.getElementById('anaDiziler').querySelectorAll('.filmpanel');

    mainSeriesPanels.forEach(function(serie) {{
        var title = serie.querySelector('.filmisim').textContent.toLowerCase();
        
        if (query.length > 0) {{
            if (title.includes(query)) {{
                serie.style.display = "block";
            }} else {{
                serie.style.display = "none";
            }}
        }} else {{
            serie.style.display = "block";
        }}
    }});
    
    return false; 
}}

function resetSeriesSearch() {{
    var query = document.getElementById('seriesSearch').value;
    if (query === "") {{
        var mainSeriesPanels = document.getElementById('anaDiziler').querySelectorAll('.filmpanel');
        mainSeriesPanels.forEach(function(serie) {{
            serie.style.display = "block";
        }});
    }}
}}
</script>
</body>
</html>
"""

# HTML dosyasını kaydet
try:
    dosya_adi = "anime.html"
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"\n✅ BAŞARILI: Tüm veriler çekildi ve '{dosya_adi}' dosyasına kaydedildi.")
    print("Oluşturulan HTML dosyasını tarayıcınızda açarak sonucu görebilirsiniz.")

except Exception as e:
    print(f"\n[KRİTİK HATA] HTML dosyası yazılırken bir sorun oluştu: {e}")
