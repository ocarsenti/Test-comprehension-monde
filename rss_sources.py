"""
Collecte des actualités du jour — aucune IA ici, juste des flux RSS
publics et gratuits. C'est volontaire : pas besoin de payer une
recherche web pour une liste de sources déjà connue à l'avance.

TRUSTED_SOURCES a été testé un par un (statut HTTP 200 + entrées non
vides) le 2026-09-02. Un flux peut changer d'adresse sans préavis —
si fetch_todays_headlines() ne renvoie plus rien pour une source, la
retester avant de la remettre en confiance aveugle.
"""

import feedparser  # pip install feedparser
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Headline:
    title: str
    summary: str
    source: str
    link: str
    published: datetime


# Testés individuellement le 2026-09-02 (statut 200, entrées présentes)
TRUSTED_SOURCES = {
    "Le Monde - International": "https://www.lemonde.fr/international/rss_full.xml",
    "Le Monde - Economie": "https://www.lemonde.fr/economie/rss_full.xml",
    "Le Monde - Planète": "https://www.lemonde.fr/planete/rss_full.xml",
    "Le Monde - Pixels": "https://www.lemonde.fr/pixels/rss_full.xml",
    "RFI - Monde": "https://www.rfi.fr/fr/monde/rss",
    "Courrier International": "https://www.courrierinternational.com/feed/all/rss.xml",
}


def fetch_todays_headlines(max_age_hours: int = 36) -> list[Headline]:
    """Récupère les titres récents de toutes les sources listées.
    Aucun appel LLM ici — juste du parsing RSS classique."""
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    headlines = []

    for source_name, feed_url in TRUSTED_SOURCES.items():
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"Erreur sur {source_name} : {e}")
            continue

        for entry in feed.entries:
            published = getattr(entry, "published_parsed", None)
            pub_dt = datetime(*published[:6]) if published else datetime.now()
            if pub_dt < cutoff:
                continue
            headlines.append(Headline(
                title=entry.get("title", ""),
                summary=entry.get("summary", ""),
                source=source_name,
                link=entry.get("link", ""),
                published=pub_dt,
            ))

    return headlines
