<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mi Tienda Jacona</title>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<style>
*{box-sizing:border-box}
body{font-family:system-ui; margin:0; background:#f8f8f8; padding-bottom:200px}
header{background:#111; color:white; padding:24px; text-align:center}
#productos{display:grid; grid-template-columns: repeat(auto-fill,minmax(160px,1fr)); gap:14px; padding:16px}
.card{background:white; border-radius:16px; padding:10px; box-shadow:0 2px 10px rgba(0,0,0,.08)}
.card img{width:100%; height:140px; object-fit:cover; border-radius:10px}
.card button{background:#111; color:white; border:0; padding:10px; width:100%; border-radius:10px; margin-top:8px; font-weight:bold}
#carrito{position:fixed; bottom:0; left:0; right:0; background:white; padding:16px; border-radius:20px 20px 0 0; box-shadow:0 -4px 20px rgba(0,0,0,.15)}
</style>
</head>
<body>
<header><h1 id="storeName">Cargando...</h1><p id="storeInfo"></p></header>
<div id="productos"></div>
<div id="carrito" style="display:none">
  <div id="lista"></div>
  <button id="btnWa" style="background:#25D366; color:white; border:0; padding:16px; width:100%; border-radius:12px; font-size:17px; font-weight:bold; margin-top:12px">Pedir por WhatsApp</button>
</div>
<script>
const SUPABASE_URL = 'https://txuggnfohyevpvdfxpfu.supabase.co';
const SUPABASE_KEY = 'sb_publishable_cKnKD52yQyFTiyVeIFNc_A_Jy6O-lEC';
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
const storeId = new URLSearchParams(window.location.search).get('id') || 'eedfc281-71bb-4765-8883-8bec75ea3102';
let perfil=null, carrito=[];
async function cargar(){
  const {data:prof}=await supabaseClient.from('profiles').select('*').eq('id',storeId).single();
  perfil=prof;
  document.getElementById('storeName').innerText=prof.business_name;
  let {data:prods}=await supabaseClient.from('products').select('*').eq('user_id',storeId);
  if(!prods||!prods.length){let r=await supabaseClient.from('products').select('*').limit(20); prods=r.data||[]}
  document.getElementById('productos').innerHTML=prods.map(p=>`<div class="card"><img src="${p.image_url||p.imagen||'https://via.placeholder.com/300'}"><h3>${p.name||p.nombre}</h3><p>$${p.price||p.precio}</p><button onclick="agregar('${(p.name||'Prod').replace(/'/g,'')}',${p.price||0})">Agregar</button></div>`).join('');
}
function agregar(n,p){carrito.push({nombre:n,precio:Number(p)}); render()}
function render(){
  document.getElementById('carrito').style.display=carrito.length?'block':'none';
  const total=carrito.reduce((s,c)=>s+c.precio,0);
  document.getElementById('lista').innerHTML=carrito.map(c=>`• ${c.nombre} $${c.precio}`).join('<br>')+`<br><b>Total: $${total}</b>`;
  const wa=(perfil?.whatsapp||'523513053390').replace(/[^0-9]/g,'');
  const txt=encodeURIComponent(`Hola ${perfil.business_name}! Quiero:\n${carrito.map(c=>`- ${c.nombre} $${c.precio}`).join('\n')}\nTotal $${total}`);
  document.getElementById('btnWa').onclick=()=>window.open(`https://wa.me/${wa}?text=${txt}`,'_blank');
}
cargar();
</script>
</body>
</html>
