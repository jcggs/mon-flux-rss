import datetime
import requests
from bs4 import BeautifulSoup

# 1. Télécharger la page du site
url = "https://textes-a-la-pelle.fr"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Erreur lors de l'accès au site.")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# 2. Trouver toutes les annonces
annonces = []
items = soup.find_all("h2")

for h2 in items[:5]:
    editeur = h2.text.strip()
    h3 = h2.find_next("h3")
    titre_concours = h3.text.strip() if h3 else "Appel à textes"

    details = h2.find_next_siblings("p")
    echeance = "Non spécifiée"
    for p in details:
        if "Envois jusqu'au" in p.text:
            echeance = p.text.strip()
            break

    annonces.append(
        {
            "title": f"[{editeur}] {titre_concours}",
            "description": f"Date limite : {echeance}. Consultez le site pour plus de détails.",
            "link": url,
        }
    )

# 3. Générer la structure du fichier XML (Flux RSS)
current_date = datetime.datetime.now(datetime.timezone.utc).strftime(
    "%a, %d %b %Y %H:%M:%S GMT"
)

rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Textes à la pelle - Flux Personnalisé</title>
    <link>{url}</link>
    <description>Suivi automatisé des derniers concours d'écriture.</description>
    <lastBuildDate>{current_date}</lastBuildDate>
"""

for idx, item in enumerate(annonces):
    rss_xml += f"""    <item>
        <title><![CDATA[{item['title']}]]></title>
        <link>{item['link']}?id={idx}</link>
        <description><![CDATA[{item['description']}]]></description>
        <guid isPermaLink="false">talp-{idx}-{current_date[:11].replace(' ', '')}</guid>
    </item>
"""

rss_xml += """</channel>
</rss>"""

# 4. Enregistrer le résultat
with open("flux.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux RSS généré avec succès dans 'flux.xml' !")
