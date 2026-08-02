import datetime
import requests
from bs4 import BeautifulSoup

# Configuration sur mesure ancrée sur votre lieu de vie
flux_sources = {
    "Mont-de-Marsan": "https://sudouest.fr",
    "Landes": "https://sudouest.fr",
    "Planete": "https://sudouest.fr",
    "Eco": "https://sudouest.fr"
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
articles_gratuits = []

# Le robot scanne vos 4 flux prioritaires
for rubrique, url in flux_sources.items():
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "xml")
        items = soup.find_all("item")

        for item in items:
            title = item.title.text.strip() if item.title else ""
            link = item.link.text.strip() if item.link else "https://sudouest.fr"
            description = item.description.text.strip() if item.description else ""

            # Tri strict du paywall
            est_payant = False
            mots_cles_payants = ["abonnés", "abonné", "premium", "payant"]
            
            for mot in mots_cles_payants:
                if mot in description.lower() or mot in title.lower():
                    est_payant = True
                    break

            # Validation de l'article en libre accès sans doublon
            if not est_payant and title and not any(a["link"] == link for a in articles_gratuits):
                articles_gratuits.append({
                    "title": f"[{rubrique}] {title}",
                    "description": description if description else "Consultez cet article gratuit.",
                    "link": link
                })
    except Exception as e:
        print(f"Erreur sur {rubrique} : {e}")

# Message de secours
if not articles_gratuits:
    articles_gratuits.append({
        "title": "Sud Ouest Landes - En attente d'articles gratuits",
        "description": "Aucun article local en libre accès disponible à cet instant précis.",
        "link": "https://sudouest.frlandes/"
    })

# Génération du fichier XML final
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Sud Ouest - Landes &amp; Mont-de-Marsan</title>
    <link>https://sudouest.frlandes/</link>
    <description>Actualités locales filtrées 100% gratuites.</description>
    <lastBuildDate>{current_date}</lastBuildDate>
"""

for item in articles_gratuits[:25]:
    rss_xml += f"""    <item>
        <title><![CDATA[{item['title']}]]></title>
        <link>{item['link']}</link>
        <description><![CDATA[{item['description']}]]></description>
        <guid isPermaLink="true">{item['link']}</guid>
    </item>
"""

rss_xml += """</channel>
</rss>"""

with open("sudouest_gratuit.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux Sud Ouest Landes généré avec succès !")
