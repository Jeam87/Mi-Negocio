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
 for ruta in ['logo.png','api/logo.png',os.path.join(os.path.dirname(__file__), 'logo.png'),os.path.join(os.getcwd(), 'logo.png'),os.path.join(os.getcwd(), 'api', 'logo.png'),'/tmp/logo.png']:
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
def home():
 return """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Negocio 11.5</title><script src="https://cdn.tailwindcss.com"></script><style>body{background:#FFF8F0}input,select,textarea{color:#000!important;background:#fff!important}</style></head><body><div class="max-w-md mx-auto pb-[140px] relative"><div id="appContent">
<div id="loginScreen" class="fixed inset-0 bg-[#FFF8F0] z-[100] flex flex-col items-center justify-center p-6"><h1 class="font-black text-[32px]">Mi Negocio 11.5</h1><p class="text-[11px] text-gray-500">Logo grande + proveedores completos</p><div class="bg-white w-full rounded-[28px] p-6 shadow-xl border-2 border-black mt-8"><input id="loginEmail" placeholder="Correo" class="w-full border-2 border-black p-4 rounded-2xl font-bold"><input id="loginPass" type="password" placeholder="Contraseña" class="w-full border-2 border-black p-4 rounded-2xl font-bold mt-3"><button onclick="hacerLogin()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black text-[16px]">ENTRAR</button><button onclick="hacerRegistro()" class="w-full mt-2 bg-white border-2 border-black py-3 rounded-2xl font-bold">REGISTRARME</button><p id="loginMsg" class="hidden mt-3 text-[11px] font-bold text-center p-2 rounded-xl"></p></div></div>

<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm border-b"><div><h1 class="font-black">Mi Negocio 11.5</h1><p id="userLabel" class="text-[10px] text-gray-500"></p></div><button onclick="cerrarSesion()" class="text-[10px] bg-red-100 text-red-600 px-3 py-2 rounded-full font-black">Salir</button></div>

<div id="tab-inventario" class="p-4"><div class="bg-[#2D3748] rounded-[24px] p-4 text-white mb-4"><h2 class="font-black text-[18px]">📦 Inventario</h2><p class="text-[11px] opacity-70">Ahora acepta $30 y 500 g</p></div><div class="bg-white rounded-[24px] p-4 shadow-sm border-2 border-black"><div class="grid grid-cols-6 gap-2"><input id="inv-nombre" placeholder="Papas" class="col-span-2 border-2 border-black p-3 rounded-xl font-bold text-[13px]"><input id="inv-precio" placeholder="$30" class="col-span-1 border-2 border-black p-3 rounded-xl font-black text-[13px] bg-yellow-50"><input id="inv-stock" placeholder="500 g" class="col-span-2 border-2 border-black p-3 rounded-xl font-black text-[13px] bg-yellow-50"><select id="inv-unidad" class="col-span-1 border-2 border-black p-2 rounded-xl font-bold text-[12px]"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>pza</option></select></div><button onclick="addInventario()" class="w-full mt-3 bg-black text-white py-3 rounded-xl font-black">+ AGREGAR</button><div id="listaInvMaster" class="mt-6 space-y-2"></div></div></div>

</div></div>
<script>
let currentUser=null, negocioId=null;
function msgLogin(t,ok){let el=document.getElementById('loginMsg');el.innerText=t;el.classList.remove('hidden');el.className='mt-3 text-[11px] font-bold text-center p-2 rounded-xl '+(ok?'bg-green-100 text-green-700':'bg-red-100 text-red-700')}
async function hacerRegistro(){let e=document.getElementById('loginEmail').value.trim().toLowerCase();let p=document.getElementById('loginPass').value.trim();if(!e||!p)return msgLogin('Pon correo y pass',false);let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(!j.ok)return msgLogin(j.msg,false);msgLogin('✅ Creada, ahora entra',true)}
async function hacerLogin(){let e=document.getElementById('loginEmail').value.trim().toLowerCase();let p=document.getElementById('loginPass').value.trim();if(!e||!p)return msgLogin('Pon correo',false);let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(!j.ok)return msgLogin('Error de correo/pass',false);currentUser=e;negocioId=j.negocio_id;localStorage.setItem('session_email',e);localStorage.setItem('session_negocio',negocioId);document.getElementById('loginScreen').classList.add('hidden');document.getElementById('userLabel').innerText=e;await cargarDeNube();}
function cerrarSesion(){localStorage.removeItem('session_email');localStorage.removeItem('session_negocio');location.reload();}
async function cargarDeNube(){if(!currentUser)return;let r=await fetch('/api/load?email='+encodeURIComponent(currentUser));let j=await r.json();if(!j.ok)return;let data=j.data||{};for(let k in data){localStorage.setItem(k+'_'+negocioId,data[k]);}renderInventarioMaster();}
async function guardarEnNube(){if(!currentUser)return;let keys=['inventarioMaestro'];let data={};keys.forEach(k=>{let v=localStorage.getItem(k+'_'+negocioId)||localStorage.getItem(k);if(v)data[k]=v;});await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:currentUser,data})});}
window.addEventListener('load',async()=>{let e=localStorage.getItem('session_email');let n=localStorage.getItem('session_negocio');if(e&&n){document.getElementById('loginEmail').value=e;currentUser=e;negocioId=n;document.getElementById('loginScreen').classList.add('hidden');document.getElementById('userLabel').innerText=e;await cargarDeNube();}})
function getInv(){return JSON.parse(localStorage.getItem('inventarioMaestro_'+negocioId)||localStorage.getItem('inventarioMaestro')||'[]')}
function setItem(k,v){localStorage.setItem(k+'_'+negocioId,typeof v==='string'?v:JSON.stringify(v));localStorage.setItem(k,typeof v==='string'?v:JSON.stringify(v));guardarEnNube();}
function normalizarUnidad(u){u=(u||'').toLowerCase().trim();if(['g','gr'].includes(u))return 'g';if(['kg'].includes(u))return 'kg';if(['L','l','litro'].includes(u))return 'L';if(['ml'].includes(u))return 'ml';return u||'kg';}
function factorABase(u){u=normalizarUnidad(u);let map={g:1,kg:1000,ml:1,L:1000,pza:1};return map[u]||1;}
function convertir(cant,de,a){de=normalizarUnidad(de);a=normalizarUnidad(a);if(de==a)return cant;return cant*factorABase(de)/factorABase(a);}
function parseNumTxt(v){v=String(v||'').trim().replace(',','.').toLowerCase();if(!v)return 0;let limpio=v.replace(/[^0-9.\\/]/g,'');if(!limpio)return 0;if(limpio.includes('/')){let p=limpio.split('/');return (parseFloat(p[0])||0)/(parseFloat(p[1])||1);}return parseFloat(limpio)||0;}
function parseCantidadTexto(texto,unidadBase){if(!texto)return 0;texto=texto.toString().toLowerCase().trim().replace(',', '.');let num=parseNumTxt(texto);if(isNaN(num))return 0;if(texto.includes('kg'))return convertir(num,'kg',unidadBase);if(texto.includes('ml'))return convertir(num,'ml',unidadBase);if((texto.includes(' g')||texto.endsWith('g'))&&!texto.includes('kg'))return convertir(num,'g',unidadBase);if(texto.includes('l')&&!texto.includes('ml'))return convertir(num,'L',unidadBase);return num;}

function addInventario(){
 let n=document.getElementById('inv-nombre').value.trim();
 if(!n) return alert('Pon nombre');
 let p=parseNumTxt(document.getElementById('inv-precio').value);
 let stockTxt=document.getElementById('inv-stock').value.trim()||'0';
 let u=document.getElementById('inv-unidad').value;
 let stock=parseCantidadTexto(stockTxt,u);
 let inv=getInv();
 inv.push({id:Date.now().toString(),nombre:n,precio:p,stock:stock,unidad:u});
 setItem('inventarioMaestro',inv);
 document.getElementById('inv-nombre').value='';
 document.getElementById('inv-precio').value='';
 document.getElementById('inv-stock').value='';
 renderInventarioMaster();
}
function renderInventarioMaster(){
 let inv=getInv();
 let el=document.getElementById('listaInvMaster');
 if(!el) return;
 el.innerHTML=inv.map(it=>`<div class="flex justify-between bg-gray-50 p-3 rounded-xl border-2"><div><b>${it.nombre}</b> <span class="text-[11px]">Stock ${it.stock} ${it.unidad} - $${it.precio}</span></div><button onclick="if(confirm('Borrar?')){setItem('inventarioMaestro',getInv().filter(x=>x.id!='${it.id}'));renderInventarioMaster();}" class="text-red-500 font-black">X</button></div>`).join('')||'<p class="text-center text-gray-400 text-[11px]">Sin inventario</p>';
}
</script></body></html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
