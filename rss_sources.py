"""
Collecte des actualités du jour — aucune IA ici, juste des flux RSS
publics et gratuits. C'est volontaire : pas besoin de payer une
recherche web pour une liste de sources déjà connue à l'avance.

Les URLs ci-dessous sont indicatives — À VÉRIFIER une par une avant mise
en prod (certains flux changent d'adresse sans préavis). Ne pas faire
confiance à cette liste telle quelle sans un test réel de chaque flux.
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


# Sources à vérifier individuellement — placeholders pour la structure,
# pas une liste validée
TRUSTED_SOURCES = {
    "AFP": "https://www.afp.com/fr/rss.xml",  # à vérifier
    "Reuters France": "https://www.reuters.com/world/france/rss",  # à vérifier
    "Le Monde - International": "https://www.lemonde.fr/international/rss_full.xml",  # à vérifier
    "Les Echos - Economie": "https://www.lesechos.fr/rss/rss_economie.xml",  # à vérifier
    "France Info": "https://www.francetvinfo.fr/titres.rss",  # à vérifier
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
