import datetime
import requests
from bs4 import BeautifulSoup

# 1. Télécharger la page de Chaos Reign
url = "https://chaosreign.fr"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Erreur lors de l'accès au site Chaos Reign.")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# 2. Trouver les articles de "A la une" (balises h3)
articles = []
items = soup.find_all("h3")

# On extrait les 5 premiers articles de la liste
for h3 in items[:5]:
    titre = h3.text.strip()
    
    # On cherche le lien de l'article s'il existe dans la balise h3
    a_tag = h3.find("a")
    lien_article = a_tag["href"] if a_tag and "href" in a_tag.attrs else url

    articles.append({
        "title": titre,
        "description": "Nouvel article publié sur Chaos Reign. Consultez le site pour lire la critique.",
        "link": lien_article
    })

# 3. Générer le fichier XML
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

# 4. Enregistrer dans un nouveau fichier XML séparé
with open("chaos.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux Chaos Reign généré avec succès dans 'chaos.xml' !")
