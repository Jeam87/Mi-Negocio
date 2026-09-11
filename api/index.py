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
def manifest():
 return jsonify({"name":"Mi Negocio 11.5","short_name":"Mi Negocio","start_url":"/","display":"standalone","icons":[{"src":"/logo.png","sizes":"512x512","type":"image/png"},{"src":"/api/logo.png","sizes":"512x512","type":"image/png"}]})

@app.route('/logo.png')
@app.route('/api/logo.png')
def logo_file():
 posibles = [
  'logo.png',
  'api/logo.png',
  os.path.join(os.path.dirname(__file__), 'logo.png'),
  os.path.join(os.getcwd(), 'logo.png'),
  os.path.join(os.getcwd(), 'api', 'logo.png'),
  '/tmp/logo.png'
 ]
 for ruta in posibles:
  try:
   if os.path.exists(ruta):
    return send_file(ruta, mimetype='image/png')
  except: pass
 return "",204

@app.route('/api/register', methods=['POST'])
def api_register():
 d=request.json; email=d.get('email','').lower().strip(); pwd=d.get('password','')
 users=load_users()
 if email in users: return jsonify({"ok":False,"msg":"Ya existe"}),400
 users[email]={"password":pwd,"negocio_id":email,"rol":"owner"}; save_users(users)
 with open(get_user_file(email),'w') as f: json.dump({},f)
 return jsonify({"ok":True})
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
 data=json.load(open(get_user_file(users[email]['negocio_id']))) if os.path.exists(get_user_file(users[email]['negocio_id'])) else {}
 return jsonify({"ok":True,"data":data})
@app.route('/api/save', methods=['POST'])
def api_save():
 d=request.json; email=d.get('email','').lower().strip(); data=d.get('data',{})
 users=load_users()
 if email not in users: return jsonify({"ok":False}),404
 with open(get_user_file(users[email]['negocio_id']),'w') as f: json.dump(data,f)
 return jsonify({"ok":True})
@app.route('/')
@app.route('/api')
@app.route('/api/')
def home():
 return """<!DOCTYPE html><html><head><link rel="manifest" href="/manifest.json"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Negocio 11.5</title><script src="https://tailwindcss.com"></script><link rel="stylesheet" href="https://cloudflare.com"><style>input,select,textarea{color:#000!important;background:#fff!important}.logo-watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:650px;height:650px;pointer-events:none;z-index:0;opacity:0.18;object-fit:contain;}#appContent{position:relative;z-index:1;}#splashInicio{position:fixed;inset:0;background:white;z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center}#splashInicio img{width:85vw;max-width:380px;height:auto;animation:pop 0.8s ease}@keyframes pop{0%{transform:scale(0.5);opacity:0}100%{transform:scale(1);opacity:1}}button{transition:background-color 0.1s ease, transform 0.1s ease;}button:active{transform:scale(0.95);filter:brightness(0.7);}</style></head><body class="bg-[#FFF8F0] min-h-screen"><div id="splashInicio"><img src="/logo.png" onerror="this.src='/api/logo.png'"><p style="margin-top:20px;font-weight:900;font-size:22px">Mi Negocio 11.5</p><p style="font-size:12px;color:#888">Cargando...</p></div><script>setTimeout(()=>{let s=document.getElementById('splashInicio'); if(s) s.style.display='none'},1800)</script><div class="max-w-md mx-auto pb-[140px] relative"><img id="logoBg" class="logo-watermark hidden"><div id="appContent">
<div id="loginScreen" class="fixed inset-0 bg-[#FFF8F0] z-[100] flex flex-col items-center justify-center p-6"><h1 class="font-black text-[24px]">Mi Negocio 11.5</h1><p class="text-[11px] text-gray-500">Logo grande + proveedores completos</p><div class="bg-white w-full rounded-[28px] p-5 shadow-xl border-2 border-black mt-6"><input id="loginEmail" type="email" placeholder="Correo" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[14px]"><input id="loginPass" type="password" placeholder="Contraseña" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[14px] mt-3"><button onclick="hacerLogin()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">ENTRAR</button><button onclick="hacerRegistro()" class="w-full mt-2 bg-white border-2 border-black py-3 rounded-2xl font-bold text-[13px]">REGISTRARME</button><p id="loginMsg" class="hidden mt-3 text-[11px] font-bold text-center p-2 rounded-xl"></p></div></div>
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><div class="flex items-center gap-3"><img id="logoHeader" class="w-20 h-20 rounded-full object-cover border-[4px] border-black hidden shadow-xl" onerror="this.src='/api/logo.png'"><div><h1 class="font-black text-[16px]">Mi Negocio 11.5</h1><p id="userLabel" class="text-[10px] text-gray-500"></p><p id="horaActual" class="text-[10px] font-black text-green-600"></p></div></div><div class="flex gap-2"><button onclick="showTab('config')" class="text-[10px] bg-black text-white px-3 py-2 rounded-full">Config</button><button onclick="cerrarSesion()" class="text-[10px] bg-red-100 text-red-600 px-2 py-1 rounded-full">Salir</button></div></div>

<div id="tab-vender" class="p-3 hidden">
<div class="bg-white rounded-[20px] p-3 shadow-sm mb-3"><div class="flex justify-between items-center"><h3 class="font-black text-[13px]">Categorías</h3><button onclick="document.getElementById('boxNuevaCat').classList.toggle('hidden')" class="text-[10px] bg-black text-white px-3 py-1 rounded-full">+ Nueva</button></div><div id="filtrosCats" class="flex gap-2 mt-3 overflow-x-auto pb-2"></div><div id="boxNuevaCat" class="hidden mt-3 bg-amber-50 border-2 p-3 rounded-xl"><div id="listaCatsEdit" class="space-y-2 mb-3"></div><div class="grid grid-cols-5 gap-2"><input id="nuevaCatNombre" placeholder="Ej: Alitas" class="col-span-4 border-2 border-black p-2 rounded-xl text-[12px] font-bold"><button onclick="addCategoriaVenta()" class="bg-black text-white rounded-xl font-black">+</button></div></div></div>
<div id="alertaStock" class="hidden bg-red-100 border-2 border-red-300 rounded-xl p-2 mb-3 text-[11px] font-bold text-red-700"></div>
<div id="listaVenta" class="grid grid-cols-2 gap-3"></div>
<div class="mt-6 bg-white rounded-[28px] p-4 shadow-xl border-2 border-black">
<div class="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-2 mb-3"><p class="text-[10px] font-black">👤 Cliente</p><select id="selCliente" class="w-full border-2 border-black p-3 rounded-xl text-[12px] font-bold mt-2" onchange="actualizarClienteTicket()"></select><div class="flex gap-2 mt-2"><input id="quickClienteNombre" placeholder="Nombre" class="flex-1 border-2 border-black p-2 rounded-xl text-[11px] font-bold"><input id="quickClienteTel" placeholder="WhatsApp" class="flex-1 border-2 border-black p-2 rounded-xl text-[11px] font-bold"><button onclick="addClienteRapido()" class="bg-black text-white px-3 rounded-xl font-black text-[12px]">+</button></div></div>
<div id="ticket" class="space-y-2">Vacío</div>
<div class="mt-3 bg-gray-50 p-2 rounded-xl flex gap-2 items-center"><span class="text-[11px] font-black">Descuento %</span><input id="descPorc" type="number" value="0" class="w-16 border-2 border-black p-1 rounded-xl text-center font-black" oninput="renderCarrito()"><span class="text-[10px]">Motivo</span><input id="descMotivo" placeholder="Promo" class="flex-1 border-2 border-black p-1 rounded-xl text-[10px]"></div>
<div class="flex justify-between font-black text-[20px] mt-3 border-t-2 pt-3">Total $ <span id="c-total">0</span></div>
<div class="grid grid-cols-2 gap-2 mt-3"><button onclick="enviarPresupuestoWhatsApp()" class="bg-blue-600 text-white py-3 rounded-2xl font-black text-[12px]">📋 PRESUPUESTO</button><button onclick="abrirCobro()" class="bg-black text-white py-3 rounded-2xl font-black text-[13px]">COBRAR</button></div></div></div>

<div id="tab-costos" class="p-3"><div id="crear-menu" class="space-y-4">
