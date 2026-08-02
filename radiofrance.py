import html
import sys
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup


FEEDS = [
    {
        "name": "France Inter",
        "url": "https://www.radiofrance.fr/franceinter/rss",
    },
    {
        "name": "France Culture",
        "url": "https://www.radiofrance.fr/franceculture/rss",
    },
    {
        "name": "France Musique",
        "url": "https://www.radiofrance.fr/francemusique/rss",
    },
    {
        "name": "FIP",
        "url": "https://www.radiofrance.fr/fip/rss",
    },
    {
        "name": "Mouv'",
        "url": "https://www.radiofrance.fr/mouv/rss",
    },
]

OUTPUT_FILE = "radiofrance.xml"
PUBLIC_FEED_URL = "https://jcggs.github.io/mon-flux-rss/radiofrance.xml"
MAX_ITEMS = 300
REQUEST_TIMEOUT = 30

USER_AGENT = (
    "Mozilla/5.0 (compatible; mon-flux-rss/1.0; "
    "+https://jcggs.github.io/mon-flux-rss/)"
)


def clean_text(value):
    """
    Nettoie un texte venant d'un flux RSS :
    - accepte None ;
    - décode les entités HTML ;
    - retire les espaces parasites.
    """
    if value is None:
        return ""

    text = str(value)
    text = html.unescape(text)
    text = text.strip()
    return text


def get_tag_text(parent, tag_name, default=""):
    """
    Récupère le texte d'une balise XML/RSS.
    """
    tag = parent.find(tag_name)
    if tag is None:
        return default

    text = tag.get_text()
    text = clean_text(text)

    if not text:
        return default

    return text


def parse_date(value):
    """
    Convertit une date RSS en objet datetime.

    Si la date est absente ou invalide, on renvoie la date actuelle.
    Cela évite que tout le script échoue pour un seul item mal formé.
    """
    value = clean_text(value)

    if not value:
        return datetime.now(timezone.utc)

    try:
        parsed = parsedate_to_datetime(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed
    except Exception:
        return datetime.now(timezone.utc)


def fetch_feed(feed_url):
    """
    Télécharge un flux RSS.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }

    response = requests.get(feed_url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.text


def parse_items(xml_text, source_name, source_url):
    """
    Analyse le XML d'un flux Radio France et renvoie une liste d'épisodes.
    """
    soup = BeautifulSoup(xml_text, "xml")

    channel = soup.find("channel")
    channel_title = source_name

    if channel is not None:
        channel_title = get_tag_text(channel, "title", source_name)

    items = []

    for item in soup.find_all("item"):
        title = get_tag_text(item, "title", "Sans titre")
        link = get_tag_text(item, "link", "")
        description = get_tag_text(item, "description", "")
        pub_date_raw = get_tag_text(item, "pubDate", "")
        pub_date = parse_date(pub_date_raw)

        guid = get_tag_text(item, "guid", "")
        if not guid:
            guid = link or f"{source_name}-{title}-{format_datetime(pub_date)}"

        enclosure = item.find("enclosure")
        enclosure_data = None

        if enclosure is not None:
            enclosure_url = clean_text(enclosure.get("url", ""))
            enclosure_type = clean_text(enclosure.get("type", "audio/mpeg"))
            enclosure_length = clean_text(enclosure.get("length", "0"))

            if enclosure_url:
                enclosure_data = {
                    "url": enclosure_url,
                    "type": enclosure_type or "audio/mpeg",
                    "length": enclosure_length or "0",
                }

        # On ignore les items sans lien et sans audio : ils seraient peu utiles.
        if not link and not enclosure_data:
            continue

        items.append(
            {
                "source_name": source_name,
                "channel_title": channel_title,
                "title": title,
                "display_title": f"{source_name} — {title}",
                "link": link,
                "description": description,
                "pub_date": pub_date,
                "guid": guid,
                "source_url": source_url,
                "enclosure": enclosure_data,
            }
        )

    return items


def add_text_element(parent, tag_name, text):
    """
    Ajoute une balise texte en s'assurant que None ne casse pas le XML.
    """
    element = ET.SubElement(parent, tag_name)
    element.text = clean_text(text)
    return element


def build_rss(items):
    """
    Génère le fichier RSS final.
    """
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")

    rss = ET.Element(
        "rss",
        {
            "version": "2.0",
            "xmlns:atom": "http://www.w3.org/2005/Atom",
        },
    )

    channel = ET.SubElement(rss, "channel")

    add_text_element(channel, "title", "Radio France — Grand flux")
    add_text_element(channel, "link", "https://www.radiofrance.fr/rss")
    add_text_element(
        channel,
        "description",
        (
            "Flux chronologique compilant les podcasts de France Inter, "
            "France Culture, France Musique, FIP et Mouv'."
        ),
    )
    add_text_element(channel, "language", "fr")
    add_text_element(channel, "lastBuildDate", format_datetime(datetime.now(timezone.utc)))

    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", PUBLIC_FEED_URL)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for item_data in items:
        item = ET.SubElement(channel, "item")

        add_text_element(item, "title", item_data["display_title"])

        # Le lien web officiel Radio France est important :
        # sur téléphone, il peut ouvrir l'application Radio France si le système
        # et le lecteur RSS prennent en charge les liens universels.
        add_text_element(item, "link", item_data["link"])

        add_text_element(item, "description", item_data["description"])
        add_text_element(item, "pubDate", format_datetime(item_data["pub_date"]))

        guid = add_text_element(item, "guid", item_data["guid"])
        guid.set("isPermaLink", "false")

        source = add_text_element(item, "source", item_data["source_name"])
        source.set("url", item_data["source_url"])

        if item_data["enclosure"] is not None:
            ET.SubElement(
                item,
                "enclosure",
                {
                    "url": item_data["enclosure"]["url"],
                    "type": item_data["enclosure"]["type"],
                    "length": item_data["enclosure"]["length"],
                },
            )

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)


def main():
    all_items = []
    failed_feeds = []

    for feed in FEEDS:
        source_name = feed["name"]
        source_url = feed["url"]

        print(f"Téléchargement : {source_name} — {source_url}")

        try:
            xml_text = fetch_feed(source_url)
            items = parse_items(xml_text, source_name, source_url)

            print(f"  {len(items)} éléments trouvés.")
            all_items.extend(items)

        except Exception as error:
            print(f"  Erreur avec {source_name} : {error}")
            failed_feeds.append(source_name)

    if not all_items:
        print("Aucun élément récupéré. Le fichier RSS ne sera pas généré.")
        sys.exit(1)

    all_items.sort(key=lambda item: item["pub_date"], reverse=True)
    all_items = all_items[:MAX_ITEMS]

    build_rss(all_items)

    print(f"{OUTPUT_FILE} généré avec {len(all_items)} éléments.")

    if failed_feeds:
        print("Flux en erreur : " + ", ".join(failed_feeds))


if __name__ == "__main__":
    main()
