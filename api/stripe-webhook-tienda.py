import os
import json
import hmac
import hashlib
import time
import urllib.parse
import urllib.request
import urllib.error
import base64
from http.server import BaseHTTPRequestHandler


# ============================================================
# STRIPE WEBHOOK - TIENDA EN LINEA
# ============================================================
#
# Archivo:
# api/stripe-webhook-tienda.py
#
# Variables de Vercel:
# SUPABASE_URL
# SUPABASE_SERVICE_ROLE_KEY
# STRIPE_SECRET_KEY
# STRIPE_WEBHOOK_SECRET
#
# Funciones:
# - Confirma pagos de Stripe.
# - Crea el pedido en la Agenda.
# - Evita crear la Agenda dos veces.
# - Devuelve inventario cuando un pago asincrónico falla.
# - Devuelve inventario cuando un Checkout expira.
# ============================================================


def env(nombre):
    return os.getenv(nombre, "").strip()


def responder(handler, datos, codigo=200):
    cuerpo = json.dumps(
        datos,
        ensure_ascii=False
    ).encode("utf-8")

    handler.send_response(codigo)
    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )
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
    handler.end_headers()
    handler.wfile.write(cuerpo)


def leer_cuerpo(handler):
    try:
        cantidad = int(
            handler.headers.get(
                "Content-Length",
                "0"
            ) or "0"
        )
    except Exception:
        cantidad = 0

    return handler.rfile.read(cantidad)


# ============================================================
# SUPABASE
# ============================================================

def supabase_request(
    metodo,
    tabla,
    params=None,
    data=None,
    prefer=None
):
    url_base = env("SUPABASE_URL").rstrip("/")
    service_key = env("SUPABASE_SERVICE_ROLE_KEY")

    if not url_base:
        raise RuntimeError(
            "Falta SUPABASE_URL en Vercel."
        )

    if not service_key:
        raise RuntimeError(
            "Falta SUPABASE_SERVICE_ROLE_KEY en Vercel."
        )

    url = f"{url_base}/rest/v1/{tabla}"

    if params:
        url += "?" + urllib.parse.urlencode(
            params,
            doseq=True
        )

    cuerpo = None

    if data is not None:
        cuerpo = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=cuerpo,
        method=metodo
    )

    request.add_header(
        "apikey",
        service_key
    )

    request.add_header(
        "Authorization",
        "Bearer " + service_key
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

            texto = respuesta.read().decode(
                "utf-8"
            ) or ""

            if not texto:
                return None

            try:
                return json.loads(texto)
            except Exception:
                return texto

    except urllib.error.HTTPError as error:

        texto = (
            error.read().decode("utf-8")
            if error.fp
            else ""
        )

        try:
            detalle = json.loads(texto)
        except Exception:
            detalle = texto

        raise RuntimeError(
            f"Supabase {metodo} {tabla}: {detalle}"
        )


def supabase_rpc(nombre_funcion, argumentos):

    url_base = env("SUPABASE_URL").rstrip("/")
    service_key = env("SUPABASE_SERVICE_ROLE_KEY")

    if not url_base:
        raise RuntimeError(
            "Falta SUPABASE_URL en Vercel."
        )

    if not service_key:
        raise RuntimeError(
            "Falta SUPABASE_SERVICE_ROLE_KEY en Vercel."
        )

    url = (
        f"{url_base}/rest/v1/rpc/"
        f"{nombre_funcion}"
    )

    cuerpo = json.dumps(
        argumentos,
        ensure_ascii=False
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=cuerpo,
        method="POST"
    )

    request.add_header(
        "apikey",
        service_key
    )

    request.add_header(
        "Authorization",
        "Bearer " + service_key
    )

    request.add_header(
        "Content-Type",
        "application/json"
    )

    request.add_header(
        "Accept",
        "application/json"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20
        ) as respuesta:

            texto = respuesta.read().decode(
                "utf-8"
            ) or ""

            if not texto:
                return None

            try:
                return json.loads(texto)
            except Exception:
                return texto

    except urllib.error.HTTPError as error:

        texto = (
            error.read().decode("utf-8")
            if error.fp
            else ""
        )

        try:
            detalle = json.loads(texto)
        except Exception:
            detalle = texto

        raise RuntimeError(
            f"Supabase RPC {nombre_funcion}: "
            f"{detalle}"
        )


# ============================================================
# VERIFICAR FIRMA DE STRIPE
# ============================================================

def verificar_firma_stripe(
    payload,
    encabezado,
    secreto
):

    if not encabezado:
        return False

    if not secreto:
        return False

    timestamp = None
    firmas = []

    partes = encabezado.split(",")

    for parte in partes:

        parte = parte.strip()

        if "=" not in parte:
            continue

        clave, valor = parte.split(
            "=",
            1
        )

        if clave == "t":

            try:
                timestamp = int(valor)
            except Exception:
                timestamp = None

        elif clave == "v1":

            firmas.append(valor)

    if timestamp is None:
        return False

    if not firmas:
        return False

    # Evita aceptar eventos demasiado antiguos.
    if abs(int(time.time()) - timestamp) > 300:
        return False

    mensaje = (
        str(timestamp).encode("utf-8")
        + b"."
        + payload
    )

    esperado = hmac.new(
        secreto.encode("utf-8"),
        mensaje,
        hashlib.sha256
    ).hexdigest()

    for firma in firmas:

        if hmac.compare_digest(
            esperado,
            firma
        ):
            return True

    return False


# ============================================================
# PEDIDOS
# ============================================================

def obtener_pedido(order_id):

    filas = supabase_request(
        "GET",
        "store_orders",
        {
            "id": f"eq.{order_id}",
            "select": "*",
            "limit": "1"
        }
    )

    if filas:
        return filas[0]

    return None


def obtener_items_pedido(order_id):

    filas = supabase_request(
        "GET",
        "store_order_items",
        {
            "order_id": f"eq.{order_id}",
            "select": (
                "product_id,"
                "nombre,"
                "precio,"
                "cantidad,"
                "subtotal"
            )
        }
    )

    return filas or []


# ============================================================
# CREAR TEXTO PARA AGENDA
# ============================================================

def crear_contenido_agenda(
    pedido,
    items
):

    contenido = pedido.get(
        "contenido"
    )

    if contenido:
        return str(contenido)[:5000]

    partes = []

    for item in items:

        nombre = str(
            item.get("nombre")
            or "Producto"
        )

        cantidad = int(
            item.get("cantidad")
            or 1
        )

        precio = item.get(
            "precio"
        ) or 0

        try:
            precio_texto = (
                f"${float(precio):,.2f}"
            )
        except Exception:
            precio_texto = str(precio)

        partes.append(
            f"{cantidad} x {nombre} "
            f"({precio_texto})"
        )

    if not partes:
        return "Pedido de tienda en línea"

    return ", ".join(partes)[:5000]


# ============================================================
# CREAR PEDIDO EN AGENDA
# ============================================================

def crear_agenda_si_no_existe(order_id):

    pedido = obtener_pedido(
        order_id
    )

    if not pedido:
        raise RuntimeError(
            "No se encontró el pedido: "
            + str(order_id)
        )

    # Si ya fue creado anteriormente,
    # no volvemos a crear otro.
    if bool(
        pedido.get("agenda_created")
    ):
        return False

    items = obtener_items_pedido(
        order_id
    )

    contenido = crear_contenido_agenda(
        pedido,
        items
    )

    created_at = str(
        pedido.get("created_at")
        or ""
    )

    if len(created_at) >= 10:
        fecha_venta = created_at[:10]
    else:
        fecha_venta = None

    fecha_entrega = (
        pedido.get("fecha_entrega")
        or fecha_venta
    )

    hora_entrega = pedido.get(
        "hora_entrega"
    )

    tipo_entrega = str(
        pedido.get("tipo_entrega")
        or ""
    ).lower()

    if tipo_entrega in (
        "recoger",
        "pickup",
        "recogida"
    ):

        entregar_a = (
            "Recoger en tienda"
        )

    else:

        entregar_a = str(
            pedido.get("direccion")
            or ""
        ).strip()

        if not entregar_a:
            entregar_a = "Domicilio"

    observaciones = str(
        pedido.get("comentarios")
        or ""
    ).strip()

    referencia = str(
        pedido.get("referencia")
        or ""
    ).strip()

    if referencia:

        if observaciones:
            observaciones += (
                " | Referencia: "
                + referencia
            )
        else:
            observaciones = (
                "Referencia: "
                + referencia
            )

    observaciones = (
        "Pedido de tienda en línea. "
        + observaciones
    ).strip()[:5000]

    agenda = {
        "negocio_id": pedido.get(
            "negocio_id"
        ),

        "fecha_venta": fecha_venta,

        "fecha_entrega": fecha_entrega,

        "hora_entrega": hora_entrega,

        "contenido": contenido,

        "observaciones": observaciones,

        "quien_ordena": str(
            pedido.get(
                "cliente_nombre"
            )
            or "Cliente tienda"
        )[:200],

        "telefono_ordena": str(
            pedido.get(
                "cliente_telefono"
            )
            or ""
        )[:50],

        "entregar_a": entregar_a[:1000],

        "estado": "pendiente"
    }

    # Insertamos en la misma tabla que
    # utiliza la Agenda principal.
    supabase_request(
        "POST",
        "entregas",
        data=agenda,
        prefer="return=minimal"
    )

    # Marcamos el pedido para que una
    # segunda notificación de Stripe
    # no vuelva a crear la Agenda.
    supabase_request(
        "PATCH",
        "store_orders",
        {
            "id": f"eq.{order_id}"
        },
        {
            "agenda_created": True
        },
        prefer="return=minimal"
    )

    return True # ============================================================
# MARCAR PEDIDO COMO PAGADO
# ============================================================

def marcar_pedido_pagado(
    order_id,
    session
):

    pedido = obtener_pedido(
        order_id
    )

    if not pedido:
        raise RuntimeError(
            "No se encontró el pedido: "
            + str(order_id)
        )

    payment_intent = session.get(
        "payment_intent"
    )

    supabase_request(
        "PATCH",
        "store_orders",
        {
            "id": f"eq.{order_id}"
        },
        {
            "estado": "confirmado",
            "estado_pago": "pagado",
            "stripe_session_id": session.get(
                "id"
            ),
            "stripe_payment_intent_id":
                payment_intent
        },
        prefer="return=minimal"
    )

    # Después de confirmar el pago,
    # creamos la Agenda si todavía no existe.
    crear_agenda_si_no_existe(
        order_id
    )


# ============================================================
# DEVOLVER INVENTARIO
# ============================================================

def devolver_inventario(
    order_id,
    nuevo_estado_pago,
    nuevo_estado_pedido
):

    pedido = obtener_pedido(
        order_id
    )

    if not pedido:
        raise RuntimeError(
            "No se encontró el pedido: "
            + str(order_id)
        )

    estado_pago_actual = str(
        pedido.get("estado_pago")
        or ""
    ).lower()

    # Si ya fue pagado, jamás devolvemos
    # el inventario.
    if estado_pago_actual == "pagado":
        return False

    # Si ya fue procesado anteriormente,
    # no devolvemos el inventario otra vez.
    if estado_pago_actual in (
        "fallido",
        "expirado",
        "cancelado"
    ):
        return False

    items = obtener_items_pedido(
        order_id
    )

    # Cambiamos el estado solamente si
    # todavía estaba pendiente.
    #
    # Esto hace que un webhook repetido
    # de Stripe no devuelva el inventario
    # dos veces.
    cambiados = supabase_request(
        "PATCH",
        "store_orders",
        {
            "id": f"eq.{order_id}",
            "estado_pago": "eq.pendiente"
        },
        {
            "estado": nuevo_estado_pedido,
            "estado_pago": nuevo_estado_pago
        },
        prefer="return=representation"
    ) or []

    if not cambiados:
        return False

    if not items:
        return True

    elementos = []

    for item in items:

        product_id = item.get(
            "product_id"
        )

        try:
            cantidad = int(
                item.get("cantidad")
                or 0
            )
        except Exception:
            cantidad = 0

        if product_id and cantidad > 0:

            elementos.append({
                "product_id": str(
                    product_id
                ),
                "cantidad": cantidad
            })

    if elementos:

        # Utilizamos la función SQL que
        # ya creaste en Supabase.
        supabase_rpc(
            "store_devolver_stock",
            {
                "p_items": elementos
            }
        )

    return True


# ============================================================
# PROCESAR EVENTOS DE STRIPE
# ============================================================

def procesar_evento(evento):

    tipo_evento = evento.get(
        "type"
    )

    datos = evento.get(
        "data"
    ) or {}

    objeto = datos.get(
        "object"
    ) or {}

    metadata = objeto.get(
        "metadata"
    ) or {}

    order_id = str(
        metadata.get(
            "order_id"
        )
        or ""
    ).strip()

    # Si no tiene order_id, no pertenece
    # a un pedido de nuestra tienda.
    if not order_id:

        return {
            "ok": True,
            "ignorado": True,
            "motivo": (
                "El evento no tiene "
                "metadata.order_id."
            )
        }


    # ========================================================
    # PAGO CONFIRMADO
    # ========================================================

    if tipo_evento in (
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded"
    ):

        estado_pago = str(
            objeto.get(
                "payment_status"
            )
            or ""
        ).lower()

        # Para checkout.session.completed,
        # si todavía no está pagado, esperamos
        # el evento async_payment_succeeded.
        if (
            tipo_evento
            == "checkout.session.completed"
            and estado_pago != "paid"
        ):

            return {
                "ok": True,
                "ignorado": True,
                "motivo": (
                    "Checkout completado, "
                    "pero el pago todavía "
                    "no está confirmado."
                ),
                "order_id": order_id
            }

        marcar_pedido_pagado(
            order_id,
            objeto
        )

        return {
            "ok": True,
            "procesado": True,
            "order_id": order_id,
            "evento": tipo_evento,
            "payment_status": estado_pago
        }


    # ========================================================
    # PAGO ASINCRÓNICO FALLIDO
    # ========================================================

    if tipo_evento == (
        "checkout.session.async_payment_failed"
    ):

        procesado = devolver_inventario(
            order_id,
            "fallido",
            "cancelado"
        )

        return {
            "ok": True,
            "procesado": procesado,
            "order_id": order_id,
            "evento": tipo_evento
        }


    # ========================================================
    # CHECKOUT EXPIRADO
    # ========================================================

    if tipo_evento == (
        "checkout.session.expired"
    ):

        procesado = devolver_inventario(
            order_id,
            "expirado",
            "cancelado"
        )

        return {
            "ok": True,
            "procesado": procesado,
            "order_id": order_id,
            "evento": tipo_evento
        }


    # ========================================================
    # OTROS EVENTOS
    # ========================================================

    return {
        "ok": True,
        "ignorado": True,
        "motivo": (
            "Evento de Stripe no utilizado "
            "por la tienda."
        ),
        "evento": tipo_evento
    }


# ============================================================
# HANDLER DE VERCEL
# ============================================================

class handler(
    BaseHTTPRequestHandler
):

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
                "service": (
                    "stripe-webhook-tienda"
                )
            }
        )


    def do_POST(self):

        try:

            payload = leer_cuerpo(
                self
            )

            firma = self.headers.get(
                "Stripe-Signature",
                ""
            )

            secreto = env(
                "STRIPE_WEBHOOK_SECRET"
            )

            if not secreto:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg": (
                            "Falta configurar "
                            "STRIPE_WEBHOOK_SECRET "
                            "en Vercel."
                        )
                    },
                    500
                )


            # Verificar que la petición
            # realmente venga de Stripe.
            if not verificar_firma_stripe(
                payload,
                firma,
                secreto
            ):

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg": (
                            "La firma de Stripe "
                            "no es válida."
                        )
                    },
                    400
                )


            try:

                evento = json.loads(
                    payload.decode(
                        "utf-8"
                    )
                )

            except Exception:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg": (
                            "El evento recibido "
                            "no es JSON válido."
                        )
                    },
                    400
                )


            resultado = procesar_evento(
                evento
            )

            return responder(
                self,
                resultado,
                200
            )


        except Exception as error:

            return responder(
                self,
                {
                    "ok": False,
                   
