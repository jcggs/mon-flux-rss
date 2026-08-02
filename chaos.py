import datetime
import requests
from bs4 import BeautifulSoup

url = "https://chaosreign.fr"

# En-têtes complets pour simuler un vrai navigateur et contourner les protections antirobots
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    # On cherche les balises H3 qui contiennent les titres des articles
    items = soup.find_all("h3")
except Exception as e:
    print(f"Erreur de connexion : {e}")
    items = []

articles = []

# Extraction des articles trouvés
for h3 in items:
    titre = h3.text.strip()
    if not titre or len(titre) < 5:
        continue
        
    a_tag = h3.find("a")
    lien_article = a_tag["href"] if a_tag and "href" in a_tag.attrs else url
    
    # Éviter les doublons
    if any(a["title"] == titre for a in articles):
        continue

    articles.append({
        "title": titre,
        "description": f"Nouvel article publié sur Chaos Reign : {titre}. Visitez le site pour lire la suite.",
        "link": lien_article
    })
    if len(articles) >= 5:
        break

# Si le site bloque encore, on crée un flux vide temporaire pour éviter que GitHub ne plante
if not articles:
    articles.append({
        "title": "Chaos Reign - Flux en attente",
        "description": "Le site est temporairement inaccessible pour le robot. Vérification automatique au prochain cycle.",
        "link": url
    })

# Génération du XML
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Chaos Reign - Flux Personnalisé</title>
    <link>{url}</link>
    <description>Suivi de l'actualité cinéma Chaos Reign.</description>
    <lastBuildDate>{current_date}</lastBuildDate>
"""

for idx, item in enumerate(articles):
    rss_xml += f"""    <item>
        <title><![CDATA[{item['title']}]]></title>
        <link>{item['link']}</link>
        <description><![CDATA[{item['description']}]]></description>
        <guid isPermaLink="true">{item['link']}</guid>
    </item>
"""

rss_xml += """</channel>
</rss>"""

with open("chaos.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux Chaos Reign généré avec succès dans 'chaos.xml' !")
