"""
2e patch ponctuel de /etc/nginx/sites-available/docalib_demo — à lancer
une seule fois avec sudo. Ajoute une location pour favicon.png (icône
propre à ce projet, indépendante du favicon.ico partagé du domaine).

Usage : sudo python3 apply_nginx_patch_2.py
"""

import shutil
import sys
from datetime import datetime

CONF = "/etc/nginx/sites-available/docalib_demo"

OLD = """      location = /edition_comprehension_monde.json {
        alias /home/olive/comprehension_monde/edition_comprehension_monde.json;
        default_type application/json;
        auth_basic off;
        add_header Cache-Control "no-store";
    }"""

NEW = """      location = /edition_comprehension_monde.json {
        alias /home/olive/comprehension_monde/edition_comprehension_monde.json;
        default_type application/json;
        auth_basic off;
        add_header Cache-Control "no-store";
    }

      location = /favicon.png {
        alias /home/olive/comprehension_monde/favicon.png;
        auth_basic off;
    }"""

if __name__ == "__main__":
    with open(CONF) as f:
        content = f.read()

    if OLD not in content:
        print("ERREUR : bloc attendu introuvable dans", CONF)
        print("Le fichier a peut-être déjà été modifié — vérifier à la main.")
        sys.exit(1)

    backup = f"{CONF}.bak-{datetime.now():%Y%m%d%H%M%S}"
    shutil.copy2(CONF, backup)
    print("Sauvegarde :", backup)

    with open(CONF, "w") as f:
        f.write(content.replace(OLD, NEW))
    print("Patché. Lancer maintenant : sudo nginx -t && sudo systemctl reload nginx")
