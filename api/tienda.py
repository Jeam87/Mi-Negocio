<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mi Tienda Jacona</title>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<style>
body{font-family:Arial,sans-serif;margin:0;padding:0;background:#f5f5f5}
header{background:#25D366;color:white;padding:15px;text-align:center}
#productos{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px;padding-bottom:200px}
.card{background:white;border-radius:12px;padding:10px;box-shadow:0 2px 5px rgba(0,0,0,.1);text-align:center}
.card img{width:100%;height:110px;object-fit:contain;background:#fff;border-radius:8px}
.card h3{font-size:14px;margin:8px 0 2px;min-height:20px}
.card.desc{font-size:11px;color:#666;margin:2px 0 6px;min-height:28px;line-height:12px}
.card p.precio{font-weight:bold;margin:4px 0;color:#111;font-size:15px}
.card button{background:#25D366;border:none;color:white;padding:8px 12px;border-radius:8px;width:100%;font-weight:bold}
#carrito{position:fixed;bottom:0;left:0;right:0;background:white;padding:12px;box-shadow:0 -2px 10px rgba(0,0,0,.2);border-radius:16px 16px 0 0}
#lista-carrito{max-height:120px;overflow:auto;margin-bottom:8px;font-size:13px}
.total{font-weight:bold;font-size:18px;margin:8px 0}
.btn-ws{background:#25D366;color:white;border:none;width:100%;padding:14px;border-radius:10px;font-size:16px;font-weight:bold}
</style>
</head>
<body>
<header>
<h1 id="nombre-tienda">Cargando tienda...</h1>
</header>
<div id="productos"></div>
<div id="carrito">
<div id="lista-carrito">Carrito vacío</div>
<div class="total" id="total-txt">Total: $0</div>
<button class="btn-ws" onclick="enviarWhatsApp()">Pedir por WhatsApp</button>
</div>
<script>
// --- CONFIGURA ESTO ---
const SUPABASE_URL = "https://TU-PROYECTO.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbG...TU_LLAVE_LARGA";
let NUMERO_WHATSAPP = "523521234567";
// ----------------------

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
let carrito = [];
let nombreTienda = "Mi Tienda Jacona";
const params = new URLSearchParams(window.location.search);
const tienda_id = params.get('id');

async function cargarTienda(){
 if(!tienda_id){
   document.getElementById('nombre-tienda').innerText = "Falta?id= en la URL";
   return;
 }
 const {data: tienda} = await supabaseClient.from('tiendas').select('*').eq('id', tienda_id).single();
 if(tienda){
   nombreTienda = tienda.nombre;
   document.getElementById('nombre-tienda').innerText = tienda.nombre;
   document.title = tienda.nombre;
   if(tienda.whatsapp) NUMERO_WHATSAPP = tienda.whatsapp;
 }
 const {data: productos} = await supabaseClient.from('productos').select('*').eq('tienda_id', tienda_id);
 const cont = document.getElementById('productos');
 cont.innerHTML = "";
 productos.forEach(p => {
   const img = p.imagen_url || p.imagen || 'https://via.placeholder.com/150?text=Sin+Foto';
   const descripcion = p.descripcion || p.descripcion_producto || '';
   cont.innerHTML += `
     <div class="card">
       <img src="${img}" onerror="this.src='https://via.placeholder.com/150?text=Sin+Foto'">
       <h3>${p.nombre}</h3>
       <div class="desc">${descripcion}</div>
       <p class="precio">$${p.precio}</p>
       <button onclick="agregar('${p.nombre.replace(/'/g,"\\'")}', ${p.precio})">Agregar</button>
     </div>`;
 });
}

function agregar(nombre, precio){
 carrito.push({nombre, precio});
 renderCarrito();
}

function renderCarrito(){
 const agrupado = {};
 carrito.forEach(p => {
   if(agrupado[p.nombre]) agrupado[p.nombre].cantidad += 1;
   else agrupado[p.nombre] = {...p, cantidad: 1};
 });
 let html = "";
 let total = 0;
 for(let k in agrupado){
   let it = agrupado[k];
   let sub = it.precio * it.cantidad;
   html += `${it.nombre} x${it.cantidad} = $${sub}<br>`;
   total += sub;
 }
 if(carrito.length==0) html = "Carrito vacío";
 document.getElementById('lista-carrito').innerHTML = html;
 document.getElementById('total-txt').innerText = "Total: $"+total;
}

function enviarWhatsApp(){
 if(carrito.length==0) { alert("Carrito vacío"); return; }
 const agrupado = {};
 carrito.forEach(p => {
   if(agrupado[p.nombre]) agrupado[p.nombre].cantidad += 1;
   else agrupado[p.nombre] = {...p, cantidad: 1};
 });
 let mensaje = `Hola ${nombreTienda}! Quiero:%0A`;
 let total = 0;
 for(let k in agrupado){
   let it = agrupado[k];
   let sub = it.precio * it.cantidad;
   mensaje += `• ${it.nombre} x${it.cantidad} = $${sub}%0A`;
   total += sub;
 }
 mensaje += `%0ATotal: $${total}%0A%0AGracias!`;
 window.open(`https://wa.me/${NUMERO_WHATSAPP.replace(/\D/g,'')}?text=${mensaje}`, '_blank');
}

cargarTienda();
</script>
</body>
</html>
