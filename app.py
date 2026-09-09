from flask import Flask, jsonify, send_file, request
import os, json, requests
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
 with open(USERS_FILE,'w') as f: json.dump(u,f)
def get_user_file(nid):
 safe=nid.replace("@","_at_").replace(".","_")
 return os.path.join(BASE_DATA, f"{safe}.json")
@app.route('/manifest.json')
def manifest():
 return jsonify({"name":"Mi Negocio 11.5.2","short_name":"Mi Negocio","start_url":"/","display":"standalone"})
@app.route('/logo.png')
def logo_file():
 for r in ['logo.png','api/logo.png']:
  if os.path.exists(r): return send_file(r, mimetype='image/png')
 return "",204
@app.route('/api/login', methods=['POST'])
def api_login():
 d=request.json; e=d.get('email','').lower().strip(); p=d.get('password','')
 users=load_users()
 if e not in users:
  users[e]={"password":p,"negocio_id":e}; save_users(users)
  fp=get_user_file(e)
  if not os.path.exists(fp):
   with open(fp,'w') as f: json.dump({},f)
  return jsonify({"ok":True,"email":e,"negocio_id":e})
 users[e]['password']=p; save_users(users)
 return jsonify({"ok":True,"email":e,"negocio_id":e})
@app.route('/api/load', methods=['GET'])
def api_load():
 e=request.args.get('email','').lower().strip(); users=load_users()
 if e not in users: users[e]={"password":"temp","negocio_id":e}; save_users(users)
 fp=get_user_file(e); data=json.load(open(fp)) if os.path.exists(fp) else {}
 return jsonify({"ok":True,"data":data})
@app.route('/api/save', methods=['POST'])
def api_save():
 d=request.json; e=d.get('email','').lower().strip(); data=d.get('data',{})
 users=load_users()
 if e not in users: users[e]={"password":"temp","negocio_id":e}; save_users(users)
 with open(get_user_file(e),'w') as f: json.dump(data,f)
 return jsonify({"ok":True})
@app.route('/')
def home():
 return """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Negocio 11.5.2</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>input,select,textarea{color:#000!important;background:#fff!important}.logo-watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:600px;height:600px;pointer-events:none;z-index:0;opacity:0.15;object-fit:contain;}#appContent{position:relative;z-index:1;}#splash{position:fixed;inset:0;background:white;z-index:9999;display:flex;align-items:center;justify-content:center;flex-direction:column}</style></head><body class="bg-[#FFF8F0] min-h-screen"><div id="splash"><p style="font-weight:900">Mi Negocio 11.5.2</p><p style="font-size:11px">Solo parche de inventario en producto</p></div><script>setTimeout(()=>document.getElementById('splash').style.display='none',800)</script><div class="max-w-md mx-auto pb-[140px] relative"><img id="logoBg" class="logo-watermark hidden"><div id="appContent"><div id="loginScreen" class="fixed inset-0 bg-[#FFF8F0] z-[100] flex flex-col items-center justify-center p-6"><h1 class="font-black text-[22px]">Mi Negocio 11.5.2</h1><div class="bg-white w-full rounded-[28px] p-5 shadow-xl border-2 border-black mt-6"><input id="loginEmail" type="email" placeholder="Correo" value="esaul_1987@hotmail.com" class="w-full border-2 border-black p-4 rounded-2xl font-bold"><input id="loginPass" type="password" placeholder="Contraseña" class="w-full border-2 border-black p-4 rounded-2xl font-bold mt-3"><button onclick="hacerLogin()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">ENTRAR</button><button onclick="entrarLocal()" class="w-full mt-2 bg-yellow-400 border-2 border-black py-3 rounded-2xl font-black text-[12px]">⚡ ENTRAR SIN INTERNET</button></div></div><div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><div class="flex items-center gap-2"><img id="logoHeader" class="w-12 h-12 rounded-full object-cover border-2 border-black hidden"><div><h1 class="font-black text-[14px]">Mi Negocio 11.5.2</h1><p id="userLabel" class="text-[10px] text-gray-500"></p></div></div><div class="flex gap-2"><button onclick="showTab('config')" class="text-[10px] bg-black text-white px-3 py-2 rounded-full">Config</button><button onclick="cerrarSesion()" class="text-[10px] bg-red-100 text-red-600 px-2 py-1 rounded-full">Salir</button></div></div><div id="tab-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div><div class="mt-6 bg-white rounded-[28px] p-4 shadow-xl border-2 border-black"><select id="selCliente" class="w-full border-2 border-black p-3 rounded-xl text-[12px] font-bold mb-3"></select><div id="ticket" class="space-y-2">Vacio</div><div class="flex justify-between font-black text-[20px] mt-3 border-t-2 pt-3">Total $ <span id="c-total">0</span></div><button onclick="abrirCobro()" class="w-full mt-3 bg-black text-white py-4 rounded-2xl font-black">COBRAR</button></div></div><div id="tab-costos" class="p-3"><div id="crear-menu" class="space-y-4"><div class="bg-white rounded-[28px] p-5 shadow-sm border-2 border-black"><h2 class="font-black">Gastos Fijos</h2><div class="grid grid-cols-5 gap-2 mt-3"><input id="fijoNombre" placeholder="Renta" class="col-span-2 border-2 border-black p-3 rounded-xl font-bold text-[12px]"><input id="fijoMonto" type="number" placeholder="$3000" class="col-span-2 border-2 border-black p-3 rounded-xl font-black text-[12px]"><button onclick="addFijo()" class="bg-black text-white rounded-xl font-black">+</button></div><div id="listaFijos" class="mt-3 space-y-2"></div></div><div class="bg-white rounded-[28px] p-5 shadow-sm text-center"><button onclick="setCrear('base')" class="w-full bg-[#FFF8F0] border-2 border-black rounded-[20px] p-5 font-black">1. HACER BASE (salsas)</button><button onclick="setCrear('producto')" class="w-full mt-3 bg-[#0F172A] text-white rounded-[20px] p-5 font-black">2. HACER PRODUCTO (ahora con inventario)</button></div><div class="bg-white rounded-[20px] p-4"><h3 class="font-black text-[14px] mb-2">Mis creaciones</h3><div id="listaInv"></div></div></div><div id="crear-base" class="hidden"><button onclick="cancelarEdicion()" class="mb-3 font-bold">← Volver</button><div class="bg-white rounded-[28px] p-4 shadow-sm"><h2 class="font-black">HACER BASE</h2><input id="nombre" placeholder="Ej: Salsa bbq" class="w-full border-2 border-black p-4 rounded-2xl font-bold mt-3"><div id="insumos" class="mt-4 space-y-3"></div><button onclick="addInsumo()" class="w-full mt-3 bg-orange-100 border-2 border-black py-3 rounded-2xl font-black text-[12px]">+ Ingrediente de inventario</button><div class="mt-3 p-4 bg-[#0F172A] text-white rounded-[16px]"><div class="flex justify-between"><span>Ingredientes</span><b>$<span id="c-ing">0.00</span></b></div><div class="flex justify-between font-black border-t border-white/20 mt-2 pt-2"><span>Costo</span><span>$<span id="costo">0.00</span></span></div><div class="flex justify-between mt-2 text-[#4FD1C5]"><span>Venta</span><span>$<span id="venta">0.00</span></span></div><input id="margen" type="number" value="0" class="w-full mt-2 text-black rounded-lg text-center font-black py-2" oninput="calc()"></div><button onclick="guardarProd('recetario')" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR BASE</button></div></div><div id="crear-producto" class="hidden"><button onclick="cancelarEdicion()" class="mb-3 font-bold">← Volver</button><div class="bg-white rounded-[28px] p-4"><h2 class="font-black">HACER PRODUCTO FINAL - 11.5.2</h2><p class="text-[10px] bg-yellow-100 p-2 rounded-lg mt-2 font-bold">Ahora puedes mezclar inventario (alitas, papas, lechuga) + bases (salsa)</p><input id="nombreProd" placeholder="Ej: Alitas bbq con papas" class="w-full border-2 border-black p-4 rounded-2xl font-bold mt-2"><div id="basesSel" class="mt-4 space-y-3 bg-amber-50 border-2 border-black p-3 rounded-2xl min-h-[120px]"></div><button onclick="addBase()" class="w-full mt-2 bg-yellow-400 border-2 border-black py-3 rounded-xl font-black text-[12px]">+ AGREGAR INVENTARIO O BASE</button><div class="mt-3 p-4 bg-black text-white rounded-[16px]"><div class="flex justify-between text-[13px]"><span>Ingredientes</span><b>$<span id="c-ing2">0.00</span></b></div><div class="flex justify-between font-black text-[16px] mt-2 border-t border-white/20 pt-2"><span>Costo total</span><span>$<span id="costo2">0.00</span></span></div><div class="flex justify-between font-black text-[16px] mt-1"><span>Venta</span><span class="text-[#4FD1C5]">$<span id="venta2">0.00</span></span></div><input id="margen2" type="number" value="100" class="w-full mt-2 text-black rounded-lg text-center font-black py-1" oninput="calc2()"></div><button onclick="guardarProd('catalogo')" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR PRODUCTO</button></div></div></div><div id="tab-config" class="p-3 hidden"><div class="bg-white rounded-[28px] p-5 shadow-sm"><h2 class="font-black">Config</h2><div class="mt-4 bg-gray-50 border-2 rounded-[20px] p-4"><input id="empNombre" placeholder="Nombre negocio" class="w-full border-2 border-black p-3 rounded-xl mt-3 font-bold"></div><button onclick="guardarEmpresa()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR</button></div></div><div id="tab-clientes" class="p-3 hidden"><div id="listaClientes" class="space-y-3"></div></div><div id="tab-proveedores" class="p-3 hidden"><div id="listaProveedores" class="space-y-3"></div></div><div id="tab-inventario" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[28px] p-4 text-white mb-3"><h2 class="font-black">📦 Inventario</h2></div><div class="bg-white rounded-[20px] p-4"><div class="grid grid-cols-6 gap-1"><input id="inv-nombre" placeholder="Alita" class="col-span-2 border-2 border-black p-2 rounded-xl font-bold text-[12px]"><input id="inv-precio" type="number" placeholder="$" class="border-2 border-black p-2 rounded-xl font-black text-[12px]"><input id="inv-stock" type="text" placeholder="500 g" class="col-span-2 border-2 border-black p-2 rounded-xl font-black text-[12px]"><button onclick="addInventario()" class="bg-black text-white rounded-xl font-black">+</button></div><select id="inv-unidad" class="w-full border-2 border-black p-2 rounded-xl text-[11px] font-bold mt-2"><option value="kg">kg</option><option value="g">g</option><option value="L">L</option><option value="ml">ml</option><option value="pza">pza</option></select><div id="listaInvMaster" class="mt-4"></div></div></div><div id="tab-finanzas" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[24px] p-4 text-white"><h2 class="font-black">Finanzas</h2><p id="fin-balance" class="font-black">$0</p></div><div id="flu-lista" class="mt-4 space-y-2 bg-white p-4 rounded-xl"></div></div><div id="modalCobro" class="hidden fixed inset-0 bg-black/70 z-50 flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5"><h2 class="font-black">Cobrar $<span id="cobroTotal">0</span></h2><button onclick="confirmarCobro()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">CONFIRMAR</button><button onclick="cerrarCobro()" class="w-full mt-2 bg-gray-100 py-3 rounded-xl">Cancelar</button></div></div><div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30"><button onclick="showTab('costos')" class="flex flex-col items-center"><span class="text-[7px]">Crear</span></button><button onclick="showTab('vender')" class="flex flex-col items-center"><span class="text-[7px]">Vender</span></button><button onclick="showTab('inventario')" class="flex flex-col items-center"><span class="text-[7px]">Invent</span></button><button onclick="showTab('finanzas')" class="flex flex-col items-center"><span class="text-[7px]">Finanzas</span></button><button onclick="showTab('clientes')" class="flex flex-col items-center"><span class="text-[7px]">Clientes</span></button><button onclick="showTab('proveedores')" class="flex flex-col items-center"><span class="text-[7px]">Prov</span></button></div></div></div><script>
let carrito=[], editId=null, currentUser=null, negocioId=null;
function getFechaLocal(){return new Date().toLocaleString('es-MX')}
function getFechaSoloLocal(){return new Date().toISOString().slice(0,10)}
async function hacerLogin(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); currentUser=e; negocioId=e; localStorage.setItem('session_email',e); localStorage.setItem('session_negocio',e); document.getElementById('loginScreen').classList.add('hidden'); renderFijos(); renderInventario(); renderInventarioMaster(); renderClientes(); renderProveedores(); showTab('costos');}
function entrarLocal(){hacerLogin()}
function cerrarSesion(){location.reload();}
function getFijos(){return JSON.parse(localStorage.getItem('gastosFijos_'+negocioId)||'[]')}
function getProd(){return JSON.parse(localStorage.getItem('productosV2_'+negocioId)||'[]')}
function getInv(){return JSON.parse(localStorage.getItem('inventarioMaestro_'+negocioId)||'[]')}
function getFacts(){return JSON.parse(localStorage.getItem('facturas_'+negocioId)||'[]')}
function getCli(){return JSON.parse(localStorage.getItem('clientesV2_'+negocioId)||'[]')}
function getProveedores(){return JSON.parse(localStorage.getItem('proveedores_'+negocioId)||'[]')}
function getEmp(){return JSON.parse(localStorage.getItem('empresaConfig_'+negocioId)||'{"nombre":"Mi negocio"}')}
function setItem(k,v){localStorage.setItem(k+'_'+negocioId, JSON.stringify(v));}
function normalizarUnidad(u){u=(u||'').toLowerCase(); if(['g','gr'].includes(u)) return 'g'; if(['kg'].includes(u)) return 'kg'; if(['l','litro'].includes(u)) return 'L'; if(['ml'].includes(u)) return 'ml'; return u||'kg';}
function factorABase(u){u=normalizarUnidad(u); let m={g:1,kg:1000,ml:1,L:1000,pza:1}; return m[u]||1;}
function convertir(c,de,a){de=normalizarUnidad(de); a=normalizarUnidad(a); if(de==a) return c; return c*factorABase(de)/factorABase(a);}
function parseCantidadTexto(t, base){if(!t) return 0; t=t.toString().toLowerCase().replace(',', '.'); let num=parseFloat(t); if(isNaN(num)) return 0; if(t.includes('kg')) return convertir(num,'kg',base); if(t.includes('ml')) return convertir(num,'ml',base); if(t.includes('g') &&!t.includes('kg')) return convertir(num,'g',base); if(t.includes('l') &&!t.includes('ml')) return convertir(num,'L',base); return num;}
function showTab(t){['costos','vender','inventario','finanzas','clientes','config','proveedores'].forEach(x=>{let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hidden',x!=t);}); if(t=='costos') renderInventario(); if(t=='vender') renderVenta(); if(t=='inventario') renderInventarioMaster(); }
function addFijo(){let n=document.getElementById('fijoNombre').value.trim(), m=parseFloat(document.getElementById('fijoMonto').value); if(!n||!m) return; let f=getFijos(); f.push({id:Date.now().toString(),nombre:n,monto:m}); setItem('gastosFijos',f); renderFijos(); calc(); calc2();}
function renderFijos(){let f=getFijos(); window._costoFijoPorLote= f.reduce((s,x)=>s+x.monto,0)/30; let el=document.getElementById('listaFijos'); if(!el) return; el.innerHTML=f.map(x=>'<div class="flex justify-between bg-gray-50 p-3 rounded-xl border mt-2"><b>'+x.nombre+'</b><span>$'+x.monto+'</span></div>').join('');}
function setCrear(v){document.getElementById('crear-menu').classList.toggle('hidden',v!='menu'); document.getElementById('crear-base').classList.toggle('hidden',v!='base'); document.getElementById('crear-producto').classList.toggle('hidden',v!='producto'); if(v=='base'&&!editId){document.getElementById('insumos').innerHTML=''; document.getElementById('nombre').value=''; addInsumo({}); calc();} if(v=='producto'&&!editId){document.getElementById('basesSel').innerHTML=''; document.getElementById('nombreProd').value=''; addBase(); calc2();}}
function cancelarEdicion(){editId=null; setCrear('menu');}
function addInsumo(d={}){let inv=getInv(); let opts=inv.map(it=>'<option value="'+it.id+'" '+(d.invId==it.id?'selected':'')+'>'+it.nombre+' $'+it.precio+'/'+it.unidad+'</option>').join(''); let div=document.createElement('div'); div.className='insumo-row bg-[#FFF8F0] p-3 rounded-[16px] border-2'; div.innerHTML='<select class="in-n w-full bg-white border-2 border-black p-2 rounded-xl font-bold text-[13px]" onchange="calc()"><option value="">-- Ingrediente --</option>'+opts+'</select><div class="grid grid-cols-5 gap-2 mt-2"><input type="number" value="'+(d.cu||'')+'" placeholder="Cant" class="in-cu col-span-2 border-2 border-black p-3 rounded-xl font-bold" oninput="calc()"><select class="in-uu col-span-3 border-2 border-black p-3 rounded-xl font-bold" onchange="calc()"><option value="kg">kg</option><option value="g">g</option><option value="L">L</option><option value="ml">ml</option><option value="pza">pza</option></select></div><div class="text-right font-black text-[12px] mt-1">$<span class="in-sub">0.00</span></div><button onclick="this.parentElement.remove();calc()" class="text-red-400 text-[10px]">Quitar</button>'; document.getElementById('insumos').appendChild(div); if(d.uu) div.querySelector('.in-uu').value=d.uu; calc();}
function calc(){let tot=0; document.querySelectorAll('#insumos.insumo-row').forEach(row=>{let invId=row.querySelector('.in-n')?.value; let it=getInv().find(x=>String(x.id)==String(invId)); let cu=parseFloat(row.querySelector('.in-cu')?.value)||0; let uu=row.querySelector('.in-uu')?.value||'g'; let baseCost=0; if(it&&cu){let cant=convertir(cu,uu,it.unidad); baseCost=cant*it.precio;} if(row.querySelector('.in-sub')) row.querySelector('.in-sub').innerText=baseCost.toFixed(2); tot+=baseCost;}); document.getElementById('c-ing').innerText=tot.toFixed(2); document.getElementById('costo').innerText=tot.toFixed(2); let m=parseFloat(document.getElementById('margen').value)||0; document.getElementById('venta').innerText=(tot*(1+m/100)).toFixed(2);}
function addBase(d={}){
  let inv=getInv(); let bases=getProd().filter(p=>p.esBase);
  let optsInv=inv.map(it=>'<option value="inv:'+it.id+'" '+(d.type=='inv'&&String(d.invId)==String(it.id)?'selected':'')+'>[INV] '+it.nombre+' $'+it.precio+'/'+it.unidad+' stock:'+parseFloat(it.stock).toFixed(1)+'</option>').join('');
  let optsBase=bases.map(b=>'<option value="base:'+b.id+'" '+(d.type=='base'&&String(d.baseId)==String(b.id)?'selected':'')+'>[BASE] '+b.nombre+' $'+b.costo.toFixed(2)+'</option>').join('');
  let div=document.createElement('div'); div.className='comp-row bg-white border-2 border-black rounded-xl p-2';
  div.innerHTML='<select class="b-sel w-full border-2 border-black p-2 rounded-lg font-bold text-[12px]" onchange="calc2()"><option value="">-- Elige ingrediente o base --</option><optgroup label="INVENTARIO (alitas, papas, lechuga)">'+optsInv+'</optgroup><optgroup label="TUS BASES (salsas)">'+optsBase+'</optgroup></select><div class="grid grid-cols-6 gap-2 mt-2"><input type="number" value="'+(d.cu||'')+'" placeholder="Ej 300" class="b-cu col-span-2 border-2 border-black p-2 rounded-lg font-black text-[12px]" oninput="calc2()"><select class="b-uu col-span-2 border-2 border-black p-2 rounded-lg font-bold text-[11px]" onchange="calc2()"><option value="g">g</option><option value="kg">kg</option><option value="ml">ml</option><option value="L">L</option><option value="pza">pza</option></select><button onclick="this.parentElement.parentElement.remove();calc2()" class="col-span-2 bg-red-100 text-red-600 rounded-lg font-black text-[11px]">Quitar</button></div><div class="text-right text-[10px] font-bold">Sub: $<span class="b-sub">0.00</span></div>';
  document.getElementById('basesSel').appendChild(div); if(d.uu) div.querySelector('.b-uu').value=d.uu; calc2();
}
function calc2(){
  let tot=0;
  document.querySelectorAll('#basesSel.comp-row').forEach(row=>{
    let val=row.querySelector('.b-sel')?.value||''; let cu=parseFloat(row.querySelector('.b-cu')?.value)||0; let uu=row.querySelector('.b-uu')?.value||'g'; let sub=0;
    if(!val||!cu){ row.querySelector('.b-sub').innerText='0.00'; return; }
    if(val.startsWith('inv:')){
      let it=getInv().find(x=>String(x.id)==String(val.split(':')[1]));
      if(it){ sub=convertir(cu,uu,it.unidad)*it.precio; }
    }else if(val.startsWith('base:')){
      let b=getProd().find(x=>String(x.id)==String(val.split(':')[1]));
      if(b){ sub=b.costo*cu; }
    }
    row.querySelector('.b-sub').innerText=sub.toFixed(2); tot+=sub;
  });
  document.getElementById('c-ing2').innerText=tot.toFixed(2);
  document.getElementById('costo2').innerText=tot.toFixed(2);
  let m=parseFloat(document.getElementById('margen2').value)||0;
  document.getElementById('venta2').innerText=(tot*(1+m/100)).toFixed(2);
}
function guardarProd(tipo){
  let isBase=tipo=='recetario';
  let nomEl=isBase?document.getElementById('nombre'):document.getElementById('nombreProd');
  let nom=nomEl.value.trim(); if(!nom) return alert('Pon nombre');
  let costo=parseFloat((isBase?document.getElementById('costo'):document.getElementById('costo2')).innerText)||0;
  let venta=parseFloat((isBase?document.getElementById('venta'):document.getElementById('venta2')).innerText)||0;
  let ps=getProd(); let receta=[];
  if(isBase){
    document.querySelectorAll('#insumos.insumo-row').forEach(row=>{
      let invId=row.querySelector('.in-n')?.value;
      let cu=row.querySelector('.in-cu')?.value;
      let uu=row.querySelector('.in-uu')?.value;
      if(invId&&cu) receta.push({type:'inv', invId, cu:parseFloat(cu), uu});
    });
  }else{
    document.querySelectorAll('#basesSel.comp-row').forEach(row=>{
      let val=row.querySelector('.b-sel')?.value||'';
      let cu=parseFloat(row.querySelector('.b-cu')?.value)||0;
      let uu=row.querySelector('.b-uu')?.value||'g';
      if(!val||!cu) return;
      if(val.startsWith('inv:')) receta.push({type:'inv', invId:val.split(':')[1], cu, uu});
      if(val.startsWith('base:')) receta.push({type:'base', baseId:val.split(':')[1], cu, uu});
    });
    if(!receta.length) return alert('Agrega al menos 1 ingrediente de inventario o base');
  }
  let margen=parseFloat((isBase?document.getElementById('margen'):document.getElementById('margen2'))?.value)||0;
  if(editId){
    let idx=ps.findIndex(p=>String(p.id)==String(editId));
    if(idx>=0){ps[idx].nombre=nom; ps[idx].costo=costo; ps[idx].venta=venta; ps[idx].receta=receta; ps[idx].margen=margen; ps[idx].esBase=isBase;}
  }else{
    ps.push({id:Date.now(),nombre:nom,costo,venta,receta,margen,esBase:isBase});
  }
  setItem('productosV2',ps); alert('Guardado: '+nom); editId=null; renderInventario(); setCrear('menu'); renderVenta();
}
function renderInventario(){let ps=getProd(); let el=document.getElementById('listaInv'); if(!el) return; el.innerHTML=ps.map(p=>'<div class="bg-white p-3 rounded-2xl flex gap-3 shadow-sm mt-3 border-2 items-center"><div class="flex-1"><b>'+p.nombre+'</b> '+(p.esBase?'<span class="text-[8px] bg-orange-100 px-1 rounded">BASE</span>':'<span class="text-[8px] bg-black text-white px-1 rounded">PROD</span>')+'<br>$'+p.costo.toFixed(2)+' → $'+p.venta.toFixed(2)+'<br><span class="text-[9px] text-gray-500">'+(p.receta||[]).map(r=>{if(r.type=='inv'){let it=getInv().find(x=>String(x.id)==String(r.invId)); return it? it.nombre+':'+r.cu+r.uu:''}else{let b=getProd().find(x=>String(x.id)==String(r.baseId)); return b? b.nombre+':'+r.cu+r.uu:''}}).join(', ')+'</span></div><button onclick="setItem(\\'productosV2\\',getProd().filter(x=>String(x.id)!=\\''+p.id+'\\')); renderInventario(); renderVenta();" class="bg-red-100 text-red-600 w-10 h-10 rounded-full">X</button></div>').join('');}
function addInventario(){let n=document.getElementById('inv-nombre').value.trim(); let p=parseFloat(document.getElementById('inv-precio').value)||0; let stockTxt=document.getElementById('inv-stock').value.trim()||'0'; let u=document.getElementById('inv-unidad').value||'kg'; if(!n) return; let stock=parseCantidadTexto(stockTxt, u); let inv=getInv(); inv.push({id:Date.now().toString(),nombre:n,precio:p,stock:stock,unidad:u}); setItem('inventarioMaestro',inv); document.getElementById('inv-nombre').value=''; document.getElementById('inv-precio').value=''; document.getElementById('inv-stock').value=''; renderInventarioMaster(); renderInventario();}
function renderInventarioMaster(){let inv=getInv(); let el=document.getElementById('listaInvMaster'); if(!el) return; el.innerHTML=inv.map(it=>'<div class="flex gap-2 items-center bg-gray-50 p-3 rounded-xl border mb-2"><div class="flex-1"><b>'+it.nombre+'</b> <span class="text-[10px] bg-white border px-2 py-0.5 rounded-full">'+parseFloat(it.stock).toFixed(2)+' '+it.unidad+' - $'+it.precio+'</span></div><button onclick="if(confirm(\\'Borrar?\\')){setItem(\\'inventarioMaestro\\',getInv().filter(x=>String(x.id)!=\\''+it.id+'\\')); renderInventarioMaster();}" class="text-red-400">X</button></div>').join('');}
function renderVenta(){let ps=getProd().filter(p=>!p.esBase); let cont=document.getElementById('listaVenta'); if(!cont) return; cont.innerHTML=ps.map(p=>'<div class="bg-white rounded-2xl shadow-sm border p-3"><b>'+p.nombre+'</b><p class="text-green-600 font-black">$'+p.venta.toFixed(2)+'</p><p class="text-[9px]">'+(p.receta||[]).length+' ingredientes</p><button onclick="carrito.push({...getProd().find(x=>String(x.id)==String('+p.id+')),qty:1}); renderCarrito()" class="w-full mt-2 bg-black text-white py-2 rounded-xl text-[11px]">Agregar</button></div>').join('');}
function renderCarrito(){if(!carrito.length){document.getElementById('ticket').innerHTML='Vacio'; document.getElementById('c-total').innerText='0'; document.getElementById('cobroTotal').innerText='0'; return;} let sub=0,h=''; carrito.forEach((x,idx)=>{sub+=x.venta*x.qty; h+='<div class="flex justify-between bg-gray-50 p-2 rounded-xl"><span>'+x.nombre+' x'+x.qty+'</span><span>$'+(x.venta*x.qty).toFixed(0)+' <button onclick="carrito.splice('+idx+',1); renderCarrito();" class="text-red-500">X</button></span></div>';}); document.getElementById('ticket').innerHTML=h; document.getElementById('c-total').innerText=sub.toFixed(0); document.getElementById('cobroTotal').innerText=sub.toFixed(0);}
function abrirCobro(){if(!carrito.length) return alert('Vacio'); document.getElementById('modalCobro').classList.remove('hidden');}
function cerrarCobro(){document.getElementById('modalCobro').classList.add('hidden');}
function confirmarCobro(){
  let inv=getInv(); let prod=getProd();
  carrito.forEach(itemCar=>{
    let producto=prod.find(p=>String(p.id)==String(itemCar.id)); if(!producto||!producto.receta) return;
    let qty=itemCar.qty||1;
    producto.receta.forEach(r=>{
      if(r.type=='inv'){
        let ing=inv.find(i=>String(i.id)==String(r.invId)); if(!ing) return;
        let uso=convertir(r.cu,r.uu,ing.unidad)*qty; ing.stock=parseFloat(ing.stock)-uso; if(ing.stock<0) ing.stock=0;
      }else if(r.type=='base'){
        let base=prod.find(b=>String(b.id)==String(r.baseId)); if(!base||!base.receta) return;
        let mult=parseFloat(r.cu)||1;
        base.receta.forEach(ri=>{
          let ing=inv.find(i=>String(i.id)==String(ri.invId)); if(!ing) return;
          let uso=convertir(ri.cu,ri.uu,ing.unidad)*mult*qty; ing.stock=parseFloat(ing.stock)-uso; if(ing.stock<0) ing.stock=0;
        });
      }
    });
  });
  setItem('inventarioMaestro',inv);
  let facts=getFacts(); facts.push({id:Date.now(),concepto:'Venta: '+carrito.map(c=>c.nombre).join(', '),monto:parseFloat(document.getElementById('c-total').innerText)||0,fecha:getFechaSoloLocal()}); setItem('facturas',facts);
  carrito=[]; renderCarrito(); renderInventarioMaster(); cerrarCobro(); alert('Cobrado y descontado del inventario');
}
function renderClientes(){}
function renderProveedores(){}
function guardarEmpresa(){}
</script></body></html>
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
