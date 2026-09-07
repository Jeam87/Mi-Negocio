from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi Negocio 10.1</title>
<style>
*{box-sizing:border-box} body{font-family:system-ui;background:#fff7ed;margin:0;padding-bottom:80px}
header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:white;border-bottom:1px solid #eee;position:sticky;top:0;z-index:10}
.card{background:white;border-radius:18px;padding:16px;margin:12px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
input,select{width:100%;padding:12px;border-radius:12px;border:1.5px solid #ddd;margin:6px 0;font-size:16px}
.btn{width:100%;padding:14px;border-radius:12px;border:0;background:black;color:white;font-weight:bold;font-size:16px;margin-top:8px}
.btn-white{background:white;color:black;border:1.5px solid #000}
.tab{position:fixed;bottom:0;left:0;right:0;background:white;display:flex;justify-content:space-around;padding:8px 0;border-top:1px solid #eee}
.tab button{border:0;background:none;font-size:13px;padding:8px 16px;border-radius:20px}
.tab button.active{background:black;color:white}
.product{display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #f2f2f2}
.pay-box{background:black;color:white;border-radius:18px;padding:16px;margin:12px}
.ticket{border:1px dashed #ccc;padding:12px;border-radius:12px;background:#fffff8}
</style>
</head>
<body>
<header>
<div style="display:flex;align-items:center;gap:10px">
<img id="logoImg" src="https://i.imgur.com/8Km9tLL.png" width="36" height="36" style="border-radius:50%;object-fit:cover">
<b>Mi Negocio 10.1 Pagos Auto</b>
</div>
</header>

<!-- VENDER -->
<div id="view-vender">
<div class="card">
<h3>🛒 Vender</h3>
<input id="searchProd" placeholder="Buscar producto..." oninput="filtrar()">
<div id="listaVenta"></div>
<hr>
<div id="carrito"></div>
<b>Total: $<span id="total">0</span></b>
<button class="btn" onclick="cobrar()">Cobrar</button>
<button class="btn btn-white" onclick="cobrarMP()">Cobrar con Mercado Pago 💳</button>
<div id="qrMP" style="margin-top:10px"></div>
</div>
<div class="card ticket" id="ticketView" style="display:none"></div>
</div>

<!-- PRODUCTOS -->
<div id="view-productos" style="display:none">
<div class="card">
<h3>📦 Productos</h3>
<input id="p_nombre" placeholder="Nombre producto">
<input id="p_precio" type="number" placeholder="Precio">
<input id="p_stock" type="number" placeholder="Stock">
<button class="btn" onclick="addProd()">Agregar producto</button>
<div id="listaProd" style="margin-top:12px"></div>
</div>
</div>

<!-- CONFIG -->
<div id="view-config" style="display:none">
<div class="pay-box">
<h3>💳 Conectar pagos - Mercado Pago</h3>
<p style="opacity:.8;font-size:13px">Pega tu Access Token y se guardará automático.</p>
<input id="mp_token" placeholder="APP_USR-xxxxxxxxxxxxxxxx" style="background:#222;color:white;border-color:#444">
<button class="btn" style="background:white;color:black" onclick="guardarToken()">Conectar pagos</button>
<p id="mpStatus" style="font-size:13px;margin-top:8px"></p>
</div>

<div class="card">
<h3>⚙️ Config Ticket + Logo</h3>
<label>📷 Logo</label>
<input type="file" id="logoInput" accept="image/*">
<div style="margin:8px 0">Vista previa - Snoopy</div>
<input id="c_nombre" placeholder="Nombre negocio" value="Mi Negocio">
<input id="c_dir" placeholder="Dirección" value="La que sea">
<div style="display:flex;gap:8px"><input id="c_tel1" value="5966666"><input id="c_tel2" value="3510000000"></div>
<button class="btn btn-white" onclick="guardarConfig()">Guardar Config</button>
</div>
</div>

<div class="tab">
<button id="t-vender" class="active" onclick="showTab('vender')">Vender</button>
<button id="t-productos" onclick="showTab('productos')">Productos</button>
<button id="t-config" onclick="showTab('config')">Config</button>
</div>

<script>
let productos = JSON.parse(localStorage.getItem('prods')||'[{"nombre":"Soda","precio":20,"stock":10},{"nombre":"Papas","precio":15,"stock":20}]');
let carrito = [];
let config = JSON.parse(localStorage.getItem('config')||'{"nombre":"Mi Negocio","dir":"La que sea","tel1":"5966666","tel2":"3510000000","logo":"https://i.imgur.com/8Km9tLL.png"}');
let mpToken = localStorage.getItem('mp_token')||'';

function render(){
 document.getElementById('c_nombre').value=config.nombre;
 document.getElementById('logoImg').src=config.logo;
 document.getElementById('mp_token').value=mpToken;
 listaProductos(); listaVenta();
}
function listaProductos(){
 let h=''; productos.forEach((p,i)=>{ h+=`<div class=product><span>${p.nombre} - $${p.precio} (Stock ${p.stock})</span><button onclick="delProd(${i})">X</button></div>` });
 document.getElementById('listaProd').innerHTML=h;
}
function listaVenta(){
 let h=''; let q=document.getElementById('searchProd').value.toLowerCase();
 productos.filter(p=>p.nombre.toLowerCase().includes(q)).forEach((p,i)=>{
   h+=`<div class=product><span>${p.nombre} - $${p.precio}</span><button class="btn" style="width:auto;padding:6px 12px" onclick="addCarrito(${productos.indexOf(p)})">Agregar</button></div>`
 });
 document.getElementById('listaVenta').innerHTML=h;
 let hc=''; let tot=0; carrito.forEach((c,i)=>{ tot+=c.precio*c.cant; hc+=`<div>${c.nombre} x${c.cant} - $${c.precio*c.cant} <button onclick="removeCart(${i})">x</button></div>` });
 document.getElementById('carrito').innerHTML=hc; document.getElementById('total').innerText=tot;
}
function addProd(){ let n=document.getElementById('p_nombre').value; let pr=parseFloat(document.getElementById('p_precio').value); let st=parseInt(document.getElementById('p_stock').value); if(!n)return; productos.push({nombre:n,precio:pr,stock:st}); localStorage.setItem('prods',JSON.stringify(productos)); listaProductos(); listaVenta(); }
function delProd(i){ productos.splice(i,1); localStorage.setItem('prods',JSON.stringify(productos)); render(); }
function addCarrito(i){ let p=productos[i]; let f=carrito.find(x=>x.nombre==p.nombre); if(f)f.cant++; else carrito.push({...p,cant:1}); listaVenta(); }
function removeCart(i){ carrito.splice(i,1); listaVenta(); }
function filtrar(){ listaVenta(); }
function cobrar(){ if(!carrito.length)return alert('Carrito vacío'); let tot=document.getElementById('total').innerText; alert('Venta de $'+tot+' cobrada'); carrito.forEach(c=>{ let pr=productos.find(p=>p.nombre==c.nombre); if(pr)pr.stock-=c.cant; }); localStorage.setItem('prods',JSON.stringify(productos)); carrito=[]; render(); }
function showTab(t){ document.getElementById('view-vender').style.display=t=='vender'?'block':'none'; document.getElementById('view-productos').style.display=t=='productos'?'block':'none'; document.getElementById('view-config').style.display=t=='config'?'block':'none'; document.querySelectorAll('.tab button').forEach(b=>b.classList.remove('active')); document.getElementById('t-'+t).classList.add('active'); }
function guardarConfig(){ config.nombre=document.getElementById('c_nombre').value; config.dir=document.getElementById('c_dir').value; config.tel1=document.getElementById('c_tel1').value; config.tel2=document.getElementById('c_tel2').value; localStorage.setItem('config',JSON.stringify(config)); alert('Guardado'); render(); }
document.getElementById('logoInput').addEventListener('change',e=>{ let r=new FileReader(); r.onload=()=>{ config.logo=r.result; localStorage.setItem('config',JSON.stringify(config)); render(); }; r.readAsDataURL(e.target.files[0]); });
function guardarToken(){
 let t=document.getElementById('mp_token').value.trim();
 if(!t.startsWith('APP_USR-')){ document.getElementById('mpStatus').innerText='❌ Debe empezar con APP_USR-'; return; }
 localStorage.setItem('mp_token',t);
 fetch('/api/save_token',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:t})}).then(r=>r.json()).then(d=>{ document.getElementById('mpStatus').innerText=d.message; });
}
function cobrarMP(){
 if(!mpToken &&!localStorage.getItem('mp_token')){ showTab('config'); alert('Primero conecta tu Mercado Pago en Config'); return; }
 let tot=document.getElementById('total').innerText;
 fetch('/api/create_payment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:tot, token: localStorage.getItem('mp_token')})}).then(r=>r.json()).then(d=>{
   if(d.init_point){ document.getElementById('qrMP').innerHTML=`<a href="${d.init_point}" target="_blank" class="btn" style="display:block;text-align:center;text-decoration:none;background:#009ee3">Pagar $${tot} con Mercado Pago</a>`; }
   else document.getElementById('qrMP').innerText=JSON.stringify(d);
 });
}
render();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/save_token', methods=['POST'])
def save_token():
    data = request.get_json() or {}
    token = data.get('token','')
    if not token.startswith('APP_USR-'):
        return jsonify({"message":"❌ Token inválido"}),400
    try:
        r = requests.get("https://api.mercadopago.com/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=8)
        if r.status_code==200:
            return jsonify({"message":"✅ Conectado a Mercado Pago correctamente"})
        return jsonify({"message":f"⚠️ Token guardado pero MP dijo {r.status_code}"})
    except Exception as e:
        return jsonify({"message":f"✅ Token guardado: {e}"})

@app.route('/api/create_payment', methods=['POST'])
def create_payment():
    data = request.get_json() or {}
    amount = data.get('amount',10)
    token = data.get('token','')
    try:
        amount = float(amount)
    except:
        amount = 10
    # Crea preferencia de MP
    try:
        r = requests.post("https://api.mercadopago.com/checkout/preferences",
            headers={"Authorization": f"Bearer {token}", "Content-Type":"application/json"},
            json={"items":[{"title":"Venta Mi Negocio","quantity":1,"unit_price":amount}]},
            timeout=10)
        j=r.json()
        return jsonify({"init_point": j.get('init_point') or j.get('sandbox_init_point'), "raw": j})
    except Exception as e:
        return jsonify({"error": str(e)}),500
