import datetime
import requests
from bs4 import BeautifulSoup

domaine = "liberation.fr"
url_fil = "https://" + "www." + domaine + "/dernieres-nouvelles/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

articles_chrono = []

try:
    response = requests.get(url_fil, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    for card in soup.find_all(["div", "article"]):
        a_tag = card.find("a", href=True)
        if not a_tag:
            continue
            
        link = a_tag["href"]
        if link.startswith("/") and len(link) > 15 and not any(x in link for x in ["/recherche", "/auteur", "/plan"]):
            title_element = a_tag.find(["h2", "h3", "span"])
            titre = title_element.text.strip() if title_element else a_tag.text.strip()
            
            if titre and len(titre) > 10 and not any(art["link"] == link for art in articles_chrono):
                url_complete = "https://www." + domaine + link
                articles_chrono.append({
                    "title": titre,
                    "link": url_complete,
                    "description": "Nouvel article publie en direct sur Liberation."
                })
except Exception as e:
    print(f"Erreur : {e}")

if not articles_chrono:
    try:
        for a_tag in soup.find_all("a", href=True):
            link = a_tag["href"]
            if link.startswith("/") and len(link) > 25 and not any(x in link for x in ["/recherche", "/conditions"]):
                titre = a_tag.text.strip()
                if titre and len(titre) > 15 and not any(art["link"] == link for art in articles_chrono):
                    articles_chrono.append({
                        "title": titre,
                        "link": "https://www." + domaine + link,
                        "description": "Article du fil d'actualite."
                    })
    except:
        pass

if not articles_chrono:
    articles_chrono.append({
        "title": "Liberation - En attente de nouvelles publications",
        "description": "Le flux se synchronisera automatiquement des l'apparition d'une nouvelle depeche.",
        "link": url_fil
    })

current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
rss_xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<rss version=\"2.0\">\n<channel>\n"
rss_xml += f"    <title>Liberation - Fil Chrono Personnel</title>\n    <link>{url_fil}</link>\n"
rss_xml += f"    <description>Flux d'actualite brute minute par minute.</description>\n    <lastBuildDate>{current_date}</lastBuildDate>\n"

for item in articles_chrono[:20]:
    rss_xml += "    <item>\n"
    rss_xml += f"        <title><![CDATA[{item['title']}]]></title>\n"
    rss_xml += f"        <link>{item['link']}</link>\n"
    rss_xml += f"        <description><![CDATA[{item['description']}]]></description>\n"
    rss_xml += f"        <guid isPermaLink=\"true\">{item['link']}</guid>\n"
    rss_xml += "    </item>\n"

rss_xml += "</channel>\n</rss>"

# Enregistrement avec le nouveau nom de fichier propre pour forcer Feedbin
with open("libe_direct.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("Flux Libe Direct mis a jour !")
