"""
3e correctif du patch admin-editions — à lancer avec sudo.

Symptôme signalé par Olivier : cliquer sur http://54.38.26.33/admin-editions
télécharge un fichier au lieu d'afficher la page. Confirmé par curl -I :
Content-Type: application/octet-stream au lieu de text/html.

Cause : nginx détermine le type MIME d'après l'extension de l'URL
demandée, pas d'après le fichier réel servi via `alias`. Comme l'URL
/admin-editions n'a pas d'extension .html (contrairement à
/test-comprehension-mondev.html, qui fonctionne pour cette raison), nginx
retombe sur le type par défaut. Ajoute `default_type text/html;` pour
forcer le bon type sur cette location précise.

Usage : sudo python3 apply_nginx_patch_admin_editions_4.py
"""

import shutil
import sys
from datetime import datetime

CONF = "/etc/nginx/sites-available/docalib_demo"

OLD = """      location = /admin-editions {
          alias /home/olive/comprehension_monde/admin_editions.html;
          auth_basic off;
      }"""

NEW = """      location = /admin-editions {
          alias /home/olive/comprehension_monde/admin_editions.html;
          default_type text/html;
          auth_basic off;
      }"""

if __name__ == "__main__":
    with open(CONF) as f:
        content = f.read()

    if OLD not in content:
        print("ERREUR : bloc attendu introuvable dans", CONF)
        print("Vérifier à la main avec :")
        print("  grep -B1 -A8 'location = /admin-editions {' ", CONF)
        sys.exit(1)

    backup = f"{CONF}.bak-{datetime.now():%Y%m%d%H%M%S}"
    shutil.copy2(CONF, backup)
    print("Sauvegarde :", backup)

    with open(CONF, "w") as f:
        f.write(content.replace(OLD, NEW))
    print("Patché. Lancer maintenant :")
    print("  sudo nginx -t && sudo systemctl reload nginx")
    print("Puis vérifier : curl -sI http://54.38.26.33/admin-editions | grep Content-Type")
    print("(doit afficher : Content-Type: text/html)")
