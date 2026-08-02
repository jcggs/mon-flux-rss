    # ... (le début reste identique) ...
    - name: Run Scraper
      run: |
        python scraper.py
        python chaos.py

    - name: Commit and Push changes
      run: |
        git config --global user.name "GitHub Action Robot"
        git config --global user.email "actions@github.com"
        git add flux.xml chaos.xml
        git commit -m "Mise à jour des flux RSS" || exit 0
        git push
