"""
Backend minimal de la page d'administration des éditions en attente
(admin_editions.html) — lister / approuver / rejeter les éditions parties
en revue humaine (voir edition_builder.py).

Volontairement sans nouvelle dépendance : http.server (stdlib) suffit pour
un outil interne à trois routes et faible trafic. L'authentification n'est
JAMAIS gérée ici — ce serveur n'écoute que sur 127.0.0.1, jamais exposé
directement à internet ; c'est nginx (auth_basic sur /admin-editions/, voir
apply_nginx_patch_admin_editions.py) qui protège l'accès. Si ce serveur
tournait un jour sans le reverse-proxy nginx devant lui, N'IMPORTE QUI
pourrait approuver/rejeter des éditions — ne jamais l'exposer autrement.

Lancement manuel : .venv/bin/python3 admin_server.py
Lancement persistant : voir la ligne crontab @reboot ajoutée par
apply_nginx_patch_admin_editions.py.
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from edition_builder import approve_pending_edition, list_pending_reviews, reject_pending_edition
from mechanisms_pool import get_mechanism

PORT = 8098


def _pending_with_mechanism_details() -> list[dict]:
    pending = list_pending_reviews()
    for item in pending:
        mechanism = get_mechanism(item["mechanism_id"])
        item["mechanism"] = {
            "label": mechanism.label,
            "category": mechanism.category.value,
            "type": mechanism.mechanism_type.value,
            "explanation": mechanism.explanation,
            "cause_effect": mechanism.cause_effect,
            "source": mechanism.source,
        } if mechanism else None
    return pending


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw or b"{}")

    def do_GET(self):
        if self.path == "/api/pending":
            try:
                self._send_json(200, {"pending": _pending_with_mechanism_details()})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "route inconnue"})

    def do_POST(self):
        try:
            data = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(400, {"error": "JSON invalide"})
            return

        day = data.get("date")
        if self.path == "/api/approve":
            if not day:
                self._send_json(400, {"error": "champ 'date' requis"})
                return
            try:
                edition = approve_pending_edition(day)
                self._send_json(200, {"ok": True, "edition": edition})
            except ValueError as e:
                self._send_json(404, {"error": str(e)})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        elif self.path == "/api/reject":
            if not day:
                self._send_json(400, {"error": "champ 'date' requis"})
                return
            try:
                edition = reject_pending_edition(day, data.get("reason", ""))
                self._send_json(200, {"ok": True, "edition": edition})
            except ValueError as e:
                self._send_json(404, {"error": str(e)})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "route inconnue"})

    def log_message(self, fmt, *args):
        pass  # silencieux : les erreurs passent déjà par _send_json / stderr du process


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"admin_server sur 127.0.0.1:{PORT} (routes : GET /api/pending, POST /api/approve, POST /api/reject)")
    server.serve_forever()
