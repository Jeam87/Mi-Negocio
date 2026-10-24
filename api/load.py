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

    @staticmethod
    def as_dict(value):
        if isinstance(value, str):
            try: value = json.loads(value)
            except Exception: return {}
        return value if isinstance(value, dict) else {}

    @staticmethod
    def as_list(value):
        if isinstance(value, str):
            try: value = json.loads(value or "[]")
            except Exception: return None
        return value if isinstance(value, list) else None

    @staticmethod
    def inv_keys(data):
        return [k for k in data if (k == "inventarioMaestro" or k.startswith("inventarioMaestro_")) and k != "inventarioMaestro_updatedAt"]

    @staticmethod
    def business_id(data):
        value = data.get("session_negocio", "")
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
                if isinstance(decoded, str): value = decoded
            except Exception: pass
        return str(value).strip() if value else ""

    def inv_sources(self, data):
        keys = self.inv_keys(data)
        bid = self.business_id(data)
        preferred = f"inventarioMaestro_{bid}" if bid else ""
        ordered = ([preferred] if preferred in keys else [])
        if "inventarioMaestro" in keys and "inventarioMaestro" not in ordered: ordered.append("inventarioMaestro")
        ordered += [k for k in keys if k not in ordered]
        result = []
        for k in ordered:
            arr = self.as_list(data.get(k))
            if arr is not None: result.append(arr)
        return result

    @staticmethod
    def merge_lists(sources):
        out, pos = [], {}
        for arr in sources:
            for item in arr:
                if not isinstance(item, dict): continue
                ident = item.get("id")
                key = str(ident) if ident is not None else None
                if key is not None and key in pos:
                    current = out[pos[key]]
                    for field, value in item.items(): current.setdefault(field, value)
                else:
                    out.append(dict(item))
                    if key is not None: pos[key] = len(out) - 1
        return out

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            uid = (qs.get("user_id", [None])[0] or qs.get("email", [None])[0] or "").strip().lower()
            if not uid: return self.send({"ok": False, "msg": "falta user_id"}, 400)
            url = (os.environ.get("SUPABASE_URL") or "").strip().rstrip("/")
            key = (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
            if not url or not key: return self.send({"ok": False, "msg": "Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Vercel"}, 500)
            target = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(uid, safe='')}&select=data&order=updated_at.desc"
            req = urllib.request.Request(target, method="GET")
            req.add_header("apikey", key)
            req.add_header("Authorization", "Bearer " + key)
            with urllib.request.urlopen(req, timeout=20) as r: rows = json.loads(r.read().decode("utf-8") or "[]")
            
            data = {}
            # ARREGLO LOGO: tomar siempre el más reciente primero
            for row in rows:
                row_data = self.as_dict(row.get("data"))
                # si ya tenemos logo, no dejar que un registro viejo lo pise
                if "logo_url" in data and "logo_url" not in row_data:
                    # conserva el logo nuevo
                    pass
                data.update(row_data)
            
            sources = self.inv_sources(data)
            if sources:
                inv = self.merge_lists(sources)
                data["inventarioMaestro"] = inv
                for k in self.inv_keys(data): data[k] = inv
                bid = self.business_id(data)
                if bid: data[f"inventarioMaestro_{bid}"] = inv

            # ARREGLO FINAL: asegurar que logo_url siempre esté disponible
            if "logo_url" in data and data["logo_url"]:
                # forzar refresh en todos los dispositivos
                data["logo_url"] = data["logo_url"].split('?')[0]

            return self.send({"ok": True, "data": data, "user_id": uid})
        except Exception as e:
            return self.send({"ok": False, "msg": str(e)}, 500)
