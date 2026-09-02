"""
Point d'entrée de la tâche planifiée (cron, une fois par jour).

Construit l'édition partagée du jour si elle n'existe pas encore, puis
régénère le fichier public consommé par test-comprehension-mondev.html.
Ne touche jamais à la progression individuelle des joueurs — ça, c'est
le rôle de get_edition_for_user()/submit_answer(), appelés par l'appli.

Envoie une notification push (ntfy.sh) UNIQUEMENT quand une édition
vraiment fraîche vient d'être ajoutée à l'instant — jamais sur un jour
creux, jamais en relisant le cache d'un jour déjà traité (rareté
volontaire du concept, cf. mémoire projet).
"""

import json
import os
import sys
from datetime import date, datetime

import requests

from edition_builder import SHARED_EDITIONS_FILE, build_shared_edition_of_the_day, get_mechanism

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
DEMO_URL = "http://54.38.26.33/test-comprehension-mondev.html"


def today_already_recorded() -> bool:
    try:
        with open(SHARED_EDITIONS_FILE) as f:
            editions = json.load(f)
    except FileNotFoundError:
        editions = {}
    return date.today().isoformat() in editions


def notify_new_edition(edition: dict):
    if not NTFY_TOPIC:
        return
    mechanism = get_mechanism(edition["mechanism_id"])
    message = f"{mechanism.label} — {mechanism.category.value}\n\nOuvre la démo pour deviner avant de comprendre."
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": "Nouvelle actu dans Le monde en mecanismes",
                "Click": DEMO_URL,
                "Tags": "newspaper",
            },
            timeout=10,
        )
    except Exception as e:
        # Une notif ratée ne doit jamais faire échouer le cron.
        print(f"notification ntfy échouée : {e}")


if __name__ == "__main__":
    is_new_run = not today_already_recorded()
    edition = build_shared_edition_of_the_day()

    if is_new_run and edition.get("type") == "fraîche":
        notify_new_edition(edition)

    stamp = datetime.now().isoformat(timespec="seconds")
    print(f"[{stamp}] type={edition.get('type')} "
          f"mechanism_id={edition.get('mechanism_id', '-')} "
          f"reason={edition.get('reason', '-')}")
    sys.exit(0)
