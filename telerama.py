import datetime
import requests
from bs4 import BeautifulSoup

# 1. Récupérer le flux RSS officiel du Cinéma de Télérama
url_source = "https://telerama.fr"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

articles_gratuits = []

try:
    response = requests.get(url_source, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "xml")  # On lit le format XML de Télérama
    items = soup.find_all("item")

    for item in items:
        title = item.title.text.strip() if item.title else "Article"
        link = item.link.text.strip() if item.link else "https://telerama.fr"
        description = item.description.text.strip() if item.description else ""

        # RUSE : Télérama ajoute souvent une mention ou coupe la description pour les abonnés.
        # On vérifie aussi si le mot "abonné" ou "payant" se cache dans le texte.
        est_payant = False
        mots_cles_payants = ["réservé aux abonnés", "article abonnés", "payant"]
        
        for mot in mots_cles_payants:
            if mot in description.lower() or mot in title.lower():
                est_payant = True
                break

        # Si l'article n'est pas détecté comme payant, on le garde !
        if not est_payant:
            articles_gratuits.append({
                "title": title,
                "description": description if description else "Consultez l'article gratuit sur Télérama.",
                "link": link
            })

except Exception as e:
    print(f"Erreur lors de la lecture de Télérama : {e}")

# Si aucun article gratuit n'a été trouvé (rare), on met un message informatif
if not articles_gratuits:
    articles_gratuits.append({
        "title": "Télérama - Aucun nouvel article gratuit",
        "description": "Tous les articles récents sont réservés aux abonnés.",
        "link": "https://telerama.fr"
    })

# 2. Générer le fichier XML propre pour votre Feedbin
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Télérama Cinéma - 100% Gratuit</title>
    <link>https://telerama.fr</link>
    <description>Flux filtré sans aucun article payant.</description>
    <lastBuildDate>{current_date}</lastBuildDate>
"""

for item in articles_gratuits[:10]:  # On garde les 10 derniers gratuits
    rss_xml += f"""    <item>
        <title><![CDATA[{item['title']}]]></title>
        <link>{item['link']}</link>
        <description><![CDATA[{item['description']}]]></description>
        <guid isPermaLink="true">{item['link']}</guid>
    </item>
"""

rss_xml += """</channel>
</rss>"""

# 3. Enregistrer le résultat dans votre espace public
with open("telerama_gratuit.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux Télérama gratuit généré avec succès !")
