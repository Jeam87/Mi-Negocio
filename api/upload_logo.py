from http.server import BaseHTTPRequestHandler
import json, os, base64, urllib.request, urllib.parse, time, urllib.error

class handler(BaseHTTPRequestHandler):
    def send(self, obj, code=200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8") if length else "{}")
            b64 = body.get("logo") or ""
            negocio_id = (body.get("negocio_id") or "default").strip()
            user_id = (body.get("user_id") or "").strip().lower()
            if not b64: return self.send({"ok": False, "msg": "falta logo"}, 400)
            url = (os.environ.get("SUPABASE_URL") or "").strip().rstrip("/")
            key = (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
            if "," in b64: b64 = b64.split(",", 1)[1]
            img_bytes = base64.b64decode(b64)
            bucket = "logos"
            path = f"{negocio_id}/logo.png"
            target = f"{url}/storage/v1/object/{bucket}/{path}"
            req = urllib.request.Request(target, data=img_bytes, method="POST")
            req.add_header("apikey", key)
            req.add_header("Authorization", f"Bearer {key}")
            req.add_header("Content-Type", "image/png")
            req.add_header("x-upsert", "true")
            try:
                with urllib.request.urlopen(req, timeout=30) as r: r.read()
            except urllib.error.HTTPError as e:
                if e.code in (400, 409, 404):
                    req2 = urllib.request.Request(target, data=img_bytes, method="PUT")
                    req2.add_header("apikey", key)
                    req2.add_header("Authorization", f"Bearer {key}")
                    req2.add_header("Content-Type", "image/png")
                    req2.add_header("x-upsert", "true")
                    with urllib.request.urlopen(req2, timeout=30) as r2: r2.read()
            public_url = f"{url}/storage/v1/object/public/{bucket}/{path}?t={int(time.time())}"
            if user_id:
                get_target = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id, safe='')}&select=data"
                greq = urllib.request.Request(get_target, method="GET")
                greq.add_header("apikey", key)
                greq.add_header("Authorization", f"Bearer {key}")
                with urllib.request.urlopen(greq, timeout=15) as gr:
                    rows = json.loads(gr.read().decode("utf-8") or "[]")
                old_data = {}
                for row in rows:
                    d = row.get("data")
                    if isinstance(d, str):
                        try: d = json.loads(d)
                        except: d = {}
                    if isinstance(d, dict): old_data.update(d)
                old_data["logo_url"] = public_url
                payload = json.dumps({"user_id": user_id, "data": old_data}).encode("utf-8")
                up_target = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id, safe='')}" if rows else f"{url}/rest/v1/negocio_data"
                ureq = urllib.request.Request(up_target, data=payload, method="PATCH" if rows else "POST")
                ureq.add_header("apikey", key)
                ureq.add_header("Authorization", f"Bearer {key}")
                ureq.add_header("Content-Type", "application/json")
                ureq.add_header("Prefer", "return=minimal")
                with urllib.request.urlopen(ureq, timeout=15) as ur: ur.read()
            return self.send({"ok": True, "url": public_url})
        except Exception as e:
            return self.send({"ok": False, "msg": str(e)}, 500)
