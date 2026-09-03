#!/bin/bash
# Démarre admin_server.py au (re)démarrage du VPS — @reboot dans la
# crontab de l'utilisateur olive. Même pattern que daily_agent_cron.sh.
cd /home/olive/comprehension_monde || exit 1
exec .venv/bin/python3 admin_server.py
