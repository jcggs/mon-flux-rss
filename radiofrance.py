def fetch_feed(feed_url):
    """
    Télécharge un flux RSS en simulant un vrai navigateur pour éviter les blocages de Radio France.
    """
    headers = {
        # Un User-Agent plus proche d'un vrai navigateur pour éviter le blocage des datacenters GitHub
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    }

    # On autorise explicitement les redirections (allow_redirects=True)
    response = requests.get(feed_url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    
    # Si Radio France bloque, on affiche le code d'erreur exact dans les logs GitHub
    if response.status_code != 200:
        print(f"  [Attention] Code HTTP de retour : {response.status_code} pour {feed_url}")
        
    response.raise_for_status()
    return response.text


def build_rss(items):
    """
    Génère le fichier RSS final avec un encodage strict UTF-8 en majuscules pour Feedbin.
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
    
    # FORCE l'écriture en UTF-8 propre avec la déclaration XML attendue par Feedbin
    with open(OUTPUT_FILE, "wb") as f:
        f.write(b"<?xml version='1.0' encoding='UTF-8'?>\n")
        tree.write(f, encoding="utf-8", xml_declaration=False)
