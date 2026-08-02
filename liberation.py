import datetime
import requests
from bs4 import BeautifulSoup

url_fil = "https://liberation.fr"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

articles_chrono = []

try:
    response = requests.get(url_fil, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Sur le site de Libé, les articles du fil d'actu sont dans des balises h2 ou h3 spécifiques
    # Nous ciblons les liens des articles de la page de flux
    for a_tag in soup.find_all("a", href=True):
        link = a_tag["href"]
        
        # On ne garde que les vrais liens d'articles (qui commencent par une catégorie)
        if link.startswith("/") and len(link) > 20 and not link.startswith("/recherche"):
            titre = a_tag.text.strip()
            # On évite les textes vides, les doublons et les tags de rubriques
            if titre and len(titre) > 10 and not any(art["link"] == link for art in articles_chrono):
                url_complete = "https://liberation.fr" + link
                articles_chrono.append({
                    "title": titre,
                    "link": url_complete,
                    "description": "Nouvel article publié sur le fil d'actualité Libération."
                })
except Exception as e:
    print(f"Erreur Libération : {e}")

if not articles_chrono:
    articles_chrono.append({
        "title": "Libération - En attente de dépêches",
        "description": "Aucun article extrait pour le moment.",
        "link": url_fil
    })

# Génération de la structure XML
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Libération - Fil Chrono Personnel</title>
    <link>{url_fil}</link>
    <description>Flux d'actualité brute minute par minute.</description>
    <lastBuildDate>{current_date}</lastBuildDate>
"""

for item in articles_chrono[:20]: # On liste les 20 plus récents
    rss_xml += f"""    <item>
        <title><![CDATA[{item['title']}]]></title>
        <link>{item['link']}</link>
        <description><![CDATA[{item['description']}]]></description>
        <guid isPermaLink="true">{item['link']}</guid>
    </item>
"""

rss_xml += """</channel>
</rss>"""

with open("libe_chrono.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux Libé Chrono généré !")
