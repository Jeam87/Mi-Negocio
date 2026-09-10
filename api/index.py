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
 posibles = ['logo.png','api/logo.png',os.path.join(os.path.dirname(__file__), 'logo.png'),os.path.join(os.getcwd(), 'logo.png'),os.path.join(os.getcwd(), 'api', 'logo.png'),'/tmp/logo.png']
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
 return """<!DOCTYPE html><html><head><link rel="manifest" href="/manifest.json"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Negocio 11.5</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>input,select,textarea{color:#000!important;background:#fff!important}.logo-watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:650px;height:650px;pointer-events:none;z-index:0;opacity:0.18;object-fit:contain;}#appContent{position:relative;z-index:1;}#splashInicio{position:fixed;inset:0;background:white;z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center}#splashInicio img{width:85vw;max-width:380px;height:auto;animation:pop 0.8s ease}@keyframes pop{0%{transform:scale(0.5);opacity:0}100%{transform:scale(1);opacity:1}}</style></head><body class="bg-[#FFF8F0] min-h-screen"><div id="splashInicio"><img src="/logo.png" onerror="this.src='/api/logo.png'"><p style="margin-top:20px;font-weight:900;font-size:22px">Mi Negocio 11.5</p><p style="font-size:12px;color:#888">Cargando...</p></div><script>setTimeout(()=>{let s=document.getElementById('splashInicio'); if(s) s.style.display='none'},1800)</script><div class="max-w-md mx-auto pb-[140px] relative"><img id="logoBg" class="logo-watermark hidden"><div id="appContent">
<div id="loginScreen" class="fixed inset-0 bg-[#FFF8F0] z-[100] flex flex-col items-center justify-center p-6"><h1 class="font-black text-[24px]">Mi Negocio 11.5</h1><p class="text-[11px] text-gray-500">Logo grande + proveedores completos</p><div class="bg-white w-full rounded-[28px] p-5 shadow-xl border-2 border-black mt-6"><input id="loginEmail" type="email" placeholder="Correo" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[14px]"><input id="loginPass" type="password" placeholder="Contraseña" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[14px] mt-3"><button onclick="hacerLogin()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">ENTRAR</button><button onclick="hacerRegistro()" class="w-full mt-2 bg-white border-2 border-black py-3 rounded-2xl font-bold text-[13px]">REGISTRARME</button><p id="loginMsg" class="hidden mt-3 text-[11px] font-bold text-center p-2 rounded-xl"></p></div></div>
""" + open(os.path.join(os.path.dirname(__file__), 'app.html'), 'r', encoding='utf-8').read() if os.path.exists(os.path.join(os.path.dirname(__file__), 'app.html')) else """
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><div class="flex items-center gap-3"><img id="logoHeader" class="w-20 h-20 rounded-full object-cover border-[4px] border-black hidden shadow-xl" onerror="this.src='/api/logo.png'"><div><h1 class="font-black text-[16px]">Mi Negocio 11.5</h1><p id="userLabel" class="text-[10px] text-gray-500"></p><p id="horaActual" class="text-[10px] font-black text-green-600"></p></div></div><div class="flex gap-2"><button onclick="showTab('config')" class="text-[10px] bg-black text-white px-3 py-2 rounded-full">Config</button><button onclick="cerrarSesion()" class="text-[10px] bg-red-100 text-red-600 px-2 py-1 rounded-full">Salir</button></div></div>
<div id="tab-inventario" class="p-3"><div class="bg-[#2D3748] rounded-[28px] p-4 text-white mb-3"><h2 class="font-black">📦 Inventario</h2></div><div class="bg-white rounded-[20px] p-4"><div class="grid grid-cols-7 gap-1"><input id="inv-nombre" placeholder="Papas" class="col-span-2 border-2 border-black p-2 rounded-xl font-bold text-[12px]"><input id="inv-precio" type="text" placeholder="$30" class="col-span-1 border-2 border-black p-2 rounded-xl font-black text-[12px] bg-yellow-50"><input id="inv-stock" type="text" placeholder="500 g" class="col-span-2 border-2 border-black p-2 rounded-xl font-black text-[12px] bg-yellow-50"><select id="inv-unidad" class="col-span-1 border-2 border-black p-2 rounded-xl text-[10px] font-bold"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>pza</option></select><button onclick="addInventario()" class="col-span-1 bg-black text-white rounded-xl font-black">+</button></div><div id="listaInvMaster" class="mt-4"></div></div></div>
</div></div>
<script>
let carrito=[], fotoTemp='', logoTemp='', categoriaFiltro='todas', editId=null, currentUser=null, negocioId=null, ultimoTicket=null, ultimoCierre=null, clienteDeudaActual=null, gastoTipoSel='salida';
function getFechaLocal(){ let now=new Date(); return now.toLocaleDateString('es-MX',{day:'2-digit',month:'2-digit',year:'numeric'})+', '+now.toLocaleTimeString('es-MX',{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true}); }
function getFechaSoloLocal(){ let now=new Date(); return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`; }
let vistaCal='mes', fechaVista=new Date(), fechaSel=getFechaSoloLocal(), metodoPagoSel='Efectivo';
function actualizarHora(){ let el=document.getElementById('horaActual'); if(el) el.innerText='🕒 '+getFechaLocal(); } setInterval(actualizarHora,1000);
function msgLogin(txt,ok){let el=document.getElementById('loginMsg'); el.innerText=txt; el.classList.remove('hidden'); el.className='mt-3 text-[11px] font-bold text-center p-2 rounded-xl '+(ok?'bg-green-100 text-green-700':'bg-red-100 text-red-700');}
async function hacerRegistro(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); if(!e||!p) return msgLogin('Pon correo y pass',false); let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})}); let j=await r.json(); if(!j.ok) return msgLogin(j.msg,false); msgLogin('✅ Cuenta creada',true);}
async function hacerLogin(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); if(!e||!p) return msgLogin('Pon correo',false); let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})}); let j=await r.json(); if(!j.ok) return msgLogin(j.msg,false); currentUser=e; negocioId=j.negocio_id; localStorage.setItem('session_email',e); localStorage.setItem('session_negocio',negocioId); document.getElementById('loginScreen').classList.add('hidden'); document.getElementById('userLabel').innerText=e; await cargarDeNube();}
function cerrarSesion(){localStorage.removeItem('session_email'); localStorage.removeItem('session_negocio'); location.reload();}
async function cargarDeNube(){if(!currentUser) return; let r=await fetch('/api/load?email='+encodeURIComponent(currentUser)); let j=await r.json(); if(!j.ok) return; let data=j.data||{}; for(let k in data){ localStorage.setItem(k+'_'+negocioId, data[k]); } renderInventarioMaster();}
async function guardarEnNube(){if(!currentUser) return; let keys=['productosV2','inventarioMaestro','clientesV2','facturas','categoriasVenta','gastosFijos','empresaConfig','lotesMes','deudas','proveedores']; let data={}; keys.forEach(k=>{ let v=localStorage.getItem(k+'_'+negocioId) || localStorage.getItem(k); if(v) data[k]=v; }); await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:currentUser,data})});}
window.addEventListener('load', async ()=>{ let e=localStorage.getItem('session_email'); let n=localStorage.getItem('session_negocio'); if(e&&n){ document.getElementById('loginEmail').value=e; currentUser=e; negocioId=n; document.getElementById('loginScreen').classList.add('hidden'); document.getElementById('userLabel').innerText=e; await cargarDeNube(); }});
function getInv(){ return JSON.parse(localStorage.getItem('inventarioMaestro_'+negocioId)||localStorage.getItem('inventarioMaestro')||'[]'); }
function setItem(k,v){ localStorage.setItem(k+'_'+negocioId, typeof v==='string'? v: JSON.stringify(v)); localStorage.setItem(k, typeof v==='string'? v: JSON.stringify(v)); guardarEnNube(); }
function normalizarUnidad(u){ u=(u||'').toLowerCase().trim(); if(['g','gr'].includes(u)) return 'g'; if(['kg'].includes(u)) return 'kg'; if(['L','l','litro'].includes(u)) return 'L'; if(['ml'].includes(u)) return 'ml'; return u||'kg'; }
function factorABase(u){ u=normalizarUnidad(u); let map={g:1,kg:1000,ml:1,L:1000,pza:1}; return map[u]||1; }
function convertir(cant, de, a){ de=normalizarUnidad(de); a=normalizarUnidad(a); if(de==a) return cant; return cant * factorABase(de) / factorABase(a); }
function parseNumTxt(v){ v=String(v||'').trim().replace(',','.').toLowerCase(); if(!v) return 0; let limpio=v.replace(/[^0-9.\\/]/g,''); if(!limpio) return 0; if(limpio.includes('/')){ let p=limpio.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1); } return parseFloat(limpio)||0; }
function parseCantidadTexto(texto, unidadBase){ if(!texto) return 0; texto=texto.toString().toLowerCase().trim().replace(',', '.'); let num=parseNumTxt(texto); if(isNaN(num)) return 0; if(texto.includes('kg')) return convertir(num, 'kg', unidadBase); if(texto.includes('ml')) return convertir(num, 'ml', unidadBase); if((texto.includes(' g') || texto.endsWith('g')) &&!texto.includes('kg')) return convertir(num, 'g', unidadBase); if(texto.includes('l') &&!texto.includes('ml')) return convertir(num, 'L', unidadBase); return num; }

function addInventario(){
 let n=document.getElementById('inv-nombre').value.trim();
 if(!n) return alert('Pon nombre');
 let pTxt=document.getElementById('inv-precio').value.trim();
 let p=parseNumTxt(pTxt);
 let stockTxt=document.getElementById('inv-stock').value.trim()||'0';
 let u=document.getElementById('inv-unidad').value;
 let stock = parseCantidadTexto(stockTxt, u);
 if(isNaN(stock)) stock=0;
 let inv=getInv();
 inv.push({id:Date.now().toString(),nombre:n,precio:p,stock:stock,unidad:u});
 setItem('inventarioMaestro',inv);
 document.getElementById('inv-nombre').value='';
 document.getElementById('inv-precio').value='';
 document.getElementById('inv-stock').value='';
 renderInventarioMaster();
}

function renderInventarioMaster(){
 let inv=getInv(); let el=document.getElementById('listaInvMaster');
 if(el){ el.innerHTML=inv.map(it=>`<div class="flex gap-2 items-center bg-gray-50 p-3 rounded-xl border"><div class="flex-1"><b class="text-[13px]">${it.nombre}</b> <span class="text-[10px]">Stock ${it.stock} ${it.unidad} - $${it.precio}/${it.unidad}</span></div><button onclick="if(confirm('Borrar?')){setItem('inventarioMaestro',getInv().filter(x=>x.id!='${it.id}')); renderInventarioMaster();}" class="text-red-400 px-1">X</button></div>`).join('')||'<p class="text-center text-gray-400 text-[11px]">Sin inventario</p>'; }
}
</script></body></html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
