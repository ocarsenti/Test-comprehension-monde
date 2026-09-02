"""
Point d'entrée de la tâche planifiée (cron, une fois par jour).

Construit l'édition partagée du jour si elle n'existe pas encore, puis
régénère le fichier public consommé par test-comprehension-mondev.html.
Ne touche jamais à la progression individuelle des joueurs — ça, c'est
le rôle de get_edition_for_user()/submit_answer(), appelés par l'appli.
"""

import sys
from datetime import datetime

from edition_builder import build_shared_edition_of_the_day

if __name__ == "__main__":
    edition = build_shared_edition_of_the_day()
    stamp = datetime.now().isoformat(timespec="seconds")
    print(f"[{stamp}] type={edition.get('type')} "
          f"mechanism_id={edition.get('mechanism_id', '-')} "
          f"reason={edition.get('reason', '-')}")
    sys.exit(0)
