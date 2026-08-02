import datetime
import requests
from bs4 import BeautifulSoup

url_fil = "https://liberation.fr"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

articles_chrono = []

try:
    response = requests.get(url_fil, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Nouvelle technique : on cible spécifiquement les titres d'articles du fil d'actu
    # Libération utilise souvent des classes ou des structures imbriquées pour ses listes
    for card in soup.find_all(["div", "article"]):
        a_tag = card.find("a", href=True)
        if not a_tag:
            continue
            
        link = a_tag["href"]
        # On valide les liens d'articles de Libé
        if link.startswith("/") and len(link) > 15 and not any(x in link for x in ["/recherche", "/auteur", "/plan"]):
            # On cherche le texte du titre (parfois dans un h2, h3 ou span interne)
            title_element = a_tag.find(["h2", "h3", "span"])
            titre = title_element.text.strip() if title_element else a_tag.text.strip()
            
            if titre and len(titre) > 10 and not any(art["link"] == link for art in articles_chrono):
                url_complete = "https://liberation.fr" + link
                articles_chrono.append({
                    "title": titre,
                    "link": url_complete,
                    "description": "Nouvel article publié en direct sur Libération."
                })
except Exception as e:
    print(f"Erreur Libération : {e}")

# Si la structure principale a résisté, on utilise une méthode de secours globale sur la page
if not articles_chrono:
    try:
        for a_tag in soup.find_all("a", href=True):
            link = a_tag["href"]
            if link.startswith("/") and len(link) > 25 and not any(x in link for x in ["/recherche", "/conditions"]):
                titre = a_tag.text.strip()
                if titre and len(titre) > 15 and not any(art["link"] == link for art in articles_chrono):
                    articles_chrono.append({
                        "title": titre,
                        "link": "https://liberation.fr" + link,
                        "description": "Article du fil d'actualité."
                    })
    except:
        pass

if not articles_chrono:
    articles_chrono.append({
        "title": "Libération - En attente de nouvelles publications",
        "description": "Le flux se synchronisera automatiquement dès l'apparition d'une nouvelle dépêche.",
        "link": url_fil
    })

# Génération XML
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Libération - Fil Chrono Personnel</title>
    <link>{url_fil}</link>
    <description>Flux d'actualité brute minute par minute.</description>
    <lastBuildDate>{current_date}</lastBuildDate>
"""

for item in articles_chrono[:20]:
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

print("Flux Libé Chrono mis à jour !")
