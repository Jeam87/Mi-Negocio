from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse


class handler(BaseHTTPRequestHandler):

    def send_json(self, obj, code=200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            json.dumps(obj, ensure_ascii=False).encode("utf-8")
        )

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        try:
            qs = urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query
            )

            negocio_id = (
                qs.get("negocio_id", [None])[0]
                or qs.get("id", [None])[0]
                or ""
            ).strip()

            if not negocio_id:
                return self.send_json(
                    {"ok": False, "error": "Falta negocio_id"},
                    400
                )

            supabase_url = (
                os.environ.get("SUPABASE_URL") or ""
            ).strip().rstrip("/")

            service_key = (
                os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
            ).strip()

            if not supabase_url or not service_key:
                return self.send_json(
                    {
                        "ok": False,
                        "error": "Faltan las variables de Supabase en Vercel"
                    },
                    500
                )

            # 1. Buscar el negocio para obtener su user_id.
            negocio_url = (
                f"{supabase_url}/rest/v1/negocios"
                f"?id=eq.{urllib.parse.quote(negocio_id, safe='')}"
                f"&select=id,user_id"
            )

            req = urllib.request.Request(
                negocio_url,
                method="GET"
            )
            req.add_header("apikey", service_key)
            req.add_header("Authorization", f"Bearer {service_key}")

            with urllib.request.urlopen(req, timeout=15) as response:
                negocios = json.loads(
                    response.read().decode("utf-8") or "[]"
                )

            if not negocios:
                return self.send_json(
                    {"ok": False, "error": "No se encontró el negocio"},
                    404
                )

            user_id = str(negocios[0].get("user_id") or "").strip()

            if not user_id:
                return self.send_json(
                    {"ok": False, "error": "El negocio no tiene user_id"},
                    404
                )

            # 2. Leer solamente el respaldo de ese negocio.
            data_url = (
                f"{supabase_url}/rest/v1/negocio_data"
                f"?user_id=eq.{urllib.parse.quote(user_id, safe='')}"
                f"&select=data"
            )

            req = urllib.request.Request(
                data_url,
                method="GET"
            )
            req.add_header("apikey", service_key)
            req.add_header("Authorization", f"Bearer {service_key}")

            with urllib.request.urlopen(req, timeout=15) as response:
                rows = json.loads(
                    response.read().decode("utf-8") or "[]"
                )

            cloud_data = {}
            if rows:
                cloud_data = rows[0].get("data") or {}

            # La app principal guarda una copia específica por negocio.
            raw_products = cloud_data.get(
                "productosV2_" + negocio_id
            )

            # Respaldo para instalaciones que todavía usan la clave general.
            if raw_products is None:
                raw_products = cloud_data.get("productosV2")

            if raw_products is None:
                raw_products = []

            if isinstance(raw_products, str):
                try:
                    raw_products = json.loads(raw_products)
                except Exception:
                    raw_products = []

            if not isinstance(raw_products, list):
                raw_products = []

            productos = []

            for p in raw_products:
                if not isinstance(p, dict):
                    continue

                productos.append({
                    "id": p.get("id"),
                    "nombre": p.get("nombre") or "Producto",
                    "precio": p.get("venta") or 0,
                    "costo": p.get("costo") or 0,
                    "stock": None,
                    "categoria": p.get("categoria") or "Otros",
                    "barcode": p.get("barcode") or "",
                    "foto": p.get("foto") or ""
                })

            return self.send_json({
                "ok": True,
                "negocio_id": negocio_id,
                "productos": productos
            })

        except Exception as e:
            return self.send_json(
                {"ok": False, "error": str(e)},
                500
            )
