"""
Patch ponctuel de /etc/nginx/sites-available/docalib_demo — à lancer avec
sudo. Ajoute la page d'administration des éditions en attente
(admin_editions.html + son API admin_server.py sur 127.0.0.1:8098),
protégée par un htpasswd dédié — même pattern que /naming-tool/ et
/nextmove-v5/admin_retest.html déjà en place sur ce serveur.

Étapes après avoir lancé ce script :
  1. sudo htpasswd -c /etc/nginx/.htpasswd_comprehension_admin <identifiant>
     (choisir un identifiant/mot de passe à donner à la personne à qui la
     tâche de revue est déléguée — -c écrase le fichier s'il existe déjà,
     retirer -c pour AJOUTER un identifiant sans effacer les autres)
  2. sudo nginx -t && sudo systemctl reload nginx
  3. démarrer le backend (si pas déjà fait) :
     cd /home/olive/comprehension_monde && nohup .venv/bin/python3 admin_server.py >> logs/admin_server.log 2>&1 &
  4. pour qu'il redémarre après un reboot du VPS, ajouter à la crontab de
     l'utilisateur olive (crontab -e, PAS besoin de sudo pour cette ligne) :
     @reboot cd /home/olive/comprehension_monde && nohup .venv/bin/python3 admin_server.py >> logs/admin_server.log 2>&1 &

Usage : sudo python3 apply_nginx_patch_admin_editions.py
"""

import shutil
import sys
from datetime import datetime

CONF = "/etc/nginx/sites-available/docalib_demo"

OLD = """      location = /favicon.png {
        alias /home/olive/comprehension_monde/favicon.png;
        auth_basic off;
    }"""

NEW = """      location = /favicon.png {
        alias /home/olive/comprehension_monde/favicon.png;
        auth_basic off;
    }

      location /admin-editions/api/ {
          proxy_pass http://127.0.0.1:8098/api/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          auth_basic "Comprehension Monde admin";
          auth_basic_user_file /etc/nginx/.htpasswd_comprehension_admin;
      }

      location = /admin-editions {
          return 301 /admin-editions/;
      }

      location /admin-editions/ {
          alias /home/olive/comprehension_monde/;
          try_files admin_editions.html =404;
          auth_basic "Comprehension Monde admin";
          auth_basic_user_file /etc/nginx/.htpasswd_comprehension_admin;
      }"""

if __name__ == "__main__":
    with open(CONF) as f:
        content = f.read()

    if OLD not in content:
        print("ERREUR : bloc attendu introuvable dans", CONF)
        print("Le fichier a peut-être déjà été modifié — vérifier à la main.")
        sys.exit(1)

    if "/admin-editions/" in content:
        print("Le bloc /admin-editions/ semble déjà présent — rien fait, vérifier à la main.")
        sys.exit(1)

    backup = f"{CONF}.bak-{datetime.now():%Y%m%d%H%M%S}"
    shutil.copy2(CONF, backup)
    print("Sauvegarde :", backup)

    with open(CONF, "w") as f:
        f.write(content.replace(OLD, NEW))
    print("Patché. Voir le docstring de ce fichier pour les 4 étapes restantes")
    print("(htpasswd, reload nginx, démarrer admin_server.py, ligne @reboot).")
