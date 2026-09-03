"""
Correctif du patch précédent (apply_nginx_patch_admin_editions.py) — à
lancer avec sudo. Le bloc `location /admin-editions/ { alias ...;
try_files admin_editions.html =404; }` renvoyait 404 (piège classique
nginx : `try_files` avec un `alias` de répertoire ne résout pas les noms
de fichiers comme on l'attendrait). Remplacé par le même schéma déjà
éprouvé pour /nextmove-v5/admin_retest.html : `alias` pointant
directement sur le fichier, sur une location à correspondance exacte.

Usage : sudo python3 apply_nginx_patch_admin_editions_2.py
"""

import shutil
import sys
from datetime import datetime

CONF = "/etc/nginx/sites-available/docalib_demo"

OLD = """      location /admin-editions/ {
          alias /home/olive/comprehension_monde/;
          try_files admin_editions.html =404;
          auth_basic "Comprehension Monde admin";
          auth_basic_user_file /etc/nginx/.htpasswd_comprehension_admin;
      }"""

NEW = """      location = /admin-editions/ {
          alias /home/olive/comprehension_monde/admin_editions.html;
          auth_basic "Comprehension Monde admin";
          auth_basic_user_file /etc/nginx/.htpasswd_comprehension_admin;
      }"""

if __name__ == "__main__":
    with open(CONF) as f:
        content = f.read()

    if OLD not in content:
        print("ERREUR : bloc attendu introuvable dans", CONF)
        print("Le fichier a peut-être déjà été corrigé — vérifier à la main avec :")
        print("  grep -A4 'location.*admin-editions/ {' ", CONF)
        sys.exit(1)

    backup = f"{CONF}.bak-{datetime.now():%Y%m%d%H%M%S}"
    shutil.copy2(CONF, backup)
    print("Sauvegarde :", backup)

    with open(CONF, "w") as f:
        f.write(content.replace(OLD, NEW))
    print("Patché. Lancer maintenant :")
    print("  sudo nginx -t && sudo systemctl reload nginx")
    print("Puis créer le mot de passe (SANS les chevrons, remplacer par un vrai nom) :")
    print("  sudo htpasswd -c /etc/nginx/.htpasswd_comprehension_admin nom_utilisateur")
