from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):

    def send(self, obj, code=200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization"
        )
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.end_headers()

        self.wfile.write(
            json.dumps(
                obj,
                ensure_ascii=False
            ).encode("utf-8")
        )

    def do_OPTIONS(self):

        self.send_response(200)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization"
        )

        self.end_headers()

    def supabase(self):

        url = (
            os.environ.get("SUPABASE_URL")
            or ""
        ).strip().rstrip("/")

        key = (
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or ""
        ).strip()

        return url, key

    def get_rows(self, user_id):

        url, key = self.supabase()

        if not url or not key:
            return []

        full = (
            f"{url}/rest/v1/negocio_data"
            f"?user_id=eq."
            f"{urllib.parse.quote(user_id, safe='')}"
            f"&select=data"
        )

        req = urllib.request.Request(
            full,
            method="GET"
        )

        req.add_header(
            "apikey",
            key
        )

        req.add_header(
            "Authorization",
            f"Bearer {key}"
        )

        with urllib.request.urlopen(
            req,
            timeout=15
        ) as r:

            return json.loads(
                r.read().decode() or "[]"
            )

    # ---------------------------------------------------------
    # COMBINAR PRODUCTOS SIN BORRAR LOS EXISTENTES
    # ---------------------------------------------------------

    def merge_product_lists(self, old_list, new_list):

        if not isinstance(old_list, list):
            old_list = []

        if not isinstance(new_list, list):
            new_list = []

        productos = {}

        # Primero los productos que ya estaban guardados
        for p in old_list:

            if not isinstance(p, dict):
                continue

            pid = str(
                p.get("id") or ""
            ).strip()

            if not pid:
                continue

            productos[pid] = dict(p)

        # Después los nuevos/modificados
        for p in new_list:

            if not isinstance(p, dict):
                continue

            pid = str(
                p.get("id") or ""
            ).strip()

            if not pid:
                continue

            anterior = productos.get(
                pid,
                {}
            )

            combinado = dict(anterior)

            # Lo nuevo tiene prioridad
            combinado.update(p)

            # Si la nueva versión trae una foto válida,
            # conservarla.
            if p.get("foto"):
                combinado["foto"] = p.get("foto")

            # Si trae descripción, conservarla.
            if (
                p.get("descripcion")
                or p.get("descripcion_producto")
                or p.get("descripcionProducto")
            ):
                combinado["descripcion"] = (
                    p.get("descripcion")
                    or p.get("descripcion_producto")
                    or p.get("descripcionProducto")
                )

            productos[pid] = combinado

        return list(productos.values())

    # ---------------------------------------------------------
    # COMBINAR TODO EL OBJETO DE DATOS
    # ---------------------------------------------------------

    def merge_data(self, old_data, new_data):

        if not isinstance(old_data, dict):
            old_data = {}

        if not isinstance(new_data, dict):
            new_data = {}

        merged = dict(old_data)

        for key, value in new_data.items():

            # Productos por tienda
            if key.startswith("productosV2_"):

                merged[key] = self.merge_product_lists(
                    old_data.get(key, []),
                    value
                )

            # Lista general de productos
            elif key == "productosV2":

                merged[key] = self.merge_product_lists(
                    old_data.get(key, []),
                    value
                )

            else:

                # Para todos los demás datos:
                # lo nuevo reemplaza lo anterior.
                merged[key] = value

        return merged

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------

    def do_GET(self):

        try:

            qs = parse_qs(
                urlparse(self.path).query
            )

            user_id = (
                qs.get("user_id", [None])[0]
                or qs.get("email", [None])[0]
                or ""
            ).strip().lower()

            if not user_id:

                return self.send({
                    "ok": True,
                    "data": {}
                })

            rows = self.get_rows(
                user_id
            )

            data = {}

            for row in rows:

                row_data = (
                    row.get("data")
                    or {}
                )

                if isinstance(
                    row_data,
                    str
                ):

                    try:
                        row_data = json.loads(
                            row_data
                        )

                    except Exception:
                        row_data = {}

                if isinstance(
                    row_data,
                    dict
                ):

                    data = self.merge_data(
                        data,
                        row_data
                    )

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

    # ---------------------------------------------------------
    # POST
    # ---------------------------------------------------------

    def do_POST(self):

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            raw = (
                self.rfile.read(length)
                .decode("utf-8")
                if length
                else "{}"
            )

            body = json.loads(
                raw or "{}"
            )

            user_id = (
                body.get("user_id")
                or body.get("email")
                or ""
            ).strip().lower()

            incoming = (
                body.get("data")
                or {}
            )

            if not user_id:

                return self.send({
                    "ok": False,
                    "msg": "falta user_id"
                }, 400)

            if not isinstance(
                incoming,
                dict
            ):

                return self.send({
                    "ok": False,
                    "msg": "data debe ser un objeto"
                }, 400)

            url, key = self.supabase()

            if not url or not key:

                return self.send({

                    "ok": False,

                    "msg":
                        "Faltan SUPABASE_URL "
                        "o SUPABASE_SERVICE_ROLE_KEY "
                        "en Vercel"

                }, 500)

            # -------------------------------------------------
            # LEER LO QUE YA EXISTE
            # -------------------------------------------------

            rows = self.get_rows(
                user_id
            )

            merged = {}

            for row in rows:

                row_data = (
                    row.get("data")
                    or {}
                )

                if isinstance(
                    row_data,
                    str
                ):

                    try:

                        row_data = json.loads(
                            row_data
                        )

                    except Exception:

                        row_data = {}

                if isinstance(
                    row_data,
                    dict
                ):

                    merged = self.merge_data(
                        merged,
                        row_data
                    )

            # -------------------------------------------------
            # AGREGAR LO NUEVO SIN BORRAR PRODUCTOS
            # -------------------------------------------------

            merged = self.merge_data(
                merged,
                incoming
            )

            # -------------------------------------------------
            # PREPARAR DATOS PARA SUPABASE
            # -------------------------------------------------

            payload = json.dumps({

                "user_id": user_id,

                "data": merged

            }).encode("utf-8")

            # -------------------------------------------------
            # ACTUALIZAR FILA EXISTENTE
            # -------------------------------------------------

            if rows:

                patch_url = (

                    f"{url}/rest/v1/negocio_data"

                    f"?user_id=eq."
                    f"{urllib.parse.quote(user_id, safe='')}"

                )

                req = urllib.request.Request(

                    patch_url,

                    data=payload,

                    method="PATCH"

                )

                req.add_header(
                    "apikey",
                    key
                )

                req.add_header(
                    "Authorization",
                    f"Bearer {key}"
                )

                req.add_header(
                    "Content-Type",
                    "application/json"
                )

                req.add_header(
                    "Prefer",
                    "return=minimal"
                )

                with urllib.request.urlopen(
                    req,
                    timeout=15
                ) as r:

                    r.read()

            # -------------------------------------------------
            # CREAR PRIMERA FILA
            # -------------------------------------------------

            else:

                post_url = (
                    f"{url}/rest/v1/negocio_data"
                )

                req = urllib.request.Request(

                    post_url,

                    data=payload,

                    method="POST"

                )

                req.add_header(
                    "apikey",
                    key
                )

                req.add_header(
                    "Authorization",
                    f"Bearer {key}"
                )

                req.add_header(
                    "Content-Type",
                    "application/json"
                )

                req.add_header(
                    "Prefer",
                    "return=minimal"
                )

                with urllib.request.urlopen(
                    req,
                    timeout=15
                ) as r:

                    r.read()

            # -------------------------------------------------
            # RESPUESTA
            # -------------------------------------------------

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
