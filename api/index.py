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
 return jsonify({"name":"Mi Negocio 11.5","short_name":"Mi Negocio","start_url":"/","display":"standalone","icons":[{"src":"/logo.png","sizes":"512x512","type":"image/png"},{"src":"/api/logo.png","siz[...]

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
 if email in users: return jsonify({"ok":false,"msg":"Ya existe"}),400
 users[email]={"password":pwd,"negocio_id":email,"rol":"owner"}; save_users(users)
 with open(get_user_file(email),'w') as f: json.dump({},f)
 return jsonify({"ok":true})
@app.route('/api/login', methods=['POST'])
def api_login():
 d=request.json; email=d.get('email','').lower().strip(); pwd=d.get('password','')
 users=load_users()
 if email not in users or users[email]['password']!=pwd: return jsonify({"ok":false,"msg":"Error"}),401
 return jsonify({"ok":true,"email":email,"negocio_id":users[email]['negocio_id'],"rol":users[email]['rol']})
@app.route('/api/invite', methods=['POST'])
def api_invite():
 d=request.json; owner=d.get('owner_email','').lower().strip(); owner_pwd=d.get('owner_password',''); colab=d.get('colab_email','').lower().strip(); colab_pwd=d.get('colab_password','') or '1234'
 users=load_users()
 if owner not in users or users[owner]['password']!=owner_pwd: return jsonify({"ok":false,"msg":"No autorizado"}),403
 users[colab]={"password":colab_pwd,"negocio_id":users[owner]['negocio_id'],"rol":"colab"}; save_users(users)
 return jsonify({"ok":true})
@app.route('/api/load', methods=['GET'])
def api_load():
 email=request.args.get('email','').lower().strip(); users=load_users()
 if email not in users: return jsonify({"ok":false}),404
 data=json.load(open(get_user_file(users[email]['negocio_id']))) if os.path.exists(get_user_file(users[email]['negocio_id'])) else {}
 return jsonify({"ok":true,"data":data})
@app.route('/api/save', methods=['POST'])
def api_save():
 d=request.json; email=d.get('email','').lower().strip(); data=d.get('data',{})
 users=load_users()
 if email not in users: return jsonify({"ok":false}),404
 with open(get_user_file(users[email]['negocio_id']),'w') as f: json.dump(data,f)
 return jsonify({"ok":true})
@app.route('/')
@app.route('/api')
@app.route('/api/')
def home():
 return """<!DOCTYPE html><html><head><link rel="manifest" href="/manifest.json"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Negocio 11.5</title>[...]
<div id="loginScreen" class="fixed inset-0 bg-[#FFF8F0] z-[100] flex flex-col items-center justify-center p-6"><h1 class="font-black text-[24px]">Mi Negocio 11.5</h1><p class="text-[11px] text-gray-50[...]
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><div class="flex items-center gap-3"><img id="logoHeader" class="w-20 h-20 rounded-full object-cover border-[4px[...]

<div id="tab-vender" class="p-3 hidden">
<div class="bg-white rounded-[20px] p-3 shadow-sm mb-3"><div class="flex justify-between items-center"><h3 class="font-black text-[13px]">Categorías</h3><button onclick="document.getElementById('boxN[...]
<div id="alertaStock" class="hidden bg-red-100 border-2 border-red-300 rounded-xl p-2 mb-3 text-[11px] font-bold text-red-700"></div>
<div id="listaVenta" class="grid grid-cols-2 gap-3"></div>
<div class="mt-6 bg-white rounded-[28px] p-4 shadow-xl border-2 border-black">
<div class="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-2 mb-3"><p class="text-[10px] font-black">👤 Cliente</p><select id="selCliente" class="w-full border-2 border-black p-3 rounded-xl te[...]
<div id="ticket" class="space-y-2">Vacío</div>
<div class="mt-3 bg-gray-50 p-2 rounded-xl flex gap-2 items-center"><span class="text-[11px] font-black">Descuento %</span><input id="descPorc" type="number" value="0" class="w-16 border-2 border-blac[...]
<div class="flex justify-between font-black text-[20px] mt-3 border-t-2 pt-3">Total $ <span id="c-total">0</span></div><div class="grid grid-cols-2 gap-2 mt-3"><button onclick="abrirCobro()" class="bg[...]

<div id="tab-costos" class="p-3"><div id="crear-menu" class="space-y-4">
<div class="bg-white rounded-[28px] p-5 shadow-sm border-2 border-black"><h2 class="font-black">💰 Gastos Fijos</h2><div class="grid grid-cols-5 gap-2 mt-3"><input id="fijoNombre" placeholder="Renta[...]
<div class="bg-white rounded-[28px] p-5 shadow-sm text-center"><button onclick="setCrear('base')" class="w-full bg-[#FFF8F0] border-2 border-black rounded-[20px] p-5 font-black">1. Crear BASE</button>[...]
<div class="bg-white rounded-[20px] p-4"><h3 class="font-black text-[14px] mb-2">Mis recetas</h3><div id="listaInv"></div></div>
</div>
<div id="crear-base" class="hidden"><button onclick="cancelarEdicion()" class="mb-3 font-bold">← Volver</button><div class="bg-white rounded-[28px] p-4 shadow-sm"><h2 class="font-black">BASE</h2><in[...]
<div id="crear-producto" class="hidden"><button onclick="cancelarEdicion()" class="mb-3 font-bold">← Volver</button><div class="bg-white rounded-[28px] p-4"><h2 class="font-black">Producto</h2><inpu[...]

<div id="tab-config" class="p-3 hidden"><div class="bg-white rounded-[28px] p-5 shadow-sm"><h2 class="font-black">⚙️ Configuración y Ticket</h2>
<div class="mt-4 bg-blue-50 border-2 border-blue-200 rounded-[20px] p-4"><p class="font-black text-[13px]">📸 Logo - se verá grande arriba</p><input type="file" id="logoInput" accept="image/*" onch[...]
<div class="mt-4 bg-gray-50 border-2 rounded-[20px] p-4"><p class="font-black text-[12px]">🏪 Datos del negocio</p><input id="empNombre" placeholder="Mi s receta" class="w-full border-2 border-black[...]
<div class="mt-4 bg-purple-50 border-2 border-purple-200 rounded-2xl p-3"><p class="font-black text-[12px]">👥 Colaboradores</p><div class="grid grid-cols-5 gap-2 mt-2"><input id="colabEmail" type="[...]
<button onclick="guardarEmpresa()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR</button><button onclick="probarTicket()" class="w-full mt-2 bg-white border-2 border-blac[...]
<div id="ticketVista" class="mt-6 border-2 border-dashed border-black p-3 rounded-xl bg-yellow-50"><p class="text-[11px] font-black text-center mb-2">VISTA PREVIA</p><div id="ticketContenido" class="b[...]
</div></div>

<div id="tab-clientes" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[28px] p-4 text-white"><div class="flex justify-between items-center"><h2 class="font-black">👥 Clientes</h2><span class="t[...]
<div id="tab-presupuestos" class="p-3 hidden"><div class="bg-blue-700 rounded-[28px] p-4 text-white"><div class="flex justify-between items-center"><h2 class="font-black">📋 Presupuestos</h2><span i[...]

<div id="tab-proveedores" class="p-3 hidden">
<div class="bg-[#0F172A] rounded-[28px] p-4 text-white"><h2 class="font-black">🏭 Proveedores</h2><div class="grid grid-cols-7 gap-1 mt-3"><input id="provNombre" placeholder="Nombre" class="col-span[...]
<div class="mt-3 bg-white rounded-[20px] p-4"><div id="listaProveedores" class="space-y-3"></div></div>
</div>

<div id="tab-inventario" class="p-3 hidden">
<div class="bg-[#2D3748] rounded-[28px] p-4 text-white mb-3"><h2 class="font-black">📦 Inventario</h2></div>
<div class="bg-white rounded-[20px] p-4">
<div class="grid grid-cols-7 gap-1"><input id="inv-nombre" placeholder="Papas" class="col-span-2 border-2 border-black p-2 rounded-xl font-bold text-[12px]"><input id="inv-precio" type="number" placeh[...]
<div class="mt-4 bg-yellow-50 border-2 border-yellow-300 rounded-xl p-2"><div class="flex items-center gap-2"><span class="text-[14px]">🔍</span><input id="buscInv" placeholder="Buscar producto..." [...]
<div id="listaInvMaster" class="mt-4"></div></div></div>

<div id="tab-finanzas" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[24px] p-4 text-white"><div class="flex justify-between items-center"><h2 class="font-black">📅 Finanzas</h2><div class="fl[...]

<div id="modalCobro" class="hidden fixed inset-0 bg-black/70 z-50 flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5 max-h-[90vh] overflow-y-auto"><h2 class="fo[...]
<div id="modalGasto" class="hidden fixed inset-0 bg-black/70 z-[60] flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5 max-h-[90vh] overflow-y-auto"><h2 class="fo[...]
<div id="modalInv" class="hidden fixed inset-0 bg-black/70 z-[70] flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5"><h2 class="font-black text-[15px]">📦 Edit[...]
<div id="modalProv" class="hidden fixed inset-0 bg-black/70 z-[70] flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5 max-h-[90vh] overflow-y-auto"><h2 class="fon[...]
<div id="modalDeuda" class="hidden fixed inset-0 bg-black/70 z-50 flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5 max-h-[85vh] overflow-y-auto"><h2 class="fon[...]
<div id="modalCierre" class="hidden fixed inset-0 bg-black/70 z-50 flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5 max-h-[85vh] overflow-y-auto"><h2 class="fon[...]
<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30 overflow-x-auto"><button onclick="showTab('costos')" class="flex flex-col items-center text-b[...]
<script>
let carrito=[], fotoTemp='', logoTemp='', categoriaFiltro='todas', editId=null, currentUser=null, negocioId=null, ultimoTicket=null, ultimoCierre=null, clienteDeudaActual=null, gastoTipoSel='salida', [...]
function getFechaLocal(){ let now=new Date(); return now.toLocaleDateString('es-MX',{day:'2-digit',month:'2-digit',year:'numeric'})+', '+now.toLocaleTimeString('es-MX',{hour:'2-digit',minute:'2-digit'[...]
function getFechaSoloLocal(){ let now=new Date(); return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`; }
let vistaCal='mes', fechaVista=new Date(), fechaSel=getFechaSoloLocal(), metodoPagoSel='Efectivo';
function setMetodoPago(m){ metodoPagoSel=m; document.getElementById('metodoPago').value=m; ['efectivo','tarjeta','transferencia','fiado','apartado'].forEach(x=>{ let b=document.getElementById('mp-'+x)[...]
function actualizarHora(){ let el=document.getElementById('horaActual'); if(el) el.innerText='🕒 '+getFechaLocal(); } setInterval(actualizarHora,1000);
function msgLogin(txt,ok){let el=document.getElementById('loginMsg'); el.innerText=txt; el.classList.remove('hidden'); el.className='mt-3 text-[11px] font-bold text-center p-2 rounded-xl '+(ok?'bg-gre[...]
async function hacerRegistro(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); if(!e||!p) return msgLogin('Pon correo y[...]
async function hacerLogin(){
 let e=document.getElementById('loginEmail').value.trim().toLowerCase();
 let p=document.getElementById('loginPass').value;
 if(!e||!p) return msgLogin('Escribe tu correo y contraseña',false);
 let btn=document.querySelector('#loginScreen button[onclick="hacerLogin()"]');
 if(btn){btn.disabled=true; btn.innerText='ENTRANDO...';}
 try{
  let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});
  let texto=await r.text(); let j={}; try{j=JSON.parse(texto)}catch(err){j={ok:false,msg:'El servidor no respondió correctamente. Vuelve a abrir la app.'};}
  if(!r.ok || !j.ok) return msgLogin(j.msg||'Correo o contraseña incorrectos',false);
  currentUser=e; negocioId=j.negocio_id||e;
  localStorage.setItem('session_email',e); localStorage.setItem('session_negocio',negocioId);
  document.getElementById('loginScreen').classList.add('hidden');
  document.getElementById('userLabel').innerText=e;
  await cargarDeNube(); showTab('inventario');
 }catch(err){ msgLogin('No se pudo conectar con la app. Revisa que esté abierta correctamente y vuelve a intentar.',false); }
 finally{ if(btn){btn.disabled=false; btn.innerText='ENTRAR';} }
}
function cerrarSesion(){localStorage.removeItem('session_email'); localStorage.removeItem('session_negocio'); location.reload();}
async function cargarDeNube(){if(!currentUser) return; let r=await fetch('/api/load?email='+encodeURIComponent(currentUser)); let j=await r.json(); if(!j.ok) return; let data=j.data||{}; for(let k in [...]
async function guardarEnNube(){if(!currentUser) return; let keys=['productosV2','inventarioMaestro','clientesV2','facturas','presupuestos','categoriasVenta','gastosFijos','empresaConfig','lotesMes','d[...]
window.addEventListener('load', async ()=>{ let e=localStorage.getItem('session_email'); let n=localStorage.getItem('session_negocio'); if(e&&n){ document.getElementById('loginEmail').value=e; current[...]
async function invitarColab(){let colab=document.getElementById('colabEmail').value.trim().toLowerCase(); let pass=document.getElementById('colabPass').value.trim()||'1234'; if(!colab) return alert('P[...]
function getFijos(){ return JSON.parse(localStorage.getItem('gastosFijos_'+negocioId)||localStorage.getItem('gastosFijos')||'[]'); }
function getProd(){ return JSON.parse(localStorage.getItem('productosV2_'+negocioId)||localStorage.getItem('productosV2')||'[]'); }
function getInv(){ return JSON.parse(localStorage.getItem('inventarioMaestro_'+negocioId)||localStorage.getItem('inventarioMaestro')||'[]'); }
function getCli(){ return JSON.parse(localStorage.getItem('clientesV2_'+negocioId)||localStorage.getItem('clientesV2')||'[]'); }
function getFacts(){ return JSON.parse(localStorage.getItem('facturas_'+negocioId)||localStorage.getItem('facturas')||'[]'); }
function getPresupuestos(){ return JSON.parse(localStorage.getItem('presupuestos_'+negocioId)||localStorage.getItem('presupuestos')||'[]'); }
function normalizarTelefono(tel){ tel=(tel||'').replace(/\D/g,''); if(tel.length==10) tel='52'+tel; return tel; }
function getDeudas(){ return JSON.parse(localStorage.getItem('deudas_'+negocioId)||localStorage.getItem('deudas')||'[]'); }
function getProveedores(){ return JSON.parse(localStorage.getItem('proveedores_'+negocioId)||localStorage.getItem('proveedores')||'[]'); }
function getEmp(){ return JSON.parse(localStorage.getItem('empresaConfig_'+negocioId)||localStorage.getItem('empresaConfig')||'{"nombre":"Mi s receta","logo":"","mostrarLogo":true,"mostrarFondo":true,[...]
function getCategoriasVenta(){ let cats=JSON.parse(localStorage.getItem('categoriasVenta_'+negocioId)||localStorage.getItem('categoriasVenta')||'[]'); if(!cats.length){ cats=[{id:'todas',nombre:'Todas[...]
function setItem(k,v){ localStorage.setItem(k+'_'+negocioId, typeof v==='string'? v: JSON.stringify(v)); localStorage.setItem(k, typeof v==='string'? v: JSON.stringify(v)); guardarEnNube(); }
function normalizarUnidad(u){ u=(u||'').toLowerCase().trim(); if(['g','gr'].includes(u)) return 'g'; if(['kg'].includes(u)) return 'kg'; if(['L','l','litro'].includes(u)) return 'L'; if(['ml'].include[...]
function factorABase(u){ u=normalizarUnidad(u); let map={g:1,kg:1000,ml:1,L:1000,pza:1}; return map[u]||1; }
function convertir(cant, de, a){ de=normalizarUnidad(de); a=normalizarUnidad(a); if(de==a) return cant; return cant * factorABase(de) / factorABase(a); }
function parseCantidadTexto(texto, unidadBase){ if(!texto) return 0; texto=texto.toString().toLowerCase().trim().replace(',', '.'); let num=parseFloat(texto); if(isNaN(num)) return 0; if(texto.include[...]

function addProveedor(){ let n=document.getElementById('provNombre').value.trim(), tel=document.getElementById('provTel').value.trim(), que=document.getElementById('provQue').value.trim(); if(!n) retu[...]
function abrirProvEdit(id){ let p=getProveedores().find(x=>x.id==id); if(!p) return; document.getElementById('pe-id').value=p.id; document.getElementById('pe-nombre').value=p.nombre||''; document.getE[...]
function cerrarProvEdit(){ document.getElementById('modalProv').classList.add('hidden'); }
function guardarProvEdit(){ let id=document.getElementById('pe-id').value; let provs=getProveedores(); let p=provs.find(x=>x.id==id); if(!p) return; p.nombre=document.getElementById('pe-nombre').value[...]
function renderProveedores(){ let provs=getProveedores(); let el=document.getElementById('listaProveedores'); if(!el) return; if(!provs.length){ el.innerHTML='<p class="text-[11px] text-gray-400 text-[...]

function addCategoriaVenta(){ let n=document.getElementById('nuevaCatNombre').value.trim(); if(!n) return; let cats=getCategoriasVenta(); cats.push({id:n.toLowerCase().replace(/\\s+/g,'-')+'-'+Date.no[...]
function addCategoriaVentaDesdeProd(){ let n=document.getElementById('quickCat').value.trim(); if(!n) return; let cats=getCategoriasVenta(); let id=n.toLowerCase().replace(/\\s+/g,'-')+'-'+Date.now();[...]
function renderCategoriasVenta(){ let cats=getCategoriasVenta(); let el=document.getElementById('filtrosCats'); if(el) el.innerHTML=cats.map(c=>`<button onclick="categoriaFiltro='${c.id}'; renderVenta[...]
function renderProdCategoriaSelect(){ let cats=getCategoriasVenta(); let sel=document.getElementById('prodCategoria'); if(!sel) return; sel.innerHTML=cats.map(c=>`<option value="${c.id}">${c.nombre}</[...]
function addCliente(){ let nombre=document.getElementById('cliNombre').value.trim(); let tel=document.getElementById('cliTel').value.trim(); if(!nombre) return; let cli=getCli(); cli.push({id:Date.now[...]
function addClienteRapido(){ let nombre=document.getElementById('quickClienteNombre').value.trim(); let tel=document.getElementById('quickClienteTel').value.trim(); if(!nombre) return alert('Nombre');[...]
function recordarDeuda(){ if(!clienteDeudaActual) return; let cli=getCli().find(c=>c.id==clienteDeudaActual); let deudas=getDeudas().filter(d=>d.clienteId==clienteDeudaActual && d.restante>0); let tot[...]
function renderClientes(){ let cli=getCli(); let deudas=getDeudas(); let totalPorCobrar=0; deudas.forEach(d=>{ if(d.restante>0) totalPorCobrar+=d.restante; }); document.getElementById('totalDeudaGloba[...]
function abrirDeuda(id){ let cli=getCli().find(c=>c.id==id); if(!cli) return; clienteDeudaActual=id; document.getElementById('deudaClienteNombre').innerText=cli.nombre; document.getElementById('deudaC[...]
function cerrarDeuda(){ document.getElementById('modalDeuda').classList.add('hidden'); }
function hacerAbono(){ if(!clienteDeudaActual) return; let monto=parseFloat(document.getElementById('abonoMonto').value)||0; if(monto<=0) return; let deudas=getDeudas(); let pendientes=deudas.filter(d[...]

function addFijo(){ let n=document.getElementById('fijoNombre').value.trim(), m=parseFloat(document.getElementById('fijoMonto').value); if(!n||!m) return; let f=getFijos(); f.push({id:Date.now().toStr[...]
function renderFijos(){ let f=getFijos(); let total=f.reduce((s,x)=>s+x.monto,0); document.getElementById('totalFijos').innerText=total.toFixed(0); let lotes=parseInt(localStorage.getItem('lotesMes_'+[...]
function showTab(t){ ['costos','vender','inventario','finanzas','clientes','config','presupuestos','proveedores'].forEach(x=>{ let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hid[...]
function setCrear(v){ document.getElementById('crear-menu').classList.toggle('hidden',v!='menu'); document.getElementById('crear-base').classList.toggle('hidden',v!='base'); document.getElementById('c[...]
function cancelarEdicion(){ editId=null; fotoTemp=''; setCrear('menu'); }
function previewFoto(i){ if(i.files&&i.files[0]){ let r=new FileReader(); r.onload=function(e){ fotoTemp=e.target.result; document.getElementById('fotoImg').src=fotoTemp; document.getElementById('foto[...]
function previewLogo(input){ if(input.files&&input.files[0]){ let reader=new FileReader(); reader.onload=function(e){ logoTemp=e.target.result; document.getElementById('logoPreview').src=logoTemp; doc[...]
function quitarLogo(){ logoTemp=''; document.getElementById('logoPreviewBox').classList.add('hidden'); actualizarFondo(); actualizarVistaTicket(); }
function actualizarFondo(){ let emp=getEmp(); let logo=logoTemp||emp.logo||''; let mostrarFondo=document.getElementById('empMostrarFondo')?.checked?? emp.mostrarFondo; let op=parseInt(document.getElem[...]
function cargarEmpresa(){ let emp=getEmp(); document.getElementById('empNombre').value=emp.nombre||''; document.getElementById('empDireccion').value=emp.direccion||''; document.getElementById('empCP')[...]
function guardarEmpresa(){ let emp={nombre:document.getElementById('empNombre').value.trim()||'Mi Negocio',direccion:document.getElementById('empDireccion').value.trim(),cp:document.getElementById('em[...]
function generarTicket(data){ let emp=getEmp(); let logoHtml=emp.mostrarLogo && emp.logo? `<div style="text-align:center;"><img src="${emp.logo}" style="display:block; margin:0 auto; max-width:90px; m[...]
function generarTextoWhatsApp(data){ let emp=getEmp(); let lineas=[ `*${emp.nombre}*`, `${emp.direccion||''} ${emp.tel||''}`.trim(), `-------------------------`, `Fecha: ${data.fechaStr}`, `Cliente: $[...]
function actualizarVistaTicket(){ generarTicket({fecha:new Date(),fechaStr:getFechaLocal(),items:[{nombre:'Ejemplo Alitas',qty:2,venta:57}],total:114,cliente:'Mostrador',vendedor:currentUser, metodoPa[...]
function imprimirTicket(){ let contenido=document.getElementById('ticketContenido').innerHTML; let w=window.open('','','width=300,height=600'); w.document.write('<html><head><style>body{font-family:mo[...]
function enviarWhatsAppTicket(esPrueba){ if(!ultimoTicket && esPrueba){ actualizarVistaTicket(); ultimoTicket={fechaStr:getFechaLocal(),items:[{nombre:'Ejemplo',qty:2,venta:57}],total:114,cliente:'Mos[...]
function probarTicket(){ guardarEmpresa(); actualizarVistaTicket(); imprimirTicket(); }

function addInventario(){ let n=document.getElementById('inv-nombre').value.trim(), p=parseFloat(document.getElementById('inv-precio').value)||0, stockTxt=document.getElementById('inv-stock').value.tr[...]
function abrirInvEdit(id){ let it=getInv().find(x=>x.id==id); if(!it) return; document.getElementById('ie-id').value=it.id; document.getElementById('ie-nombre').value=it.nombre||''; document.getElem[...]
function cerrarInvEdit(){ document.getElementById('modalInv').classList.add('hidden'); }
function guardarInvEdit(){ let id=document.getElementById('ie-id').value; let inv=getInv(); let it=inv.find(x=>x.id==id); if(!it) return; let n=document.getElementById('ie-nombre').value.trim(); if(!n[...]
function registrarMerma(id){ let inv=getInv(); let it=inv.find(x=>x.id==id); if(!it) return; let txt=prompt(`Merma de ${it.nombre} Actual: ${it.stock} ${it.unidad} Cuánto se tiró? Ej: 200 g`); if(!t[...]
function renderInventarioMaster(){ let inv=getInv(); let el=document.getElementById('listaInvMaster'); let busc=document.getElementById('buscInv')?.value.toLowerCase().trim()||''; let alerta=document.[...]

function addInsumo(d={}){ let inv=getInv(); let opts=inv.map(it=>`<option value="${it.id}" ${d.invId==it.id?'selected':''}>${it.nombre} $${it.precio}/${it.unidad}</option>`).join(''); let div=document[...]
function calc(){ try{ let tot=0; document.querySelectorAll('#insumos > div').forEach(row=>{ let invId=row.querySelector('.in-n')?.value; let it=getInv().find(x=>x.id==invId); let cu=parseFloat(row.que[...]
function baseSeleccionada(sel){ let b=getProd().find(x=>String(x.id)==String(sel.value)); let row=sel.closest('#basesSel > div'); if(!b||!row) return; let uu=row.querySelector('.b-uu'); if(uu) uu.valu[...]
function addBase(d={}){ let bases=getProd().filter(p=>p.esBase); let opts=bases.map(b=>`<option value="${b.id}" ${d.id==b.id?'selected':''}>${b.nombre} (rinde ${b.rendimiento?.cant||1} ${b.rendimiento[...]
function calc2(){ let tot=0; document.querySelectorAll('#basesSel > div').forEach(r=>{ let id=r.querySelector('.b-sel')?.value; let b=getProd().find(x=>String(x.id)==String(id)); let cant=parseFloat(r[...]
function guardarProd(tipo){ let isBase=tipo=='recetario'; let nomEl=isBase?document.getElementById('nombre'):document.getElementById('nombreProd'); let nom=nomEl.value.trim(); if(!nom) return alert('P[...]
function editarProd(id){ let p=getProd().find(x=>String(x.id)==String(id)); if(!p) return; editId=p.id; if(p.esBase){ document.getElementById('crear-menu').classList.add('hidden'); document.getEl[...]
function borrarProd(id){ if(!confirm('¿Borrar esta receta?')) return; let ps=getProd().filter(x=>String(x.id)!=String(id)); setItem('productosV2',ps); renderInventario(); renderVenta(); }
function renderInventario(){ let ps=getProd(); let el=document.getElementById('listaInv'); if(!el) return; if(!ps.length){ el.innerHTML='<p class="text-center text-gray-400 py-6 text-[12px]">Sin recet[...]

function construirPresupuestoActual(){ let total=parseFloat(document.getElementById('c-total').innerText)||0; let sel=document.getElementById('selCliente'); let clienteNombre=sel? sel.options[sel.sele[...]
function generarTextoPresupuesto(p){ let emp=getEmp(); let lineas=[`*${emp.nombre}*`,`📋 *PRESUPUESTO*`,`${emp.direccion||''} ${emp.tel||''}`.trim(),`-------------------------`,`Fecha: ${p.fechaStr}[...]
function enviarPresupuestoWhatsApp(p, telDirecto){ let tel=normalizarTelefono(telDirecto||''); if(!tel) tel=normalizarTelefono(getCli().find(c=>c.id==p.clienteId)?.tel||''); if(!tel) tel=normalizarTel[...]
function guardarPresupuesto(){ if(!carrito.length) return alert('Agrega productos al pedido'); let p=construirPresupuestoActual(); let ps=getPresupuestos(); let idx=ps.findIndex(x=>String(x.id)==Strin[...]
function editarPresupuesto(id){ let p=getPresupuestos().find(x=>String(x.id)==String(id)); if(!p||p.estado!='pendiente') return; carrito=p.items.map(i=>({...i})); presupuestoEditandoId=p.id; document.[...]
function abrirCobroPresupuesto(id){ let p=getPresupuestos().find(x=>String(x.id)==String(id)); if(!p||p.estado!='pendiente') return; carrito=p.items.map(i=>({...i})); presupuestoEnCobroId=p.id; presup[...]
function cancelarPresupuesto(id){ let ps=getPresupuestos(); let p=ps.find(x=>String(x.id)==String(id)); if(!p||p.estado!='pendiente') return; if(!confirm('¿Cancelar este presupuesto?')) return; p.est[...]
function renderPresupuestos(){ let ps=getPresupuestos(); let pendientes=ps.filter(p=>p.estado=='pendiente'); let badge=document.getElementById('totalPresupuestosPendientes'); if(badge) badge.innerText[...]
function renderVenta(){ let ps=getProd().filter(p=>!p.esBase); let cats=getCategoriasVenta(); if(categoriaFiltro!='todas') ps=ps.filter(p=>p.categoria==categoriaFiltro); let cont=document.getElementBy[...]
function addCart(id){ let p=getProd().find(x=>String(x.id)==String(id)); if(!p) return; let ex=carrito.find(x=>String(x.id)==String(id)); if(ex) ex.qty++; else carrito.push({...p,qty:1}); renderCarrit[...]
function renderCarrito(){ if(!carrito.length){ document.getElementById('ticket').innerHTML='Vacío'; document.getElementById('c-total').innerText='0'; document.getElementById('cobroTotal').innerT[...]
function abrirCobro(){ if(!carrito.length) return alert('Vacío'); document.getElementById('cobroHora').innerText=getFechaLocal(); setMetodoPago('Efectivo'); document.getElementById('modalCobro').clas[...]
function cerrarCobro(){ document.getElementById('modalCobro').classList.add('hidden'); }
function calcCambio(){ let tot=parseFloat(document.getElementById('c-total').innerText)||0; let rec=parseFloat(document.getElementById('pagoRecibido').value)||0; document.getElementById('cambio').inne[...]
function confirmarCobro(tipo){ let facts=getFacts(); let deudas=getDeudas(); let fechaStr=getFechaLocal(); let fechaSolo=getFechaSoloLocal(); let total=parseFloat(document.getElementById('c-total').in[...]
function setGastoTipo(t){ gastoTipoSel=t; document.getElementById('g-tipo').value=t; document.getElementById('g-btn-salida').className= t=='salida'? 'border-2 border-black p-3 rounded-xl font-black bg[...]
function openGasto(){ renderProveedores(); document.getElementById('modalGasto').classList.remove('hidden'); }
function cerrarGasto(){ document.getElementById('modalGasto').classList.add('hidden'); }
function guardarGasto(){ let c=document.getElementById('g-concepto').value.trim(), m=parseFloat(document.getElementById('g-monto').value), t=document.getElementById('g-tipo').value, obs=document.getEl[...]
function exportarExcel(){ let facts=getFacts(); let csv='Fecha,Concepto,Monto,Tipo,Metodo\\n'+facts.map(f=>`"${f.fecha}","${f.concepto}",${f.monto},${f.tipo},${f.metodoPago||''}`).join('\\n'); let blo[...]
function abrirCierre(){ let fechaStr=fechaSel; let facts=getFacts().filter(f=>f.fecha==fechaStr); let total=facts.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0); document.getElementById('cier[...]
function cerrarCierre(){ document.getElementById('modalCierre').classList.add('hidden'); }
function imprimirCierre(){ alert('Cierre'); }
function enviarCierreWhatsApp(){ let c=ultimoCierre; if(!c) return; let texto=`Cierre ${c.fecha}: $${c.total}`; let tel=prompt('WhatsApp'); if(!tel) return; tel=tel.replace(/\\D/g,''); if(tel.length==[...]
function setVistaCal(v){ vistaCal=v; renderCalendario(); }
function moverCal(dir){ fechaVista.setMonth(fechaVista.getMonth()+dir); renderCalendario(); }
function seleccionarDia(f){ fechaSel=f; renderCalendario(); }
function renderCalendario(){ let facts=getFacts(); let y=fechaVista.getFullYear(), m=fechaVista.getMonth(); document.getElementById('calTitulo').innerText=fechaVista.toLocaleDateString('es-MX',{month:[...]
function renderDesgloseDia(fechaStr){ let facts=getFacts().filter(f=>f.fecha==fechaStr); document.getElementById('fechaSelLabel').innerText=fechaStr; document.getElementById('flu-lista').innerHTML=fac[...]
function actualizarClienteTicket(){ let sel=document.getElementById('selCliente'); if(!sel) return; let opt=sel.options[sel.selectedIndex]; let nombre=opt? (opt.getAttribute('data-nombre')||opt.text) [...]
</script></body></html>
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
