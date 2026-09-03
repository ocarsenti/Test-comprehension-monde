"""
CLI pour trancher les éditions parties en revue humaine — rattachement
limite (confiance entre 0.5 et 0.7) ou relecture automatique (auditor.py)
ayant signalé un problème de rigueur. Rien de ce qui est listé ici n'est
visible des joueurs tant qu'il n'a pas été explicitement approuvé.

Usage :
  python3 revoir_editions.py              # liste tout ce qui est en attente
  python3 revoir_editions.py list
  python3 revoir_editions.py approve 2026-09-04
  python3 revoir_editions.py reject 2026-09-04 "raison optionnelle"
"""

import sys

from edition_builder import approve_pending_edition, list_pending_reviews, reject_pending_edition


def cmd_list():
    pending = list_pending_reviews()
    if not pending:
        print("Rien en attente de validation.")
        return

    for p in pending:
        print(f"\n=== {p['date']} — {p['mechanism_id']} (confiance rattachement : {p.get('confidence')}) ===")
        print(f"Raison de la mise en attente : {p.get('reason', '-')}")

        audit = p.get("audit") or {}
        if audit.get("issues"):
            print("Problèmes relevés par la relecture automatique :")
            for issue in audit["issues"]:
                print(f"  - {issue}")

        edition = p.get("edition") or {}
        print(f"Intro : {edition.get('intro', '')}")
        print(f"Situation : {edition.get('situation', '')}")
        for opt in edition.get("options", []):
            marker = "✓" if opt.get("correct") else " "
            print(f"  [{marker}] {opt.get('text')}")

        src = p.get("source_headline") or {}
        if src:
            print(f"Actu source : « {src.get('title')} » ({src.get('source')}) — {src.get('link')}")

    print(f"\n{len(pending)} édition(s) en attente. "
          f"python3 revoir_editions.py approve <date>  /  reject <date> [\"raison\"]")


def cmd_approve(day: str):
    approve_pending_edition(day)
    print(f"{day} approuvée et publiée (fichier public régénéré).")


def cmd_reject(day: str, reason: str = ""):
    reject_pending_edition(day, reason)
    print(f"{day} rejetée." + (f" Raison : {reason}" if reason else ""))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "list":
        cmd_list()
    elif args[0] == "approve" and len(args) >= 2:
        cmd_approve(args[1])
    elif args[0] == "reject" and len(args) >= 2:
        cmd_reject(args[1], args[2] if len(args) > 2 else "")
    else:
        print(__doc__)
        sys.exit(1)
