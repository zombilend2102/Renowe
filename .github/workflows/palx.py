name: Run Dizipall8 Scraper Daily
run-name: Dizipall8 Scraper triggered by ${{ github.actor }}

on:
  schedule:
    - cron: '0 0 * * *'  # Her gün gece yarısı UTC'de çalıştır
  workflow_dispatch:  # Manuel tetiklemeye izin ver

jobs:
  scrape-movies:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4 pyyaml

      - name: Run the scraper
        run: python palx.py

      - name: Commit and push if changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add titan_tv_filmler.html palx.yml
          git diff --staged --quiet || git commit -m "Auto-update: Filmler güncellendi - $(date +'%Y-%m-%d %H:%M:%S')"
          git push
