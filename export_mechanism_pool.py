#!/usr/bin/env python3
"""
Exporte FULL_POOL (mechanisms_pool.py) en JSON pour que le composant
MechanismGlobe (React/Three.js, globe/) puisse lire le vrai pool sans
jamais dupliquer son contenu à la main.

A relancer après toute modification manuelle du pool (ajout/retrait/
recatégorisation d'un mécanisme), puis reconstruire le globe :
    python3 export_mechanism_pool.py
    cd globe && npm run build

Sortie dans globe/public/ (pas globe/dist/) : Vite copie ce dossier tel
quel dans dist/ à chaque build, donc le fichier survit à un rebuild sans
avoir à le recopier manuellement, et nginx le sert déjà via l'alias
/globe/ existant, sans nginx config supplémentaire.
"""
import json
from pathlib import Path

from mechanisms_pool import FULL_POOL

OUT_PATH = Path(__file__).parent / "globe" / "public" / "mechanism_pool.json"


def main():
    pool = [
        {
            "id": m.id,
            "category": m.category.value,
            "label": m.label,
            "cause_effect": m.cause_effect,
        }
        for m in FULL_POOL
    ]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"mechanisms": pool}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(pool)} mécanismes exportés vers {OUT_PATH}")


if __name__ == "__main__":
    main()
