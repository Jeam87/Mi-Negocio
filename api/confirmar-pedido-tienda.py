import os
import json
import urllib.parse
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


# ============================================================
# CONFIGURACIÓN
# ============================================================

def env(nombre):
    return os.getenv(nombre, "").strip()


SUPABASE_URL = env("SUPABASE_URL")
SUPABASE_KEY = env("SUPABASE_SERVICE_ROLE_KEY")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")


# ============================================================
# RESPUESTA JSON
# ============================================================

def responder(handler, datos, codigo=200):

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

    handler.end_headers()

    handler.wfile.write(
        json.dumps(
            datos,
            ensure_ascii=False
        ).encode("utf-8")
    )


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
# SUPABASE
# ============================================================

def supabase_request(
    metodo,
    tabla,
    datos=None,
    filtros=None,
    select=None
):

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
            texto or
            (
                "Error de Supabase HTTP "
                + str(error.code)
            )
        )


# ============================================================
# STRIPE
# ============================================================

def stripe_request(
    ruta,
    parametros,
    cuenta
):

    if not STRIPE_SECRET_KEY:

        raise RuntimeError(
            "Falta STRIPE_SECRET_KEY."
        )

    cuerpo = urllib.parse.urlencode(
        parametros
    ).encode("utf-8")

    request = urllib.request.Request(
        "https://api.stripe.com" + ruta,
        data=cuerpo,
        method="POST"
    )

    import base64

    credenciales = base64.b64encode(
        (
            STRIPE_SECRET_KEY + ":"
        ).encode()
    ).decode()

    request.add_header(
        "Authorization",
        "Basic " + credenciales
    )

    request.add_header(
        "Content-Type",
        "application/x-www-form-urlencoded"
    )

    if cuenta:

        request.add_header(
            "Stripe-Account",
            cuenta
        )

    try:

        with urllib.request.urlopen(
            request,
            timeout=25
        ) as respuesta:

            return json.loads(
                respuesta
                .read()
                .decode("utf-8")
                or "{}"
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

        try:

            obj = json.loads(
                texto
            )

            mensaje = (
                obj
                .get("error", {})
                .get("message")
            )

        except Exception:

            mensaje = None

        raise RuntimeError(
            mensaje or
            texto or
            "Error de Stripe."
        )


# ============================================================
# OBTENER SESIÓN DE STRIPE
# ============================================================

def obtener_session(
    session_id,
    cuenta
):

    if not session_id:

        raise RuntimeError(
            "Falta session_id."
        )

    if not cuenta:

        raise RuntimeError(
            "No se encontró la cuenta conectada de Stripe."
        )

    # Stripe permite recuperar una Checkout Session
    # directamente desde la cuenta conectada.

    import base64

    request = urllib.request.Request(
        "https://api.stripe.com/v1/checkout/sessions/"
        + urllib.parse.quote(
            session_id,
            safe=""
        ),
        method="GET"
    )

    credenciales = base64.b64encode(
        (
            STRIPE_SECRET_KEY + ":"
        ).encode()
    ).decode()

    request.add_header(
        "Authorization",
        "Basic " + credenciales
    )

    request.add_header(
        "Stripe-Account",
        cuenta
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=25
        ) as respuesta:

            return json.loads(
                respuesta
                .read()
                .decode("utf-8")
                or "{}"
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

        try:

            obj = json.loads(
                texto
            )

            mensaje = (
                obj
                .get("error", {})
                .get("message")
            )

        except Exception:

            mensaje = None

        raise RuntimeError(
            mensaje or
            texto or
            "No se pudo consultar el pago en Stripe."
        )


# ============================================================
# BUSCAR NEGOCIO
# ============================================================

def obtener_negocio(
    negocio_id
):

    filas = supabase_request(
        "GET",
        "negocios",
        filtros={
            "id": negocio_id
        },
        select="id,user_id,nombre_negocio,nombre"
    )

    if not filas:

        raise RuntimeError(
            "No se encontró el negocio."
        )

    return filas[0]


# ============================================================
# BUSCAR PEDIDO
# ============================================================

def obtener_pedido(
    pedido_id
):

    filas = supabase_request(
        "GET",
        "store_orders",
        filtros={
            "id": pedido_id
        },
        select="*"
    )

    if not filas:

        return None

    return filas[0]


# ============================================================
# ACTUALIZAR PEDIDO COMO PAGADO
# ============================================================

def marcar_pagado(
    pedido_id,
    session_id
):

    filas = supabase_request(
        "PATCH",
        "store_orders",
        datos={
            "estado":
                "confirmado",

            "estado_pago":
                "pagado",

            "stripe_session_id":
                session_id
        },
        filtros={
            "id":
                pedido_id
        }
    )

    if not filas:

        raise RuntimeError(
            "No se pudo actualizar el pedido."
        )

    return filas[0]


# ============================================================
# CREAR ENTREGA EN AGENDA
# ============================================================

def crear_agenda(
    pedido
):

    negocio_id =
        pedido.get(
            "negocio_id"
        )

    contenido =
        pedido.get(
            "contenido",
            ""
        )

    observaciones =
        pedido.get(
            "comentarios",
            ""
        )

    quien_ordena =
        pedido.get(
            "cliente_nombre",
            ""
        )

    telefono =
        pedido.get(
            "cliente_telefono",
            ""
        )

    direccion =
        pedido.get(
            "direccion",
            ""
        )

    tipo_entrega =
        pedido.get(
            "tipo_entrega",
            "domicilio"
        )

    if tipo_entrega == "recoger":

        entregar_a = (
            "Recoger en tienda"
        )

    else:

        entregar_a = (
            direccion
            or
            "Domicilio"
        )

    # --------------------------------------------------------
    # Evitamos crear la misma agenda dos veces.
    # --------------------------------------------------------

    existente = supabase_request(
        "GET",
        "entregas",
        filtros={
            "negocio_id":
                negocio_id,

            "contenido":
                contenido,

            "quien_ordena":
                quien_ordena,

            "telefono_ordena":
                telefono
        },
        select="id"
    )

    if existente:

        return existente[0]


    entrega = {

        "negocio_id":
            negocio_id,

        "fecha_venta":
            pedido.get(
                "fecha_venta"
            ),

        "fecha_entrega":
            pedido.get(
                "fecha_entrega"
            ),

        "hora_entrega":
            pedido.get(
                "hora_entrega"
            ),

        "contenido":
            contenido,

        "observaciones":
            observaciones,

        "quien_ordena":
            quien_ordena,

        "telefono_ordena":
            telefono,

        "entregar_a":
            entregar_a,

        "estado":
            "pendiente"

    }

    filas = supabase_request(
        "POST",
        "entregas",
        datos=entrega
    )

    if not filas:

        raise RuntimeError(
            "El pedido se pagó, pero no se pudo crear la entrada en Agenda."
        )

    return filas[0]


# ============================================================
# HANDLER
# ============================================================

class handler(
    BaseHTTPRequestHandler
):

    def do_OPTIONS(self):

        responder(
            self,
            {}
        )


    def do_POST(self):

        try:

            datos =
                leer_json(
                    self
                )

            session_id = str(
                datos.get(
                    "session_id",
                    ""
                )
            ).strip()

            negocio_id = str(
                datos.get(
                    "negocio_id",
                    ""
                )
            ).strip()

            if not session_id:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Falta session_id."
                    },
                    400
                )

            if not negocio_id:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Falta negocio_id."
                    },
                    400
                )


            # ------------------------------------------------
            # NEGOCIO
            # ------------------------------------------------

            negocio =
                obtener_negocio(
                    negocio_id
                )


            # ------------------------------------------------
            # CUENTA STRIPE
            # ------------------------------------------------

            negocio_data =
                supabase_request(
                    "GET",
                    "negocio_data",
                    filtros={
                        "user_id":
                            negocio.get(
                                "user_id"
                            )
                    },
                    select="data"
                )

            stripe_account = ""

            if negocio_data:

                data =
                    negocio_data[0].get(
                        "data"
                    ) or {}

                stripe_account =
                    data.get(
                        "stripe_account_id"
                    ) or data.get(
                        "stripeAccountId"
                    ) or ""


            if not stripe_account:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Este negocio no tiene Stripe conectado."
                    },
                    400
                )


            # ------------------------------------------------
            # CONSULTAR STRIPE
            # ------------------------------------------------

            session =
                obtener_session(
                    session_id,
                    stripe_account
                )


            pago =
                session.get(
                    "payment_status"
                )

            metadata =
                session.get(
                    "metadata"
                ) or {}

            pedido_id =
                metadata.get(
                    "order_id"
                )


            # ------------------------------------------------
            # TAMBIÉN INTENTAMOS ENCONTRAR EL PEDIDO
            # ------------------------------------------------

            pedido = None

            if pedido_id:

                pedido =
                    obtener_pedido(
                        pedido_id
                    )


            if not pedido:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "No se encontró el pedido asociado a este pago."
                    },
                    404
                )


            # ------------------------------------------------
            # SI YA ESTÁ PAGADO
            # ------------------------------------------------

            if (
                pedido.get(
                    "estado_pago"
                ) == "pagado"
            ):

                return responder(
                    self,
                    {
                        "ok": True,

                        "order_id":
                            pedido_id,

                        "message":
                            "El pedido ya estaba confirmado."
                    }
                )


            # ------------------------------------------------
            # PAGO CONFIRMADO
            # ------------------------------------------------

            if pago == "paid":

                pedido_actualizado =
                    marcar_pagado(
                        pedido_id,
                        session_id
                    )


                # ------------------------------------------------
