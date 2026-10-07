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
            raw = response.read().decode("utf-8") or "[]"
            return json.loads(raw)

    def convertir_data(self, value):
        """Convierte data de negocio_data a dict aunque Supabase la devuelva como texto JSON."""
        if isinstance(value, dict):
            # Algunas instalaciones pueden envolver el contenido como {"data": {...}}.
            inner = value.get("data")
            if isinstance(inner, dict):
                return inner
            if isinstance(inner, str):
                try:
                    parsed = json.loads(inner)
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    pass
            return value

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    inner = parsed.get("data")
                    if isinstance(inner, dict):
                        return inner
                    return parsed
            except Exception:
                return None

        return None

    def extraer_raw_productos(self, cloud_data, negocio_id):
        if not isinstance(cloud_data, dict):
            return None, None

        key_especifica = "productosV2_" + negocio_id
        if key_especifica in cloud_data:
            return cloud_data.get(key_especifica), key_especifica

        # Compatibilidad con la copia antigua.
        if "productosV2" in cloud_data:
            return cloud_data.get("productosV2"), "productosV2"

        return None, None

    def convertir_lista(self, raw):
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                return []
        return raw if isinstance(raw, list) else []

    def normalizar_productos(self, raw):
        raw = self.convertir_lista(raw)
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

            # Confirmamos que el negocio existe.
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
            key_especifica = "productosV2_" + negocio_id

            # Primero buscamos por el user_id de negocios.
            rows = []
            if negocio_user_id:
                data_url = (
                    f"{supabase_url}/rest/v1/negocio_data"
                    f"?user_id=eq.{urllib.parse.quote(negocio_user_id, safe='')}"
                    f"&select=user_id,data"
                )
                rows = self.supabase_get(data_url, service_key)

            # Si no hay fila o no contiene los productos, revisamos las filas
            # disponibles y soportamos data tanto JSON como texto JSON.
            candidatos = list(rows or [])
            if not candidatos:
                all_data_url = (
                    f"{supabase_url}/rest/v1/negocio_data"
                    f"?select=user_id,data"
                )
                candidatos = self.supabase_get(all_data_url, service_key)

            # Primero exigimos la clave específica del negocio.
            for row in candidatos:
                if not isinstance(row, dict):
                    continue
                data = self.convertir_data(row.get("data"))
                if not isinstance(data, dict):
                    continue

                raw, fuente = self.extraer_raw_productos(data, negocio_id)
                if fuente == key_especifica:
                    productos = self.normalizar_productos(raw)
                    return self.send_json({
                        "ok": True,
                        "negocio_id": negocio_id,
                        "productos": productos,
                        "fuente": fuente
                    })

            # Compatibilidad: sólo usamos productosV2 genérico si pertenece
            # a la fila encontrada por negocios.user_id. Así evitamos tomar
            # accidentalmente productos de otro negocio.
            if rows:
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    data = self.convertir_data(row.get("data"))
                    if not isinstance(data, dict):
                        continue
                    raw = data.get("productosV2")
                    productos = self.normalizar_productos(raw)
                    if productos:
                        return self.send_json({
                            "ok": True,
                            "negocio_id": negocio_id,
                            "productos": productos,
                            "fuente": "productosV2"
                        })

            return self.send_json({
                "ok": True,
                "negocio_id": negocio_id,
                "productos": [],
                "fuente": "ninguna"
            })

        except Exception as e:
            return self.send_json({"ok": False, "error": str(e)}, 500)
