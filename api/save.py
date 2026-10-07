from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def send(self, obj, code=200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def supabase(self):
        url = (os.environ.get("SUPABASE_URL") or "").strip().rstrip("/")
        key = (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
        return url, key

    def get_rows(self, user_id):
        url, key = self.supabase()
        if not url or not key:
            return []
        full = (
            f"{url}/rest/v1/negocio_data"
            f"?user_id=eq.{urllib.parse.quote(user_id, safe='')}"
            f"&select=data"
        )
        req = urllib.request.Request(full, method="GET")
        req.add_header("apikey", key)
        req.add_header("Authorization", f"Bearer {key}")
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode() or "[]")

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            user_id = (
                qs.get("user_id", [None])[0]
                or qs.get("email", [None])[0]
                or ""
            ).strip().lower()

            if not user_id:
                return self.send({"ok": True, "data": {}})

            rows = self.get_rows(user_id)

            # Si por alguna razón hay más de una fila para el mismo usuario,
            # juntamos sus datos para no perder productos guardados en otra fila.
            data = {}
            for row in rows:
                row_data = row.get("data") or {}
                if isinstance(row_data, str):
                    try:
                        row_data = json.loads(row_data)
                    except Exception:
                        row_data = {}
                if isinstance(row_data, dict):
                    data.update(row_data)

            return self.send({
                "ok": True,
                "data": data,
                "user_id": user_id
            })

        except Exception as e:
            return self.send({
                "ok": False,
                "msg": str(e)
            }, 500)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            body = json.loads(raw or "{}")

            user_id = (
                body.get("user_id")
                or body.get("email")
                or ""
            ).strip().lower()

            incoming = body.get("data") or {}

            if not user_id:
                return self.send({"ok": False, "msg": "falta user_id"}, 400)

            if not isinstance(incoming, dict):
                return self.send({"ok": False, "msg": "data debe ser un objeto"}, 400)

            url, key = self.supabase()
            if not url or not key:
                return self.send({
                    "ok": False,
                    "msg": "Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Vercel"
                }, 500)

            # Leer TODAS las filas que existan para este usuario.
            # Esto también corrige el caso de que existan duplicados antiguos.
            rows = self.get_rows(user_id)

            merged = {}

            for row in rows:
                row_data = row.get("data") or {}
                if isinstance(row_data, str):
                    try:
                        row_data = json.loads(row_data)
                    except Exception:
                        row_data = {}
                if isinstance(row_data, dict):
                    merged.update(row_data)

            # Lo nuevo siempre tiene prioridad.
            merged.update(incoming)

            payload = json.dumps({
                "user_id": user_id,
                "data": merged
            }).encode("utf-8")

            if rows:
                # Actualiza las filas existentes en vez de hacer INSERT.
                # Así no dependemos de que user_id tenga una restricción UNIQUE.
                patch_url = (
                    f"{url}/rest/v1/negocio_data"
                    f"?user_id=eq.{urllib.parse.quote(user_id, safe='')}"
                )
                req = urllib.request.Request(
                    patch_url,
                    data=payload,
                    method="PATCH"
                )
                req.add_header("apikey", key)
                req.add_header("Authorization", f"Bearer {key}")
                req.add_header("Content-Type", "application/json")
                req.add_header("Prefer", "return=minimal")

                with urllib.request.urlopen(req, timeout=15) as r:
                    r.read()

            else:
                # Primera vez que se guarda este usuario.
                post_url = f"{url}/rest/v1/negocio_data"
                req = urllib.request.Request(
                    post_url,
                    data=payload,
                    method="POST"
                )
                req.add_header("apikey", key)
                req.add_header("Authorization", f"Bearer {key}")
                req.add_header("Content-Type", "application/json")
                req.add_header("Prefer", "return=minimal")

                with urllib.request.urlopen(req, timeout=15) as r:
                    r.read()

            return self.send({
                "ok": True,
                "data": merged,
                "user_id": user_id,
                "filas_encontradas": len(rows)
            })

        except Exception as e:
            return self.send({
                "ok": False,
                "msg": str(e)
            }, 500)
