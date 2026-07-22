name: Weekly Analyst Targets - Save to Repo 06:30 UK

on:
  schedule:
    - cron: '30 5 * * 6'  # 05:30 UTC = 06:30 BST. Use '30 6 * * 6' in winter
  workflow_dispatch:

permissions:
  contents: write

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install deps
        run: pip install requests beautifulsoup4 pandas lxml

      - name: Run scan
        run: python analyst_ratings_weekly_email.py

      - name: Save file with date and commit to repo
        run: |
          ls -lh analyst_targets_*.csv
          DATE=$(date +"%Y-%m-%d")
          cp analyst_targets_*.csv analyst_targets_weekly_${DATE}.csv || true
          cp analyst_targets_*.csv analyst_targets_weekly_latest.csv || true
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add analyst_targets_*.csv
          git commit -m "Weekly scan $DATE" || echo "No changes"
          git push


