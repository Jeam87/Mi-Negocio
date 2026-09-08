from flask import Flask, jsonify, send_file, request
import os, json
app = Flask(__name__)
BASE_DATA = '/tmp/data' if os.path.exists('/tmp') else 'data'
os.makedirs(BASE_DATA, exist_ok=True)
USERS_FILE = os.path.join(BASE_DATA, 'users.json')
def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE,'r') as f: return json.load(f)
    except: pass
    return {}
def save_users(u):
    try:
        with open(USERS_FILE,'w') as f: json.dump(u,f)
    except: pass
def get_user_file(nid):
    safe=nid.replace("@","_at_").replace(".","_")
    return os.path.join(BASE_DATA, f"{safe}.json")
@app.route('/manifest.json')
def manifest(): return jsonify({"name":"Mi Negocio 10.4","short_name":"Mi Negocio","start_url":"/","display":"standalone"})
@app.route('/logo.png')
def logo_file():
    if os.path.exists('logo.png'): return send_file('logo.png', mimetype='image/png')
    return "",204
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        d=request.json; email=d.get('email','').lower().strip(); pwd=d.get('password','')
        users=load_users()
        if email in users: return jsonify({"ok":False,"msg":"Ya existe"}),400
        users[email]={"password":pwd,"negocio_id":email,"rol":"owner"}; save_users(users)
        with open(get_user_file(email),'w') as f: json.dump({},f)
        return jsonify({"ok":True,"email":email,"negocio_id":email})
    except Exception as e: return jsonify({"ok":False,"msg":str(e)}),500
@app.route('/api/login', methods=['POST'])
def api_login():
    d=request.json; email=d.get('email','').lower().strip(); pwd=d.get('password','')
    users=load_users()
    if email not in users or users[email]['password']!=pwd: return jsonify({"ok":False,"msg":"Error"}),401
    return jsonify({"ok":True,"email":email,"negocio_id":users[email]['negocio_id'],"rol":users[email]['rol']})
@app.route('/api/invite', methods=['POST'])
def api_invite():
    d=request.json; owner=d.get('owner_email','').lower().strip(); owner_pwd=d.get('owner_password',''); colab=d.get('colab_email','').lower().strip(); colab_pwd=d.get('colab_password','') or '1234'
    users=load_users()
    if owner not in users or users[owner]['password']!=owner_pwd: return jsonify({"ok":False,"msg":"No autorizado"}),403
    users[colab]={"password":colab_pwd,"negocio_id":users[owner]['negocio_id'],"rol":"colab"}; save_users(users)
    return jsonify({"ok":True})
@app.route('/api/load', methods=['GET'])
def api_load():
    email=request.args.get('email','').lower().strip(); users=load_users()
    if email not in users: return jsonify({"ok":False}),404
    fname=get_user_file(users[email]['negocio_id'])
    data=json.load(open(fname)) if os.path.exists(fname) else {}
    return jsonify({"ok":True,"data":data})
@app.route('/api/save', methods=['POST'])
def api_save():
    d=request.json; email=d.get('email','').lower().strip(); data=d.get('data',{})
    users=load_users()
    if email not in users: return jsonify({"ok":False}),404
    with open(get_user_file(users[email]['negocio_id']),'w') as f: json.dump(data,f)
    return jsonify({"ok":True})
@app.route('/')
def home():
 return """<!DOCTYPE html>
<html><head><link rel="manifest" href="/manifest.json"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 10.4</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>input,select,textarea{color:#000!important;background:#fff!important}.logo-watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:360px;height:360px;pointer-events:none;z-index:0;opacity:0.08;object-fit:contain;}#appContent{position:relative;z-index:1;}</style></head>
<body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[130px] relative">
<img id="logoBg" class="logo-watermark hidden"><div id="appContent">
<div id="loginScreen" class="fixed inset-0 bg-[#FFF8F0] z-[100] flex flex-col items-center justify-center p-6">
<h1 class="font-black text-[24px]">Mi Negocio 10.4</h1><p class="text-[11px] text-gray-500">Hora celular real + pago</p>
<div class="bg-white w-full rounded-[28px] p-5 shadow-xl border-2 border-black mt-6">
<input id="loginEmail" type="email" placeholder="Correo" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[14px]">
<input id="loginPass" type="password" placeholder="Contraseña" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[14px] mt-3">
<button onclick="hacerLogin()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">ENTRAR</button>
<button onclick="hacerRegistro()" class="w-full mt-2 bg-white border-2 border-black py-3 rounded-2xl font-bold text-[13px]">REGISTRARME</button>
<p id="loginMsg" class="hidden mt-3 text-[11px] font-bold text-center p-2 rounded-xl"></p></div></div>

<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><div class="flex items-center gap-2"><img id="logoHeader" class="w-9 h-9 rounded-full object-cover border-2 border-black hidden"><div><h1 class="font-black text-[14px]">Mi Negocio 10.4</h1><p id="userLabel" class="text-[10px] text-gray-500"></p><p id="horaActual" class="text-[10px] font-black text-green-600"></p></div></div><div class="flex gap-2"><button onclick="showTab('config')" class="text-[10px] bg-black text-white px-3 py-1 rounded-full">Config</button><button onclick="cerrarSesion()" class="text-[10px] bg-red-100 text-red-600 px-2 py-1 rounded-full">Salir</button></div></div>

<div id="tab-vender" class="p-3 hidden">
<div class="bg-white rounded-[20px] p-3 shadow-sm mb-3"><div class="flex justify-between items-center"><h3 class="font-black text-[13px]">Categorías</h3><button onclick="document.getElementById('boxNuevaCat').classList.toggle('hidden')" class="text-[10px] bg-black text-white px-3 py-1 rounded-full">+ Nueva</button></div><div id="filtrosCats" class="flex gap-2 mt-3 overflow-x-auto pb-2"></div><div id="boxNuevaCat" class="hidden mt-3 bg-amber-50 border-2 p-3 rounded-xl"><div id="listaCatsEdit" class="space-y-2 mb-3"></div><div class="grid grid-cols-5 gap-2"><input id="nuevaCatNombre" placeholder="Ej: Alitas" class="col-span-4 border-2 border-black p-2 rounded-xl text-[12px] font-bold"><button onclick="addCategoriaVenta()" class="bg-black text-white rounded-xl font-black">+</button></div></div></div>
<div id="listaVenta" class="grid grid-cols-2 gap-3"></div>
<div class="mt-6 bg-white rounded-[28px] p-4 shadow-xl border-2 border-black">
<div class="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-2 mb-3">
<p class="text-[10px] font-black">👤 ¿A quién le cobras?</p>
<select id="selCliente" class="w-full border-2 border-black p-3 rounded-xl text-[12px] font-bold mt-2" onchange="actualizarClienteTicket()"></select>
<div class="flex gap-2 mt-2">
<input id="quickClienteNombre" placeholder="Nombre nuevo" class="flex-1 border-2 border-black p-2 rounded-xl text-[11px] font-bold">
<input id="quickClienteTel" placeholder="WhatsApp 443..." class="flex-1 border-2 border-black p-2 rounded-xl text-[11px] font-bold">
<button onclick="addClienteRapido()" class="bg-black text-white px-3 rounded-xl font-black text-[12px]">+</button>
</div>
</div>
<div id="ticket" class="space-y-2">Vacío</div>
<div class="flex justify-between font-black text-[20px] mt-4 border-t-2 pt-3">Total $ <span id="c-total">0</span></div>
<button onclick="abrirCobro()" class="w-full mt-3 bg-black text-white py-4 rounded-2xl font-black">COBRAR</button>
</div>
</div>

<div id="tab-costos" class="p-3"><div id="crear-menu" class="space-y-4">
<div class="bg-white rounded-[28px] p-5 shadow-sm border-2 border-black"><h2 class="font-black">💰 Gastos Fijos</h2><div class="grid grid-cols-5 gap-2 mt-3"><input id="fijoNombre" placeholder="Ej: Renta" class="col-span-2 border-2 border-black p-3 rounded-xl font-bold text-[12px]"><input id="fijoMonto" type="number" placeholder="$3000" class="col-span-2 border-2 border-black p-3 rounded-xl font-black text-[12px]"><button onclick="addFijo()" class="bg-black text-white rounded-xl font-black">+</button></div><div id="listaFijos" class="mt-3 space-y-2"></div><div class="mt-3 bg-black text-white p-3 rounded-xl flex justify-between font-black"><span>Total Fijos/mes</span><span>$<span id="totalFijos">0</span></span></div><div class="mt-2 bg-amber-50 border-2 p-3 rounded-xl"><input id="lotesMes" type="number" value="30" class="w-full border-2 border-black p-2 rounded-xl font-black" oninput="localStorage.setItem('lotesMes_'+negocioId,this.value); renderFijos(); calc(); guardarEnNube();"></div></div>
<div class="bg-white rounded-[28px] p-5 shadow-sm text-center"><button onclick="setCrear('base')" class="w-full bg-[#FFF8F0] border-2 border-black rounded-[20px] p-5 font-black">1. Crear BASE</button><button onclick="setCrear('producto')" class="w-full mt-3 bg-[#0F172A] text-white rounded-[20px] p-5 font-black">2. Producto + Categoría</button></div><div class="bg-white rounded-[20px] p-4"><h3 class="font-black text-[12px] mb-2">Mis recetas</h3><div id="listaInv"></div></div></div>
<div id="crear-base" class="hidden"><button onclick="cancelarEdicion()" class="mb-3 font-bold">← Volver</button><div class="bg-white rounded-[28px] p-4 shadow-sm"><h2 class="font-black">BASE</h2><input id="nombre" placeholder="Ej: Salsa" class="w-full border-2 border-black p-4 rounded-2xl font-bold mt-3"><div id="insumos" class="mt-4 space-y-3"></div><button onclick="addInsumo()" class="w-full mt-3 bg-orange-100 border-2 py-3 rounded-2xl font-black text-[12px]">+ Ingrediente</button><div class="mt-4 bg-amber-50 border-2 p-3 rounded-2xl"><div class="flex gap-2"><input id="rendCant" type="number" value="10" class="flex-1 border-2 border-black p-3 rounded-xl font-black" oninput="calc()"><select id="rendUni" class="border-2 border-black p-3 rounded-xl font-bold" onchange="calc()"><option>L</option><option>ml</option><option>kg</option><option>g</option><option>pza</option><option>m</option><option>cm</option></select></div></div><div class="mt-3 p-4 bg-[#0F172A] text-white rounded-[16px]"><div class="flex justify-between"><span>Ingredientes</span><b>$<span id="c-ing">0.00</span></b></div><div class="flex justify-between text-amber-300 text-[12px]"><span>+ Fijos</span><b>$<span id="c-fijos">0.00</span></b></div><div class="font-black border-t border-white/20 mt-2 pt-2 flex justify-between"><span>Total</span><span>$<span id="costo">0.00</span></span></div><div class="flex justify-between mt-2 text-[#4FD1C5]"><span>Venta</span><span>$<span id="venta">0.00</span></span></div><div class="mt-3 flex gap-2 bg-white/10 p-2 rounded-xl"><input id="margen" type="number" value="50" class="w-16 text-black rounded-lg text-center font-black py-2" oninput="calc()"><input id="ventaManual" type="number" placeholder="$ final" class="flex-1 text-black rounded-lg px-2 py-2 font-black" oninput="calc()"></div></div><button onclick="guardarProd('recetario')" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR BASE</button></div></div>
<div id="crear-producto" class="hidden"><button onclick="cancelarEdicion()" class="mb-3 font-bold">← Volver</button><div class="bg-white rounded-[28px] p-4"><h2 class="font-black">Producto</h2><input id="nombreProd" placeholder="Ej: Alitas" class="w-full border-2 border-black p-4 rounded-2xl font-bold mt-3"><div class="mt-3 bg-blue-50 border-2 border-blue-200 p-3 rounded-xl"><p class="text-[11px] font-black">📂 Categoría</p><select id="prodCategoria" class="w-full border-2 border-black p-3 rounded-xl mt-2 font-bold text-[12px]"></select><div class="mt-2 flex gap-2"><input id="quickCat" placeholder="Nueva" class="flex-1 border-2 border-black p-2 rounded-xl text-[11px]"><button onclick="addCategoriaVentaDesdeProd()" class="bg-black text-white px-3 rounded-xl text-[11px] font-bold">Crear</button></div></div><div class="mt-3"><input type="file" id="fotoInput" accept="image/*" onchange="previewFoto(this)" class="w-full mt-2 text-[12px]"><div id="fotoPreview" class="mt-2 hidden"><img id="fotoImg" class="w-24 h-24 object-cover rounded-xl border-2 border-black"></div></div><div class="mt-4 bg-amber-50 border-2 p-3 rounded-2xl"><p class="text-[11px] font-black">Bases que lleva:</p><div id="basesSel" class="mt-2 space-y-3"></div><button onclick="addBase()" class="w-full mt-2 bg-white border-2 py-2 rounded-xl font-bold text-[11px]">+ Base</button></div><div class="mt-3 p-4 bg-black text-white rounded-[16px]"><div class="flex justify-between"><span>Costo</span><b>$<span id="c-ing2">0.00</span></b></div><div class="flex justify-between font-black text-[16px] mt-1"><span>Venta</span><span class="text-[#4FD1C5]">$<span id="venta2">0.00</span></span></div><div class="mt-2 flex gap-2"><input id="margen2" type="number" value="100" class="w-14 text-black rounded-lg text-center font-black py-1" oninput="calc2()"><input id="ventaManual2" type="number" placeholder="$ final" class="ml-auto w-20 text-black rounded-lg px-2 py-1 font-black" oninput="calc2()"></div></div><button onclick="guardarProd('catalogo')" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR</button></div></div></div>

<div id="tab-config" class="p-3 hidden"><div class="bg-white rounded-[28px] p-5 shadow-sm"><h2 class="font-black">⚙️ Config</h2>
<div class="mt-4 bg-purple-50 border-2 border-purple-200 rounded-2xl p-3"><p class="font-black text-[12px]">👥 Colaboradores</p><div class="grid grid-cols-5 gap-2 mt-3"><input id="colabEmail" type="email" placeholder="colab@gmail.com" class="col-span-3 border-2 border-black p-2 rounded-xl text-[12px]"><input id="colabPass" placeholder="Pass" class="col-span-1 border-2 border-black p-2 rounded-xl text-[11px]"><button onclick="invitarColab()" class="bg-purple-600 text-white rounded-xl font-black">+</button></div></div>
<div class="mt-4 bg-blue-50 border-2 border-blue-200 rounded-2xl p-3"><p class="font-black text-[12px]">📸 Logo</p><input type="file" id="logoInput" accept="image/*" onchange="previewLogo(this)" class="w-full mt-2 text-[12px]"><div id="logoPreviewBox" class="mt-3 hidden flex gap-3 items-center"><img id="logoPreview" class="w-20 h-20 object-contain rounded-xl border-2 border-black bg-white"><button onclick="quitarLogo()" class="text-[10px] bg-red-100 text-red-600 px-2 py-1 rounded-full font-bold">X</button></div><div class="mt-3 grid grid-cols-2 gap-2"><label class="text-[11px] font-bold flex items-center gap-1"><input type="checkbox" id="empMostrarLogo" checked> Logo ticket</label><label class="text-[11px] font-bold flex items-center gap-1"><input type="checkbox" id="empMostrarFondo" checked> Fondo</label></div><div class="mt-3"><input type="range" id="empOpacidad" min="2" max="20" value="8" class="w-full" oninput="document.getElementById('opacidadVal').innerText=this.value+'%'; actualizarFondo();"><span id="opacidadVal" class="text-[10px]">8%</span></div></div><input id="empNombre" placeholder="Nombre negocio" class="w-full border-2 border-black p-3 rounded-xl mt-4 font-bold"><input id="empDireccion" placeholder="Dirección" class="w-full border-2 border-black p-3 rounded-xl mt-2 text-[13px]"><div class="grid grid-cols-2 gap-2 mt-2"><input id="empCP" placeholder="CP" class="border-2 border-black p-3 rounded-xl text-[13px]"><input id="empTel" placeholder="Tel" class="border-2 border-black p-3 rounded-xl text-[13px]"></div><input id="empRFC" placeholder="RFC" class="w-full border-2 border-black p-3 rounded-xl mt-2 text-[13px]"><textarea id="empMensaje" placeholder="Mensaje ticket" class="w-full border-2 border-black p-3 rounded-xl mt-2 text-[12px]" rows="2"></textarea><button onclick="guardarEmpresa()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR</button><button onclick="probarTicket()" class="w-full mt-2 bg-white border-2 border-black py-3 rounded-2xl font-bold">🧾 Probar ticket</button><div id="ticketVista" class="mt-6 border-2 border-dashed p-3 rounded-xl"><div id="ticketContenido" class="bg-white p-3 rounded-xl text-[12px] font-mono shadow-sm"></div><div class="grid grid-cols-2 gap-2 mt-3"><button onclick="imprimirTicket()" class="bg-black text-white py-3 rounded-xl font-black text-[12px]">🖨️ Imprimir</button><button onclick="enviarWhatsAppTicket(true)" class="bg-[#25D366] text-white py-3 rounded-xl font-black text-[12px]">📲 WhatsApp</button></div></div></div></div>

<div id="tab-clientes" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[28px] p-4 text-white"><div class="flex justify-between"><h2 class="font-black">👥 Clientes</h2></div><div class="grid grid-cols-5 gap-2 mt-3"><input id="cliNombre" placeholder="Nombre" class="col-span-2 border-2 border-black p-2 rounded-xl text-[12px] text-black"><input id="cliTel" placeholder="WhatsApp" class="col-span-2 border-2 border-black p-2 rounded-xl text-[12px] text-black"><button onclick="addCliente()" class="bg-[#25D366] text-white rounded-xl font-black">+</button></div></div><div class="mt-3 bg-white rounded-[20px] p-4"><div id="listaClientes" class="space-y-3"></div></div></div>
<div id="tab-inventario" class="p-3 hidden"><div class="bg-white rounded-[20px] p-4"><div class="grid grid-cols-5 gap-2"><input id="inv-nombre" placeholder="Papas" class="col-span-2 border-2 border-black p-3 rounded-xl font-bold"><input id="inv-precio" type="number" placeholder="$30" class="border-2 border-black p-3 rounded-xl font-black"><select id="inv-unidad" class="border-2 border-black p-3 rounded-xl text-[10px] font-bold"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>pza</option><option>m</option><option>cm</option><option>lb</option><option>oz</option></select><button onclick="addInventario()" class="bg-black text-white rounded-xl font-black">+</button></div><div id="listaInvMaster" class="mt-4"></div></div></div>

<div id="tab-finanzas" class="p-3 hidden">
<div class="bg-[#2D3748] rounded-[24px] p-4 text-white"><div class="flex justify-between items-center"><h2 class="font-black">📅 Finanzas</h2><button onclick="openGasto()" class="bg-[#4FD1C5] text-black w-10 h-10 rounded-xl font-black text-xl">+</button></div><div class="grid grid-cols-3 gap-2 mt-3"><div class="bg-white/10 rounded-xl p-2 text-center"><p class="text-[9px] opacity-60">BALANCE</p><p class="font-black text-[14px]" id="fin-balance">$0</p></div><div class="bg-green-500/20 rounded-xl p-2 text-center"><p class="text-[9px]">ENTRADAS</p><p class="font-black text-[14px] text-green-300" id="fin-entradas">$0</p></div><div class="bg-red-500/20 rounded-xl p-2 text-center"><p class="text-[9px]">SALIDAS</p><p class="font-black text-[14px] text-red-300" id="fin-salidas">$0</p></div></div><div class="flex gap-2 mt-4 bg-white/10 p-1 rounded-xl"><button onclick="setVistaCal('dia')" id="vc-dia" class="flex-1 py-2 rounded-lg font-black text-[11px] bg-white text-black">Día</button><button onclick="setVistaCal('semana')" id="vc-semana" class="flex-1 py-2 rounded-lg font-bold text-[11px]">Semana</button><button onclick="setVistaCal('mes')" id="vc-mes" class="flex-1 py-2 rounded-lg font-bold text-[11px]">Mes</button><button onclick="setVistaCal('ano')" id="vc-ano" class="flex-1 py-2 rounded-lg font-bold text-[11px]">Año</button></div></div>
<div class="mt-3 bg-white rounded-[24px] p-4 shadow-sm"><div class="flex justify-between items-center"><button onclick="moverCal(-1)" class="w-9 h-9 bg-gray-100 rounded-full font-black"><</button><h3 id="calTitulo" class="font-black text-[14px]"></h3><button onclick="moverCal(1)" class="w-9 h-9 bg-gray-100 rounded-full font-black">></button></div><div id="calGrid" class="mt-4"></div><div id="calSemana" class="mt-4 hidden"></div><div id="calAno" class="mt-4 hidden grid grid-cols-3 gap-2"></div></div>
<div id="desgloseDia" class="mt-3 bg-white rounded-[24px] p-4 shadow-sm border-2 border-black"><h3 class="font-black text-[13px]">Desglose del <span id="fechaSelLabel"></span></h3><div class="grid grid-cols-3 gap-2 mt-3 text-center"><div class="bg-green-50 border-2 border-green-200 p-2 rounded-xl"><p class="text-[9px]">ENTRADAS</p><p id="diaEntradas" class="font-black text-green-600">$0</p><p id="diaNumEntradas" class="text-[9px]">0 ventas</p></div><div class="bg-red-50 border-2 border-red-200 p-2 rounded-xl"><p class="text-[9px]">SALIDAS</p><p id="diaSalidas" class="font-black text-red-600">$0</p></div><div class="bg-black text-white p-2 rounded-xl"><p class="text-[9px]">GANANCIA</p><p id="diaGanancia" class="font-black text-[#4FD1C5]">$0</p></div></div><div id="flu-lista" class="mt-4 space-y-2"></div></div>
</div>

<div id="modalCobro" class="hidden fixed inset-0 bg-black/70 z-50 flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5">
<h2 class="font-black text-[14px]">Cobrar $<span id="cobroTotal">0</span> a <span id="cobroClienteNombre" class="text-blue-600"></span></h2>
<p class="text-[11px] mt-1">Hora: <span id="cobroHora" class="font-black text-green-600"></span></p>

<div class="mt-3">
<p class="text-[11px] font-black">💳 Método de pago</p>
<div class="grid grid-cols-3 gap-2 mt-2">
<button onclick="setMetodoPago('Efectivo')" id="mp-efectivo" class="py-3 rounded-xl border-2 font-black text-[12px] bg-black text-white border-black">💵 Efectivo</button>
<button onclick="setMetodoPago('Tarjeta')" id="mp-tarjeta" class="py-3 rounded-xl border-2 font-bold text-[12px] bg-white border-black">💳 Tarjeta</button>
<button onclick="setMetodoPago('Transferencia')" id="mp-transferencia" class="py-3 rounded-xl border-2 font-bold text-[12px] bg-white border-black">🏦 Transfer.</button>
</div>
<input type="hidden" id="metodoPago" value="Efectivo">
</div>

<input id="pagoRecibido" type="number" placeholder="$ Recibido (solo efectivo)" class="w-full border-2 border-black p-3 rounded-xl mt-3 font-black text-[18px]" oninput="calcCambio()">
<p class="mt-2 font-black text-[13px]">Cambio: $<span id="cambio">0.00</span> • <span id="vendedorCobro" class="text-blue-600 text-[11px]"></span></p>

<div class="grid grid-cols-2 gap-2 mt-4">
<button onclick="confirmarCobro('print')" class="bg-black text-white py-4 rounded-2xl font-black text-[13px]">🖨️ IMPRIMIR</button>
<button onclick="confirmarCobro('whatsapp')" class="bg-[#25D366] text-white py-4 rounded-2xl font-black text-[13px]">📲 WHATSAPP</button>
</div>
<button onclick="confirmarCobro('solo')" class="w-full mt-2 bg-gray-100 py-3 rounded-xl font-bold text-[13px]">Solo cobrar</button>
<button onclick="cerrarCobro()" class="w-full mt-2 bg-white border-2 border-black py-2 rounded-xl">Cancelar</button>
</div></div>

<div id="modalGasto" class="hidden fixed inset-0 bg-black/70 z-50 flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5"><input id="g-concepto" placeholder="Concepto" class="w-full border-2 border-black p-3 rounded-xl"><input id="g-monto" type="number" placeholder="Monto" class="w-full border-2 border-black p-3 rounded-xl mt-2"><input type="hidden" id="g-tipo" value="salida"><div class="grid grid-cols-2 gap-2 mt-3"><button onclick="document.getElementById('g-tipo').value='salida'" class="border-2 border-black p-3 rounded-xl font-bold bg-red-500 text-white">SALIDA</button><button onclick="document.getElementById('g-tipo').value='entrada'" class="border-2 border-black p-3 rounded-xl font-bold">ENTRADA</button></div><button onclick="guardarGasto()" class="w-full mt-4 bg-black text-white py-3 rounded-xl font-black">Guardar</button><button onclick="cerrarGasto()" class="w-full mt-2 bg-gray-100 py-2 rounded-xl">Cerrar</button></div></div>

<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30"><button onclick="showTab('costos')" class="flex flex-col items-center text-black"><i class="fa-solid fa-book"></i><span class="text-[7px] font-bold">Crear</span></button><button onclick="showTab('vender')" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-store"></i><span class="text-[7px]">Catalogo</span></button><button onclick="showTab('inventario')" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-boxes-stacked"></i><span class="text-[7px]">Inventario</span></button><button onclick="showTab('finanzas')" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-chart-line"></i><span class="text-[7px]">Finanzas</span></button><button onclick="showTab('clientes')" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-users"></i><span class="text-[7px]">Clientes</span></button></div></div></div>
<script>
let carrito=[], fotoTemp='', logoTemp='', categoriaFiltro='todas', editId=null, currentUser=null, negocioId=null, ultimoTicket=null;

// === HORA 100% CELULAR, SIN ZONA HORARIA ===
function getFechaLocal(){
  let now = new Date();
  let fecha = now.toLocaleDateString('es-MX', {day:'2-digit', month:'2-digit', year:'numeric'});
  let hora = now.toLocaleTimeString('es-MX', {hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:true});
  return fecha + ', ' + hora;
}
function getFechaSoloLocal(){
  let now = new Date();
  let y=now.getFullYear(), m=String(now.getMonth()+1).padStart(2,'0'), d=String(now.getDate()).padStart(2,'0');
  return `${y}-${m}-${d}`;
}
function getHoraCorta(){ return new Date().toLocaleTimeString('es-MX',{hour:'2-digit',minute:'2-digit',hour12:true}); }

let vistaCal='mes', fechaVista=new Date(), fechaSel=getFechaSoloLocal(), metodoPagoSel='Efectivo';

function setMetodoPago(m){
  metodoPagoSel=m;
  document.getElementById('metodoPago').value=m;
  ['efectivo','tarjeta','transferencia'].forEach(x=>{
    let b=document.getElementById('mp-'+x);
    if(!b) return;
    let es=b.id=='mp-'+m.toLowerCase();
    b.className= es? 'py-3 rounded-xl border-2 font-black text-[12px] bg-black text-white border-black' : 'py-3 rounded-xl border-2 font-bold text-[12px] bg-white border-black';
  });
  let pagoInput=document.getElementById('pagoRecibido');
  if(m=='Efectivo'){ pagoInput.classList.remove('hidden'); pagoInput.placeholder='$ Recibido'; }
  else { pagoInput.classList.add('hidden'); document.getElementById('cambio').innerText='0.00'; }
}

function actualizarHora(){ let el=document.getElementById('horaActual'); if(el) el.innerText='🕒 Hora cel: '+getFechaLocal(); let el2=document.getElementById('cobroHora'); if(el2 &&!document.getElementById('modalCobro').classList.contains('hidden')) el2.innerText=getFechaLocal(); }
setInterval(actualizarHora,1000);

function msgLogin(txt,ok){let el=document.getElementById('loginMsg'); el.innerText=txt; el.classList.remove('hidden'); el.className='mt-3 text-[11px] font-bold text-center p-2 rounded-xl '+(ok?'bg-green-100 text-green-700':'bg-red-100 text-red-700');}
async function hacerRegistro(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); if(!e||!p) return msgLogin('Pon correo y pass',false); let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})}); let j=await r.json(); if(!j.ok) return msgLogin(j.msg,false); msgLogin('✅ Cuenta creada, ahora entra',true);}
async function hacerLogin(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); if(!e||!p) return msgLogin('Pon correo',false); let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})}); let j=await r.json(); if(!j.ok) return msgLogin(j.msg,false); currentUser=e; negocioId=j.negocio_id; localStorage.setItem('session_email',e); localStorage.setItem('session_negocio',negocioId); document.getElementById('loginScreen').classList.add('hidden'); document.getElementById('userLabel').innerText=e+' • '+(j.rol=='owner'?'Dueño':'Colab'); await cargarDeNube(); showTab('vender');}
function cerrarSesion(){localStorage.removeItem('session_email'); localStorage.removeItem('session_negocio'); location.reload();}
async function cargarDeNube(){if(!currentUser) return; let r=await fetch('/api/load?email='+encodeURIComponent(currentUser)); let j=await r.json(); if(!j.ok) return; let data=j.data||{}; for(let k in data){ localStorage.setItem(k+'_'+negocioId, data[k]); } renderFijos(); renderInventario(); renderCategoriasVenta(); renderProdCategoriaSelect(); renderClientes(); renderCalendario(); cargarEmpresa(); actualizarHora();}
async function guardarEnNube(){if(!currentUser) return; let keys=['productosV2','inventarioMaestro','clientesV2','facturas','categoriasVenta','gastosFijos','empresaConfig','lotesMes']; let data={}; keys.forEach(k=>{ let v=localStorage.getItem(k+'_'+negocioId) || localStorage.getItem(k); if(v) data[k]=v; }); await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:currentUser,data})});}
window.addEventListener('load', async ()=>{ let e=localStorage.getItem('session_email'); let n=localStorage.getItem('session_negocio'); if(e&&n){ document.getElementById('loginEmail').value=e; currentUser=e; negocioId=n; document.getElementById('loginScreen').classList.add('hidden'); document.getElementById('userLabel').innerText=e; await cargarDeNube(); }});
async function invitarColab(){let colab=document.getElementById('colabEmail').value.trim().toLowerCase(); let pass=document.getElementById('colabPass').value.trim()||'1234'; if(!colab) return alert('Pon correo'); let ownerPass=prompt('Confirma TU contraseña de dueño:'); if(!ownerPass) return; let r=await fetch('/api/invite',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({owner_email:currentUser,owner_password:ownerPass,colab_email:colab,colab_password:pass})}); let j=await r.json(); if(!j.ok) return alert(j.msg); alert('✅ Agregado Pass: '+pass);}

function getFijos(){ return JSON.parse(localStorage.getItem('gastosFijos_'+negocioId)||localStorage.getItem('gastosFijos')||'[]'); }
function getProd(){ return JSON.parse(localStorage.getItem('productosV2_'+negocioId)||localStorage.getItem('productosV2')||'[]'); }
function getInv(){ return JSON.parse(localStorage.getItem('inventarioMaestro_'+negocioId)||localStorage.getItem('inventarioMaestro')||'[]'); }
function getCli(){ return JSON.parse(localStorage.getItem('clientesV2_'+negocioId)||localStorage.getItem('clientesV2')||'[]'); }
function getFacts(){ return JSON.parse(localStorage.getItem('facturas_'+negocioId)||localStorage.getItem('facturas')||'[]'); }
function getEmp(){ return JSON.parse(localStorage.getItem('empresaConfig_'+negocioId)||localStorage.getItem('empresaConfig')||'{"nombre":"Mi Negocio","logo":"","mostrarLogo":true,"mostrarFondo":true,"opacidad":8}'); }
function getCategoriasVenta(){ let cats=JSON.parse(localStorage.getItem('categoriasVenta_'+negocioId)||localStorage.getItem('categoriasVenta')||'[]'); if(!cats.length){ cats=[{id:'todas',nombre:'Todas'},{id:'alitas',nombre:'Alitas'},{id:'papas',nombre:'Papas'},{id:'bebidas',nombre:'Bebidas'}]; localStorage.setItem('categoriasVenta_'+negocioId,JSON.stringify(cats)); } return cats; }
function getLotes(){ return parseInt(localStorage.getItem('lotesMes_'+negocioId)||localStorage.getItem('lotesMes')||'30')||30; }
function setItem(k,v){ localStorage.setItem(k+'_'+negocioId, typeof v==='string'? v: JSON.stringify(v)); localStorage.setItem(k, typeof v==='string'? v: JSON.stringify(v)); guardarEnNube(); }
function normalizarUnidad(u){ u=(u||'').toLowerCase().trim(); if(['g','gr'].includes(u)) return 'g'; if(['kg'].includes(u)) return 'kg'; if(['mg'].includes(u)) return 'mg'; if(['l','litro','litros'].includes(u)) return 'L'; if(['ml'].includes(u)) return 'ml'; if(['m','metro'].includes(u)) return 'm'; if(['cm'].includes(u)) return 'cm'; if(['lb','libra'].includes(u)) return 'lb'; if(['oz'].includes(u)) return 'oz'; if(['pza','pieza'].includes(u)) return 'pza'; return u; }
function factorABase(u){ u=normalizarUnidad(u); let map={mg:0.001,g:1,kg:1000,lb:453.592,oz:28.3495,ml:1,L:1000,m:100,cm:1,pza:1}; return map[u]||1; }
function convertir(cant, de, a){ de=normalizarUnidad(de); a=normalizarUnidad(a); if(de==a) return cant; return cant * factorABase(de) / factorABase(a); }

function addCategoriaVenta(){ let n=document.getElementById('nuevaCatNombre').value.trim(); if(!n) return; let cats=getCategoriasVenta(); let id=n.toLowerCase().replace(/\\s+/g,'-')+'-'+Date.now(); cats.push({id,nombre:n}); setItem('categoriasVenta',cats); document.getElementById('nuevaCatNombre').value=''; renderCategoriasVenta(); renderProdCategoriaSelect(); }
function addCategoriaVentaDesdeProd(){ let n=document.getElementById('quickCat').value.trim(); if(!n) return; let cats=getCategoriasVenta(); let id=n.toLowerCase().replace(/\\s+/g,'-')+'-'+Date.now(); cats.push({id,nombre:n}); setItem('categoriasVenta',cats); document.getElementById('quickCat').value=''; renderCategoriasVenta(); renderProdCategoriaSelect(); document.getElementById('prodCategoria').value=id; }
function editarCategoria(id){ let cats=getCategoriasVenta(); let cat=cats.find(c=>c.id==id); let nuevo=prompt('Nuevo nombre:', cat.nombre); if(!nuevo) return; cat.nombre=nuevo.trim(); setItem('categoriasVenta',cats); renderCategoriasVenta(); renderProdCategoriaSelect(); renderInventario(); renderVenta(); }
function borrarCategoria(id){ if(id=='todas') return; if(!confirm('¿Borrar?')) return; let cats=getCategoriasVenta().filter(c=>c.id!=id); setItem('categoriasVenta',cats); if(categoriaFiltro==id) categoriaFiltro='todas'; renderCategoriasVenta(); renderProdCategoriaSelect(); renderVenta(); }
function renderCategoriasVenta(){ let cats=getCategoriasVenta(); let html=`<button onclick="filtrarCategoria('todas')" class="px-4 py-2 rounded-full font-black text-[11px] whitespace-nowrap border-2 ${categoriaFiltro=='todas'?'bg-black text-white border-black':'bg-white border-black'}">Todas</button>`; html+=cats.filter(c=>c.id!='todas').map(c=>`<button onclick="filtrarCategoria('${c.id}')" class="px-4 py-2 rounded-full font-bold text-[11px] whitespace-nowrap border-2 ${categoriaFiltro==c.id?'bg-black text-white border-black':'bg-white border-black'}">${c.nombre}</button>`).join(''); let el=document.getElementById('filtrosCats'); if(el) el.innerHTML=html; let editHtml=cats.filter(c=>c.id!='todas').map(c=>`<div class="flex justify-between items-center bg-white p-2 rounded-xl border"><span class="text-[12px] font-bold">${c.nombre}</span><div class="flex gap-1"><button onclick="editarCategoria('${c.id}')" class="bg-blue-100 text-blue-600 px-2 py-1 rounded-full text-[10px]">✏️</button><button onclick="borrarCategoria('${c.id}')" class="bg-red-100 text-red-600 px-2 py-1 rounded-full text-[10px]">X</button></div></div>`).join(''); let ec=document.getElementById('listaCatsEdit'); if(ec) ec.innerHTML=editHtml||''; }
function filtrarCategoria(id){ categoriaFiltro=id; renderCategoriasVenta(); renderVenta(); }
function renderProdCategoriaSelect(){ let cats=getCategoriasVenta().filter(c=>c.id!='todas'); let sel=document.getElementById('prodCategoria'); if(!sel) return; sel.innerHTML=cats.map(c=>`<option value="${c.id}">${c.nombre}</option>`).join('')+'<option value="general">General</option>'; }

function addCliente(){ let nombre=document.getElementById('cliNombre').value.trim(); let tel=document.getElementById('cliTel').value.trim(); if(!nombre) return alert('Nombre'); let cli=getCli(); cli.push({id:Date.now().toString(),nombre,tel}); setItem('clientesV2',cli); document.getElementById('cliNombre').value=''; document.getElementById('cliTel').value=''; renderClientes(); }
function addClienteRapido(){ let nombre=document.getElementById('quickClienteNombre').value.trim(); let tel=document.getElementById('quickClienteTel').value.trim(); if(!nombre) return alert('Pon nombre'); let cli=getCli(); let nuevo={id:Date.now().toString(),nombre,tel}; cli.push(nuevo); setItem('clientesV2',cli); document.getElementById('quickClienteNombre').value=''; document.getElementById('quickClienteTel').value=''; renderClientes(); document.getElementById('selCliente').value=nuevo.id; actualizarClienteTicket(); }
function renderClientes(){
  let cli=getCli();
  let lista=document.getElementById('listaClientes');
  if(lista) lista.innerHTML=cli.map(c=>`<div class="bg-gray-50 p-3 rounded-xl border flex justify-between items-center"><div><b class="text-[13px]">${c.nombre}</b><br><span class="text-[11px] text-green-600">📲 ${c.tel||'sin tel'}</span></div><div class="flex gap-1"><button onclick="enviarWhatsAppDirecto('${c.tel}','Hola ${c.nombre}')" class="bg-[#25D366] text-white px-3 py-1 rounded-full text-[11px]">Whats</button><button onclick="let cl=getCli().filter(x=>x.id!='${c.id}'); setItem('clientesV2',cl); renderClientes();" class="text-red-400 px-2">X</button></div></div>`).join('')||'<p class="text-center text-gray-400 text-[11px] py-4">Sin clientes</p>';
  let sel=document.getElementById('selCliente');
  if(sel){
    let actual=sel.value;
    sel.innerHTML='<option value="">🏪 Mostrador (sin cliente)</option>'+cli.map(c=>`<option value="${c.id}" data-tel="${c.tel||''}" data-nombre="${c.nombre}">${c.nombre} - ${c.tel||''}</option>`).join('');
    if(actual) sel.value=actual;
  }
}
function actualizarClienteTicket(){ let sel=document.getElementById('selCliente'); if(!sel) return; let opt=sel.options[sel.selectedIndex]; let nombre=opt? (opt.getAttribute('data-nombre')||opt.text) : 'Mostrador'; let el=document.getElementById('cobroClienteNombre'); if(el) el.innerText=nombre; }

function addFijo(){ let n=document.getElementById('fijoNombre').value.trim(), m=parseFloat(document.getElementById('fijoMonto').value); if(!n||!m) return; let f=getFijos(); f.push({id:Date.now().toString(), nombre:n, monto:m}); setItem('gastosFijos',f); document.getElementById('fijoNombre').value=''; document.getElementById('fijoMonto').value=''; renderFijos(); calc(); }
function renderFijos(){ let f=getFijos(); let total=f.reduce((s,x)=>s+x.monto,0); let el=document.getElementById('totalFijos'); if(el) el.innerText=total.toFixed(0); let lotes=getLotes(); let lm=document.getElementById('lotesMes'); if(lm) lm.value=lotes; window._costoFijoPorLote=lotes>0? total/lotes : 0; let lf=document.getElementById('listaFijos'); if(lf) lf.innerHTML=f.map(x=>`<div class="flex justify-between bg-gray-50 p-3 rounded-xl border"><div><b class="text-[12px]">${x.nombre}</b><br><span class="text-[10px]">$${x.monto}/mes</span></div><button onclick="borrarFijo('${x.id}')" class="text-red-500 font-black">X</button></div>`).join('')||'<p class="text-[11px] text-gray-400 text-center">Agrega gastos</p>'; }
function borrarFijo(id){ let f=getFijos().filter(x=>x.id!=id); setItem('gastosFijos',f); renderFijos(); calc(); }
function showTab(t){ ['costos','vender','inventario','finanzas','clientes','config'].forEach(x=>{ let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hidden',x!=t); }); if(t=='costos'){ renderFijos(); renderInventario(); } if(t=='vender'){ renderCategoriasVenta(); renderVenta(); renderCarrito(); renderClientes(); } if(t=='inventario') renderInventarioMaster(); if(t=='clientes') renderClientes(); if(t=='finanzas') renderCalendario(); if(t=='config') cargarEmpresa(); actualizarFondo(); }
function setCrear(v){ document.getElementById('crear-menu').classList.toggle('hidden',v!='menu'); document.getElementById('crear-base').classList.toggle('hidden',v!='base'); document.getElementById('crear-producto').classList.toggle('hidden',v!='producto'); if(v=='menu'){ editId=null; renderFijos(); renderInventario(); } if(v=='base' &&!editId){ document.getElementById('insumos').innerHTML=''; document.getElementById('nombre').value=''; addInsumo({}); calc(); } if(v=='producto' &&!editId){ document.getElementById('basesSel').innerHTML=''; document.getElementById('nombreProd').value=''; renderProdCategoriaSelect(); addBase(); calc2(); } }
function cancelarEdicion(){ editId=null; setCrear('menu'); }
function previewFoto(i){ if(i.files&&i.files[0]){ let r=new FileReader(); r.onload=function(e){ fotoTemp=e.target.result; document.getElementById('fotoImg').src=fotoTemp; document.getElementById('fotoPreview').classList.remove('hidden'); }; r.readAsDataURL(i.files[0]); } }
function previewLogo(input){ if(input.files&&input.files[0]){ let reader=new FileReader(); reader.onload=function(e){ logoTemp=e.target.result; document.getElementById('logoPreview').src=logoTemp; document.getElementById('logoPreviewBox').classList.remove('hidden'); actualizarFondo(); actualizarVistaTicket(); }; reader.readAsDataURL(input.files[0]); } }
function quitarLogo(){ logoTemp=''; document.getElementById('logoPreviewBox').classList.add('hidden'); actualizarFondo(); actualizarVistaTicket(); }
function actualizarFondo(){ let emp=getEmp(); let logo=logoTemp||emp.logo||''; let mostrarFondo=document.getElementById('empMostrarFondo')?.checked?? emp.mostrarFondo; let op=parseInt(document.getElementById('empOpacidad')?.value || emp.opacidad || 8); let bg=document.getElementById('logoBg'); let header=document.getElementById('logoHeader'); if(logo && mostrarFondo){ bg.src=logo; bg.classList.remove('hidden'); bg.style.opacity=(op/100); } else { bg.classList.add('hidden'); } if(logo){ header.src=logo; header.classList.remove('hidden'); } else { header.classList.add('hidden'); } }
function cargarEmpresa(){ let emp=getEmp(); document.getElementById('empNombre').value=emp.nombre||''; document.getElementById('empDireccion').value=emp.direccion||''; document.getElementById('empCP').value=emp.cp||''; document.getElementById('empTel').value=emp.tel||''; document.getElementById('empRFC').value=emp.rfc||''; document.getElementById('empMensaje').value=emp.mensaje||''; document.getElementById('empMostrarLogo').checked=emp.mostrarLogo!==false; document.getElementById('empMostrarFondo').checked=emp.mostrarFondo!==false; document.getElementById('empOpacidad').value=emp.opacidad||8; document.getElementById('opacidadVal').innerText=(emp.opacidad||8)+'%'; logoTemp=emp.logo||''; if(logoTemp){ document.getElementById('logoPreview').src=logoTemp; document.getElementById('logoPreviewBox').classList.remove('hidden'); } actualizarFondo(); actualizarVistaTicket(); }
function guardarEmpresa(){ let emp={nombre:document.getElementById('empNombre').value.trim()||'Mi Negocio',direccion:document.getElementById('empDireccion').value.trim(),cp:document.getElementById('empCP').value.trim(),tel:document.getElementById('empTel').value.trim(),rfc:document.getElementById('empRFC').value.trim(),mensaje:document.getElementById('empMensaje').value.trim()||'¡Gracias!',mostrarLogo:document.getElementById('empMostrarLogo').checked,mostrarFondo:document.getElementById('empMostrarFondo').checked,opacidad:parseInt(document.getElementById('empOpacidad').value)||8,logo:logoTemp||getEmp().logo||''}; setItem('empresaConfig',emp); alert('✅ Guardada'); actualizarFondo(); actualizarVistaTicket(); }

function generarTicket(data){
  let emp=getEmp();
  let logoHtml=emp.mostrarLogo && emp.logo? `<div style="text-align:center;"><img src="${emp.logo}" style="display:block; margin:0 auto; max-width:90px;"></div>` : '';
  let fechaHora = data.fechaStr || getFechaLocal();
  let pagoTxt = data.metodoPago || metodoPagoSel || 'Efectivo';
  let html=`${logoHtml}<div style="text-align:center; border-bottom:1px dashed #000; padding-bottom:8px;"><b>${emp.nombre}</b><br><span style="font-size:9px">${emp.direccion||''} ${emp.tel||''}</span></div><div style="font-size:10px;">Fecha: ${fechaHora}<br>Cliente: ${data.cliente}<br>Pago: ${pagoTxt}<br>Vendedor: ${data.vendedor||currentUser}</div><div style="border-top:1px dashed #000; border-bottom:1px dashed #000; padding:6px 0; margin:6px 0;">${data.items.map(i=>`<div style="display:flex; justify-content:space-between;"><span>${i.nombre} x${i.qty}</span><span>$${(i.venta*i.qty).toFixed(2)}</span></div>`).join('')}</div><div style="display:flex; justify-content:space-between; font-weight:bold;"><span>TOTAL (${pagoTxt})</span><span>$${data.total.toFixed(2)}</span></div><div style="text-align:center; margin-top:12px; border-top:1px dashed #000; padding-top:8px;">${emp.mensaje}</div>`;
  document.getElementById('ticketContenido').innerHTML=html;
  return html;
}
function generarTextoWhatsApp(data){
  let emp=getEmp();
  let pagoTxt=data.metodoPago||'Efectivo';
  let iconoPago = pagoTxt=='Efectivo'?'💵':(pagoTxt=='Tarjeta'?'💳':'🏦');
  let lineas=[
    `*${emp.nombre}*`,
    `${emp.direccion||''} ${emp.tel||''}`.trim(),
    `-------------------------`,
    `Fecha: ${data.fechaStr}`,
    `Cliente: ${data.cliente}`,
    `${iconoPago} Pago: ${pagoTxt}`,
    `Vendedor: ${data.vendedor||currentUser}`,
    `-------------------------`,
  ...data.items.map(i=>`${i.nombre} x${i.qty} = $${(i.venta*i.qty).toFixed(2)}`),
    `-------------------------`,
    `*TOTAL (${pagoTxt}): $${data.total.toFixed(2)}*`,
    ``,
    `${emp.mensaje}`,
    `¡Gracias! 😊`
  ];
  return lineas.join('\\n');
}
function actualizarVistaTicket(){ generarTicket({fecha:new Date(),fechaStr:getFechaLocal(),items:[{nombre:'Alitas',qty:2,venta:57}],total:114,cliente:'Mostrador',vendedor:currentUser, metodoPago: metodoPagoSel}); }
function imprimirTicket(){ let contenido=document.getElementById('ticketContenido').innerHTML; let w=window.open('','','width=300,height=600'); w.document.write('<html><head><style>body{font-family:monospace; width:58mm; margin:0 auto; text-align:center;} img{display:block; margin:0 auto;}</style></head><body>'+contenido+'<script>window.onload=function(){window.print(); setTimeout(()=>window.close(),500);}<\\/script></body></html>'); w.document.close(); }
function enviarWhatsAppDirecto(tel,msg){ if(!tel){ tel=prompt('Numero WhatsApp'); if(!tel) return; } tel=tel.toString().replace(/\\D/g,''); if(tel.length==10) tel='52'+tel; let url=`https://wa.me/${tel}?text=${encodeURIComponent(msg||'Hola')}`; window.open(url,'_blank'); }
function enviarWhatsAppTicket(esPrueba){
  if(!ultimoTicket && esPrueba){ actualizarVistaTicket(); ultimoTicket={fechaStr:getFechaLocal(),items:[{nombre:'Alitas',qty:2,venta:57}],total:114,cliente:'Mostrador',vendedor:currentUser, metodoPago: metodoPagoSel}; }
  if(!ultimoTicket) return alert('No hay ticket');
  let sel=document.getElementById('selCliente'); let opt=sel? sel.options[sel.selectedIndex] : null; let tel=opt? opt.getAttribute('data-tel') : ''; if(esPrueba &&!tel){ tel=prompt('Numero WhatsApp para prueba'); } if(!tel){ let cliId=sel? sel.value : ''; let cli=getCli().find(c=>c.id==cliId); tel=cli? cli.tel : ''; } if(!tel){ tel=prompt('WhatsApp del cliente:'); if(!tel) return; } tel=tel.toString().replace(/\\D/g,''); if(tel.length==10) tel='52'+tel; let texto=generarTextoWhatsApp(ultimoTicket); window.open(`https://wa.me/${tel}?text=${encodeURIComponent(texto)}`,'_blank');
}
function probarTicket(){ guardarEmpresa(); actualizarVistaTicket(); imprimirTicket(); }

function addInventario(){ let n=document.getElementById('inv-nombre').value.trim(), p=parseFloat(document.getElementById('inv-precio').value), u=document.getElementById('inv-unidad').value; if(!n||!p) return; let inv=getInv(); inv.push({id:Date.now().toString(),nombre:n,precio:p,unidad:u}); setItem('inventarioMaestro',inv); document.getElementById('inv-nombre').value=''; document.getElementById('inv-precio').value=''; renderInventarioMaster(); }
function renderInventarioMaster(){ let inv=getInv(); let el=document.getElementById('listaInvMaster'); if(el) el.innerHTML=inv.map(it=>`<div class="flex gap-2 items-center bg-gray-50 p-3 rounded-xl border"><div class="flex-1"><b>${it.nombre}</b> $${it.precio}/${it.unidad}</div><button onclick="let inv=getInv().filter(x=>x.id!='${it.id}'); setItem('inventarioMaestro',inv); renderInventarioMaster();" class="text-red-400">X</button></div>`).join(''); }
function addInsumo(d={}){ let inv=getInv(); let opts=inv.map(it=>`<option value="${it.id}" ${d.invId==it.id?'selected':''}>${it.nombre} $${it.precio}/${it.unidad}</option>`).join(''); let div=document.createElement('div'); div.className='bg-[#FFF8F0] p-3 rounded-[16px] border-2 border-orange-100'; div.innerHTML=`<select class="in-n w-full bg-white border-2 border-black p-2 rounded-xl font-bold text-[13px]" onchange="calc()"><option value="">-- Ingrediente --</option>${opts}</select><div class="grid grid-cols-5 gap-2 mt-2"><input type="number" value="${d.cu||''}" placeholder="Uso" class="in-cu col-span-2 border-2 border-black p-3 rounded-xl font-bold text-[13px]" oninput="calc()"><select class="in-uu col-span-3 border-2 border-black p-3 rounded-xl font-bold text-[12px]" onchange="calc()"><option value="kg">kg</option><option value="g">g</option><option value="mg">mg</option><option value="L">L</option><option value="ml">ml</option><option value="pza">pza</option><option value="m">m</option><option value="cm">cm</option><option value="lb">lb</option><option value="oz">oz</option></select></div><div class="text-right font-black text-[12px] mt-1">Costo: $<span class="in-sub">0.00</span></div><button onclick="this.parentElement.remove();calc()" class="w-full mt-2 text-[10px] text-red-400">Quitar</button>`; document.getElementById('insumos').appendChild(div); if(d.uu) div.querySelector('.in-uu').value=d.uu; }
function calc(){ try{ let tot=0; document.querySelectorAll('#insumos > div').forEach(row=>{ let invId=row.querySelector('.in-n')?.value; let it=getInv().find(x=>x.id==invId); let cu=parseFloat(row.querySelector('.in-cu').value)||0; let uu=row.querySelector('.in-uu')?.value||'g'; let baseCost=0; if(it && cu){ let cantConvertida=convertir(cu, uu, it.unidad); baseCost=cantConvertida * it.precio; } row.querySelector('.in-sub').innerText=baseCost.toFixed(2); tot+=baseCost; }); document.getElementById('c-ing').innerText=tot.toFixed(2); let fijos=window._costoFijoPorLote||0; document.getElementById('c-fijos').innerText=fijos.toFixed(2); let total=tot+fijos; document.getElementById('costo').innerText=total.toFixed(2); let m=parseFloat(document.getElementById('margen').value)||0; let vm=document.getElementById('ventaManual').value; document.getElementById('venta').innerText= vm? parseFloat(vm).toFixed(2) : (total*(1+m/100)).toFixed(2); }catch(e){} }
function addBase(d={}){ let bases=getProd(); let opts=bases.map(b=>`<option value="${b.id}" ${d.id==b.id?'selected':''}>${b.nombre} $${b.costo.toFixed(2)}</option>`).join(''); let div=document.createElement('div'); div.className='bg-white border-2 border-black rounded-xl p-3 flex gap-2 items-center'; div.innerHTML=`<select class="b-sel flex-1 border-2 p-2 rounded-lg font-bold text-[12px]" onchange="calc2()">${opts}</select><button onclick="this.parentElement.remove();calc2()" class="text-red-400 font-black px-2">X</button>`; document.getElementById('basesSel').appendChild(div); }
function calc2(){ let tot=0; document.querySelectorAll('#basesSel > div').forEach(r=>{ let id=r.querySelector('.b-sel').value; let b=getProd().find(x=>x.id==id); if(b) tot+=b.costo; }); document.getElementById('c-ing2').innerText=tot.toFixed(2); let m=parseFloat(document.getElementById('margen2').value)||0; let vm=document.getElementById('ventaManual2').value; document.getElementById('venta2').innerText= vm? parseFloat(vm).toFixed(2) : (tot*(1+m/100)).toFixed(2); }
function guardarProd(tipo){ let isBase=tipo=='recetario'; let nomEl=isBase?document.getElementById('nombre'):document.getElementById('nombreProd'); let nom=nomEl.value.trim(); if(!nom) return alert('Pon nombre'); let costo=parseFloat((isBase?document.getElementById('costo'):document.getElementById('c-ing2')).innerText)||0; let venta=parseFloat((isBase?document.getElementById('venta'):document.getElementById('venta2')).innerText)||0; let catId=isBase?'base':(document.getElementById('prodCategoria')?.value||'general'); let ps=getProd(); let receta=[]; if(isBase){ document.querySelectorAll('#insumos > div').forEach(row=>{ let invId=row.querySelector('.in-n')?.value; let cu=row.querySelector('.in-cu')?.value; let uu=row.querySelector('.in-uu')?.value; if(invId && cu) receta.push({invId, cu:parseFloat(cu), uu}); }); } else { document.querySelectorAll('#basesSel > div').forEach(row=>{ let id=row.querySelector('.b-sel')?.value; if(id) receta.push({baseId:id}); }); } let margen=parseFloat((isBase?document.getElementById('margen'):document.getElementById('margen2'))?.value)||50; if(editId){ let idx=ps.findIndex(p=>p.id==editId); if(idx>=0){ ps[idx].nombre=nom; ps[idx].costo=costo; ps[idx].venta=venta; ps[idx].categoria=catId; ps[idx].receta=receta; ps[idx].margen=margen; if(fotoTemp) ps[idx].foto=fotoTemp; } } else { ps.push({id:Date.now(),nombre:nom,costo,venta,foto:fotoTemp,categoria:catId,receta,margen,esBase:isBase}); } setItem('productosV2',ps); alert(editId?'✅ Actualizado':'✅ Guardado'); fotoTemp=''; editId=null; renderInventario(); setCrear('menu'); renderVenta(); }
function editarProd(id){ let p=getProd().find(x=>x.id==id); if(!p) return; editId=id; if(p.esBase){ document.getElementById('crear-menu').classList.add('hidden'); document.getElementById('crear-base').classList.remove('hidden'); document.getElementById('crear-producto').classList.add('hidden'); document.getElementById('nombre').value=p.nombre; document.getElementById('insumos').innerHTML=''; if(p.receta && p.receta.length){ p.receta.forEach(r=> addInsumo({invId:r.invId, cu:r.cu, uu:r.uu})); } else { addInsumo({}); } calc(); } else { document.getElementById('crear-menu').classList.add('hidden'); document.getElementById('crear-base').classList.add('hidden'); document.getElementById('crear-producto').classList.remove('hidden'); document.getElementById('nombreProd').value=p.nombre; renderProdCategoriaSelect(); document.getElementById('prodCategoria').value=p.categoria||'general'; document.getElementById('basesSel').innerHTML=''; if(p.receta && p.receta.length){ p.receta.forEach(r=> addBase({id:r.baseId})); } else { addBase(); } if(p.foto){ fotoTemp=p.foto; document.getElementById('fotoImg').src=fotoTemp; document.getElementById('fotoPreview').classList.remove('hidden'); } calc2(); } }
function renderInventario(){ let ps=getProd(); let el=document.getElementById('listaInv'); if(!el) return; el.innerHTML=ps.map(p=>{ let catNombre=getCategoriasVenta().find(c=>c.id==p.categoria)?.nombre||p.categoria||'General'; if(p.categoria=='base') catNombre='BASE'; let tipoBadge=p.esBase? '<span class="bg-orange-100 text-orange-700 text-[8px] px-2 py-0.5 rounded-full font-black">BASE</span>' : `<span class="bg-blue-100 text-blue-700 text-[8px] px-2 py-0.5 rounded-full font-black">${catNombre}</span>`; return `<div class="bg-white p-3 rounded-2xl flex gap-2 shadow-sm mt-3 border items-center"><div class="flex-1"><div class="flex gap-1 items-center">${tipoBadge}</div><b class="text-[13px]">${p.nombre}</b><br><span class="text-[11px]">$${p.costo.toFixed(2)} → $${p.venta.toFixed(2)}</span></div><div class="flex flex-col gap-1"><button onclick="editarProd(${p.id})" class="bg-blue-500 text-white w-8 h-8 rounded-full text-[12px]">✏️</button><button onclick="let pr=getProd().filter(x=>x.id!=${p.id}); setItem('productosV2',pr); renderInventario(); renderVenta();" class="bg-red-100 text-red-500 w-8 h-8 rounded-full font-black">X</button></div></div>`; }).join('')||'<p class="text-center text-gray-400 py-4 text-[11px]">Sin recetas</p>'; }
function renderVenta(){ let ps=getProd().filter(p=>!p.esBase); let cats=getCategoriasVenta(); if(categoriaFiltro!='todas') ps=ps.filter(p=>p.categoria==categoriaFiltro); let cont=document.getElementById('listaVenta'); if(!cont) return; if(!ps.length){ cont.innerHTML='<p class="col-span-2 text-center text-gray-400 text-[12px] py-10">Sin productos</p>'; return; } cont.innerHTML=ps.map(p=>`<div class="bg-white rounded-2xl shadow-sm border p-3"><div class="flex justify-between"><div class="text-[8px] bg-black text-white px-2 py-0.5 rounded-full inline-block mb-1">${cats.find(c=>c.id==p.categoria)?.nombre||p.categoria||'General'}</div><button onclick="editarProd(${p.id})" class="text-[10px] bg-gray-100 px-2 rounded-full">✏️</button></div><b class="text-[13px] block mt-1">${p.nombre}</b><p class="text-green-600 font-black">$${p.venta.toFixed(2)}</p><button onclick="addCart(${p.id})" class="w-full mt-2 bg-black text-white py-2 rounded-xl text-[11px]">Agregar</button></div>`).join(''); }
function addCart(id){ let p=getProd().find(x=>x.id==id); let ex=carrito.find(x=>x.id==id); if(ex) ex.qty++; else carrito.push({...p,qty:1}); renderCarrito(); }
function renderCarrito(){ if(!carrito.length){ document.getElementById('ticket').innerHTML='Vacío'; document.getElementById('c-total').innerText='0'; return; } let t=0,h=''; carrito.forEach((x,idx)=>{ t+=x.venta*x.qty; h+=`<div class="flex justify-between bg-gray-50 p-2 rounded-xl"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)} <button onclick="carrito.splice(${idx},1); renderCarrito();" class="text-red-500">X</button></span></div>`; }); document.getElementById('ticket').innerHTML=h; document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('cobroTotal').innerText=t.toFixed(0); }
function abrirCobro(){ if(!carrito.length) return alert('Vacío'); actualizarClienteTicket(); document.getElementById('cobroHora').innerText=getFechaLocal(); setMetodoPago('Efectivo'); document.getElementById('modalCobro').classList.remove('hidden'); }
function cerrarCobro(){ document.getElementById('modalCobro').classList.add('hidden'); }
function calcCambio(){ let tot=parseFloat(document.getElementById('c-total').innerText)||0; let rec=parseFloat(document.getElementById('pagoRecibido').value)||0; document.getElementById('cambio').innerText=(rec-tot>0?rec-tot:0).toFixed(2); }

function confirmarCobro(tipo){
  let facts=getFacts();
  let fechaStr=getFechaLocal();
  let fechaSolo=getFechaSoloLocal();
  let total=parseFloat(document.getElementById('c-total').innerText)||0;
  let sel=document.getElementById('selCliente');
  let opt=sel.options[sel.selectedIndex];
  let clienteNombre=opt? (opt.getAttribute('data-nombre')||opt.text) : 'Mostrador';
  let clienteTel=opt? opt.getAttribute('data-tel') : '';
  let clienteId=sel.value;
  let metodo=document.getElementById('metodoPago').value||'Efectivo';
  facts.push({id:Date.now(),concepto:'Venta: '+carrito.map(c=>c.nombre+' x'+c.qty).join(', ')+' | Cliente: '+clienteNombre+' | Pago: '+metodo,monto:total,fecha:fechaSolo,fechaHora:fechaStr,tipo:'entrada',vendedor:currentUser||'dueño',clienteId,clienteNombre,clienteTel,metodoPago:metodo});
  setItem('facturas',facts);
  ultimoTicket={fecha:new Date(),fechaStr:fechaStr,items:[...carrito],total,cliente:clienteNombre,clienteTel:clienteTel,vendedor:currentUser, metodoPago:metodo};
  generarTicket(ultimoTicket);
  cerrarCobro();
  if(tipo=='print'){ imprimirTicket(); }
  else if(tipo=='whatsapp'){
    let tel=clienteTel;
    if(!tel || tel==''){ tel=prompt('WhatsApp del cliente para enviar ticket:'); }
    if(tel){ tel=tel.toString().replace(/\\D/g,''); if(tel.length==10) tel='52'+tel; let texto=generarTextoWhatsApp(ultimoTicket); window.open(`https://wa.me/${tel}?text=${encodeURIComponent(texto)}`,'_blank'); }
  }
  carrito=[]; renderCarrito(); renderCalendario(); renderClientes();
}

function openGasto(){ document.getElementById('modalGasto').classList.remove('hidden'); }
function cerrarGasto(){ document.getElementById('modalGasto').classList.add('hidden'); }
function guardarGasto(){ let c=document.getElementById('g-concepto').value.trim(), m=parseFloat(document.getElementById('g-monto').value), t=document.getElementById('g-tipo').value; if(!c||!m) return; let f=getFacts(); f.push({id:Date.now(),concepto:c,monto:m,fecha:getFechaSoloLocal(),fechaHora:getFechaLocal(),tipo:t,vendedor:currentUser, metodoPago:'Efectivo'}); setItem('facturas',f); document.getElementById('g-concepto').value=''; document.getElementById('g-monto').value=''; cerrarGasto(); renderCalendario(); }

function setVistaCal(v){ vistaCal=v; ['dia','semana','mes','ano'].forEach(x=>{ let b=document.getElementById('vc-'+x); if(b) b.className='flex-1 py-2 rounded-lg font-bold text-[11px] '+(x==v?'bg-white text-black font-black':'bg-transparent text-white/60'); }); renderCalendario(); }
function moverCal(dir){ if(vistaCal=='mes'||vistaCal=='dia'){ fechaVista.setMonth(fechaVista.getMonth()+dir); } else if(vistaCal=='ano'){ fechaVista.setFullYear(fechaVista.getFullYear()+dir); } else { fechaVista.setDate(fechaVista.getDate()+(dir*7)); } renderCalendario(); }
function seleccionarDia(f){ fechaSel=f; renderCalendario(); }
function renderCalendario(){
  let facts=getFacts(); let titulo=document.getElementById('calTitulo'); let grid=document.getElementById('calGrid'); let sem=document.getElementById('calSemana'); let ano=document.getElementById('calAno');
  if(!titulo) return;
  if(vistaCal=='mes'||vistaCal=='dia'){
    grid.classList.remove('hidden'); sem.classList.add('hidden'); ano.classList.add('hidden');
    let y=fechaVista.getFullYear(), m=fechaVista.getMonth();
    titulo.innerText=fechaVista.toLocaleDateString('es-MX',{month:'long',year:'numeric'});
    let primerDia=new Date(y,m,1).getDay(); let diasMes=new Date(y,m+1,0).getDate();
    let html='<div class="grid grid-cols-7 gap-1 text-center text-[10px] font-bold text-gray-400"><div>D</div><div>L</div><div>M</div><div>M</div><div>J</div><div>V</div><div>S</div></div><div class="grid grid-cols-7 gap-1 mt-2">';
    for(let i=0;i<primerDia;i++) html+='<div></div>';
    for(let d=1;d<=diasMes;d++){
      let fechaStr=`${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
      let diaFacts=facts.filter(f=>f.fecha==fechaStr);
      let ent=diaFacts.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0);
      let sal=diaFacts.filter(f=>f.tipo=='salida').reduce((s,f)=>s+f.monto,0);
      let tiene=diaFacts.length>0; let hoy=getFechaSoloLocal(); let esHoy=fechaStr==hoy; let esSel=fechaStr==fechaSel;
      html+=`<button onclick="seleccionarDia('${fechaStr}')" class="aspect-square rounded-xl p-1 flex flex-col items-center justify-center border-2 ${esSel?'bg-black text-white border-black':'bg-gray-50 border-transparent'} ${esHoy&&!esSel?'border-black':''}"><span class="font-black text-[13px]">${d}</span>${tiene?`<span class="text-[8px] font-bold ${esSel?'text-green-300':(ent>sal?'text-green-600':'text-red-500')}">$${(ent-sal).toFixed(0)}</span>`:''}</button>`;
    }
    html+='</div>'; grid.innerHTML=html;
    let mesFacts=facts.filter(f=>{ let fd=new Date(f.fecha+'T12:00:00'); return fd.getMonth()==m && fd.getFullYear()==y; });
    let entMes=mesFacts.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0); let salMes=mesFacts.filter(f=>f.tipo=='salida').reduce((s,f)=>s+f.monto,0);
    document.getElementById('fin-balance').innerText='$'+(entMes-salMes).toFixed(0); document.getElementById('fin-entradas').innerText='$'+entMes.toFixed(0); document.getElementById('fin-salidas').innerText='$'+salMes.toFixed(0);
    renderDesgloseDia(fechaSel);
  } else if(vistaCal=='semana'){
    grid.classList.add('hidden'); sem.classList.remove('hidden'); ano.classList.add('hidden');
    let inicio=new Date(fechaVista); inicio.setDate(fechaVista.getDate()-inicio.getDay()); let fin=new Date(inicio); fin.setDate(inicio.getDate()+6);
    titulo.innerText=`${inicio.toLocaleDateString('es-MX')} - ${fin.toLocaleDateString('es-MX')}`;
    let html='<div class="space-y-2">'; let maxVal=1; let datos=[];
    for(let i=0;i<7;i++){ let d=new Date(inicio); d.setDate(inicio.getDate()+i); let fechaStr=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); let diaFacts=facts.filter(f=>f.fecha==fechaStr); let ent=diaFacts.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0); let sal=diaFacts.filter(f=>f.tipo=='salida').reduce((s,f)=>s+f.monto,0); datos.push({fechaStr,dia:d.toLocaleDateString('es-MX',{weekday:'short',day:'numeric'}),ent,sal}); if(ent>maxVal) maxVal=ent; }
    datos.forEach(o=>{ let h=Math.max(8,(o.ent/maxVal)*100); html+=`<div class="flex items-center gap-2"><span class="w-14 text-[10px] font-bold">${o.dia}</span><div class="flex-1 bg-gray-100 rounded-full h-8 relative overflow-hidden"><div class="bg-green-500 h-full rounded-full" style="width:${h}%"></div><span class="absolute inset-0 flex items-center px-2 text-[10px] font-black">$${o.ent.toFixed(0)} / $${o.sal.toFixed(0)}</span></div><button onclick="seleccionarDia('${o.fechaStr}')" class="text-[10px] bg-black text-white px-2 py-1 rounded-full">Ver</button></div>`; });
    let totEnt=datos.reduce((s,o)=>s+o.ent,0), totSal=datos.reduce((s,o)=>s+o.sal,0);
    document.getElementById('fin-balance').innerText='$'+(totEnt-totSal).toFixed(0); document.getElementById('fin-entradas').innerText='$'+totEnt.toFixed(0); document.getElementById('fin-salidas').innerText='$'+totSal.toFixed(0);
    html+='</div>'; sem.innerHTML=html;
  } else if(vistaCal=='ano'){
    grid.classList.add('hidden'); sem.classList.add('hidden'); ano.classList.remove('hidden');
    let y=fechaVista.getFullYear(); titulo.innerText=y; let html='';
    for(let m=0;m<12;m++){ let mesFacts=facts.filter(f=>{ let fd=new Date(f.fecha+'T12:00:00'); return fd.getMonth()==m && fd.getFullYear()==y; }); let ent=mesFacts.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0); let sal=mesFacts.filter(f=>f.tipo=='salida').reduce((s,f)=>s+f.monto,0); let nombre=new Date(y,m,1).toLocaleDateString('es-MX',{month:'short'}); html+=`<button onclick="fechaVista=new Date(${y},${m},1); setVistaCal('mes')" class="bg-gray-50 border-2 p-3 rounded-2xl text-left ${ent>0?'border-green-200 bg-green-50':''}"><p class="font-black text-[12px] uppercase">${nombre}</p><p class="text-[10px] text-green-600 font-bold">$${ent.toFixed(0)}</p><p class="text-[9px] text-red-400">-$${sal.toFixed(0)}</p><p class="text-[10px] font-black mt-1">G: $${(ent-sal).toFixed(0)}</p></button>`; }
    ano.innerHTML=html;
    let anoFacts=facts.filter(f=> new Date(f.fecha+'T12:00:00').getFullYear()==y); let entAno=anoFacts.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0); let salAno=anoFacts.filter(f=>f.tipo=='salida').reduce((s,f)=>s+f.monto,0);
    document.getElementById('fin-balance').innerText='$'+(entAno-salAno).toFixed(0); document.getElementById('fin-entradas').innerText='$'+entAno.toFixed(0); document.getElementById('fin-salidas').innerText='$'+salAno.toFixed(0);
  }
}
function renderDesgloseDia(fechaStr){
  let facts=getFacts().filter(f=>f.fecha==fechaStr);
  let fechaLegible=new Date(fechaStr+'T12:00:00').toLocaleDateString('es-MX',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
  document.getElementById('fechaSelLabel').innerText=fechaLegible;
  let ent=facts.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0); let sal=facts.filter(f=>f.tipo=='salida').reduce((s,f)=>s+f.monto,0);
  document.getElementById('diaEntradas').innerText='$'+ent.toFixed(0); document.getElementById('diaSalidas').innerText='$'+sal.toFixed(0); document.getElementById('diaGanancia').innerText='$'+(ent-sal).toFixed(0);
  document.getElementById('diaNumEntradas').innerText=facts.filter(f=>f.tipo=='entrada').length+' ventas';
  document.getElementById('flu-lista').innerHTML=facts.slice().reverse().map(f=>`<div class="flex justify-between items-center p-3 bg-gray-50 rounded-xl border"><div><b class="text-[12px]">${f.concepto}</b><br><span class="text-[10px] text-gray-500">${f.fechaHora||f.fecha} • ${f.metodoPago||'Efectivo'} • 👤 ${f.vendedor||'dueño'} • ${f.clienteNombre||''}</span></div><span class="${f.tipo=='entrada'?'text-green-600':'text-red-500'} font-black">$${f.monto.toFixed(0)}</span></div>`).join('')||'<p class="text-center text-gray-400 text-[12px] py-4">Sin movimientos</p>';
}
</script>
</body></html>
    """
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
