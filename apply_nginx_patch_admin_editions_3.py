"""
2e correctif du patch admin-editions — à lancer avec sudo.

Cause exacte (confirmée par /var/log/nginx/error.log) :
  [alert] "/home/olive/comprehension_monde/admin_editions.htmlindex.html"
  is not a directory
Un `index index.html;` hérité d'un contexte plus large fait que nginx,
dès qu'une location se termine par `/`, traite l'`alias` comme un
répertoire et lui accole le nom du fichier d'index — d'où le nom de
fichier corrompu ci-dessus. La page qui fonctionne déjà sur ce VPS
(/test-comprehension-mondev.html) n'a justement PAS de `/` final dans sa
location. Même correctif ici : le chemin sans slash (/admin-editions)
sert directement le fichier ; le chemin avec slash (/admin-editions/)
redirige vers lui, pour rester tolérant si quelqu'un tape le slash par
habitude.

Usage : sudo python3 apply_nginx_patch_admin_editions_3.py
"""

import shutil
import sys
from datetime import datetime

CONF = "/etc/nginx/sites-available/docalib_demo"

OLD = """      location = /admin-editions {
          return 301 /admin-editions/;
      }

      location = /admin-editions/ {
          alias /home/olive/comprehension_monde/admin_editions.html;
          auth_basic off;
      }"""

NEW = """      location = /admin-editions/ {
          return 301 /admin-editions;
      }

      location = /admin-editions {
          alias /home/olive/comprehension_monde/admin_editions.html;
          auth_basic off;
      }"""

if __name__ == "__main__":
    with open(CONF) as f:
        content = f.read()

    if OLD not in content:
        print("ERREUR : bloc attendu introuvable dans", CONF)
        print("Vérifier à la main avec :")
        print("  grep -B1 -A8 'location.*admin-editions' ", CONF)
        sys.exit(1)

    backup = f"{CONF}.bak-{datetime.now():%Y%m%d%H%M%S}"
    shutil.copy2(CONF, backup)
    print("Sauvegarde :", backup)

    with open(CONF, "w") as f:
        f.write(content.replace(OLD, NEW))
    print("Patché. Lancer maintenant :")
    print("  sudo nginx -t && sudo systemctl reload nginx")
    print("Puis tester : curl -s -o /dev/null -w '%{http_code}\\n' http://54.38.26.33/admin-editions")
