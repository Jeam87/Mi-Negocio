from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
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

    # ---------------------------------------------------------
    # SUPABASE
    # ---------------------------------------------------------

    def supabase(self):
        url = (
            os.environ.get("SUPABASE_URL") or ""
        ).strip().rstrip("/")

        key = (
            os.environ.get(
                "SUPABASE_SERVICE_ROLE_KEY"
            ) or ""
        ).strip()

        return url, key

    # ---------------------------------------------------------
    # LEER FILAS DEL USUARIO
    # ---------------------------------------------------------

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

        req.add_header("apikey", key)
        req.add_header(
            "Authorization",
            "Bearer " + key
        )

        with urllib.request.urlopen(
            req,
            timeout=20
        ) as r:

            contenido = r.read().decode() or "[]"

            return json.loads(contenido)

    # ---------------------------------------------------------
    # CONVERTIR DATA A DICCIONARIO
    # ---------------------------------------------------------

    def convertir_data(self, data):

        if not data:
            return {}

        if isinstance(data, str):

            try:
                data = json.loads(data)
            except Exception:
                return {}

        if not isinstance(data, dict):
            return {}

        return data

    # ---------------------------------------------------------
    # OBTENER LISTAS DE PRODUCTOS
    # ---------------------------------------------------------

    def obtener_listas_productos(self, data):

        listas = []

        if not isinstance(data, dict):
            return listas

        for clave, valor in data.items():

            # productosV2
            if clave == "productosV2":

                if isinstance(valor, str):
                    try:
                        valor = json.loads(valor)
                    except Exception:
                        valor = []

                if isinstance(valor, list):
                    listas.append(valor)

            # productosV2_ID_DE_NEGOCIO
            elif clave.startswith("productosV2_"):

                if isinstance(valor, str):
                    try:
                        valor = json.loads(valor)
                    except Exception:
                        valor = []

                if isinstance(valor, list):
                    listas.append(valor)

        return listas

    # ---------------------------------------------------------
    # UNIR PRODUCTOS SIN DUPLICAR
    # ---------------------------------------------------------

    def unir_productos(self, *listas):

        resultado = {}

        for lista in listas:

            if not isinstance(lista, list):
                continue

            for producto in lista:

                if not isinstance(producto, dict):
                    continue

                producto_id = producto.get("id")

                if producto_id is None:
                    continue

                clave = str(producto_id)

                # Si todavía no existe, agregarlo
                if clave not in resultado:

                    resultado[clave] = dict(producto)

                else:

                    # Si ya existe, combinar campos.
                    # Los valores nuevos NO vacíos tienen prioridad.
                    anterior = resultado[clave]

                    for campo, valor in producto.items():

                        if valor is None:
                            continue

                        if isinstance(valor, str) and not valor.strip():
                            continue

                        # No reemplazar una foto existente
                        # con una cadena vacía.
                        if campo == "foto":
                            if valor:
                                anterior[campo] = valor
                            continue

                        # No reemplazar descripción existente
                        # con una cadena vacía.
                        if campo == "descripcion":
                            if valor:
                                anterior[campo] = valor
                            continue

                        anterior[campo] = valor

        return list(resultado.values())

    # ---------------------------------------------------------
    # ASEGURAR PRODUCTOS EN DATA
    # ---------------------------------------------------------

    def proteger_productos(self, data):

        if not isinstance(data, dict):
            return data

        listas = self.obtener_listas_productos(data)

        # Buscar la lista que realmente tenga productos
        listas_validas = [
            lista
            for lista in listas
            if isinstance(lista, list) and len(lista) > 0
        ]

        if not listas_validas:
            return data

        productos_unidos = self.unir_productos(
            *listas_validas
        )

        if not productos_unidos:
            return data

        # Mantener productosV2 principal
        data["productosV2"] = productos_unidos

        # Mantener también cualquier clave
        # productosV2_ID que ya exista
        for clave in list(data.keys()):

            if clave.startswith("productosV2_"):
                data[clave] = productos_unidos

        return data

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

            rows = self.get_rows(user_id)

            data = {}

            for row in rows:

                row_data = self.convertir_data(
                    row.get("data")
                )

                if row_data:
                    data.update(row_data)

            # Proteger productos
            data = self.proteger_productos(data)

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
                self.rfile.read(length).decode(
                    "utf-8"
                )
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

            incoming = body.get("data") or {}

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
                    "msg": (
                        "Faltan SUPABASE_URL o "
                        "SUPABASE_SERVICE_ROLE_KEY "
                        "en Vercel"
                    )
                }, 500)

            # -------------------------------------------------
            # LEER DATOS EXISTENTES
            # -------------------------------------------------

            rows = self.get_rows(user_id)

            existente = {}

            for row in rows:

                row_data = self.convertir_data(
                    row.get("data")
                )

                if row_data:
                    existente.update(
                        row_data
                    )

            # -------------------------------------------------
            # UNIR DATOS GENERALES
            # -------------------------------------------------

            merged = dict(existente)

            for clave, valor in incoming.items():

                # Para productos, no permitir que [] borre
                # una lista que sí contiene productos.
                if (
                    clave == "productosV2"
                    or clave.startswith("productosV2_")
                ):

                    continue

                merged[clave] = valor

            # -------------------------------------------------
            # PRODUCTOS DEL SERVIDOR
            # -------------------------------------------------

            productos_existentes = []

            for lista in self.obtener_listas_productos(
                existente
            ):

                if lista:
                    productos_existentes = (
                        self.unir_productos(
                            productos_existentes,
                            lista
                        )
                    )

            # -------------------------------------------------
            # PRODUCTOS QUE LLEGAN DE LA APP
            # -------------------------------------------------

            productos_nuevos = []

            for lista in self.obtener_listas_productos(
                incoming
            ):

                if lista:
                    productos_nuevos = (
                        self.unir_productos(
                            productos_nuevos,
                            lista
                        )
                    )

            # -------------------------------------------------
            # COMBINAR PRODUCTOS
            # -------------------------------------------------

            todos_los_productos = self.unir_productos(
                productos_existentes,
                productos_nuevos
            )

            # -------------------------------------------------
            # GUARDAR PRODUCTOS
            # -------------------------------------------------

            if todos_los_productos:

                # Siempre guardar la lista buena
                merged["productosV2"] = (
                    todos_los_productos
                )

                # Conservar todas las claves
                # productosV2_ID que ya existan
                # o que lleguen desde la aplicación.

                claves_productos = set()

                for clave in existente.keys():

                    if clave.startswith(
                        "productosV2_"
                    ):
                        claves_productos.add(
                            clave
                        )

                for clave in incoming.keys():

                    if clave.startswith(
                        "productosV2_"
                    ):
                        claves_productos.add(
                            clave
                        )

                # Si no existe una clave específica,
                # no inventamos una.
                for clave in claves_productos:

                    merged[clave] = (
                        todos_los_productos
                    )

            else:

                # Si no llegaron productos,
                # conservar los que ya hubiera.
                for clave, valor in existente.items():

                    if (
                        clave == "productosV2"
                        or clave.startswith(
                            "productosV2_"
                        )
                    ):
                        if (
                            isinstance(valor, list)
                            and len(valor) > 0
                        ):
                            merged[clave] = valor

            # -------------------------------------------------
            # CREAR PAYLOAD
            # -------------------------------------------------

            payload = json.dumps({
                "user_id": user_id,
                "data": merged
            }, ensure_ascii=False).encode(
                "utf-8"
            )

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
                    "Bearer " + key
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
                    timeout=30
                ) as r:

                    r.read()

            # -------------------------------------------------
            # CREAR FILA NUEVA
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
                    "Bearer " + key
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
                    timeout=30
                ) as r:

                    r.read()

            return self.send({
                "ok": True,
                "user_id": user_id,
                "filas_encontradas": len(rows),
                "productos_guardados": len(
                    todos_los_productos
                ),
                "data": merged
            })

        except Exception as e:

            return self.send({
                "ok": False,
                "msg": str(e)
            }, 500)
