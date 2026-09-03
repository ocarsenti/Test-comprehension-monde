"""
4e correctif du patch admin-editions — à lancer avec sudo.

Le Content-Type était bien corrigé côté serveur (curl -I le confirme :
text/html), mais Olivier voyait toujours un téléchargement : le navigateur
avait mis en cache la première réponse (application/octet-stream) sous le
même ETag/Last-Modified, et continuait de s'y fier sans redemander au
serveur. Ajoute Cache-Control: no-store (même traitement que
edition_comprehension_monde.json) pour que ça ne se reproduise jamais,
quel que soit le contenu futur de la page.

Usage : sudo python3 apply_nginx_patch_admin_editions_5.py
"""

import shutil
import sys
from datetime import datetime

CONF = "/etc/nginx/sites-available/docalib_demo"

OLD = """      location = /admin-editions {
          alias /home/olive/comprehension_monde/admin_editions.html;
          default_type text/html;
          auth_basic off;
      }"""

NEW = """      location = /admin-editions {
          alias /home/olive/comprehension_monde/admin_editions.html;
          default_type text/html;
          add_header Cache-Control "no-store";
          auth_basic off;
      }"""

if __name__ == "__main__":
    with open(CONF) as f:
        content = f.read()

    if OLD not in content:
        print("ERREUR : bloc attendu introuvable dans", CONF)
        print("Vérifier à la main avec :")
        print("  grep -B1 -A9 'location = /admin-editions {' ", CONF)
        sys.exit(1)

    backup = f"{CONF}.bak-{datetime.now():%Y%m%d%H%M%S}"
    shutil.copy2(CONF, backup)
    print("Sauvegarde :", backup)

    with open(CONF, "w") as f:
        f.write(content.replace(OLD, NEW))
    print("Patché. Lancer maintenant :")
    print("  sudo nginx -t && sudo systemctl reload nginx")
    print("Puis, côté navigateur, un rechargement forcé (Ctrl+Maj+R) ou la navigation")
    print("privée pour ignorer l'ancien cache déjà posé avant ce correctif.")
