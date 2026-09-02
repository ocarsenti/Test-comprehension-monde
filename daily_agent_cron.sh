#!/bin/bash
# Appelé par cron une fois par jour. Toute la config (clé API) vit dans
# .env, jamais dans le crontab lui-même.
set -a
cd /home/olive/comprehension_monde || exit 1
source .env
set +a
exec .venv/bin/python3 run_daily_agent.py
