import datetime
import requests
from bs4 import BeautifulSoup

# 1. Récupérer le flux RSS général de Sud Ouest
url_source = "https://sudouest.fr"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

articles_gratuits = []

try:
    response = requests.get(url_source, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "xml")
    items = soup.find_all("item")

    for item in items:
        title = item.title.text.strip() if item.title else ""
        link = item.link.text.strip() if item.link else "https://sudouest.fr"
        description = item.description.text.strip() if item.description else ""

        # Détection du paywall Sud Ouest
        est_payant = False
        mots_cles_payants = ["abonnés", "abonné", "premium", "payant"]
        
        # Sud Ouest marque souvent ses articles payants avec "Abonnés" au début de la description
        for mot in mots_cles_payants:
            if mot in description.lower() or mot in title.lower():
                est_payant = True
                break

        # Si l'article est gratuit, on le garde
        if not est_payant and title:
            articles_gratuits.append({
                "title": title,
                "description": description if description else "Consultez cet article gratuit sur Sud Ouest.",
                "link": link
            })

except Exception as e:
    print(f"Erreur de lecture Sud Ouest : {e}")

# Message de sécurité si le flux est vide
if not articles_gratuits:
    articles_gratuits.append({
        "title": "Sud Ouest - En attente d'articles gratuits",
        "description": "Aucun article en libre accès disponible dans le flux actuel.",
        "link": "https://sudouest.fr"
    })

# 2. Générer le fichier XML final
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Sud Ouest - 100% Gratuit</title>
    <link>https://sudouest.fr</link>
    <description>Fil d'actualité Sud Ouest filtré sans articles abonnés.</description>
    <lastBuildDate>{current_date}</lastBuildDate>
"""

for item in articles_gratuits[:20]: # On garde les 20 derniers gratuits
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

print("Flux Sud Ouest gratuit généré !")
