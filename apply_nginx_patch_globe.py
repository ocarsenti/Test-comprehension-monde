#!/usr/bin/env python3
"""
A LANCER PAR OLIVIER AVEC SUDO :
    sudo python3 /home/olive/comprehension_monde/apply_nginx_patch_globe.py

Ajoute un bloc `location /globe/` (dossier de build du composant
MechanismGlobe) dans /etc/nginx/sites-enabled/docalib_demo, juste avant le
bloc `location = /test-comprehension-mondev.html` existant, puis recharge
nginx. Idempotent : ne fait rien si le bloc existe déjà.
"""
import subprocess
import sys

CONF_PATH = "/etc/nginx/sites-enabled/docalib_demo"

BLOCK = """      location /globe/ {
        alias /home/olive/comprehension_monde/globe/dist/;
        index index.html;
        try_files $uri $uri/ /globe/index.html;
        auth_basic off;
    }

"""

ANCHOR = "      location = /test-comprehension-mondev.html {"


def main():
    with open(CONF_PATH, "r") as f:
        content = f.read()

    if "location /globe/" in content:
        print("Bloc /globe/ déjà présent — rien à faire.")
        return

    if ANCHOR not in content:
        print(f"ERREUR : ancre introuvable dans {CONF_PATH}, patch non appliqué.", file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(ANCHOR, BLOCK + ANCHOR, 1)

    with open(CONF_PATH, "w") as f:
        f.write(new_content)
    print(f"Bloc /globe/ inséré dans {CONF_PATH}.")

    test = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    print(test.stdout, test.stderr)
    if test.returncode != 0:
        print("ERREUR : nginx -t a échoué, restaure l'ancien fichier avant de recharger.", file=sys.stderr)
        with open(CONF_PATH, "w") as f:
            f.write(content)
        sys.exit(1)

    subprocess.run(["systemctl", "reload", "nginx"], check=True)
    print("nginx rechargé avec succès.")


if __name__ == "__main__":
    main()
