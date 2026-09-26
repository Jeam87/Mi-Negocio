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

@app.route('/api/registro', methods=['POST'])
@app.route('/api/register', methods=['POST'])
def api_register():
    d=request.get_json(silent=True) or {}
    email=(d.get('email','') or '').lower().strip()
    pwd=d.get('password') or d.get('pass') or ''
    if not email or not pwd:
        return jsonify({"ok": False, "msg":"Falta email/pass"}),400
    users=load_users()
    if email in users:
        return jsonify({"ok":False,"msg":"Ya existe"}),400
    users[email]={"password":pwd,"negocio_id":email,"rol":"owner"}
    save_users(users)
    with open(get_user_file(email),'w') as f: json.dump({},f)
    return jsonify({"ok":True})

@app.route('/api/crear-link-cobro', methods=['POST'])
def crear_link_cobro():
    try:
        import stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe.api_key:
            return jsonify({"ok":False,"msg":"Falta STRIPE_SECRET_KEY"}),500
        data = request.get_json(silent=True) or {}
        monto = int(float(data.get('monto',0))*100)
        link = stripe.PaymentLink.create(line_items=[{"price_data":{"currency":"mxn","product_data":{"name":data.get('concepto','Pago')},"unit_amount":monto},"quantity":1}])
        return jsonify({"ok":True,"url": link.url})
    except Exception as e:
        return jsonify({"ok":False,"msg":str(e)}),500

@app.route('/api/login', methods=['POST'])
def api_login():
 d=request.get_json(silent=True) or {}; email=d.get('email','').lower().strip(); pwd=d.get('password','')
 users=load_users()
 if email not in users or users[email].get('password')!=pwd: return jsonify({"ok":False,"msg":"Correo o pass mal"}),401
 return jsonify({"ok":True,"email":email,"negocio_id":users[email]['negocio_id'],"rol":users[email]['rol']})

@app.route('/api/load', methods=['GET'])
def api_load():
 email=request.args.get('email','').lower().strip(); users=load_users()
 if email not in users: return jsonify({"ok":False}),404
 data=json.load(open(get_user_file(users[email]['negocio_id']))) if os.path.exists(get_user_file(users[email]['negocio_id'])) else {}
 return jsonify({"ok":True,"data":data})

@app.route('/api/save', methods=['POST'])
def api_save():
 d=request.get_json(silent=True) or {}; email=d.get('email','').lower().strip(); data=d.get('data',{})
 users=load_users()
 if email not in users: return jsonify({"ok":False}),404
 with open(get_user_file(users[email]['negocio_id']),'w') as f: json.dump(data,f)
 return jsonify({"ok":True})

@app.route('/')
def home():
 return '''
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Negocio 11.5</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"></head><body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[150px]"><div id="loginScreen" class="fixed inset-0 bg-[#FFF8F0] z-[100] flex flex-col items-center justify-center p-6"><h1 class="font-black">Mi Negocio 11.5 FINAL COLOR</h1><div class="bg-white w-full rounded-[28px] p-5 shadow-xl border-2 border-black mt-6"><input id="loginEmail" type="email" placeholder="Correo" class="w-full border-2 border-black p-4 rounded-2xl font-bold"><input id="loginPass" type="password" placeholder="Contraseña" class="w-full border-2 border-black p-4 rounded-2xl font-bold mt-3"><button onclick="hacerLogin()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">ENTRAR</button><button onclick="hacerRegistro()" class="w-full mt-2 bg-white border-2 border-black py-3 rounded-2xl font-bold">REGISTRARME</button><p id="loginMsg" class="hidden mt-3 text-[11px] font-bold text-center p-2 rounded-xl"></p></div></div>
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><div><h1 class="font-black text-[16px]">Mi Negocio 11.5</h1><p id="userLabel" class="text-[10px] text-gray-500"></p></div><button onclick="cerrarSesion()" class="text-[10px] bg-red-100 px-2 py-1 rounded-full">Salir</button></div>
<div id="tab-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div><div class="mt-6 bg-white rounded-[28px] p-4 shadow-xl border-2 border-black"><select id="selCliente" class="w-full border-2 border-black p-3 rounded-xl text-[12px] font-bold"></select><div id="ticket" class="space-y-2 mt-3">Vacio</div><div class="flex justify-between font-black text-[20px] mt-3 border-t-2 pt-3">Total $ <span id="c-total">0</span></div><div class="grid grid-cols-2 gap-2 mt-3"><button onclick="abrirCobro()" class="bg-black text-white py-4 rounded-2xl font-black">COBRAR</button><button onclick="guardarPresupuestoWhatsApp()" class="bg-[#25D366] text-white py-4 rounded-2xl font-black">PRESUPUESTO</button></div></div></div>
<div id="tab-costos" class="p-3"><div class="bg-white rounded-[20px] p-4 border-2 border-black"><h3 class="font-black mb-2">Mis recetas con color</h3><div id="listaInv"></div></div></div>
<div id="tab-inventario" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[28px] p-4 text-white mb-3"><h2 class="font-black">Inventario</h2></div><div class="bg-white rounded-[20px] p-4 border-2 border-black"><div id="listaInvMaster" class="mt-4"></div><div class="grid grid-cols-6 gap-1 mt-3"><input id="inv-nombre" placeholder="Prod" class="col-span-2 border-2 border-black p-2 rounded-xl"><input id="inv-precio" type="number" placeholder="$" class="border-2 border-black p-2 rounded-xl"><input id="inv-stock" placeholder="Stock" class="border-2 border-black p-2 rounded-xl"><select id="inv-unidad" class="border-2 border-black p-2 rounded-xl"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>pza</option></select><button onclick="addInventario()" class="bg-black text-white rounded-xl font-black">+</button></div></div></div>
<div id="tab-clientes" class="p-3 hidden"><div id="listaClientes"></div></div>
<div id="tab-proveedores" class="p-3 hidden"><div class="grid grid-cols-7 gap-1"><input id="provNombre" placeholder="Nombre" class="col-span-3 border-2 border-black p-2 rounded-xl"><input id="provTel" placeholder="Tel" class="col-span-2 border-2 border-black p-2 rounded-xl"><input id="provQue" placeholder="Que" class="col-span-1 border-2 border-black p-2 rounded-xl"><button onclick="addProveedor()" class="col-span-1 bg-yellow-400 text-black rounded-xl font-black">+</button></div><div id="listaProveedores" class="mt-3"></div></div>
<div id="tab-finanzas" class="p-3 hidden"><div id="calGrid" class="mt-4"></div><div id="flu-lista" class="mt-4"></div></div>
<div id="modalCobro" class="hidden fixed inset-0 bg-black/70 z-50 flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5"><h2 class="font-black">Cobrar $<span id="cobroTotal">0</span></h2><input id="pagoRecibido" type="number" placeholder="$ Recibido" class="w-full border-2 border-black p-3 rounded-xl mt-3 font-black" oninput="calcCambio()"><p>Cambio: $<span id="cambio">0.00</span></p><button onclick="crearLinkCobroStripe()" id="btnStripeLink" class="w-full mt-3 bg-blue-600 text-white py-4 rounded-2xl font-black border-2 border-blue-800">💳 COBRAR CON TARJETA - ENVIAR LINK</button><button onclick="confirmarCobro()" class="w-full mt-2 bg-gray-100 py-3 rounded-xl">Solo cobrar</button><button onclick="cerrarCobro()" class="w-full mt-2 bg-white border-2 border-black py-2 rounded-xl">Cancelar</button></div></div>
<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30"><button onclick="showTab('costos')">Crear</button><button onclick="showTab('vender')">Vender</button><button onclick="showTab('inventario')">Invent</button><button onclick="showTab('finanzas')">Finanzas</button><button onclick="showTab('clientes')">Clientes</button><button onclick="showTab('proveedores')">Prov</button></div></div></div>
<script>
let carrito=[], currentUser=null, negocioId=null;
function msgLogin(t){let e=document.getElementById('loginMsg'); e.innerText=t; e.classList.remove('hidden')}
async function hacerRegistro(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})}); let j=await r.json(); if(!j.ok) return msgLogin(j.msg); msgLogin('Cuenta creada')}
async function hacerLogin(){let e=document.getElementById('loginEmail').value.trim().toLowerCase(); let p=document.getElementById('loginPass').value.trim(); let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})}); let j=await r.json(); if(!j.ok) return msgLogin(j.msg); currentUser=e; negocioId=j.negocio_id; localStorage.setItem('session_email',e); localStorage.setItem('session_negocio',negocioId); document.getElementById('loginScreen').classList.add('hidden'); await cargarDeNube(); showTab('vender')}
function cerrarSesion(){localStorage.removeItem('session_email'); localStorage.removeItem('session_negocio'); location.reload()}
async function cargarDeNube(){if(!currentUser) return; let r=await fetch('/api/load?email='+encodeURIComponent(currentUser)); let j=await r.json(); if(!j.ok) return; let d=j.data||{}; for(let k in d){localStorage.setItem(k+'_'+negocioId,d[k])} renderInventario(); renderVenta(); renderInventarioMaster(); renderProveedores(); renderClientes()}
async function guardarEnNube(){if(!currentUser) return; let ks=['productosV2','inventarioMaestro','clientesV2','facturas','categoriasVenta','gastosFijos','empresaConfig','lotesMes','deudas','proveedores','presupuestos']; let data={}; ks.forEach(k=>{let v=localStorage.getItem(k+'_'+negocioId); if(v) data[k]=v}); await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:currentUser,data})})}
function getProd(){return JSON.parse(localStorage.getItem('productosV2_'+negocioId)||'[]')}
function getInv(){return JSON.parse(localStorage.getItem('inventarioMaestro_'+negocioId)||'[]')}
function getCli(){return JSON.parse(localStorage.getItem('clientesV2_'+negocioId)||'[]')}
function getProveedores(){return JSON.parse(localStorage.getItem('proveedores_'+negocioId)||'[]')}
function setItem(k,v){localStorage.setItem(k+'_'+negocioId,typeof v==='string'?v:JSON.stringify(v)); guardarEnNube()}
function renderInventario(){let ps=getProd(); let el=document.getElementById('listaInv'); if(!el) return; el.innerHTML=ps.map(p=>'<div class="bg-white p-4 rounded-[16px] border-2 border-black shadow-sm flex justify-between items-center mt-2"><div><b class="text-[13px]">'+p.nombre+'</b><br><span class="text-[11px] font-bold text-green-600">$'+(p.venta||0).toFixed(2)+'</span></div><div class="w-8 h-8 bg-black text-white rounded-full flex items-center justify-center text-[10px]">$</div></div>').join('')||'<p class="text-center text-gray-400">Sin recetas</p>';}
function renderVenta(){let ps=getProd().filter(p=>!p.esBase); let cont=document.getElementById('listaVenta'); if(!cont) return; cont.innerHTML=ps.map(p=>'<div class="bg-white rounded-[20px] shadow-sm border-2 border-black p-3 flex flex-col justify-between"><div><b class="text-[13px] block">'+p.nombre+'</b><p class="text-green-600 font-black text-[14px]">$'+(p.venta||0).toFixed(2)+'</p></div><button onclick="addCart(\\''+p.id+'\\')" class="w-full mt-2 bg-black text-white py-2 rounded-xl text-[11px] font-black">Agregar</button></div>').join('')||'<p class="col-span-2 text-center text-gray-400">Sin productos</p>';}
function addCart(id){let p=getProd().find(x=>String(x.id)==String(id)); let ex=carrito.find(x=>String(x.id)==String(id)); if(ex) ex.qty++; else carrito.push({...p,qty:1}); renderCarrito();}
function renderCarrito(){if(!carrito.length){document.getElementById('ticket').innerHTML='Vacío'; document.getElementById('c-total').innerText='0'; document.getElementById('cobroTotal').innerText='0'; return} let tot=0,h=''; carrito.forEach((x,i)=>{tot+=x.venta*x.qty; h+='<div class="flex justify-between bg-gray-50 p-2 rounded-xl border"><span class="text-[12px] font-bold">'+x.nombre+' x'+x.qty+'</span><span class="font-black">$'+(x.venta*x.qty).toFixed(0)+' <button onclick="carrito.splice('+i+',1);renderCarrito()" class="text-red-500">X</button></span></div>'}); document.getElementById('ticket').innerHTML=h; document.getElementById('c-total').innerText=tot.toFixed(0); document.getElementById('cobroTotal').innerText=tot.toFixed(0)}
function showTab(t){['costos','vender','inventario','finanzas','clientes','proveedores'].forEach(x=>{let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hidden',x!=t)}); if(t=='vender') renderVenta();}
function abrirCobro(){if(!carrito.length) return alert('Vacío'); document.getElementById('modalCobro').classList.remove('hidden');}
function cerrarCobro(){document.getElementById('modalCobro').classList.add('hidden');}
function calcCambio(){let t=parseFloat(document.getElementById('c-total').innerText)||0; let r=parseFloat(document.getElementById('pagoRecibido').value)||0; document.getElementById('cambio').innerText=(r-t>0?r-t:0).toFixed(2)}
function confirmarCobro(){let f=JSON.parse(localStorage.getItem('facturas_'+negocioId)||'[]'); f.push({id:Date.now(),monto:parseFloat(document.getElementById('c-total').innerText)||0,fecha:new Date().toISOString().slice(0,10),tipo:'entrada'}); setItem('facturas',f); cerrarCobro(); carrito=[]; renderCarrito();}
async function crearLinkCobroStripe(){
 let total=parseFloat(document.getElementById('c-total').innerText)||0;
 if(!total) return alert('Carrito vacio');
 document.getElementById('btnStripeLink').innerText='Generando...';
 try{
  let r=await fetch('/api/crear-link-cobro',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({monto:total,concepto:'Venta'})});
  let j=await r.json();
  if(!j.ok) throw new Error(j.msg||'Error');
  let tel=prompt('WhatsApp del cliente:')||'';
  tel=tel.replace(/\\D/g,''); if(tel.length==10) tel='52'+tel;
  let msg='Link de pago $'+total.toFixed(2)+':\\n'+j.url;
  if(tel) window.open('https://wa.me/'+tel+'?text='+encodeURIComponent(msg),'_blank');
  else prompt('Copia el link:',j.url);
  document.getElementById('btnStripeLink').innerText='Link enviado';
 }catch(e){ alert('Error: '+e.message); document.getElementById('btnStripeLink').innerText='COBRAR CON TARJETA - ENVIAR LINK'; }
}
function renderInventarioMaster(){let inv=getInv(); let el=document.getElementById('listaInvMaster'); if(el) el.innerHTML=inv.map(it=>'<div class="flex gap-2 items-center bg-white p-3 rounded-xl border-2 border-black mt-2 shadow-sm"><div class="flex-1"><b class="text-[13px]">'+it.nombre+'</b> <span class="text-[10px] bg-gray-100 px-2 py-1 rounded-full">Stock '+it.stock+'</span></div></div>').join('')||'Sin inventario'}
function addInventario(){let n=document.getElementById('inv-nombre').value.trim(); if(!n) return; let inv=getInv(); inv.push({id:Date.now().toString(),nombre:n,stock:document.getElementById('inv-stock').value||'0'}); setItem('inventarioMaestro',inv); renderInventarioMaster()}
function renderProveedores(){let p=getProveedores(); document.getElementById('listaProveedores').innerHTML=p.map(x=>'<div class="bg-white p-3 rounded-xl border-2 border-black mt-2">'+x.nombre+' '+x.tel+'</div>').join('')||'Sin proveedores'}
function addProveedor(){let n=document.getElementById('provNombre').value.trim(); if(!n) return; let p=getProveedores(); p.push({id:Date.now().toString(),nombre:n,tel:document.getElementById('provTel').value,que:document.getElementById('provQue').value}); setItem('proveedores',p); renderProveedores()}
function renderClientes(){let cli=getCli(); let sel=document.getElementById('selCliente'); if(sel){sel.innerHTML='<option value="">Mostrador</option>'+cli.map(c=>'<option value="'+c.id+'">'+c.nombre+'</option>').join('')} document.getElementById('listaClientes').innerHTML=cli.map(c=>'<div class="bg-white p-3 rounded-xl border-2 border-black mt-2">'+c.nombre+'</div>').join('')||'Sin clientes'}
function addClienteRapido(){let n=document.getElementById('quickClienteNombre').value.trim(); if(!n) return; let cli=getCli(); let nu={id:Date.now().toString(),nombre:n,tel:document.getElementById('quickClienteTel').value}; cli.push(nu); setItem('clientesV2',cli); renderClientes()}
function guardarPresupuestoWhatsApp(){let ps=JSON.parse(localStorage.getItem('presupuestos_'+negocioId)||'[]'); ps.push({id:Date.now(),cliente:'Mostrador',total:parseFloat(document.getElementById('c-total').innerText)||0}); setItem('presupuestos',ps); alert('Guardado')}
</script></body></html>
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
