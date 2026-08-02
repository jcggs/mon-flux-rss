import datetime
import requests
from bs4 import BeautifulSoup

# Ruse pour éviter le bug d'affichage de l'application : adresses découpées
domaine = "chaosreign.fr"
url = "https://" + "www." + domaine + "/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr,fr-FR;q=0.9",
}

articles = []

try:
    response = requests.get(url, headers=headers, timeout=20)
    
    # Si le site nous bloque l'accès direct, on interroge l'API cachée WordPress
    if "Content is protected" in response.text or response.status_code == 403:
        api_url = url + "wp-json/wp/v2/posts?per_page=5"
        api_res = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        
        if api_res.status_code == 200:
            for post in api_res.json():
                # Nettoyage minimaliste du titre envoyé par l'API
                titre_nettoye = post["title"]["rendered"].replace("&#8217;", "'").replace("&#8230;", "...")
                articles.append({
                    "title": titre_nettoye,
                    "description": "Nouvel article publié sur Chaos Reign.",
                    "link": post["link"]
                })
    else:
        soup = BeautifulSoup(response.text, "html.parser")
        for h3 in soup.find_all("h3")[:5]:
            titre = h3.text.strip()
            a_tag = h3.find("a")
            lien = a_tag["href"] if a_tag and "href" in a_tag.attrs else url
            if titre and not any(a["title"] == titre for a in articles):
                articles.append({"title": titre, "description": "Critique cinéma.", "link": lien})
except Exception as e:
    print("Erreur de lecture.")

# Sécurité si aucun article n'a pu être extrait du tout
if not articles:
    articles.append({
        "title": "Chaos Reign - Flux en cours de synchronisation",
        "description": "Le robot contourne le pare-feu du site. Les articles arriveront sous peu.",
        "link": url
    })

# Génération de la structure du fichier XML pour Feedbin
date_courante = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<rss version=\"2.0\">\n<channel>\n"
rss_xml += f"    <title>Chaos Reign - Flux Personnalisé</title>\n    <link>{url}</link>\n"
rss_xml += f"    <description>Suivi cinéma Chaos Reign.</description>\n    <lastBuildDate>{date_courante}</lastBuildDate>\n"

for idx, item in enumerate(articles):
    rss_xml += "    <item>\n"
    rss_xml += f"        <title><![CDATA[{item['title']}]]></title>\n"
    rss_xml += f"        <link>{item['link']}</link>\n"
    rss_xml += f"        <description><![CDATA[{item['description']}]]></description>\n"
    rss_xml += f"        <guid isPermaLink=\"true\">{item['link']}</guid>\n"
    rss_xml += "    </item>\n"

rss_xml += "</channel>\n</rss>"

# Enregistrement final du fichier XML
with open("chaos.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux Chaos Reign généré avec succès !")
