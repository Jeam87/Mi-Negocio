import os, json, urllib.parse, urllib.request, urllib.error, base64, uuid
from http.server import BaseHTTPRequestHandler

def responder(h, data, code=200):
    body=json.dumps(data,ensure_ascii=False).encode()
    h.send_response(code)
    h.send_header("Access-Control-Allow-Origin","*")
    h.send_header("Access-Control-Allow-Methods","POST, OPTIONS")
    h.send_header("Access-Control-Allow-Headers","Content-Type")
    h.send_header("Content-Type","application/json; charset=utf-8")
    h.send_header("Content-Length",str(len(body)))
    h.end_headers(); h.wfile.write(body)

def leer_json(h):
    try:
        n=int(h.headers.get("Content-Length","0"))
        return json.loads(h.rfile.read(n).decode() or "{}")
    except Exception: return {}

def env(n): return os.getenv(n,"").strip()
SUPABASE_URL=env("SUPABASE_URL")
SUPABASE_KEY=env("SUPABASE_SERVICE_ROLE_KEY")
STRIPE_SECRET_KEY=env("STRIPE_SECRET_KEY")
STORE_URL=env("STORE_URL")

def supabase_request(method, table, data=None, filters=None, select=None, prefer="return=representation"):
    if not SUPABASE_URL: raise RuntimeError("Falta SUPABASE_URL.")
    if not SUPABASE_KEY: raise RuntimeError("Falta SUPABASE_SERVICE_ROLE_KEY.")
    url=SUPABASE_URL.rstrip()+"/rest/v1/"+table
    q=[]
    for k,v in (filters or {}).items():
        q.append(urllib.parse.quote(k,safe="")+"=eq."+urllib.parse.quote(str(v),safe=""))
    if select: q.append("select="+urllib.parse.quote(select,safe=""))
    if q: url+="?"+"&".join(q)
    body=None if data is None else json.dumps(data,ensure_ascii=False).encode()
    r=urllib.request.Request(url,data=body,method=method)
    r.add_header("apikey",SUPABASE_KEY); r.add_header("Authorization","Bearer "+SUPABASE_KEY)
    r.add_header("Content-Type","application/json"); r.add_header("Accept","application/json"); r.add_header("Prefer",prefer)
    try:
        with urllib.request.urlopen(r,timeout=25) as x:
            t=x.read().decode(); return json.loads(t) if t else []
    except urllib.error.HTTPError as e:
        try: t=e.read().decode()
        except Exception: t=""
        raise RuntimeError(t or ("Error de Supabase HTTP "+str(e.code)))

def supabase_rpc(name,data):
    url=SUPABASE_URL.rstrip()+"/rest/v1/rpc/"+name
    r=urllib.request.Request(url,data=json.dumps(data).encode(),method="POST")
    r.add_header("apikey",SUPABASE_KEY); r.add_header("Authorization","Bearer "+SUPABASE_KEY)
    r.add_header("Content-Type","application/json"); r.add_header("Accept","application/json")
    try:
        with urllib.request.urlopen(r,timeout=25) as x:
            t=x.read().decode(); return json.loads(t) if t else None
    except urllib.error.HTTPError as e:
        try: t=e.read().decode()
        except Exception: t=""
        raise RuntimeError(t or ("Error RPC HTTP "+str(e.code)))

def cargar_negocio(nid):
    rows=supabase_request("GET","negocios",filters={"id":nid},
        select="id,user_id,nombre_negocio,nombre,whatsapp")
    if not rows: raise RuntimeError("No se encontró el negocio.")
    return rows[0]

def cargar_stripe(uid):
    rows=supabase_request("GET","negocio_data",filters={"user_id":uid},select="data")
    if not rows: return {}
    d=rows[0].get("data")
    return d if isinstance(d,dict) else {}

def cargar_productos(uid,ids):
    out=[]; seen=set()
    for pid in ids:
        pid=str(pid).strip()
        if not pid or pid in seen: continue
        seen.add(pid)
        rows=supabase_request("GET","products",
            filters={"id":pid,"user_id":uid},
            select="id,user_id,name,price,stock,category")
        if not rows: raise RuntimeError("No se encontró el producto "+pid+" para este negocio.")
        out.append(rows[0])
    return out

def preparar_items(received,products):
    if not isinstance(received,list) or not received: raise RuntimeError("El carrito está vacío.")
    mp={str(p["id"]):p for p in products}; out=[]; total=0.0
    for it in received:
        if not isinstance(it,dict): raise RuntimeError("Hay un producto inválido.")
        pid=str(it.get("product_id","")).strip()
        try: qty=int(it.get("cantidad",0) or 0)
        except Exception: qty=0
        if not pid or qty<=0: raise RuntimeError("Producto o cantidad inválida.")
        p=mp.get(pid)
        if not p: raise RuntimeError("Producto no válido.")
        stock=p.get("stock")
        if stock is not None and stock!="":
            try: s=int(stock)
            except Exception: s=0
            if s<qty: raise RuntimeError("No hay suficientes unidades de "+str(p.get("name","producto"))+".")
        try: price=float(p.get("price",0) or 0)
        except Exception: price=0
        if price<=0: raise RuntimeError("El producto "+str(p.get("name","producto"))+" no tiene un precio válido.")
        sub=round(price*qty,2); total+=sub
        out.append({"product_id":str(p["id"]),"nombre":p.get("name","Producto"),"precio":round(price,2),"cantidad":qty,"subtotal":sub})
    return out,round(total,2)

def contenido(items):
    return " | ".join("{} x{} = ${:.2f}".format(i["nombre"],i["cantidad"],i["subtotal"]) for i in items)

def stripe_post(path,form,account):
    if not STRIPE_SECRET_KEY: raise RuntimeError("Falta STRIPE_SECRET_KEY.")
    if not account: raise RuntimeError("Este negocio todavía no tiene Stripe conectado.")
    body=urllib.parse.urlencode(form).encode()
    r=urllib.request.Request("https://api.stripe.com"+path,data=body,method="POST")
    auth=base64.b64encode((STRIPE_SECRET_KEY+":").encode()).decode()
    r.add_header("Authorization","Basic "+auth); r.add_header("Stripe-Account",account)
    r.add_header("Content-Type","application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(r,timeout=30) as x: return json.loads(x.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try: raw=e.read().decode()
        except Exception: raw=""
        try: msg=json.loads(raw).get("error",{}).get("message") or raw
        except Exception: msg=raw
        raise RuntimeError(msg or "Error de Stripe.")

def borrar_pedido(oid):
    try: supabase_request("DELETE","store_orders",filters={"id":oid},prefer="return=minimal")
    except Exception: pass

def devolver_stock(items):
    try: return supabase_rpc("store_devolver_stock",{"p_items":items})
    except Exception: return None

def crear_entrega(nid,pedido):
    entrega={
        "negocio_id":nid,
        "fecha_venta":str(pedido.get("created_at",""))[:10] or None,
        "fecha_entrega":pedido.get("fecha_entrega"),
        "hora_entrega":pedido.get("hora_entrega"),
        "contenido":pedido.get("contenido",""),
        "observaciones":pedido.get("comentarios",""),
        "quien_ordena":pedido.get("cliente_nombre",""),
        "telefono_ordena":pedido.get("cliente_telefono",""),
        "entregar_a":pedido.get("direccion","") if pedido.get("tipo_entrega")=="domicilio" else "Recoger en tienda",
        "estado":"pendiente"
    }
    return supabase_request("POST","entregas",data=entrega)

def crear_pedido(d):
    nid=str(d.get("negocio_id","")).strip()
    if not nid: raise RuntimeError("Falta negocio_id.")
    negocio=cargar_negocio(nid); uid=negocio.get("user_id")
    if not uid: raise RuntimeError("El negocio no tiene user_id.")
    received=d.get("items",[])
    ids=[str(x.get("product_id","")).strip() for x in received if isinstance(x,dict) and x.get("product_id")]
    products=cargar_productos(uid,ids)
    items,total=preparar_items(received,products)

    nombre=str(d.get("cliente_nombre","") or "").strip()
    tel=str(d.get("cliente_telefono","") or "").strip()
    email=str(d.get("cliente_email","") or "").strip()
    tipo=str(d.get("tipo_entrega","domicilio") or "domicilio").strip().lower()
    direccion=str(d.get("direccion","") or "").strip()
    referencia=str(d.get("referencia","") or "").strip()
    fecha=str(d.get("fecha_entrega","") or "").strip()
    hora=str(d.get("hora_entrega","") or "").strip()
    comentarios=str(d.get("comentarios","") or "").strip()
    metodo=str(d.get("metodo_pago","stripe") or "stripe").strip().lower()
    if not nombre: raise RuntimeError("Falta el nombre del cliente.")
    if not tel: raise RuntimeError("Falta el teléfono del cliente.")
    if tipo not in ("domicilio","recoger","pickup"): tipo="domicilio"
    if tipo=="domicilio" and not direccion: raise RuntimeError("Falta la dirección de entrega.")
    if metodo not in ("stripe","efectivo"): metodo="stripe"

    oid=str(uuid.uuid4())
    pedido={
        "id":oid,"negocio_id":nid,"cliente_nombre":nombre,"cliente_telefono":tel,
        "cliente_email":email,"tipo_entrega":tipo,"direccion":direccion,"referencia":referencia,
        "fecha_entrega":fecha or None,"hora_entrega":hora or None,"comentarios":comentarios,
        "contenido":contenido(items),"metodo_pago":metodo,"total":total,
        "estado":"pendiente","estado_pago":"pendiente","agenda_created":False
    }
    try:
        rows=supabase_request("POST","store_orders",data=pedido)
        if rows: pedido=rows[0]; oid=str(pedido.get("id",oid))
        supabase_request("POST","store_order_items",data=[
            {"order_id":oid,"product_id":i["product_id"],"nombre":i["nombre"],"precio":i["precio"],"cantidad":i["cantidad"],"subtotal":i["subtotal"]} for i in items
        ])
        supabase_rpc("store_descontar_stock",{"p_items":[{"product_id":i["product_id"],"cantidad":i["cantidad"]} for i in items]})
    except Exception:
        borrar_pedido(oid)
        raise

    if metodo=="efectivo":
        try:
            rows=supabase_request("PATCH","store_orders",
                data={"estado":"confirmado","estado_pago":"pendiente"},filters={"id":oid})
            if rows: pedido=rows[0]
            crear_entrega(nid,pedido)
            supabase_request("PATCH","store_orders",data={"agenda_created":True},filters={"id":oid},select=None)
        except Exception as e:
            return {"ok":True,"metodo_pago":"efectivo","order_id":oid,"total":total,"agenda_warning":str(e)}
        return {"ok":True,"metodo_pago":"efectivo","order_id":oid,"total":total,"mensaje":"Pedido registrado correctamente. Pago pendiente en efectivo."}

    sd=cargar_stripe(uid)
    account=sd.get("stripe_account_id") or sd.get("stripeAccountId") or ""
    if not account:
        devolver_stock([{"product_id":i["product_id"],"cantidad":i["cantidad"]} for i in items])
        borrar_pedido(oid)
        raise RuntimeError("Este negocio todavía no tiene Stripe conectado.")

    success=str(d.get("success_url","") or "").strip()
    cancel=str(d.get("cancel_url","") or "").strip()
    if not success:
        if not STORE_URL: raise RuntimeError("Falta STORE_URL o success_url.")
        sep="&" if "?" in STORE_URL else "?"
        success=STORE_URL+sep+"pago=exito&order_id="+urllib.parse.quote(oid)+"&session_id={CHECKOUT_SESSION_ID}"
    if not cancel:
        if not STORE_URL: raise RuntimeError("Falta STORE_URL o cancel_url.")
        sep="&" if "?" in STORE_URL else "?"
        cancel=STORE_URL+sep+"pago=cancelado&order_id="+urllib.parse.quote(oid)

    form={
        "mode":"payment","success_url":success,"cancel_url":cancel,
        "client_reference_id":oid,"customer_email":email,
        "automatic_payment_methods[enabled]":"true",
        "metadata[order_id]":oid,"metadata[negocio_id]":nid,
        "metadata[cliente_nombre]":nombre[:500],"metadata[cliente_telefono]":tel[:500],
        "metadata[fecha_entrega]":fecha[:100],"metadata[hora_entrega]":hora[:100]
    }
    for n,i in enumerate(items):
        form[f"line_items[{n}][price_data][currency]"]="mxn"
        form[f"line_items[{n}][price_data][unit_amount]"]=str(int(round(i["precio"]*100)))
        form[f"line_items[{n}][price_data][product_data][name]"]=str(i["nombre"])[:500]
        form[f"line_items[{n}][quantity]"]=str(i["cantidad"])

    try:
        session=stripe_post("/v1/checkout/sessions",form,account)
        url=session.get("url")
        if not url: raise RuntimeError("Stripe no devolvió el enlace de pago.")
    except Exception as e:
        devolver_stock([{"product_id":i["product_id"],"cantidad":i["cantidad"]} for i in items])
        borrar_pedido(oid)
        raise RuntimeError("No se pudo crear el pago de Stripe: "+str(e))

    sid=session.get("id","")
    supabase_request("PATCH","store_orders",
        data={"stripe_session_id":sid,"estado":"pendiente","estado_pago":"pendiente"},
        filters={"id":oid},select=None)
    return {"ok":True,"metodo_pago":"stripe","order_id":oid,"stripe_session_id":sid,"url":url,"total":total}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self): responder(self,{"ok":True})
    def do_POST(self):
        try: responder(self,crear_pedido(leer_json(self)),200)
        except Exception as e:
            print("ERROR crear-pedido-tienda:",str(e))
            responder(self,{"ok":False,"msg":str(e)},400)
