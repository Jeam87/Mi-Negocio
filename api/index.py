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
 return jsonify({"name":"Mi Negocio 11.5","short_name":"Mi Negocio","start_url":"/","display":"standalone"})
@app.route('/logo.png')
@app.route('/api/logo.png')
def logo_file():
 for ruta in ['logo.png','api/logo.png',os.path.join(os.path.dirname(__file__), 'logo.png')]:
  try:
   if os.path.exists(ruta): return send_file(ruta, mimetype='image/png')
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
 return """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Negocio 11.5 FIX COMPLETO</title><script src="https://cdn.tailwindcss.com"></script><style>input,select,textarea{color:#000!important;background:#fff!important}.logo-watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:650px;height:650px;pointer-events:none;z-index:0;opacity:0.18;object-fit:contain}#appContent{position:relative;z-index:1}</style></head><body class="bg-[#FFF8F0]"><div class="max-w-md mx-auto pb-[140px] relative"><img id="logoBg" class="logo-watermark hidden"><div id="appContent">
<div id="loginScreen" class="fixed inset-0 bg-[#FFF8F0] z-[100] flex flex-col items-center justify-center p-6"><h1 class="font-black text-[28px]">Mi Negocio 11.5</h1><div class="bg-white w-full rounded-[28px] p-6 shadow-xl border-2 border-black mt-6"><input id="loginEmail" placeholder="Correo" class="w-full border-2 border-black p-4 rounded-2xl font-bold"><input id="loginPass" type="password" placeholder="Contra" class="w-full border-2 border-black p-4 rounded-2xl font-bold mt-3"><button onclick="hacerLogin()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">ENTRAR</button><button onclick="hacerRegistro()" class="w-full mt-2 bg-white border-2 border-black py-3 rounded-2xl font-bold">REGISTRARME</button><p id="loginMsg" class="hidden mt-3 text-[11px] font-bold text-center p-2 rounded-xl"></p></div></div>
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><div class="flex items-center gap-3"><img id="logoHeader" class="w-20 h-20 rounded-full object-cover border-[4px] border-black hidden shadow-xl"><div><h1 class="font-black text-[16px]">Mi Negocio 11.5 COMPLETO</h1><p id="userLabel" class="text-[10px] text-gray-500"></p></div></div><button onclick="cerrarSesion()" class="text-[10px] bg-red-100 text-red-600 px-2 py-1 rounded-full">Salir</button></div>
<div id="tab-inventario" class="p-3"><div class="bg-[#2D3748] rounded-[28px] p-4 text-white mb-3"><h2 class="font-black">📦 Inventario - $30 y 500g OK + Editar + Logo</h2></div><div class="bg-white rounded-[20px] p-4 border-2 border-black"><div class="grid grid-cols-7 gap-1"><input id="inv-nombre" placeholder="Papas" class="col-span-2 border-2 border-black p-2 rounded-xl font-bold text-[12px]"><input id="inv-costo" placeholder="$30" class="col-span-1 border-2 border-black p-2 rounded-xl font-black text-[12px] bg-yellow-50"><input id="inv-stock" placeholder="500 g" class="col-span-2 border-2 border-black p-2 rounded-xl font-black text-[12px] bg-yellow-50"><select id="inv-unit" class="col-span-1 border-2 border-black p-2 rounded-xl text-[10px] font-bold"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>pza</option></select><button id="btnAddInventario" onclick="addInventario()" class="col-span-1 bg-black text-white rounded-xl font-black">+</button></div><div id="contInventario" class="mt-4"></div><div id="listaInvMaster" class="mt-2"></div><div id="listaInv" class="mt-4"></div></div></div>
<div id="tab-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div><div class="mt-4 bg-white p-4 rounded-[20px] border-2 border-black"><div id="ticket">Vacío</div><div class="flex justify-between font-black mt-3">Total $<span id="c-total">0</span></div></div></div>
<div id="tab-proveedores" class="p-3 hidden"><div id="listaProveedores"></div></div>
<div id="tab-clientes" class="p-3 hidden"><div id="listaClientes"></div><span id="totalDeudaGlobal"></span></div>
<div id="tab-finanzas" class="p-3 hidden"><div id="calGrid"></div><div id="flu-lista"></div><span id="calTitulo"></span><span id="fechaSelLabel"></span><span id="fin-balance"></span><span id="fin-entradas"></span><span id="fin-salidas"></span></div>
<div id="tab-costos" class="p-3 hidden"><input id="fijoNombre"><input id="fijoMonto"><div id="listaFijos"></div><span id="totalFijos"></span></div>
<div id="tab-config" class="p-3 hidden"><div class="bg-white rounded-[28px] p-5"><h2 class="font-black">⚙️ Configuración y Logo</h2><div class="mt-4 bg-blue-50 border-2 border-blue-200 rounded-[20px] p-4"><p class="font-black text-[13px]">📸 Logo grande - se verá de fondo</p><input type="file" id="logoInput" accept="image/*" onchange="previewLogo(this)" class="w-full mt-2"><div id="logoPreviewBox" class="mt-3 hidden flex gap-3 items-center"><img id="logoPreview" class="w-28 h-28 object-contain rounded-xl border-2 border-black bg-white"><button onclick="quitarLogo()" class="text-[10px] bg-red-100 text-red-600 px-3 py-1 rounded-full">Quitar</button></div></div><div class="mt-4 bg-gray-50 border-2 rounded-[20px] p-4"><input id="empNombre" placeholder="Mi Negocio" class="w-full border-2 border-black p-3 rounded-xl font-bold"></div><button onclick="guardarEmpresa()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR EMPRESA Y LOGO</button><div id="ticketVista" class="mt-6 border-2 border-dashed p-3 rounded-xl bg-yellow-50"><div id="ticketContenido" class="bg-white p-4 rounded-xl border"></div></div></div></div>
<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30"><button onclick="showTab('costos')">Crear</button><button onclick="showTab('vender')">Vender</button><button onclick="showTab('inventario')">Invent</button><button onclick="showTab('finanzas')">Finanzas</button><button onclick="showTab('clientes')">Clientes</button><button onclick="showTab('proveedores')">Prov</button></div>
</div></div>
<script>
let carrito=[], fotoTemp='', logoTemp='', categoriaFiltro='todas', editId=null, currentUser=null, negocioId=null, ultimoTicket=null, editInvId=null;
function getFechaLocal(){ return new Date().toLocaleString('es-MX'); }
function getFechaSoloLocal(){ let n=new Date(); return `${n.getFullYear()}-${String(n.getMonth()+1).padStart(2,'0')}-${String(n.getDate()).padStart(2,'0')}`; }
let fechaVista=new Date(), fechaSel=getFechaSoloLocal();
function msgLogin(t,ok){let el=document.getElementById('loginMsg'); el.innerText=t; el.classList.remove('hidden'); el.className='mt-3 text-[11px] font-bold text-center p-2 rounded-xl '+(ok?'bg-green-100 text-green-700':'bg-red-100 text-red-700');}
async function hacerRegistro(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); if(!e||!p) return msgLogin('Pon correo',false); let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})}); let j=await r.json(); if(!j.ok) return msgLogin(j.msg,false); msgLogin('✅ Creada',true);}
async function hacerLogin(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); if(!e||!p) return msgLogin('Pon correo',false); let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})}); let j=await r.json(); if(!j.ok) return msgLogin('Error',false); currentUser=e; negocioId=j.negocio_id; localStorage.setItem('session_email',e); localStorage.setItem('session_negocio',negocioId); document.getElementById('loginScreen').classList.add('hidden'); document.getElementById('userLabel').innerText=e; await cargarDeNube();}
function cerrarSesion(){localStorage.removeItem('session_email'); localStorage.removeItem('session_negocio'); location.reload();}
async function cargarDeNube(){if(!currentUser) return; let r=await fetch('/api/load?email='+encodeURIComponent(currentUser)); let j=await r.json(); if(!j.ok) return; let data=j.data||{}; for(let k in data){ localStorage.setItem(k+'_'+negocioId, data[k]); } renderInventarioMaster(); cargarEmpresa();}
async function guardarEnNube(){if(!currentUser) return; let keys=['inventarioMaestro','productosV2','clientesV2','facturas','proveedores','deudas','gastosFijos','empresaConfig']; let data={}; keys.forEach(k=>{ let v=localStorage.getItem(k+'_'+negocioId)||localStorage.getItem(k); if(v) data[k]=v; }); await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:currentUser,data})});}
window.addEventListener('load', async ()=>{ let e=localStorage.getItem('session_email'); let n=localStorage.getItem('session_negocio'); if(e&&n){ document.getElementById('loginEmail').value=e; currentUser=e; negocioId=n; document.getElementById('loginScreen').classList.add('hidden'); document.getElementById('userLabel').innerText=e; await cargarDeNube(); }});
function getInv(){ return JSON.parse(localStorage.getItem('inventarioMaestro_'+negocioId)||localStorage.getItem('inventarioMaestro')||'[]'); }
function getEmp(){ return JSON.parse(localStorage.getItem('empresaConfig_'+negocioId)||localStorage.getItem('empresaConfig')||'{"nombre":"Mi Negocio","logo":""}'); }
function setItem(k,v){ localStorage.setItem(k+'_'+negocioId, typeof v==='string'? v: JSON.stringify(v)); localStorage.setItem(k, typeof v==='string'? v: JSON.stringify(v)); guardarEnNube(); }
function normalizarUnidad(u){ u=(u||'').toLowerCase().trim(); if(['g','gr'].includes(u)) return 'g'; if(['kg'].includes(u)) return 'kg'; if(['L','l','litro'].includes(u)) return 'L'; if(['ml'].includes(u)) return 'ml'; return u||'kg'; }
function factorABase(u){ u=normalizarUnidad(u); let m={g:1,kg:1000,ml:1,L:1000,pza:1}; return m[u]||1; }
function convertir(cant,de,a){ de=normalizarUnidad(de); a=normalizarUnidad(a); if(de==a) return cant; return cant*factorABase(de)/factorABase(a); }
function parseNumTxt(v){ v=String(v||'').trim().replace(',','.').toLowerCase(); if(!v) return 0; let limpio=v.replace(/[^0-9.\\/]/g,''); if(!limpio) return 0; if(limpio.includes('/')){ let p=limpio.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1); } return parseFloat(limpio)||0; }
function parseCantidadTexto(t,u){ if(!t) return 0; t=t.toString().toLowerCase(); let num=parseNumTxt(t); if(t.includes('kg')) return convertir(num,'kg',u); if(t.includes('ml')) return convertir(num,'ml',u); if((t.includes(' g')||t.endsWith('g'))&&!t.includes('kg')) return convertir(num,'g',u); if(t.includes('l')&&!t.includes('ml')) return convertir(num,'L',u); return num; }
function showTab(t){ ['costos','vender','inventario','finanzas','clientes','config','proveedores'].forEach(x=>{ let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hidden',x!=t); }); }
function previewLogo(input){ if(input.files&&input.files[0]){ let r=new FileReader(); r.onload=function(e){ logoTemp=e.target.result; let img=document.getElementById('logoPreview'); if(img){ img.src=logoTemp; document.getElementById('logoPreviewBox').classList.remove('hidden'); } let bg=document.getElementById('logoBg'); if(bg){ bg.src=logoTemp; bg.classList.remove('hidden'); bg.style.opacity='0.18'; } let hd=document.getElementById('logoHeader'); if(hd){ hd.src=logoTemp; hd.classList.remove('hidden'); } }; r.readAsDataURL(input.files[0]); } }
function quitarLogo(){ logoTemp=''; let box=document.getElementById('logoPreviewBox'); if(box) box.classList.add('hidden'); let bg=document.getElementById('logoBg'); if(bg) bg.classList.add('hidden'); let hd=document.getElementById('logoHeader'); if(hd) hd.classList.add('hidden'); }
function cargarEmpresa(){ let emp=getEmp(); let el=document.getElementById('empNombre'); if(el) el.value=emp.nombre||''; if(emp.logo){ logoTemp=emp.logo; let img=document.getElementById('logoPreview'); if(img){ img.src=logoTemp; document.getElementById('logoPreviewBox').classList.remove('hidden'); } let bg=document.getElementById('logoBg'); if(bg){ bg.src=logoTemp; bg.classList.remove('hidden'); } let hd=document.getElementById('logoHeader'); if(hd){ hd.src=logoTemp; hd.classList.remove('hidden'); } } }
function guardarEmpresa(){ let emp={nombre:document.getElementById('empNombre').value||'Mi Negocio', logo:logoTemp||getEmp().logo||'', mensaje:'¡Gracias!'}; setItem('empresaConfig',emp); alert('✅ Logo y empresa guardados'); }
function addInventario(){
 let n=document.getElementById('inv-nombre').value.trim(); if(!n) return alert('Pon nombre');
 let c=parseNumTxt(document.getElementById('inv-costo').value);
 let sTxt=document.getElementById('inv-stock').value.trim()||'0';
 let u=document.getElementById('inv-unit').value;
 let s=parseCantidadTexto(sTxt,u);
 let inv=getInv();
 if(editInvId){
  let b=inv.find(x=>String(x.id)==String(editInvId)); if(b){ b.nombre=n; b.costo=c; b.stock=s; b.unidad=u; b.precio=c; }
  editInvId=null; document.getElementById('btnAddInventario').innerText='+'; document.getElementById('btnAddInventario').classList.remove('bg-yellow-400');
 }else{
  inv.push({id:Date.now().toString(), nombre:n, costo:c, stock:s, unidad:u, precio:c});
 }
 setItem('inventarioMaestro',inv);
 document.getElementById('inv-nombre').value=''; document.getElementById('inv-costo').value=''; document.getElementById('inv-stock').value='';
 renderInventarioMaster();
}
function editarInventarioMaster(id){
 let b=getInv().find(x=>String(x.id)==String(id)); if(!b) return;
 editInvId=id;
 document.getElementById('inv-nombre').value=b.nombre;
 document.getElementById('inv-costo').value=b.costo||b.precio||'';
 document.getElementById('inv-stock').value=b.stock||'';
 document.getElementById('inv-unit').value=b.unidad||'kg';
 document.getElementById('btnAddInventario').innerText='Actualizar';
 document.getElementById('btnAddInventario').classList.add('bg-yellow-400','text-black');
 window.scrollTo({top:0,behavior:'smooth'});
}
function renderInventarioMaster(){
 let inv=getInv(); let cont=document.getElementById('contInventario')||document.getElementById('listaInvMaster'); if(!cont) return;
 cont.innerHTML=inv.map(b=>`<div class="bg-white border-2 border-black rounded-[18px] p-3 flex justify-between items-center mb-2"><div class="flex items-center gap-3"><div class="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center text-[20px] overflow-hidden"><img src="${b.foto||''}" onerror="this.style.display='none'" class="w-full h-full object-cover"></div><div><b>${b.nombre}</b><br><span class="text-[11px]">Stock ${b.stock} ${b.unidad} - $${b.costo||b.precio}</span></div></div><div class="flex gap-2"><button onclick="editarInventarioMaster('${b.id}')" class="bg-yellow-200 border-2 border-black rounded-full px-2 py-1 text-[12px] font-black">✏️</button><button onclick="if(confirm('Borrar?')){setItem('inventarioMaestro',getInv().filter(x=>x.id!='${b.id}')); renderInventarioMaster();}" class="text-red-400 font-black">X</button></div></div>`).join('')||'<p class="text-center text-gray-400 text-[11px]">Sin inventario - prueba Papas $30 500 g</p>';
 let cont2=document.getElementById('listaInvMaster'); if(cont2&&cont2!==cont) cont2.innerHTML=cont.innerHTML;
 let listaInv=document.getElementById('listaInv'); if(listaInv) listaInv.innerHTML=cont.innerHTML;
}
function renderProveedores(){}
function renderClientes(){}
function renderCalendario(){}
function renderVenta(){}
function renderFijos(){}
</script></body></html>"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
