"""
3e patch ponctuel de /etc/nginx/sites-available/docalib_demo — à lancer
avec sudo. Étend la location regex des avatars pour inclure les 3
nouvelles images John (intro, rapporteur x2).

Usage : sudo python3 apply_nginx_patch_3.py
"""

import shutil
import sys
from datetime import datetime

CONF = "/etc/nginx/sites-available/docalib_demo"

OLD = """      location ~ ^/(john-cutout\\.png|veronica-cutout\\.png|dan-cutout\\.png)$ {
        alias /home/olive/comprehension_monde/$1;
        auth_basic off;
    }"""

NEW = """      location ~ ^/(john-cutout\\.png|veronica-cutout\\.png|dan-cutout\\.png|john-intro-cutout\\.png|john-2-cutout\\.png|john-3-cutout\\.png)$ {
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
