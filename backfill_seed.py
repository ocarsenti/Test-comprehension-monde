"""
Amorçage ponctuel (à lancer une seule fois, à la main) : fait tourner le
VRAI pipeline matcher/dresser sur plusieurs sous-lots des titres du jour,
pour peupler editions_partagees.json avec quelques éditions "fraîches"
avant même que le cron n'ait eu le temps d'en accumuler une par jour.

Aucun contenu n'est inventé ici — chaque édition passe par le même
matcher (seuil de confiance 0.7) et le même dresser que la tâche
planifiée quotidienne.
"""

import json
import random
from datetime import date, timedelta

from rss_sources import fetch_todays_headlines
from matcher import match_headlines_to_mechanism, CONFIDENCE_THRESHOLD
from dresser import dress_edition
from mechanisms_pool import get_mechanism, FULL_POOL
from edition_builder import SHARED_EDITIONS_FILE, export_public_edition

TARGET = 6
CHUNK_SIZE = 12


def main():
    headlines = fetch_todays_headlines()
    random.shuffle(headlines)
    print(f"{len(headlines)} titres collectés")

    try:
        with open(SHARED_EDITIONS_FILE) as f:
            editions = json.load(f)
    except FileNotFoundError:
        editions = {}

    used_mechanisms = set()
    found = 0
    day_offset = TARGET  # les éditions amorcées sont datées dans le passé récent

    for start in range(0, len(headlines), CHUNK_SIZE):
        if found >= TARGET:
            break
        chunk = headlines[start:start + CHUNK_SIZE]
        if not chunk:
            continue

        match = match_headlines_to_mechanism(chunk, FULL_POOL)
        if not match["matched"]:
            print(f"  lot {start}: pas de candidat ({match['reason']})")
            continue
        if match["mechanism_id"] in used_mechanisms:
            print(f"  lot {start}: mécanisme {match['mechanism_id']} déjà utilisé, ignoré")
            continue

        mechanism = get_mechanism(match["mechanism_id"])
        dressed = dress_edition(mechanism, match["headline"], match["reasoning"])
        day = (date.today() - timedelta(days=day_offset)).isoformat()
        day_offset -= 1
        editions[day] = {
            "date": day, "type": "fraîche", "mechanism_id": mechanism.id,
            "confidence": match["confidence"], "edition": dressed,
        }
        used_mechanisms.add(mechanism.id)
        found += 1
        print(f"  lot {start}: OK -> {mechanism.id} (confiance {match['confidence']}) daté {day}")

    with open(SHARED_EDITIONS_FILE, "w") as f:
        json.dump(editions, f, ensure_ascii=False, indent=2, default=str)

    export_public_edition(editions)
    print(f"\n{found} éditions amorcées. Fichier public régénéré.")


if __name__ == "__main__":
    main()
