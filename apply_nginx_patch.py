"""
Patch ponctuel de /etc/nginx/sites-available/docalib_demo — à lancer une
seule fois avec sudo. Fait pointer test-comprehension-mondev.html, les
3 avatars et le nouveau edition_comprehension_monde.json directement sur
/home/olive/comprehension_monde/ (via alias), pour que le cron (utilisateur
olive, sans sudo) puisse écrire le JSON du jour sans jamais toucher à
/var/www/html/.

Usage : sudo python3 apply_nginx_patch.py
"""

import shutil
import sys
from datetime import datetime

CONF = "/etc/nginx/sites-available/docalib_demo"

OLD = """      location = /test-comprehension-mondev.html {
        root /var/www/html;
        auth_basic off;
    }

      location ~ ^/(john-cutout\\.png|veronica-cutout\\.png|dan-cutout\\.png)$ {
        root /var/www/html;
        auth_basic off;
    }"""

NEW = """      location = /test-comprehension-mondev.html {
        alias /home/olive/comprehension_monde/test-comprehension-mondev.html;
        auth_basic off;
    }

      location = /edition_comprehension_monde.json {
        alias /home/olive/comprehension_monde/edition_comprehension_monde.json;
        default_type application/json;
        auth_basic off;
        add_header Cache-Control "no-store";
    }

      location ~ ^/(john-cutout\\.png|veronica-cutout\\.png|dan-cutout\\.png)$ {
        alias /home/olive/comprehension_monde/$1;
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
