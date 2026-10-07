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
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def supabase_get(self, url, service_key):
        req = urllib.request.Request(url, method="GET")
        req.add_header("apikey", service_key)
        req.add_header("Authorization", f"Bearer {service_key}")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8") or "[]")

    def extraer_productos(self, cloud_data, negocio_id):
        if not isinstance(cloud_data, dict):
            return []

        # La app principal guarda primero la copia específica del negocio.
        raw = cloud_data.get("productosV2_" + negocio_id)

        # Compatibilidad con datos anteriores que sólo tienen productosV2.
        if raw is None:
            raw = cloud_data.get("productosV2")

        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                raw = []

        if not isinstance(raw, list):
            return []

        productos = []
        for p in raw:
            if not isinstance(p, dict):
                continue

            productos.append({
                "id": p.get("id"),
                "nombre": p.get("nombre") or "Producto",
                "precio": p.get("venta") if p.get("venta") is not None else 0,
                "costo": p.get("costo") if p.get("costo") is not None else 0,
                "stock": None,
                "categoria": p.get("categoria") or "Otros",
                "barcode": p.get("barcode") or "",
                "foto": p.get("foto") or ""
            })

        return productos

    def do_GET(self):
        try:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            negocio_id = (
                qs.get("negocio_id", [None])[0]
                or qs.get("id", [None])[0]
                or ""
            ).strip()

            if not negocio_id:
                return self.send_json({"ok": False, "error": "Falta negocio_id"}, 400)

            supabase_url = (os.environ.get("SUPABASE_URL") or "").strip().rstrip("/")
            service_key = (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()

            if not supabase_url or not service_key:
                return self.send_json({
                    "ok": False,
                    "error": "Faltan las variables de Supabase en Vercel"
                }, 500)

            # 1) Obtenemos el negocio. No suponemos que negocios.user_id
            # sea el mismo identificador que usa negocio_data.
            negocio_url = (
                f"{supabase_url}/rest/v1/negocios"
                f"?id=eq.{urllib.parse.quote(negocio_id, safe='')}"
                f"&select=*"
            )
            negocios = self.supabase_get(negocio_url, service_key)

            if not negocios:
                return self.send_json({
                    "ok": False,
                    "error": "No se encontró el negocio"
                }, 404)

            negocio = negocios[0] or {}
            negocio_user_id = str(negocio.get("user_id") or "").strip()

            # 2) Primero intentamos exactamente con negocios.user_id.
            # Es la ruta rápida y compatible con la versión anterior.
            rows = []
            if negocio_user_id:
                data_url = (
                    f"{supabase_url}/rest/v1/negocio_data"
                    f"?user_id=eq.{urllib.parse.quote(negocio_user_id, safe='')}"
                    f"&select=user_id,data"
                )
                rows = self.supabase_get(data_url, service_key)

            # 3) Si no encontramos los productos, hacemos una búsqueda de
            # respaldo dentro de negocio_data. Esto corrige el caso en que
            # la app guardó negocio_data usando el correo mientras que
            # negocios.user_id contiene otro identificador.
            if not rows:
                all_data_url = (
                    f"{supabase_url}/rest/v1/negocio_data"
                    f"?select=user_id,data"
                )
                all_rows = self.supabase_get(all_data_url, service_key)

                key_specifica = "productosV2_" + negocio_id
                for row in all_rows:
                    data = row.get("data") if isinstance(row, dict) else None
                    if not isinstance(data, dict):
                        continue

                    if key_specifica in data:
                        rows = [row]
                        break

            # 4) Extraemos únicamente los productos del negocio solicitado.
            productos = []
            fuente = "ninguna"

            for row in rows:
                data = row.get("data") if isinstance(row, dict) else None
                encontrados = self.extraer_productos(data, negocio_id)
                if encontrados:
                    productos = encontrados
                    fuente = "productosV2_" + negocio_id
                    break

                # Si existe sólo la clave antigua productosV2, la usamos como
                # compatibilidad de respaldo.
                if isinstance(data, dict) and "productosV2" in data:
                    raw = data.get("productosV2")
                    if isinstance(raw, str):
                        try:
                            raw = json.loads(raw)
                        except Exception:
                            raw = []
                    if isinstance(raw, list) and raw:
                        productos = self.extraer_productos({"productosV2": raw}, negocio_id)
                        if productos:
                            fuente = "productosV2"
                            break

            return self.send_json({
                "ok": True,
                "negocio_id": negocio_id,
                "productos": productos,
                "fuente": fuente
            })

        except Exception as e:
            return self.send_json({"ok": False, "error": str(e)}, 500)
