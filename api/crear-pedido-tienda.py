import os
import json
import urllib.parse
import urllib.request
import urllib.error
import uuid
from http.server import BaseHTTPRequestHandler


# ============================================================
# RESPUESTAS
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
# CARGAR NEGOCIO
# ============================================================

def cargar_negocio(negocio_id):

    filas = supabase_request(
        "GET",
        "negocios",
        filtros={
            "id": negocio_id
        },
        select="id,user_id,nombre_negocio,nombre,whatsapp"
    )

    if not filas:

        raise RuntimeError(
            "No se encontró el negocio."
        )

    return filas[0]


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
            select="id,user_id,name,price,stock,category"
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

    total = 0

    for item in items_recibidos:

        producto_id = str(
            item.get(
                "product_id",
                ""
            )
        ).strip()

        cantidad = int(
            item.get(
                "cantidad",
                0
            ) or 0
        )

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

        precio = float(
            producto.get(
                "price",
                0
            ) or 0
        )

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
            precio *
            cantidad
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
# GUARDAR PEDIDO
#
# Esta parte utiliza la tabla:
#
# store_orders
#
# La tabla se creará con el SQL que te voy a pasar después.
# ============================================================

def guardar_pedido(
    negocio_id,
    cliente,
    entrega,
    comentarios,
    metodo_pago,
    items,
    total
):

    pedido_id = str(
        uuid.uuid4()
    )

    pedido = {

        "id":
            pedido_id,

        "negocio_id":
            negocio_id,

        "cliente_nombre":
            cliente.get(
                "nombre",
                ""
            ).strip(),

        "cliente_telefono":
            cliente.get(
                "telefono",
                ""
            ).strip(),

        "cliente_email":
            cliente.get(
                "email",
                ""
            ).strip(),

        "tipo_entrega":
            entrega.get(
                "tipo",
                "domicilio"
            ),

        "direccion":
            entrega.get(
                "direccion",
                ""
            ).strip(),

        "referencia":
            entrega.get(
                "referencia",
                ""
            ).strip(),

        "fecha_entrega":
            entrega.get(
                "fecha"
            ),

        "hora_entrega":
            entrega.get(
                "hora"
            ),

        "comentarios":
            comentarios,

        "metodo_pago":
            metodo_pago,

        "total":
            round(
                total,
                2
            ),

        "estado":
            (
                "pendiente"
                if metodo_pago == "stripe"
                else "pendiente_pago"
            ),

        "estado_pago":
            (
                "pendiente"
                if metodo_pago == "stripe"
                else "pendiente"
            )

    }

    guardado = supabase_request(
        "POST",
        "store_orders",
        datos=pedido
    )

    if not guardado:

        raise RuntimeError(
            "No se pudo guardar el pedido."
        )

    return guardado[0]


# ============================================================
# GUARDAR PRODUCTOS DEL PEDIDO
# ============================================================

def guardar_items_pedido(
    pedido_id,
    items
):

    filas = []

    for item in items:

        filas.append({

            "order_id":
                pedido_id,

            "product_id":
                item["product_id"],

            "nombre":
                item["nombre"],

            "precio":
                round(
                    item["precio"],
                    2
                ),

            "cantidad":
                item["cantidad"],

            "subtotal":
                round(
                    item["subtotal"],
                    2
                )

        })

    if not filas:

        return

    supabase_request(
        "POST",
        "store_order_items",
        datos=filas
    )


# ============================================================
# ACTUALIZAR STOCK
#
# IMPORTANTE:
# La actualización definitiva y segura del inventario
# la terminará haciendo la función SQL que instalaremos.
#
# Este archivo NO modifica todavía el stock directamente
# para evitar vender dos veces el mismo producto si dos
# clientes compran al mismo tiempo.
# ============================================================


# ============================================================
# CREAR DESCRIPCIÓN DEL PEDIDO
# ============================================================

def crear_contenido(
    items
):

    partes = []

    for item in items:

        partes.append(
            "{} x{} = ${:.2f}".format(
                item["nombre"],
                item["cantidad"],
                item["subtotal"]
            )
        )

    return " | ".join(
        partes
    )


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

            negocio_id = str(
                datos.get(
                    "negocio_id",
                    ""
                )
            ).strip()

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

            items_recibidos =
                datos.get(
                    "items",
                    []
                )

            if not isinstance(
                items_recibidos,
                list
            ) or not items_recibidos:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "El carrito está vacío."
                    },
                    400
                )

            cliente =
                datos.get(
                    "cliente",
                    {}
                )

            entrega =
                datos.get(
                    "entrega",
                    {}
                )

            comentarios =
                str(
                    datos.get(
                        "comentarios",
                        ""
                    ) or ""
                ).strip()[:1000]

            metodo_pago =
                str(
                    datos.get(
                        "metodo_pago",
                        "stripe"
                    ) or "stripe"
                ).strip().lower()

            if metodo_pago not in (
                "stripe",
                "efectivo"
            ):

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Forma de pago no válida."
                    },
                    400
                )


            # ------------------------------------------------
            # VALIDAR CLIENTE
            # ------------------------------------------------

            nombre_cliente =
                str(
                    cliente.get(
                        "nombre",
                        ""
                    ) or ""
                ).strip()

            telefono_cliente =
                str(
                    cliente.get(
                        "telefono",
                        ""
                    ) or ""
                ).strip()

            email_cliente =
                str(
                    cliente.get(
                        "email",
                        ""
                    ) or ""
                ).strip()

            if not nombre_cliente:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Falta el nombre del cliente."
                    },
                    400
                )

            if not telefono_cliente:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Falta el teléfono del cliente."
                    },
                    400
                )

            if not email_cliente:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Falta el correo electrónico."
                    },
                    400
                )


            # ------------------------------------------------
            # VALIDAR ENTREGA
            # ------------------------------------------------

            tipo_entrega =
                str(
                    entrega.get(
                        "tipo",
                        "domicilio"
                    ) or "domicilio"
                ).strip()

            if tipo_entrega not in (
                "domicilio",
                "recoger"
            ):

                tipo_entrega =
                    "domicilio"


            fecha_entrega =
                str(
                    entrega.get(
                        "fecha",
                        ""
                    ) or ""
                ).strip()

            hora_entrega =
                entrega.get(
                    "hora"
                )

            direccion =
                str(
                    entrega.get(
                        "direccion",
                        ""
                    ) or ""
                ).strip()

            referencia =
                str(
                    entrega.get(
                        "referencia",
                        ""
                    ) or ""
                ).strip()


            if not fecha_entrega:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Falta la fecha del pedido."
                    },
                    400
                )


            if (
                tipo_entrega ==
                "domicilio"
                and not direccion
            ):

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Falta la dirección de entrega."
                    },
                    400
                )


            entrega["tipo"] =
                tipo_entrega

            entrega["fecha"] =
                fecha_entrega

            entrega["hora"] =
                hora_entrega

            entrega["direccion"] =
                direccion

            entrega["referencia"] =
                referencia


            # ------------------------------------------------
            # NEGOCIO
            # ------------------------------------------------

            negocio =
                cargar_negocio(
                    negocio_id
                )

            user_id =
                negocio.get(
                    "user_id"
                )

            if not user_id:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "El negocio no tiene usuario asociado."
                    },
                    400
                )


            # ------------------------------------------------
            # PRODUCTOS
            # ------------------------------------------------

            ids = []

            for item in items_recibidos:

                pid =
                    str(
                        item.get(
                            "product_id",
                            ""
                        )
                    ).strip()

                if pid and pid not in ids:

                    ids.append(
                        pid
                    )

            productos =
                cargar_productos(
                    user_id,
                    ids
                )

            items,
            total =
                preparar_items(
                    items_recibidos,
                    productos
                )


            if total <= 0:

                return responder(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "El total del pedido no es válido."
                    },
                    400
                )


            # ------------------------------------------------
            # CREAR PEDIDO
            # ------------------------------------------------

            pedido =
                guardar_pedido(
                    negocio_id,
                    cliente,
                    entrega,
                    comentarios,
                    metodo_pago,
                    items,
                    total
                )

            pedido_id =
                pedido.get(
                    "id"
                )

            # ------------------------------------------------
            # GUARDAR ITEMS
            # ------------------------------------------------

            try:

                guardar_items_pedido(
                    pedido_id,
                    items
                )

            except Exception:

                # Si falla la creación de items,
                # eliminamos el pedido para no dejar
                # un pedido incompleto.

                try:

                    supabase_request(
                        "DELETE",
                        "store_orders",
                        filtros={
                            "id":
                                pedido_id
                        }
                    )

                except Exception:
                    pass

                raise


            # ------------------------------------------------
            # RESPUESTA
            # ------------------------------------------------

            nombre_negocio =
                negocio.get(
                    "nombre_negocio"
                ) or negocio.get(
                    "nombre"
                ) or "Tienda"


            contenido =
                crear_contenido(
                    items
                )


            responder(
                self,
                {
                    "ok": True,

                    "order_id":
                        pedido_id,

                    "negocio_id":
                        negocio_id,

                    "total":
                        round(
                            total,
                            2
                        ),

                    "metodo_pago":
                        metodo_pago,

                    "nombre_negocio":
                        nombre_negocio,

                    "contenido":
                        contenido,

                    "message":
                        (
                            "Pedido creado correctamente."
                            if metodo_pago == "stripe"
                            else
                            "Pedido registrado correctamente."
                        )
                }
            )


        except Exception as error:

            print(
                "ERROR crear-pedido-tienda:",
                str(error)
            )

            responder(
                self,
                {
                    "ok": False,

                    "msg":
                        str(error)
                        or
                        "No se pudo crear el pedido."
                },
                500
    )
