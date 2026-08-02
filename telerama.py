import datetime
import requests
from bs4 import BeautifulSoup

# L'adresse magique qui regroupe TOUTES les rubriques du site
url_source = "https://telerama.fr"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

articles_gratuits = []

try:
    response = requests.get(url_source, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "xml")
    items = soup.find_all("item")

    for item in items:
        title = item.title.text.strip() if item.title else ""
        link = item.link.text.strip() if item.link else "https://www.telerama.fr"
        description = item.description.text.strip() if item.description else ""

        # Détection du paywall
        est_payant = False
        mots_cles_payants = ["réservé aux abonnés", "article abonnés", "abonnés", "payant"]
        
        for mot in mots_cles_payants:
            if mot in description.lower() or mot in title.lower():
                est_payant = True
                break

        # Si l'article est en libre accès, on l'engrange !
        if not est_payant and title:
            articles_gratuits.append({
                "title": title,
                "description": description if description else "Consultez cet article gratuit sur le site.",
                "link": link
            })

except Exception as e:
    print(f"Erreur de lecture générale : {e}")

# Message de sécurité si l'actualité immédiate est 100% verrouillée
if not articles_gratuits:
    articles_gratuits.append({
        "title": "Télérama - En attente d'articles gratuits",
        "description": "Aucun article en libre accès disponible dans le flux global à cet instant.",
        "link": "https://www.telerama.fr"
    })

# Création du fichier XML final
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Télérama - L'Offre Gratuite</title>
    <link>https://www.telerama.fr</link>
    <description>Le flux de la Une filtré sans aucun article payant.</description>
    <lastBuildDate>{current_date}</lastBuildDate>
"""

for item in articles_gratuits[:20]: # On garde jusqu'à 20 articles gratuits
    rss_xml += f"""    <item>
        <title><![CDATA[{item['title']}]]></title>
        <link>{item['link']}</link>
        <description><![CDATA[{item['description']}]]></description>
        <guid isPermaLink="true">{item['link']}</guid>
    </item>
"""

rss_xml += """</channel>
</rss>"""

with open("telerama_gratuit.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux Télérama Global Gratuit généré avec succès !")
