import os
import json
import urllib.parse
import urllib.request
import urllib.error
import base64
import uuid

from http.server import BaseHTTPRequestHandler


# ============================================================
# RESPUESTAS
# ============================================================

def responder(handler, datos, codigo=200):

    cuerpo = json.dumps(
        datos,
        ensure_ascii=False
    ).encode("utf-8")

    handler.send_response(codigo)

    handler.send_header(
        "Access-Control-Allow-Origin",
        "*"
    )

    handler.send_header(
        "Access-Control-Allow-Methods",
        "POST, OPTIONS"
    )

    handler.send_header(
        "Access-Control-Allow-Headers",
        "Content-Type"
    )

    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )

    handler.send_header(
        "Content-Length",
        str(len(cuerpo))
    )

    handler.end_headers()

    handler.wfile.write(cuerpo)


# ============================================================
# LEER JSON
# ============================================================

def leer_json(handler):

    try:

        cantidad = int(
            handler.headers.get(
                "Content-Length",
                "0"
            )
        )

        contenido = (
            handler.rfile
            .read(cantidad)
            .decode("utf-8")
        )

        return json.loads(
            contenido or "{}"
        )

    except Exception:

        return {}


# ============================================================
# VARIABLES DE ENTORNO
# ============================================================

def env(nombre):

    return os.getenv(
        nombre,
        ""
    ).strip()


SUPABASE_URL = env(
    "SUPABASE_URL"
)

SUPABASE_KEY = env(
    "SUPABASE_SERVICE_ROLE_KEY"
)

STRIPE_SECRET_KEY = env(
    "STRIPE_SECRET_KEY"
)

# Si quieres puedes colocar aquí la URL
# principal de la tienda mediante Vercel.
#
# También se acepta success_url enviado
# desde el frontend.

STORE_URL = env(
    "STORE_URL"
)


# ============================================================
# PETICIÓN A SUPABASE
# ============================================================

def supabase_request(
    metodo,
    tabla,
    datos=None,
    filtros=None,
    select=None
):

    if not SUPABASE_URL:

        raise RuntimeError(
            "Falta SUPABASE_URL."
        )

    if not SUPABASE_KEY:

        raise RuntimeError(
            "Falta SUPABASE_SERVICE_ROLE_KEY."
        )

    url = (
        SUPABASE_URL.rstrip("/")
        + "/rest/v1/"
        + tabla
    )

    parametros = []

    if filtros:

        for campo, valor in filtros.items():

            parametros.append(
                urllib.parse.quote(
                    campo,
                    safe=""
                )
                + "=eq."
                + urllib.parse.quote(
                    str(valor),
                    safe=""
                )
            )

    if select:

        parametros.append(
            "select="
            + urllib.parse.quote(
                select,
                safe=""
            )
        )

    if parametros:

        url += "?" + "&".join(
            parametros
        )

    cuerpo = None

    if datos is not None:

        cuerpo = json.dumps(
            datos,
            ensure_ascii=False
        ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=cuerpo,
        method=metodo
    )

    request.add_header(
        "apikey",
        SUPABASE_KEY
    )

    request.add_header(
        "Authorization",
        "Bearer " + SUPABASE_KEY
    )

    request.add_header(
        "Content-Type",
        "application/json"
    )

    request.add_header(
        "Accept",
        "application/json"
    )

    request.add_header(
        "Prefer",
        "return=representation"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as respuesta:

            texto = (
                respuesta
                .read()
                .decode("utf-8")
            )

            if not texto:

                return []

            return json.loads(
                texto
            )

    except urllib.error.HTTPError as error:

        texto = ""

        try:

            texto = (
                error.read()
                .decode("utf-8")
            )

        except Exception:
            pass

        raise RuntimeError(
            texto
            or
            (
                "Error de Supabase HTTP "
                + str(error.code)
            )
        )


# ============================================================
# CARGAR NEGOCIO
# ============================================================

def cargar_negocio(negocio_id):

    filas = supabase_request(
        "GET",
        "negocios",
        filtros={
            "id": negocio_id
        },
        select=(
            "id,"
            "user_id,"
            "nombre_negocio,"
            "nombre,"
            "whatsapp"
        )
    )

    if not filas:

        raise RuntimeError(
            "No se encontró el negocio."
        )

    return filas[0]


# ============================================================
# CARGAR DATOS DE STRIPE DEL NEGOCIO
# ============================================================

def cargar_datos_stripe(
    user_id
):

    if not user_id:

        raise RuntimeError(
            "El negocio no tiene user_id."
        )

    filas = supabase_request(
        "GET",
        "negocio_data",
        filtros={
            "user_id": user_id
        },
        select="data"
    )

    if not filas:

        return {}

    data = filas[0].get(
        "data"
    )

    if not isinstance(
        data,
        dict
    ):

        return {}

    return data


# ============================================================
# CARGAR PRODUCTOS
# ============================================================

def cargar_productos(
    user_id,
    ids
):

    if not ids:

        return []

    resultados = []

    for producto_id in ids:

        filas = supabase_request(
            "GET",
            "products",
            filtros={
                "id": producto_id,
                "user_id": user_id
            },
            select=(
                "id,"
                "user_id,"
                "name,"
                "price,"
                "stock,"
                "category"
            )
        )

        if not filas:

            raise RuntimeError(
                "No se encontró el producto "
                + str(producto_id)
                + " para este negocio."
            )

        resultados.append(
            filas[0]
        )

    return resultados


# ============================================================
# VALIDAR Y PREPARAR PRODUCTOS
# ============================================================

def preparar_items(
    items_recibidos,
    productos
):

    mapa = {
        str(p["id"]): p
        for p in productos
    }

    resultado = []

    total = 0.0

    for item in items_recibidos:

        producto_id = str(
            item.get(
                "product_id",
                ""
            )
        ).strip()

        try:

            cantidad = int(
                item.get(
                    "cantidad",
                    0
                ) or 0
            )

        except Exception:

            cantidad = 0

        if not producto_id:

            raise RuntimeError(
                "Falta el producto."
            )

        if cantidad <= 0:

            raise RuntimeError(
                "La cantidad del producto "
                + producto_id
                + " no es válida."
            )

        producto = mapa.get(
            producto_id
        )

        if not producto:

            raise RuntimeError(
                "Producto no válido."
            )

        stock = producto.get(
            "stock"
        )

        if stock is not None and stock != "":

            try:

                stock_numero = int(
                    stock
                )

            except Exception:

                stock_numero = 0

            if stock_numero < cantidad:

                raise RuntimeError(
                    "No hay suficientes unidades de "
                    + str(
                        producto.get(
                            "name",
                            "producto"
                        )
                    )
                    + "."
                )

        try:

            precio = float(
                producto.get(
                    "price",
                    0
                ) or 0
            )

        except Exception:

            precio = 0

        if precio <= 0:

            raise RuntimeError(
                "El producto "
                + str(
                    producto.get(
                        "name",
                        "producto"
                    )
                )
                + " no tiene un precio válido."
            )

        subtotal = (
            precio * cantidad
        )

        total += subtotal

        resultado.append({

            "product_id":
                producto["id"],

            "nombre":
                producto.get(
                    "name",
                    "Producto"
                ),

            "precio":
                precio,

            "cantidad":
                cantidad,

            "subtotal":
                subtotal

        })

    return resultado, total


# ============================================================
# CREAR DESCRIPCIÓN DEL PEDIDO
# ============================================================

def crear_contenido(
    items
):

    partes = []

    for item in items:

        partes.append(
            "{} x{} = ${:.
