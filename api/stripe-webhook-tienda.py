import os
import json
import hmac
import hashlib
import time
import urllib.parse
import urllib.request
import urllib.error

from http.server import BaseHTTPRequestHandler


# =========================================================
# CONFIGURACIÓN
# =========================================================

def env(nombre):
    return os.getenv(nombre, "").strip()


SUPABASE_URL = env("SUPABASE_URL")
SUPABASE_KEY = env("SUPABASE_SERVICE_ROLE_KEY")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET")


# =========================================================
# RESPUESTAS HTTP
# =========================================================

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
        "Content-Type, Stripe-Signature"
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


def leer_json(handler):
    try:
        cantidad = int(
            handler.headers.get(
                "Content-Length",
                "0"
            )
        )

        cuerpo = handler.rfile.read(cantidad)

        if not cuerpo:
            return {}

        return json.loads(
            cuerpo.decode("utf-8")
        )

    except Exception:
        return {}


def leer_cuerpo(handler):
    try:
        cantidad = int(
            handler.headers.get(
                "Content-Length",
                "0"
            )
        )

        return handler.rfile.read(cantidad)

    except Exception:
        return b""


# =========================================================
# SUPABASE
# =========================================================

def supabase_request(
    metodo,
    tabla,
    params="",
    datos=None,
    prefer=None
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

    if params:
        url += "?" + params

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

    if prefer:
        request.add_header(
            "Prefer",
            prefer
        )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20
        ) as respuesta:

            contenido = respuesta.read().decode(
                "utf-8"
            )

            if not contenido:
                return []

            try:
                return json.loads(contenido)

            except Exception:
                return contenido

    except urllib.error.HTTPError as error:

        cuerpo_error = ""

        try:
            cuerpo_error = (
                error.read()
                .decode("utf-8")
            )
        except Exception:
            pass

        raise RuntimeError(
            "Error de Supabase "
            + str(error.code)
            + ": "
            + cuerpo_error
        )


# =========================================================
# STRIPE API
# =========================================================

def stripe_request(
    metodo,
    ruta,
    cuenta=None,
    datos=None
):
    if not STRIPE_SECRET_KEY:
        raise RuntimeError(
            "Falta STRIPE_SECRET_KEY."
        )

    url = (
        "https://api.stripe.com"
        + ruta
    )

    cuerpo = None

    if datos is not None:

        cuerpo = urllib.parse.urlencode(
            datos
        ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=cuerpo,
        method=metodo
    )

    credenciales = (
        STRIPE_SECRET_KEY
        + ":"
    )

    import base64

    autorizacion = base64.b64encode(
        credenciales.encode("utf-8")
    ).decode("ascii")

    request.add_header(
        "Authorization",
        "Basic " + autorizacion
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
            timeout=20
        ) as respuesta:

            contenido = (
                respuesta.read()
                .decode("utf-8")
            )

            if not contenido:
                return {}

            return json.loads(
                contenido
            )

    except urllib.error.HTTPError as error:

        cuerpo_error = ""

        try:
            cuerpo_error = (
                error.read()
                .decode("utf-8")
            )
        except Exception:
            pass

        try:
            info = json.loads(
                cuerpo_error
            )

            mensaje = (
                info
                .get("error", {})
                .get("message")
            )

            if mensaje:
                raise RuntimeError(
                    "Stripe: " + mensaje
                )

        except RuntimeError:
            raise

        except Exception:
            pass

        raise RuntimeError(
            "Error de Stripe "
            + str(error.code)
            + ": "
            + cuerpo_error
        )


# =========================================================
# FIRMA DEL WEBHOOK DE STRIPE
# =========================================================

def verificar_firma_stripe(
    cuerpo,
    firma
):
    if not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError(
            "Falta STRIPE_WEBHOOK_SECRET."
        )

    if not firma:
        return False

    partes = {}

    for parte in firma.split(","):

        if "=" not in parte:
            continue

        clave, valor = parte.split(
            "=",
            1
        )

        partes.setdefault(
            clave,
            []
        ).append(valor)

    timestamps = partes.get(
        "t",
        []
    )

    firmas = partes.get(
        "v1",
        []
    )

    if not timestamps or not firmas:
        return False

    try:
        timestamp = int(
            timestamps[0]
        )

    except Exception:
        return False

    # Evita aceptar eventos demasiado antiguos.
    if abs(
        int(time.time())
        - timestamp
    ) > 300:
        return False

    mensaje = (
        str(timestamp)
        + "."
        + cuerpo.decode("utf-8")
    )

    esperado = hmac.new(
        STRIPE_WEBHOOK_SECRET.encode(
            "utf-8"
        ),
        mensaje.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    for firma_real in firmas:

        if hmac.compare_digest(
            esperado,
            firma_real
        ):
            return True

    return False


# =========================================================
# BUSCAR PEDIDO
# =========================================================

def obtener_pedido(order_id):

    filtro = (
        "id=eq."
        + urllib.parse.quote(
            str(order_id),
            safe=""
        )
    )

    resultado = supabase_request(
        "GET",
        "store_orders",
        filtro
        + "&select=*"
    )

    if not resultado:
        return None

    return resultado[0]


# =========================================================
# ACTUALIZAR PEDIDO
# =========================================================

def actualizar_pedido(
    order_id,
    cambios
):

    filtro = (
        "id=eq."
        + urllib.parse.quote(
            str(order_id),
            safe=""
        )
    )

    resultado = supabase_request(
        "PATCH",
        "store_orders",
        filtro,
        cambios,
        "return=representation"
    )

    if resultado:
        return resultado[0]

    return None


# =========================================================
# CREAR AGENDA
# =========================================================

def crear_agenda_desde_pedido(
    pedido
):

    negocio_id = (
        pedido.get("negocio_id")
        or ""
    )

    if not negocio_id:
        raise RuntimeError(
            "El pedido no tiene negocio_id."
        )

    # Evitar crear dos veces
    # la misma entrega.

    if pedido.get(
        "agenda_created"
    ):
        return False

    contenido = (
        pedido.get("contenido")
        or ""
    )

    if not contenido:

        # Intentamos reconstruir
        # el contenido desde los artículos.

        filtro = (
            "order_id=eq."
            + urllib.parse.quote(
                str(pedido.get("id")),
                safe=""
            )
        )

        articulos = supabase_request(
            "GET",
            "store_order_items",
            filtro
            + "&select=*"
        )

        partes = []

        for articulo in articulos:

            nombre = (
                articulo.get("nombre")
                or "Producto"
            )

            cantidad = int(
                articulo.get(
                    "cantidad",
                    1
                )
                or 1
            )

            partes.append(
                nombre
                + " x"
                + str(cantidad)
            )

        contenido = ", ".join(
            partes
        )

    fecha_entrega = (
        pedido.get(
            "fecha_entrega"
        )
        or ""
    )

    hora_entrega = (
        pedido.get(
            "hora_entrega"
        )
        or ""
    )

    cliente = (
        pedido.get(
            "cliente_nombre"
        )
        or ""
    )

    telefono = (
        pedido.get(
            "cliente_telefono"
        )
        or ""
    )

    email = (
        pedido.get(
            "cliente_email"
        )
        or ""
    )

    direccion = (
        pedido.get(
            "direccion"
        )
        or ""
    )

    referencia = (
        pedido.get(
            "referencia"
        )
        or ""
    )

    comentarios = (
        pedido.get(
            "comentarios"
        )
        or ""
    )

    tipo_entrega = (
        pedido.get(
            "tipo_entrega"
        )
        or "domicilio"
    )

    observaciones = (
        "Pedido de tienda en línea."
        + " Cliente: "
        + cliente
    )

    if email:
        observaciones += (
            " Email: "
            + email
        )

    if tipo_entrega == "domicilio":

        if direccion:
            observaciones += (
                " Dirección: "
                + direccion
            )

        if referencia:
            observaciones += (
                " Referencia: "
                + referencia
            )

    else:

        observaciones += (
            " Entrega: recoger en tienda."
        )

    if comentarios:
        observaciones += (
            " Comentarios: "
            + comentarios
        )

    entrega = {
        "negocio_id": negocio_id,
        "fecha_venta": (
            str(
                pedido.get(
                    "created_at",
                    ""
                )
            )[:10]
            or fecha_entrega
        ),
        "fecha_entrega": fecha_entrega,
        "hora_entrega": hora_entrega,
        "contenido": contenido,
        "observaciones": observaciones,
        "quien_ordena": cliente,
        "telefono_ordena": telefono,
        "entregar_a": (
            cliente
            if tipo_entrega == "domicilio"
            else "Recoger en tienda"
        ),
        "estado": "pendiente"
    }

    resultado = supabase_request(
        "POST",
        "entregas",
        "",
        entrega,
        "return=representation"
    )

    if resultado is None:
        raise RuntimeError(
            "No se pudo crear la entrega."
        )

    actualizar_pedido(
        pedido.get("id"),
        {
            "agenda_created": True
        }
    )

    return True


# =========================================================
# PROCESAR PAGO CONFIRMADO
# =========================================================

def procesar_pago_confirmado(
    session,
    evento_tipo
):

    metadata = (
        session.get(
            "metadata"
        )
        or {}
    )

    order_id = (
        metadata.get(
            "order_id"
        )
        or ""
    )

    if not order_id:
        return {
            "ok": False,
            "msg": (
                "La sesión de Stripe "
                "no tiene order_id."
            )
        }

    pedido = obtener_pedido(
        order_id
    )

    if not pedido:
        return {
            "ok": False,
            "msg": (
                "No se encontró el pedido "
                + str(order_id)
            )
        }

    payment_status = (
        session.get(
            "payment_status"
        )
        or ""
    )

    session_id = (
        session.get(
            "id"
        )
        or ""
    )

    payment_intent = (
        session.get(
            "payment_intent"
        )
    )

    # =====================================================
    # PAGO CONFIRMADO
    # =====================================================

    if (
        payment_status == "paid"
        or evento_tipo
        == "checkout.session.async_payment_succeeded"
    ):

        cambios = {
            "estado": "confirmado",
            "estado_pago": "pagado",
            "stripe_session_id": session_id
        }

        if payment_intent:
            cambios[
                "stripe_payment_intent_id"
            ] = str(
                payment_intent
            )

        actualizar_pedido(
            order_id,
            cambios
        )

        pedido = obtener_pedido(
            order_id
        )

        if not pedido:
            raise RuntimeError(
                "No se pudo volver a cargar "
                "el pedido."
            )

        crear_agenda_desde_pedido(
            pedido
        )

        return {
            "ok": True,
            "estado": "pagado",
            "order_id": order_id
        }

    # =====================================================
    # PAGO TODAVÍA PENDIENTE
    # =====================================================

    actualizar_pedido(
        order_id,
        {
            "stripe_session_id":
                session_id,
            "estado_pago":
                "pendiente"
        }
    )

    return {
        "ok": True,
        "estado": "pendiente",
        "order_id": order_id
    }


# =========================================================
# PAGO FALLIDO / SESIÓN EXPIRADA
# =========================================================

def procesar_pago_fallido(
    session,
    estado
):

    metadata = (
        session.get(
            "metadata"
        )
        or {}
    )

    order_id = (
        metadata.get(
            "order_id"
        )
        or ""
    )

    if not order_id:
        return {
            "ok": True,
            "ignorado": True
        }

    pedido = obtener_pedido(
        order_id
    )

    if not pedido:
        return {
            "ok": True,
            "ignorado": True
        }

    actualizar_pedido(
        order_id,
        {
            "estado": estado,
            "estado_pago": "fallido"
        }
    )

    return {
        "ok": True,
        "estado": estado,
        "order_id": order_id
    }


# =========================================================
# HANDLER
# =========================================================

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):

        responder(
            self,
            {
                "ok": True
            }
        )

    def do_GET(self):

        responder(
            self,
            {
                "ok": True,
                "servicio":
                    "stripe-webhook-tienda"
            }
        )

    def do_POST(self):

        try:

            cuerpo = leer_cuerpo(
                self
            )

            firma = self.headers.get(
                "Stripe-Signature",
                ""
            )

            # =================================================
            # VERIFICAR FIRMA
            # =================================================

            if not verificar_firma_stripe(
                cuerpo,
                firma
            ):

                responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Firma de Stripe inválida."
                    },
                    400
                )

                return

            evento = json.loads(
                cuerpo.decode("utf-8")
            )

            evento_tipo = (
                evento.get(
                    "type"
                )
                or ""
            )

            datos_evento = (
                evento.get(
                    "data",
                    {}
                )
            )

            session = (
                datos_evento.get(
                    "object",
                    {}
                )
            )

            # =================================================
            # EVENTOS IMPORTANTES
            # =================================================

            if evento_tipo in (
                "checkout.session.completed",
                "checkout.session.async_payment_succeeded"
            ):

                resultado = (
                    procesar_pago_confirmado(
                        session,
                        evento_tipo
                    )
                )

                responder(
                    self,
                    resultado,
                    200
                )

                return

            if evento_tipo == (
                "checkout.session.async_payment_failed"
            ):

                resultado = (
                    procesar_pago_fallido(
                        session,
                        "cancelado"
                    )
                )

                responder(
                    self,
                    resultado,
                    200
                )

                return

            if evento_tipo == (
                "checkout.session.expired"
            ):

                resultado = (
                    procesar_pago_fallido(
                        session,
                        "expirado"
                    )
                )

                responder(
                    self,
                    resultado,
                    200
                )

                return

            # =================================================
            # OTROS EVENTOS
            # =================================================

            responder(
                self,
                {
                    "ok": True,
                    "recibido": evento_tipo,
                    "ignorado": True
                },
                200
            )

        except Exception as error:

            print(
                "ERROR WEBHOOK:",
                str(error)
            )

            responder(
                self,
                {
                    "ok": False,
                    "msg": str(error)
                },
                500
  )
