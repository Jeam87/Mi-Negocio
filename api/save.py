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
        return ((os.environ.get("SUPABASE_URL") or "").strip().rstrip("/"),
                (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip())

    def get_rows(self, user_id):
        url, key = self.supabase()
        if not url or not key:
            raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Vercel")
        target = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id, safe='')}&select=user_id,data"
        req = urllib.request.Request(target, method="GET")
        req.add_header("apikey", key)
        req.add_header("Authorization", "Bearer " + key)
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8") or "[]")

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
        if "inventarioMaestro" in keys and "inventarioMaestro" not in ordered:
            ordered.append("inventarioMaestro")
        ordered += [k for k in keys if k not in ordered]
        return [a for k in ordered if (a := self.as_list(data.get(k))) is not None]

    @staticmethod
    def merge_lists(sources):
        # La primera copia manda para campos repetidos; las demás aportan artículos faltantes.
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

    @staticmethod
    def stamp(data):
        try: return int(float(data.get("inventarioMaestro_updatedAt") or 0))
        except Exception: return 0

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            uid = (qs.get("user_id", [None])[0] or qs.get("email", [None])[0] or "").strip().lower()
            if not uid: return self.send({"ok": False, "msg": "falta user_id"}, 400)
            rows = self.get_rows(uid)
            data = {}
            for row in rows: data.update(self.as_dict(row.get("data")))
            sources = self.inv_sources(data)
            if sources:
                inv = self.merge_lists(sources)
                data["inventarioMaestro"] = inv
                for k in self.inv_keys(data): data[k] = inv
            return self.send({"ok": True, "data": data, "user_id": uid})
        except Exception as e:
            return self.send({"ok": False, "msg": str(e)}, 500)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8") if length else "{}")
            uid = (body.get("user_id") or body.get("email") or "").strip().lower()
            incoming = body.get("data") or {}
            if not uid: return self.send({"ok": False, "msg": "falta user_id"}, 400)
            if not isinstance(incoming, dict): return self.send({"ok": False, "msg": "data debe ser un objeto"}, 400)
            url, key = self.supabase()
            if not url or not key: return self.send({"ok": False, "msg": "Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Vercel"}, 500)

            rows = self.get_rows(uid)
            old = {}
            for row in rows: old.update(self.as_dict(row.get("data")))
            merged = dict(old)
            for k, v in incoming.items():
                if k == "inventarioMaestro" or k.startswith("inventarioMaestro_") or k == "productosV2" or k.startswith("productosV2_"): continue
                merged[k] = v

            old_sources = self.inv_sources(old)
            new_sources = self.inv_sources(incoming)
            if old_sources or new_sources:
                # Union de todas las copias antiguas y entrantes para no perder materiales.
                inv = self.merge_lists(old_sources + new_sources)
                merged["inventarioMaestro"] = inv
                keys = set(self.inv_keys(old) + self.inv_keys(incoming))
                bid = self.business_id(incoming) or self.business_id(old)
                if bid: keys.add(f"inventarioMaestro_{bid}")
                for k in keys: merged[k] = inv
                merged["inventarioMaestro_updatedAt"] = str(max(self.stamp(incoming), self.stamp(old)))

            def product_lists(d):
                result = []
                for k, v in d.items():
                    if k == "productosV2" or k.startswith("productosV2_"):
                        a = self.as_list(v)
                        if a is not None: result.append(a)
                return result
            new_products = next((a for a in product_lists(incoming) if a), None)
            old_products = next((a for a in product_lists(old) if a), None)
            products = new_products if new_products is not None else old_products if old_products is not None else []
            if products or old_products is not None:
                merged["productosV2"] = products
                for k in set([x for x in old if x.startswith("productosV2_")] + [x for x in incoming if x.startswith("productosV2_")]): merged[k] = products

            payload = json.dumps({"user_id": uid, "data": merged}, ensure_ascii=False).encode("utf-8")
            if rows:
                target = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(uid, safe='')}"
                req = urllib.request.Request(target, data=payload, method="PATCH")
            else:
                req = urllib.request.Request(f"{url}/rest/v1/negocio_data", data=payload, method="POST")
            req.add_header("apikey", key)
            req.add_header("Authorization", "Bearer " + key)
            req.add_header("Content-Type", "application/json")
            req.add_header("Prefer", "return=minimal")
            with urllib.request.urlopen(req, timeout=30) as r: r.read()
            count = len(merged.get("inventarioMaestro", [])) if isinstance(merged.get("inventarioMaestro"), list) else 0
            return self.send({"ok": True, "user_id": uid, "filas_encontradas": len(rows), "inventario_materias_primas": count, "data": merged})
        except Exception as e:
            return self.send({"ok": False, "msg": str(e)}, 500)
 
