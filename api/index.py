from flask import Flask, request, jsonify, render_template_string
import requests
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi Negocio 10.1</title>
<style>
*{box-sizing:border-box} body{font-family:system-ui;background:#fff7ed;margin:0;padding-bottom:90px}
header{display:flex;align-items:center;gap:10px;padding:12px 16px;background:white;border-bottom:1px solid #eee;position:sticky;top:0;z-index:20}
.card{background:white;border-radius:18px;padding:16px;margin:12px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
input,select,textarea{width:100%;padding:11px;border-radius:12px;border:1.5px solid #ddd;margin:6px 0;font-size:15px}
.btn{width:100%;padding:13px;border-radius:12px;border:0;background:black;color:white;font-weight:bold;margin-top:6px}
.btn-white{background:white;color:black;border:1.5px solid #000}
.row{display:flex;gap:8px}
.pay{background:black;color:white;border-radius:18px;padding:16px;margin:12px}
.item{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f2f2f2}
.tabs{position:fixed;bottom:0;left:0;right:0;background:white;border-top:1px solid #eee;display:flex;overflow-x:auto;gap:4px;padding:6px}
.tabs button{border:0;background:#f3f3f3;padding:8px 12px;border-radius:20px;white-space:nowrap;font-size:12px}
.tabs button.active{background:black;color:white}
.badge{background:#ffedd5;padding:2px 8px;border-radius:10px;font-size:11px}
</style>
</head>
<body>
<header>
<img id="logoImg" src="https://i.imgur.com/8Km9tLL.png" width="38" height="38" style="border-radius:50%">
<b>Mi Negocio 10.1 Pagos Auto</b>
</header>

<!-- VENDER -->
<div id="v-vender">
<div class="card"><h3>🛒 Vender</h3>
<input id="busV" placeholder="Buscar en catálogo..." oninput="renderVender()">
<div id="listV"></div><hr>
<div id="carrito"></div>
<b>Total: $<span id="total">0</span></b>
<button class="btn" onclick="cobrar()">Cobrar en efectivo</button>
<button class="btn" style="background:#009ee3" onclick="cobrarMP()">Cobrar con Mercado Pago 💳</button>
<div id="qr"></div>
</div></div>

<!-- CATALOGO -->
<div id="v-catalogo" style="display:none"><div class="card">
<h3>📖 Catálogo</h3>
<input id="c_nom" placeholder="Nombre producto">
<div class="row"><input id="c_pre" type="number" placeholder="Precio"><input id="c_sto" type="number" placeholder="Stock"></div>
<input id="c_cat" placeholder="Categoría (ej. Bebidas)">
<button class="btn" onclick="addCatalogo()">Agregar a catálogo</button>
<div id="listCat"></div>
</div></div>

<!-- INVENTARIO -->
<div id="v-inventario" style="display:none"><div class="card">
<h3>📦 Inventario</h3>
<div id="listInv"></div>
</div></div>

<!-- RECETAS -->
<div id="v-recetas" style="display:none"><div class="card">
<h3>🍳 Recetas</h3>
<input id="r_nom" placeholder="Nombre receta (ej. Michelada)">
<textarea id="r_ing" placeholder="Ingredientes y cantidades"></textarea>
<input id="r_cost" type="number" placeholder="Costo">
<button class="btn" onclick="addReceta()">Guardar receta</button>
<div id="listRec"></div>
</div></div>

<!-- CLIENTES -->
<div id="v-clientes" style="display:none"><div class="card">
<h3>👥 Clientes</h3>
<input id="cl_nom" placeholder="Nombre cliente">
<input id="cl_tel" placeholder="Tel / WhatsApp">
<button class="btn" onclick="addCliente()">Agregar cliente</button>
<div id="listCli"></div>
</div></div>

<!-- CONFIG -->
<div id="v-config" style="display:none">
<div class="pay">
<h3>💳 Conectar pagos - Mercado Pago</h3>
<p style="font-size:13px;opacity:.8">Pega tu Access Token y se guardará automático.</p>
<input id="mp_tok" placeholder="APP_USR-xxxxxxxxxxxxxxxx" style="background:#222;color:white;border-color:#444">
<button class="btn" style="background:white;color:black" onclick="saveToken()">Conectar pagos</button>
<p id="mpStat" style="font-size:12px;margin-top:6px"></p>
</div>
<div class="card">
<h3>⚙️ Config Ticket + Logo</h3>
<input type="file" id="logoIn" accept="image/*"><br>
<small>Vista previa - Snoopy</small>
<input id="cfg_nom" value="Mi Negocio">
<input id="cfg_dir" value="La que sea">
<div class="row"><input id="cfg_t1" value="5966666"><input id="cfg_t2" value="3510000000"></div>
<button class="btn btn-white" onclick="saveCfg()">Guardar config</button>
</div>
</div>

<div class="tabs">
<button id="b-vender" class="active" onclick="go('vender')">Vender</button>
<button id="b-catalogo" onclick="go('catalogo')">Catálogo</button>
<button id="b-inventario" onclick="go('inventario')">Inventario</button>
<button id="b-recetas" onclick="go('recetas')">Recetas</button>
<button id="b-clientes" onclick="go('clientes')">Clientes</button>
<button id="b-config" onclick="go('config')">Config</button>
</div>

<script>
let catalogo=JSON.parse(localStorage.getItem('cat')||'[{"nombre":"Soda","precio":20,"stock":15,"cat":"Bebidas"},{"nombre":"Papas","precio":15,"stock":20,"cat":"Botanas"}]');
let recetas=JSON.parse(localStorage.getItem('rec')||'[]');
let clientes=JSON.parse(localStorage.getItem('cli')||'[]');
let carrito=[];
let cfg=JSON.parse(localStorage.getItem('cfg')||'{"nombre":"Mi Negocio","dir":"La que sea","t1":"5966666","t2":"3510000000","logo":"https://i.imgur.com/8Km9tLL.png"}');
let mp=localStorage.getItem('mp_token')||'';

function go(t){
 ['vender','catalogo','inventario','recetas','clientes','config'].forEach(x=>{
   document.getElementById('v-'+x).style.display=(x==t?'block':'none');
   document.getElementById('b-'+x).classList.toggle('active',x==t);
 });
 if(t=='catalogo')renderCat(); if(t=='inventario')renderInv(); if(t=='recetas')renderRec(); if(t=='clientes')renderCli(); if(t=='vender')renderVender();
}
function addCatalogo(){ let n=c_nom.value, p=parseFloat(c_pre.value)||0, s=parseInt(c_sto.value)||0, ca=c_cat.value||'General'; if(!n)return; catalogo.push({nombre:n,precio:p,stock:s,cat:ca}); localStorage.setItem('cat',JSON.stringify(catalogo)); c_nom.value=''; renderCat(); renderVender(); }
function renderCat(){ let h=''; catalogo.forEach((pr,i)=>{ h+=`<div class=item><span>${pr.nombre} <span class=badge>${pr.cat}</span> - $${pr.precio} | Stock ${pr.stock}</span><button onclick="delCat(${i})">X</button></div>` }); listCat.innerHTML=h; }
function delCat(i){ catalogo.splice(i,1); localStorage.setItem('cat',JSON.stringify(catalogo)); renderCat(); renderVender(); }
function renderInv(){ let h=''; catalogo.forEach(pr=>{ h+=`<div class=item><span>${pr.nombre}</span><span>Stock: ${pr.stock}</span></div>` }); listInv.innerHTML=h||'Sin productos'; }
function renderVender(){ let q=busV.value.toLowerCase(); let h=''; catalogo.filter(p=>p.nombre.toLowerCase().includes(q)).forEach((p,i)=>{ let idx=catalogo.indexOf(p); h+=`<div class=item><span>${p.nombre} - $${p.precio}</span><button class=btn style="width:auto;padding:6px 10px" onclick="addCart(${idx})">+</button></div>` }); listV.innerHTML=h; let hc='',tot=0; carrito.forEach((c,i)=>{ tot+=c.precio*c.cant; hc+=`<div class=item>${c.nombre} x${c.cant} $${c.precio*c.cant} <button onclick="remCart(${i})">x</button></div>` }); carrito.innerHTML=hc; document.getElementById('carrito').innerHTML=hc; total.innerText=tot; }
function addCart(i){ let p=catalogo[i]; let f=carrito.find(x=>x.nombre==p.nombre); if(f)f.cant++; else carrito.push({...p,cant:1}); renderVender(); }
function remCart(i){ carrito.splice(i,1); renderVender(); }
function cobrar(){ if(!carrito.length)return alert('Carrito vacío'); let t=total.innerText; carrito.forEach(c=>{ let pr=catalogo.find(p=>p.nombre==c.nombre); if(pr)pr.stock-=c.cant; }); localStorage.setItem('cat',JSON.stringify(catalogo)); carrito=[]; renderVender(); renderInv(); alert('Venta $'+t+' cobrada'); }
function addReceta(){ let n=r_nom.value, ing=r_ing.value, co=parseFloat(r_cost.value)||0; if(!n)return; recetas.push({nombre:n,ing:ing,costo:co}); localStorage.setItem('rec',JSON.stringify(recetas)); r_nom.value=''; r_ing.value=''; renderRec(); }
function renderRec(){ let h=''; recetas.forEach((r,i)=>{ h+=`<div class=item><span><b>${r.nombre}</b><br><small>${r.ing} - Costo $${r.costo}</small></span><button onclick="delRec(${i})">X</button></div>` }); listRec.innerHTML=h; }
function delRec(i){ recetas.splice(i,1); localStorage.setItem('rec',JSON.stringify(recetas)); renderRec(); }
function addCliente(){ let n=cl_nom.value, t=cl_tel.value; if(!n)return; clientes.push({nombre:n,tel:t}); localStorage.setItem('cli',JSON.stringify(clientes)); cl_nom.value=''; renderCli(); }
function renderCli(){ let h=''; clientes.forEach((c,i)=>{ h+=`<div class=item><span>${c.nombre} - ${c.tel}</span><button onclick="delCli(${i})">X</button></div>` }); listCli.innerHTML=h; }
function delCli(i){ clientes.splice(i,1); localStorage.setItem('cli',JSON.stringify(clientes)); renderCli(); }
function saveCfg(){ cfg.nombre=cfg_nom.value; cfg.dir=cfg_dir.value; cfg.t1=cfg_t1.value; cfg.t2=cfg_t2.value; localStorage.setItem('cfg',JSON.stringify(cfg)); alert('Config guardada'); logoImg.src=cfg.logo; }
logoIn.addEventListener('change',e=>{ let r=new FileReader(); r.onload=()=>{ cfg.logo=r.result; localStorage.setItem('cfg',JSON.stringify(cfg)); logoImg.src=cfg.logo; }; r.readAsDataURL(e.target.files[0]); });
function saveToken(){ let t=mp_tok.value.trim(); if(!t.startsWith('APP_USR-')){ mpStat.innerText='❌ Debe empezar con APP_USR-'; return; } localStorage.setItem('mp_token',t); fetch('/api/save_token',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:t})}).then(r=>r.json()).then(d=>{ mpStat.innerText=d.message; }); }
function cobrarMP(){ let tok=localStorage.getItem('mp_token')||''; if(!tok){ go('config'); alert('Primero conecta Mercado Pago en Config'); return; } let tot=total.innerText; fetch('/api/create_payment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:tot,token:tok})}).then(r=>r.json()).then(d=>{ if(d.init_point) qr.innerHTML=`<a href="${d.init_point}" target=_blank class=btn style="display:block;text-align:center;text-decoration:none;background:#009ee3">Pagar $${tot} con Mercado Pago</a>`; else qr.innerText=JSON.stringify(d); }); }

logoImg.src=cfg.logo; mp_tok.value=mp; renderCat(); renderVender();
</script>
</body>
</html>
"""
@app.route('/')
def home(): return render_template_string(HTML)
@app.route('/api/save_token', methods=['POST'])
def save_token():
    tok=(request.get_json() or {}).get('token','')
    if not tok.startswith('APP_USR-'): return jsonify({"message":"❌ Token inválido"}),400
    try:
        r=requests.get("https://api.mercadopago.com/users/me", headers={"Authorization": f"Bearer {tok}"}, timeout=8)
        if r.status_code==200: return jsonify({"message":"✅ Conectado a Mercado Pago correctamente"})
        return jsonify({"message":f"⚠️ Guardado, MP respondió {r.status_code}"})
    except Exception as e: return jsonify({"message":f"✅ Guardado: {e}"})
@app.route('/api/create_payment', methods=['POST'])
def create_payment():
    data=request.get_json() or {}; amt=float(data.get('amount') or 10); tok=data.get('token','')
    try:
        r=requests.post("https://api.mercadopago.com/checkout/preferences", headers={"Authorization": f"Bearer {tok}", "Content-Type":"application/json"}, json={"items":[{"title":"Venta Mi Negocio","quantity":1,"unit_price":amt}]}, timeout=10)
        j=r.json(); return jsonify({"init_point": j.get('init_point') or j.get('sandbox_init_point'), "raw": j})
    except Exception as e: return jsonify({"error":str(e)}),500 
