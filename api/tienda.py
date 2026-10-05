<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title id="title">Cargando...</title>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<style>
*{box-sizing:border-box} body{margin:0;font-family:-apple-system,BlinkMacSystemFont,Arial;background:#f5f5f7}
.header{position:sticky;top:0;z-index:20;background:#fff;display:flex;justify-content:space-between;align-items:center;padding:12px 15px;border-bottom:1px solid #eee}
.logo{height:32px;object-fit:contain}
.cats{position:sticky;top:55px;z-index:19;background:#fff;display:flex;gap:8px;padding:10px 12px;overflow:auto;border-bottom:1px solid #eee}
.cat{white-space:nowrap;padding:8px 18px;border-radius:20px;border:1px solid #e0e0e0;font-size:13px;font-weight:700;background:#fff}
.cat.active{background:#ff3346;color:#fff;border-color:#ff3346}
.list{padding:8px;padding-bottom:90px}
.card{background:#fff;border-radius:14px;display:flex;overflow:hidden;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.card img{width:125px;height:125px;object-fit:cover;background:#fafafa}
.card .info{flex:1;padding:12px 12px;display:flex;flex-direction:column;justify-content:center}
.card .name{font-size:14px;line-height:18px;color:#222}
.card .price{color:#ff3346;font-weight:800;margin-top:8px;font-size:18px}
.detalle{position:fixed;inset:0;background:#fff;z-index:50;display:none;overflow:auto}
.detalle img.top-img{width:100%;height:360px;object-fit:cover}
.detalle .pad{padding:16px}
.detalle .price{font-size:24px;font-weight:800;margin:10px 0}
.btn-wa{background:#ff3346;color:#fff;border:none;width:100%;padding:15px;border-radius:10px;font-weight:700;font-size:16px}
.desc-label{color:#ff3346;font-weight:800;font-size:12px;margin-top:18px;letter-spacing:.5px}
.desc{font-size:15px;line-height:22px;white-space:pre-line;margin-top:8px;color:#333}
.cart-bar{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:12px 15px;border-top:1px solid #eee;display:flex;justify-content:space-between;align-items:center;z-index:30}
</style>
</head>
<body>
<div class="header"><img id="logo" class="logo" src="https://via.placeholder.com/120x32?text=MI+TIENDA"><div onclick="mandarPedido()" style="font-size:22px">💬</div></div>
<div class="cats" id="cats"></div>
<div class="list" id="list"></div>
<div class="cart-bar"><div id="cart-info">Carrito vacío</div><button onclick="mandarPedido()" style="background:#25D366;color:#fff;border:none;padding:10px 16px;border-radius:8px;font-weight:700">Pedir WhatsApp</button></div>

<div class="detalle" id="detalle">
<div style="padding:12px" onclick="document.getElementById('detalle').style.display='none'">← Volver</div>
<img id="d-img" class="top-img"><div class="pad"><div id="d-price" class="price"></div>
<button class="btn-wa" onclick="pedirActual()">Enviar un mensaje por WhatsApp</button>
<div class="desc-label">DESCRIPCIÓN</div><div id="d-desc" class="desc"></div></div>
</div>

<script>
const SUPABASE_URL="https://TU-PROYECTO.supabase.co";
const SUPABASE_ANON_KEY="eyJ...TU_LLAVE_LARGA_ANON";
let WHATSAPP="523521234567";
const sb=supabase.createClient(SUPABASE_URL,SUPABASE_ANON_KEY);
let productos=[],carrito=[],actual=null,nombreTienda="Mi Tienda";
const tienda_id=new URLSearchParams(location.search).get('id');

async function init(){
 if(!tienda_id){document.getElementById('list').innerHTML="Falta ?id= en tu URL"; return;}
 const {data:t}=await sb.from('tiendas').select('*').eq('id',tienda_id).single();
 if(t){nombreTienda=t.nombre; document.getElementById('title').innerText=t.nombre; if(t.whatsapp) WHATSAPP=t.whatsapp; if(t.logo) document.getElementById('logo').src=t.logo;}
 const {data:p}=await sb.from('productos').select('*').eq('tienda_id',tienda_id).order('categoria');
 productos=p||[]; pintarCats(); pintarLista(productos);
}
function pintarCats(){
 const unicas=[...new Set(productos.map(x=>x.categoria).filter(Boolean))];
 const cont=document.getElementById('cats'); cont.innerHTML=`<div class="cat active" onclick="filtrar('todos',this)">INICIO</div>`;
 unicas.forEach(c=>cont.innerHTML+=`<div class="cat" onclick="filtrar('${c}',this)">${c.toUpperCase()}</div>`);
}
function filtrar(cat,el){ document.querySelectorAll('.cat').forEach(e=>e.classList.remove('active')); el.classList.add('active'); if(cat==='todos') pintarLista(productos); else pintarLista(productos.filter(p=>p.categoria===cat)); }
function pintarLista(arr){
 const c=document.getElementById('list'); c.innerHTML=""; arr.forEach(p=>{
 c.innerHTML+=`<div class="card" onclick="ver('${p.id}')"><img src="${p.imagen_url}" onerror="this.src='https://via.placeholder.com/200'"><div class="info"><div class="name">${p.nombre}</div><div class="price">$${p.precio}</div></div></div>`;
 });
}
function ver(id){ const p=productos.find(x=>x.id==id); actual=p; document.getElementById('d-img').src=p.imagen_url; document.getElementById('d-price').innerText="$"+p.precio; document.getElementById('d-desc').innerText=(p.descripcion||"Sin descripción"); document.getElementById('detalle').style.display='block'; }
function pedirActual(){ carrito.push(actual); actualizar(); document.getElementById('detalle').style.display='none'; mandarPedido(); }
function actualizar(){ const g={}; let total=0; carrito.forEach(it=>{total+=Number(it.precio); if(g[it.nombre]) g[it.nombre].c++; else g[it.nombre]={...it,c:1}}); let txt=""; for(let k in g){ txt+=`${g[k].nombre} x${g[k].c} | `} document.getElementById('cart-info').innerText= carrito.length? `Total $${total} (${carrito.length})` : "Carrito vacío"; }
function mandarPedido(){
 if(carrito.length===0 && actual){ pedirActual(); return; } if(carrito.length===0) return alert("Agrega algo");
 const g={}; carrito.forEach(it=>{ if(g[it.nombre]) g[it.nombre].c++; else g[it.nombre]={...it,c:1}}); let msg=`Hola ${nombreTienda}! Quiero:%0A`; let tot=0; for(let k in g){ let it=g[k]; let sub=it.precio*it.c; msg+=`• ${it.nombre} x${it.c} = $${sub}%0A`; tot+=sub;} msg+=`%0ATotal: $${tot}`; window.open(`https://wa.me/${WHATSAPP.replace(/\D/g,'')}?text=${msg}`,'_blank');
}
init();
</script>
</body>
</html>
