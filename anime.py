import requests
from bs4 import BeautifulSoup
import re
import json

# --- 1. Dizi Verileri (Sadece Karma 2025 ve Hükümsüz) ---
dizi_listesi = [
    {"ad": "Enfes Bir Akşam", "logo": "https://www.themoviedb.org/t/p/w500/kBO1JZAqgeazLV8nbPz0MSiVBU1.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9lbmZlcy1iaXItYWtzYW0="},
    {"ad": "Olympo", "logo": "https://www.themoviedb.org/t/p/w500/2X06R82PG2HVZl6h7YeXXT11EEP.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9vbHltcG8="},
    {"ad": "The Eternaut", "logo": "https://www.themoviedb.org/t/p/w500/ucI5KroZLP0KyJqQnAdOpzhVvBs.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtZXRlcm5hdXQ="},
    {"ad": "İstanbul Ansiklopedisi", "logo": "https://www.themoviedb.org/t/p/w500/UlNvxtLq87Pak18xTSNK2OJPd9.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9pc3RhbmJ1bC1hbnNpa2xvcGVkaXNp"},
    {"ad": "The Gardener", "logo": "https://www.themoviedb.org/t/p/w500/l2Fy8vvr27vbYJOPe49EfVd5Qli.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtZ2FyZGVuZXI="},
    {"ad": "Bir İhtimal Daha Var", "logo": "https://www.themoviedb.org/t/p/w500/tT16uPa4TyP8SogNA2KpWSm6IrQ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iaXItaWh0aW1hbC1kYWhhLXZhcg=="},
    {"ad": "Mezarlık", "logo": "https://www.themoviedb.org/t/p/w500/p22xaH2ZpxhdJa1ZFF528Yk7AWc.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9tZXphcmxpaw=="},
    {"ad": "Apple Cider Vinegar", "logo": "https://www.themoviedb.org/t/p/w500/5Ov4ZX2NKCpyKZicXZ6MdQasnAq.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hcHBsZS1jaWRlci12aW5lZ2Fy"},
    {"ad": "American Primeval", "logo": "https://www.themoviedb.org/t/p/w500/ff0s9OHGNSZL6cVteIb7LNvTnJD.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hbWVyaWNhbi1wcmltZXZhbA=="},
    {"ad": "Asaf", "logo": "https://www.themoviedb.org/t/p/w500/1jjkCEwJ37Sd2xNP9MVsCzMCQBd.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hc2Fm"},
    {"ad": "Doctor Climax", "logo": "https://www.themoviedb.org/t/p/w500/kSlaTrpemQL5DpxHZAQxc6fJQoL.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kb2N0b3ItY2xpbWF4"},
    {"ad": "Eric", "logo": "https://www.themoviedb.org/t/p/w500/9OV6McrRh1BAnrak3yVP9xYuUId.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9lcmlj"},
    {"ad": "Kimler Geldi Kimler Geçti", "logo": "https://www.themoviedb.org/t/p/w500/5K6jZNOjskDCtsZgF0r3nc8l26f.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9raW1sZXItZ2VsZGkta2ltbGVyLWdlY3Rp"},
    {"ad": "Dead Boy Detectives", "logo": "https://www.themoviedb.org/t/p/w500/346ju9C5zy0tkzfQoetOYtM74gw.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kZWFkLWJveS1kZXRlY3RpdmVz"},
    {"ad": "The Hijacking of Flight 601", "logo": "https://www.themoviedb.org/t/p/w500/AcSOs5wLPB9GGFY1Bact3V0riQE.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtbGlqYWNraW5nLW9mLWZsaWdodC02MDE="},
    {"ad": "Ripley", "logo": "https://www.themoviedb.org/t/p/w500/rpSo8z9alultGVTqQ3dkLEyU8xx.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9yaXBsZXk="},
    {"ad": "3 Body Problem", "logo": "https://www.themoviedb.org/t/p/w500/sphnjjiYb50SbWMToW7fyGigH1n.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS8zLWJvZHktcHJvYmxlbQ=="},
    {"ad": "Bandidos", "logo": "https://www.themoviedb.org/t/p/w500/hoM8DvKJw5KPfdHbcITxn0rO2HZ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iYW5kaWRvcw=="},
    {"ad": "The Signal", "logo": "https://www.themoviedb.org/t/p/w500/AoDYkBwRtOZPwLPaqPxXTQx0WZk.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtc2lnbmFs"},
    {"ad": "The Gentlemen", "logo": "https://www.themoviedb.org/t/p/w500/tw3tzfXaSpmUZIB8ZNqNEGzMBCy.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtZ2VudGxlbWVu"},
    {"ad": "Furies", "logo": "https://www.themoviedb.org/t/p/w500/sX3oRygqyfqGM9EIUFcdMTqxSrL.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9mdXJpZXM="},
    {"ad": "Kuvvetli Bir Alkış", "logo": "https://www.themoviedb.org/t/p/w500/8Ci7t4R4PyqI8IB7y70AJdX34z6.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9rdXZ2ZXRsaS1iaXItYWxraXM="},
    {"ad": "Alexander: The Making of a God", "logo": "https://www.themoviedb.org/t/p/w500/tKUTpdyg0wGfIYplIAfkN6hDbRw.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hbGV4YW5kZXItdGhlLW1ha2luZy1vZi1hLWdvZA=="},
    {"ad": "Griselda", "logo": "https://www.themoviedb.org/t/p/w500/nhEtK1lJKb3kqBtDBDXynGr3hJL.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9ncmlzZWxkYQ=="},
    {"ad": "Kübra", "logo": "https://www.themoviedb.org/t/p/w500/amlpVWYgv1KXiFfZKvY2t0fqvMf.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9rdWJyYQ=="},
    {"ad": "Squid Game: The Challenge", "logo": "https://www.themoviedb.org/t/p/w500/eAjXAgdjPMZH9Ugub7XYPowFoS1.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zcXVpZC1nYW1lLXRoZS1jaGFsbGVuZ2U="},
    {"ad": "Yaratılan", "logo": "https://www.themoviedb.org/t/p/w500/kINoiBSOfHHVmNwJ4i766j93RR1.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95YXJhdGlsYW4="},
    {"ad": "Kulüp", "logo": "https://www.themoviedb.org/t/p/w500/jHgMj6mtMHEBrFhmZaQCGFGYnFx.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9rdWx1cA=="},
    {"ad": "Terzi", "logo": "https://www.themoviedb.org/t/p/w500/uEd6QajI9aMHdVGVcptfdZJwHtb.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90ZXJ6aQ=="},
    {"ad": "Sıcak Kafa", "logo": "https://www.themoviedb.org/t/p/w500/dt1RGQTZs1wqywXSdygWU62zCmX.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zaWNhay1rYWZh"},
    {"ad": "Wednesday", "logo": "https://www.themoviedb.org/t/p/w500/jeGtaMwGxPmQN5xM4ClnwPQcNQz.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS93ZWRuZXNkYXk="},
    {"ad": "1899", "logo": "https://www.themoviedb.org/t/p/w500/8KGvYHQNOamON6ufQGjyhkiVn1V.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS8xODk5"},
    {"ad": "Yasuke", "logo": "https://www.themoviedb.org/t/p/w500/hgYqEkZQS2fgC6E9fe8Le1Kxbmw.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95YXN1a2U="},
    {"ad": "Dahmer – Monster: The Jeffrey Dahmer Story", "logo": "https://www.themoviedb.org/t/p/w500/f2PVrphK0u81ES256lw3oAZuF3x.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kYWhtZXItbW9uc3Rlci10aGUtamVmZnJleS1kYWhtZXItc3Rvcnk="},
    {"ad": "Terim", "logo": "https://www.themoviedb.org/t/p/w500/11dZf6VecxpYxsjvMROnAm8amBT.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90ZXJpbQ=="},
    {"ad": "La Casa de Papel: Korea", "logo": "https://www.themoviedb.org/t/p/w500/gDOC2BlwREpxdtidrRcoWNubYl1.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9sYS1jYXNhLWRlLXBhcGVsLWtvcmVh"},
    {"ad": "The Sandman", "logo": "https://www.themoviedb.org/t/p/w500/q54qEgagGOYCq5D1903eBVMNkbo.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtc2FuZG1hbg=="},
    {"ad": "Zeytin Ağacı", "logo": "https://www.themoviedb.org/t/p/w500/fWOg7CF3dRsX95z1i0E5pKBHh2U.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS96ZXl0aW4tYWdhY2k="},
    {"ad": "Kuş Uçuşu", "logo": "https://www.themoviedb.org/t/p/w500/vQqUosG4n63pYVF3JjOVDDYXUfx.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9rdXMtdWN1c3U="},
    {"ad": "Erşan Kuneri", "logo": "https://www.themoviedb.org/t/p/w500/sMuG3O5jx68ViIN8RTKtUiagdOA.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9lcnNhbi1rdW5lcmlA"},
    {"ad": "Welcome to Eden", "logo": "https://www.themoviedb.org/t/p/w500/A15lH3BWh3GtbWObKhq82qvkwVj.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS93ZWxjb21lLXRvLWVkZW4="},
    {"ad": "Heartstopper", "logo": "https://www.themoviedb.org/t/p/w500/wJJt1HG62h3WoGnLcRIbO2nNNkg.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9oZWFydHN0b3BwZXI="},
    {"ad": "Yakamoz S-245", "logo": "https://www.themoviedb.org/t/p/w500/11ur6ihlbYpl1HvKbFJBw1ox9YD.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95YWthbW96LXMtMjQ1"},
    {"ad": "Pieces of Her", "logo": "https://www.themoviedb.org/t/p/w500/yPTlbfrDv9asnHlCCd3XzM5noF1.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9waWVjZXMtb2YtaGVy"},
    {"ad": "Pera Palas’ta Gece Yarısı", "logo": "https://www.themoviedb.org/t/p/w500/iFMxljXHYaPsxN8uBBUfzfIyFeb.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9wZXJhLXBhbGFzLXRhLWdlY2UteWFyaXNp"},
    {"ad": "Vikings: Valhalla", "logo": "https://www.themoviedb.org/t/p/w500/izIMqapegdEZj0YVDyFATPR8adh.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS92aWtpbmdzLXZhbGhhbGxh"},
    {"ad": "Back to 15", "logo": "https://www.themoviedb.org/t/p/w500/iWZzSoADrns90iSrl0RIk6gupVu.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iYWNrLXRvLTE1"},
    {"ad": "Inventing Anna", "logo": "https://www.themoviedb.org/t/p/w500/jzCnl9wACp0eUMa3IG5e0aSJIXD.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9pbnZlbnRpbmctYW5uYQ=="},
    {"ad": "Toy Boy", "logo": "https://www.themoviedb.org/t/p/w500/bWC1GLZVBuYU4U0iadUfrVAtV2n.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90b3ktYm95"},
    {"ad": "In From the Cold", "logo": "https://www.themoviedb.org/t/p/w500/ntNgpXRm6C3ntN6eoINCTcypUmV.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9pbi1mcm9tLXRoZS1jb2xk"},
    {"ad": "All of Us Are Dead", "logo": "https://www.themoviedb.org/t/p/w500/8gjbGKe5WNOaLrkoeOUPLvDhPhK.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hbGwtb2YtdXMtYXJlLWRlYWQ="},
    {"ad": "Rebelde", "logo": "https://www.themoviedb.org/t/p/w500/b1IBsimEJOLjBLYsdBZ1VAcmq73.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9yZWJlbGRl"},
    {"ad": "D.P.", "logo": "https://www.themoviedb.org/t/p/w500/iJYqTUHHEzaTJQNr4LdPMb3imSQ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9kLXA="},
    {"ad": "Bad Blood", "logo": "https://www.themoviedb.org/t/p/w500/ukrAdTtJHHEaDRUJmi4XYwBUpRu.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iYWQtYmxvb2Q="},
    {"ad": "Aggretsuko", "logo": "https://www.themoviedb.org/t/p/w500/dTUE9KboSPXLoJ0K8VbOKt3O9ec.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hZ2dyZXRzdWtv"},
    {"ad": "Family Reunion", "logo": "https://www.themoviedb.org/t/p/w500/1FOJNlszjqBk5S1CDjnGvFTP2e4.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9mYW1pbHktcmV1bmlvbg=="},
    {"ad": "An Astrological Guide for Broken Hearts", "logo": "https://www.themoviedb.org/t/p/w500/m9evrUJvsRsygxB6N2LRuRUXu7e.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hbi1hc3Ryb2xvZ2ljYWwtZ3VpZGUtZm9yLWJyb2tlbi1oZWFydHM="},
    {"ad": "Alice in Borderland", "logo": "https://www.themoviedd.org/t/p/w500/20mOwAAPwZ1vLQkw0fvuQHiG7bO.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9hbGljZS1pbi1ib3JkZXJsYW5k"},
    {"ad": "Squid Game", "logo": "https://www.themoviedb.org/t/p/w500/1QdXdRYfktUSONkl1oD5gc6Be0s.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zcXVpZC1nYW1l"},
    {"ad": "Young Royals", "logo": "https://www.themoviedb.org/t/p/w500/6CHznbr0BF78ar16zJwTVRYLLOX.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95b3VuZy1yb3lhbHM="},
    {"ad": "Sexify", "logo": "https://www.themoviedb.org/t/p/w500/3mIrH23ar0lr8rj4SAW4kM6nJg6.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zZXhpZnk="},
    {"ad": "Sex Life", "logo": "https://www.themoviedb.org/t/p/w500/2ST6l4WP7ZfqAetuttBqx8F3AAH.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zZXgtbGlmZQ=="},
    {"ad": "Sweet Tooth", "logo": "https://www.themoviedb.org/t/p/w500/rgMfhcrVZjuy5b7Pn0KzCRCEnMX.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zd2VldC10b290aA=="},
    {"ad": "Fatma", "logo": "https://www.themoviedb.org/t/p/w500/efAH3wdr1ZuqK0sBmBdqvAZG7PT.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9mYXRtYQ=="},
    {"ad": "Shadow and Bone", "logo": "https://www.themoviedb.org/t/p/w500/mrVoyDFiDSqfH4mkoRtccOv2vwh.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zaGFkb3ctYW5kLWJvbmU="},
    {"ad": "Sky Rojo", "logo": "https://www.themoviedb.org/t/p/w500/lMJp1lqn6JA4uxIzsBQ79Pub5rv.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9za3ktcm9qbw=="},
    {"ad": "Ginny & Georgia", "logo": "https://www.themoviedb.org/t/p/w500/e4aqizYQ8eeTGNZMq6WiFfqoZbz.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9naW5ueS1nZW9yZ2lh"},
    {"ad": "Sweet Home", "logo": "https://www.themoviedb.org/t/p/w500/6eMg81CPLalULg8spPt2LxfQtFj.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zd2VldC1ob21l"},
    {"ad": "Lupin", "logo": "https://www.themoviedb.org/t/p/w500/sgxawbFB5Vi5OkPWQLNfl3dvkNJ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9sdXBpbg=="},
    {"ad": "Firefly Lane", "logo": "https://www.themoviedb.org/t/p/w500/zPCCi4LPsbXhOKUmpiQD2ug9a0I.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9maXJlZmx5LWxhbmU="},
    {"ad": "Fate: The Winx Saga", "logo": "https://www.themoviedb.org/t/p/w500/oHj6guMrLfQcBzo3uxwBJc8Y736.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9mYXRlLXRoZS13aW54LXNhZ2E="},
    {"ad": "Bridgerton", "logo": "https://www.themoviedb.org/t/p/w500/qaewZKBKmXjb4ZfFBb1LCug6BE8.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9icmlkZ2VydG9u"},
    {"ad": "La casa de papel", "logo": "https://www.themoviedb.org/t/p/w500/7SeDSAJHJv2z1N0tOUb5zUcBXE5.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9sYS1jYXNhLWRlLXBhcGVs"},
    {"ad": "The Crown", "logo": "https://www.themoviedb.org/t/p/w500/jkXkaZBg8GhFrnypBnVvGDuMj5c.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtY3Jvd24="},
    {"ad": "Barbarians", "logo": "https://www.themoviedb.org/t/p/w500/9SMlvujU685w9AU3at0eriDO6GO.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iYXJiYXJpYW5z"},
    {"ad": "Emily in Paris", "logo": "https://www.themoviedb.org/t/p/w500/kwMqIYOC4U9eK4NZnmmyD8pDEOi.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9lbWlseS1pbi1wYXJpcw=="},
    {"ad": "Ratched", "logo": "https://www.themoviedb.org/t/p/w500/cDNxOIm6K5D2W21QyJWZ95sJzQt.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9yYXRjaGVk"},
    {"ad": "Paradise PD", "logo": "https://www.themoviedb.org/t/p/w500/desSj4kx0y9p61vm9QBE3Wm8GxK.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9wYXJhZGlzZS1wZA=="},
    {"ad": "Young Wallander", "logo": "https://www.themoviedb.org/t/p/w500/8UhkwuaDFDarOO1GffY6XX6ZilP.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS95b3VuZy13YWxsYW5kZXI="},
    {"ad": "The Dragon Prince", "logo": "https://www.themoviedb.org/t/p/w500/d7PIRa6ez7ZEl9D4JUrnSsmcnVD.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtZHJhZ29uLXByaW5jZQ=="},
    {"ad": "Hilda", "logo": "https://www.themoviedb.org/t/p/w500/zDOuBpemOsOlnx6Mjp5bonuUjhM.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9oaWxkYQ=="},
    {"ad": "Warrior Nun", "logo": "https://www.themoviedb.org/t/p/w500/77OM9jMJ8nglaolHLwrAW7kvadV.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS93YXJyaW9yLW51bg=="},
    {"ad": "The Umbrella Academy", "logo": "https://www.themoviedb.org/t/p/w500/scZlQQYnDVlnpxFTxaIv2g0BWnL.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtdW1icmVsbGEtYWNhZGVteQ=="},
    {"ad": "How to Sell Drugs Online (Fast)", "logo": "https://www.themoviedb.org/t/p/w500/szk2hXe7etcSgyp6WxXCW1an301.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9ob3ctdG8tc2VsbC1kcnVncy1vbmxpbmUtZmFzdA=="},
    {"ad": "Outer Banks", "logo": "https://www.themoviedb.org/t/p/w500/ovDgO2LPfwdVRfvScAqo9aMiIW.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9vdXRlci1iYW5rcw=="},
    {"ad": "Never Have I Ever", "logo": "https://www.themoviedb.org/t/p/w500/ptAe2rs9MdBlaLqR4FTpfgQI5dT.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9uZXZlci1oYXZlLWktZXZlcg=="},
    {"ad": "Big Mouth", "logo": "https://www.themoviedb.org/t/p/w500/h6InpGTYbu03b6iVsnniVPqPfIw.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9iaWctbW91dGg="},
    {"ad": "The Witcher", "logo": "https://www.themoviedb.org/t/p/w500/FdsAB1Z1IbECvvPu4JMkS0eQTY.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS90aGUtd2l0Y2hlcg=="},
    {"ad": "Stranger Things", "logo": "https://www.themoviedb.org/t/p/w500/kpZHlOFAQitAj8f9gGhKBaIYWfJ.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zdHJhbmdlci10aGluZ3M="},
    {"ad": "Sex Education", "logo": "https://www.themoviedb.org/t/p/w500/gqUbBhDSnfUuo2tlJKzxFxylRWa.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9zZXgtZWR1Y2F0aW9u"},
    {"ad": "Russian Doll", "logo": "https://www.themoviedb.org/t/p/w500/4WijEAbnGMJifP6uepGALci3Jf.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9ydXNzaWFuLWRvbGw="},
    {"ad": "Ragnarok", "logo": "https://www.themoviedb.org/t/p/w500/1LRLLWGvs5sZdTzuMqLEahb88Pc.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9yYWduYXJvaw=="},
    {"ad": "Love, Death & Robots", "logo": "https://www.themoviedb.org/t/p/w500/cls82CWOAhEZB3HMpfkVLZNXTik.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9sb3ZlLWRlYXRoLXJvYm90cw=="},
    {"ad": "Elite", "logo": "https://www.themoviedb.org/t/p/w500//u4yfu7i4G1nLA6Njl7tETI1RThC.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6aS9lbGl0ZQ=="},
    {"ad": "Disenchantment", "logo": "https://www.themoviedb.org/t/p/w500//k1z30t71fZCWY2HkQBIOc7qLfBG.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6YS9kaXNlbmNoYW50bWVudA=="},
    {"ad": "Dead to Me", "logo": "https://www.themoviedb.org/t/p/w500//dU4K5KGQVqSae8IMd55XAExmxoE.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6YS9kZWFkLXRvLW1l"},
    {"ad": "Aşk 101", "logo": "https://www.themoviedb.org/t/p/w500//l6pLzAgUU2QpJ6KlsReqSqwWnfa.jpg", "link": "https://arenamovies.online/palx/Serie/aHR0cHM6Ly9kaXppcGFsMTIyMS5jb20vZGl6YS9hc2stMTAx"}
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
