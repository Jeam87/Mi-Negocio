from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 9.2 Simple</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>input,select,textarea{color:#000!important;background:#fff!important}</style></head>
<body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[110px]">
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><h1 class="font-black">Mi Negocio 9.2</h1><button onclick="showTab('config')" class="text-[10px] bg-gray-100 px-3 py-1 rounded-full">Config</button></div>

<!-- CREAR SIMPLE -->
<div id="tab-costos" class="p-3">
<div id="crear-menu" class="space-y-4">
<div class="bg-white rounded-[28px] p-5 shadow-sm text-center"><h2 class="font-black text-[18px]">¿Qué quieres crear?</h2><p class="text-[11px] text-gray-500 mt-1">Elige una opción, todo paso a paso</p>
<button onclick="setCrear('base')" class="w-full mt-5 bg-[#FFF8F0] border-2 border-black rounded-[20px] p-5 text-left flex gap-4 items-center"><div class="w-14 h-14 bg-orange-200 rounded-2xl flex items-center justify-center text-xl">🧑‍🍳</div><div><b class="text-[15px]">1. Crear BASE</b><br><span class="text-[11px] text-gray-600">Masa, salsas, guisos. Se hace con tu inventario</span><br><span class="text-[10px] font-black bg-black text-white px-2 py-1 rounded-full mt-1 inline-block">Ej: Masa crepas</span></div></button>
<button onclick="setCrear('producto')" class="w-full mt-3 bg-[#0F172A] rounded-[20px] p-5 text-left flex gap-4 items-center text-white"><div class="w-14 h-14 bg-[#4FD1C5] rounded-2xl flex items-center justify-center text-xl">🛍️</div><div><b class="text-[15px]">2. Crear PRODUCTO PARA VENDER</b><br><span class="text-[11px] opacity-70">Junta una base + extras</span><br><span class="text-[10px] font-black bg-white text-black px-2 py-1 rounded-full mt-1 inline-block">Ej: Crepa Nutella $80</span></div></button>
</div>
<div class="bg-white rounded-[20px] p-4 shadow-sm"><h3 class="font-black text-[12px]">Mis recetas y productos</h3><div id="listaInv"></div></div>
</div>

<div id="crear-base" class="hidden">
<button onclick="setCrear('menu')" class="mb-3 text-[12px] font-bold">← Volver</button>
<div class="bg-white rounded-[28px] p-4 shadow-sm">
<h2 class="font-black text-[16px]">🧑‍🍳 Crear BASE</h2><p class="text-[11px] text-gray-500">Ej: Masa para crepas, salsa verde</p>
<input id="nombre" placeholder="Nombre de la base: Ej Masa crepas" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[15px] mt-3">
<div id="insumos" class="mt-4 space-y-3"></div>
<button onclick="addInsumo()" class="w-full mt-3 bg-orange-100 border-2 border-orange-200 py-3 rounded-2xl font-black text-[12px]">+ Agregar ingrediente de mi Inventario</button>
<div class="mt-4 p-4 bg-[#0F172A] text-white rounded-[16px]"><div class="flex justify-between text-[13px]"><span>Ingredientes</span><b>$<span id="c-ing">0.00</span></b></div><div class="flex justify-between text-amber-300 text-[12px]"><span>+ Fijos</span><b>$<span id="c-fijos">0.00</span></b></div><div class="flex justify-between font-black text-[16px] border-t border-white/20 mt-2 pt-2"><span>Costo $<span id="costo">0.00</span></span><span class="text-green-300">Venta $<span id="venta">0.00</span></span></div><div class="mt-2 flex gap-2"><span class="text-[10px]">Margen %</span><input id="margen" type="number" value="100" class="w-14 text-black rounded-lg text-center font-black py-1" oninput="calc()"><input id="ventaManual" type="number" placeholder="$ final" class="ml-auto w-20 text-black rounded-lg px-2 py-1 font-black" oninput="calc()"></div></div>
<button onclick="guardarProd('recetario')" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR BASE</button><button id="btnCancel" onclick="cancelEdit()" class="hidden w-full mt-2 bg-gray-100 py-3 rounded-2xl text-[11px]">Cancelar</button>
</div>
</div>

<div id="crear-producto" class="hidden">
<button onclick="setCrear('menu')" class="mb-3 text-[12px] font-bold">← Volver</button>
<div class="bg-white rounded-[28px] p-4 shadow-sm">
<h2 class="font-black text-[16px]">🛍️ Crear PRODUCTO PARA VENDER</h2>
<input id="nombreProd" placeholder="Ej: Crepa de Nutella" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[15px] mt-3">
<div class="mt-4 bg-amber-50 border-2 border-amber-200 rounded-2xl p-3"><p class="font-black text-[12px]">Paso 1: ¿Qué base lleva?</p><p class="text-[10px] text-gray-600">Elige de tu recetario</p><div id="basesSel" class="mt-2 space-y-2"></div><button onclick="addBase()" class="w-full mt-2 bg-white border-2 py-2 rounded-xl font-bold text-[11px]">+ Agregar base</button></div>
<div class="mt-3 bg-blue-50 border-2 border-blue-200 rounded-2xl p-3"><p class="font-black text-[12px]">Paso 2: ¿Extras? (opcional)</p><p class="text-[10px] text-gray-600">Nutella extra, refresco, etc.</p><div id="extrasSel" class="mt-2 space-y-2"></div><button onclick="addExtra()" class="w-full mt-2 bg-white border-2 py-2 rounded-xl font-bold text-[11px]">+ Agregar extra del inventario o producto</button></div>
<div class="mt-4 p-4 bg-black text-white rounded-[16px]"><div class="flex justify-between"><span>Costo</span><b>$<span id="c-ing2">0.00</span></b></div><div class="flex justify-between font-black text-[16px] mt-1"><span>Precio venta</span><span class="text-[#4FD1C5]">$<span id="venta2">0.00</span></span></div><div class="mt-2 flex gap-2"><span class="text-[10px]">Margen %</span><input id="margen2" type="number" value="100" class="w-14 text-black rounded-lg text-center font-black py-1" oninput="calc2()"><input id="ventaManual2" type="number" placeholder="$ final" class="ml-auto w-20 text-black rounded-lg px-2 py-1 font-black" oninput="calc2()"></div></div>
<button onclick="guardarProd('catalogo')" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR PRODUCTO</button>
</div>
</div>
</div>

<div id="tab-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div><div class="mt-6 bg-white rounded-[20px] p-4 shadow-xl border"><select id="selCliente" class="w-full border-2 p-2 rounded-xl text-[12px]"><option value="">Cliente mostrador</option></select><div id="ticket" class="text-[12px] mt-2">Vacio</div><div class="flex justify-between font-black text-lg mt-3">Total $<span id="c-total">0</span></div><button onclick="cobrar()" class="w-full mt-3 bg-black text-white py-3 rounded-xl font-black">COBRAR</button><button onclick="enviarWA()" class="w-full mt-2 bg-green-500 text-white py-2 rounded-xl text-sm font-bold">WhatsApp</button></div></div>

<div id="tab-inventario" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[24px] p-4 text-white"><h2 class="font-black text-[15px]">📦 Inventario maestro</h2><p class="text-[11px] opacity-70">Cambia precio y recetas se actualizan solas</p></div><div class="mt-3 bg-white rounded-[20px] p-4 shadow-sm"><div class="grid grid-cols-5 gap-2"><input id="inv-nombre" placeholder="Papas" class="col-span-2 border-2 border-black p-3 rounded-xl font-bold text-[13px]"><input id="inv-precio" type="number" placeholder="$30" class="border-2 border-black p-3 rounded-xl font-black text-[13px]"><select id="inv-unidad" class="border-2 border-black p-3 rounded-xl text-[11px] font-bold"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>pza</option><option>m</option></select><button onclick="addInventario()" class="bg-black text-white rounded-xl font-black text-xl">+</button></div><button onclick="addInventario()" class="w-full mt-2 bg-black text-white py-3 rounded-2xl font-black text-[13px]">GUARDAR</button><div id="inv-msg" class="hidden mt-3 p-2 rounded-xl text-center font-bold text-[12px]"></div><input id="buscInv" placeholder="🔍 Buscar..." class="w-full border-2 p-3 rounded-xl mt-3 text-[12px]" oninput="renderInventarioMaster()"><div id="listaInvMaster" class="mt-4 space-y-2"></div></div></div>

<div id="tab-finanzas" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[24px] p-4 text-white"><div class="flex justify-between items-center"><h2 class="font-black">Finanzas</h2><button onclick="openGasto()" class="bg-[#4FD1C5] text-black w-10 h-10 rounded-xl font-black text-xl">+</button></div><div class="mt-3 flex gap-1 overflow-auto"><button onclick="setFin('flujo')" id="f-flujo" class="px-3 py-2 rounded-full text-[10px] font-black bg-white text-black">📊 Flujo</button><button onclick="setFin('facturas')" id="f-facturas" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Facturas</button><button onclick="setFin('proveedores')" id="f-proveedores" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Provee.</button><button onclick="setFin('categorias')" id="f-categorias" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Cat.</button><button onclick="setFin('fijos')" id="f-fijos" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Fijos</button></div></div>
<div id="fin-flujo" class="mt-3 bg-white rounded-[20px] p-4 shadow-sm"><div class="flex justify-between items-center"><h3 class="font-black text-[14px]">Flujo de caja</h3><input id="mesFlujo" type="month" class="border-2 border-black rounded-xl px-2 py-1 text-[12px] font-bold" onchange="renderFinanzas()"></div><div class="grid grid-cols-3 gap-2 mt-4 text-center"><div class="bg-green-50 border-2 border-green-200 rounded-2xl p-3"><p class="text-[9px] font-black text-green-700">ENTRADAS</p><p class="font-black text-green-600">$<span id="flu-e">0</span></p></div><div class="bg-red-50 border-2 border-red-200 rounded-2xl p-3"><p class="text-[9px] font-black text-red-700">SALIDAS</p><p class="font-black text-red-600">$<span id="flu-s">0</span></p></div><div class="bg-black text-white rounded-2xl p-3"><p class="text-[9px] font-black opacity-60">GANANCIA</p><p class="font-black text-[#4FD1C5]">$<span id="flu-g">0</span></p></div></div><div id="flu-lista" class="mt-4 space-y-2"></div></div>
<div id="fin-facturas" class="hidden mt-3 bg-white rounded-2xl p-3"><div id="f-lista"></div></div>
<div id="fin-proveedores" class="hidden mt-3 bg-white rounded-2xl p-4"><div class="flex gap-2"><input id="provNombre" placeholder="Proveedor" class="flex-1 border-2 border-black p-3 rounded-xl font-bold"><button onclick="addProv()" class="bg-black text-white px-6 rounded-xl font-black">+</button></div><div id="listaProv" class="mt-3 space-y-2"></div></div>
<div id="fin-categorias" class="hidden mt-3 bg-white rounded-[20px] p-4"><div class="flex gap-2"><input id="catNombre" placeholder="Ej: Gasolina" class="flex-1 border-2 border-black p-4 rounded-2xl font-bold"><button onclick="addCat()" class="bg-black text-white px-6 rounded-2xl font-black">+</button></div><div id="listaCat" class="mt-4 space-y-2"></div></div>
<div id="fin-fijos" class="hidden mt-3 bg-white rounded-[20px] p-4"><input id="prodMes" type="number" value="100" class="w-full border-2 border-black p-3 rounded-xl mt-2 font-black" oninput="calcFijos()"><div id="gastosFijos" class="mt-3 space-y-2"></div><button onclick="addFijo()" class="w-full mt-3 bg-gray-100 py-3 rounded-full font-black text-[11px]">+ Agregar gasto fijo</button><div class="mt-4 bg-black text-white p-4 rounded-2xl text-center">Total mes $<span id="totMes">0</span> | Por receta $<span id="porRec">0.00</span></div></div>
<div id="modalGasto" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"><div class="bg-white w-full max-w-sm rounded-[24px] p-5"><select id="g-tipo" class="w-full border-2 p-3 rounded-xl mt-3 font-bold"><option value="salida">🔴 Salida</option><option value="entrada">🟢 Entrada</option></select><input id="g-concepto" placeholder="Concepto" class="w-full border-2 p-3 rounded-xl mt-2 font-bold"><input id="g-monto" type="number" placeholder="$" class="w-full border-2 p-3 rounded-xl mt-2 font-black"><select id="g-cat" class="w-full border-2 p-3 rounded-xl mt-2 text-[12px]"></select><input id="g-fecha" type="date" class="w-full border-2 p-3 rounded-xl mt-2 font-bold"><div class="flex gap-2 mt-4"><button onclick="document.getElementById('modalGasto').classList.add('hidden')" class="flex-1 bg-gray-100 py-3 rounded-xl">Cerrar</button><button onclick="addMov()" class="flex-1 bg-black text-white py-3 rounded-xl font-black">Guardar</button></div></div></div>
</div>

<div id="tab-clientes" class="p-3 hidden"><div class="bg-[#2D3748] rounded-[24px] p-4 text-white"><h2 class="font-black text-[15px]">👥 Clientes</h2></div><div class="mt-3 bg-white rounded-[20px] p-4 shadow-sm"><div class="flex gap-2"><input id="cliNombre" placeholder="Nombre" class="flex-1 border-2 border-black p-3 rounded-xl font-bold text-[13px]"><input id="cliTel" placeholder="Tel" class="w-24 border-2 p-3 rounded-xl text-[12px]"><button onclick="addCliente()" class="bg-black text-white px-5 rounded-xl font-black text-xl">+</button></div><div id="listaClientes" class="mt-4 space-y-2"></div></div></div>

<div id="tab-config" class="p-3 hidden"><div class="bg-white rounded-2xl p-4"><h3 class="font-black text-sm">Categorias productos</h3><div id="listaCats" class="mt-2"></div><input id="newCat" placeholder="Nueva" class="w-full border-2 p-3 rounded-xl mt-3"><select id="newCatTipo" class="w-full border-2 p-3 rounded-xl mt-2"><option value="recetario">Recetario</option><option value="catalogo">Catalogo</option></select><button onclick="addCatProd()" class="w-full mt-2 bg-black text-white py-3 rounded-xl">+ Agregar</button></div></div>

<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30">
<button onclick="showTab('costos')" id="n-costos" class="flex flex-col items-center text-black"><i class="fa-solid fa-book"></i><span class="text-[7px] font-bold">Crear</span></button>
<button onclick="showTab('vender')" id="n-vender" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-store"></i><span class="text-[7px]">Catalogo</span></button>
<button onclick="showTab('inventario')" id="n-inventario" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-boxes-stacked"></i><span class="text-[7px]">Inventario</span></button>
<button onclick="showTab('finanzas')" id="n-finanzas" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-chart-line"></i><span class="text-[7px]">Finanzas</span></button>
<button onclick="showTab('clientes')" id="n-clientes" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-users"></i><span class="text-[7px]">Clientes</span></button>
</div></div>

<script>
let tipoAct='recetario', editId=null, carrito=[], finView='flujo', crearView='menu';
function getCats(){ let c=JSON.parse(localStorage.getItem('categoriasV2')||'[]'); if(!c.length){ c=[{id:'recetario',nombre:'Masa base',grupo:'recetario'},{id:'catalogo',nombre:'Crepas',grupo:'catalogo'}]; localStorage.setItem('categoriasV2',JSON.stringify(c)); } return c; }
function getProd(){ return JSON.parse(localStorage.getItem('productosV2')||'[]'); }
function getFijos(){ return JSON.parse(localStorage.getItem('gastosFijos')||'[]'); }
function getFacts(){ return JSON.parse(localStorage.getItem('facturas')||'[]'); }
function getCatG(){ let c=JSON.parse(localStorage.getItem('catGastos')||'[]'); if(!c.length){ c=[{id:'renta',nombre:'Renta'}]; localStorage.setItem('catGastos',JSON.stringify(c)); } return c; }
function getProv(){ return JSON.parse(localStorage.getItem('proveedores')||'[]'); }
function getInv(){ let inv=JSON.parse(localStorage.getItem('inventarioMaestro')||'[]'); if(!inv.length){ inv=[{id:'1',nombre:'Papas',precio:30,unidad:'kg'},{id:'2',nombre:'Jitomate',precio:20,unidad:'kg'},{id:'3',nombre:'Leche',precio:40,unidad:'L'}]; localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); } return inv; }
function getCli(){ return JSON.parse(localStorage.getItem('clientes')||'[]'); }

function showTab(t){
  ['costos','vender','inventario','finanzas','clientes','config'].forEach(x=>{
    let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hidden',x!=t);
    let nb=document.getElementById('n-'+x); if(nb){ nb.classList.toggle('text-black',x==t); nb.classList.toggle('text-gray-400',x!=t); }
  });
  if(t=='costos') setCrear('menu');
  if(t=='finanzas') renderFinanzas();
  if(t=='vender') { renderVenta(); renderClientesSel(); }
  if(t=='config') renderCatsProd();
  if(t=='inventario') renderInventarioMaster();
  if(t=='clientes') renderClientes();
}
function setCrear(v){
  crearView=v;
  document.getElementById('crear-menu').classList.toggle('hidden',v!='menu');
  document.getElementById('crear-base').classList.toggle('hidden',v!='base');
  document.getElementById('crear-producto').classList.toggle('hidden',v!='producto');
  if(v=='menu') renderInventario();
  if(v=='base'){ tipoAct='recetario'; document.getElementById('insumos').innerHTML=''; addInsumo({}); calc(); }
  if(v=='producto'){ document.getElementById('basesSel').innerHTML=''; document.getElementById('extrasSel').innerHTML=''; addBase(); calc2(); }
}

// INVENTARIO
function addInventario(){
  let n=document.getElementById('inv-nombre').value.trim(), p=parseFloat(document.getElementById('inv-precio').value), u=document.getElementById('inv-unidad').value;
  let msg=document.getElementById('inv-msg');
  if(!n||!p){ msg.className='mt-3 p-2 rounded-xl text-center font-bold bg-red-100'; msg.innerText='Pon nombre y precio'; msg.classList.remove('hidden'); return; }
  let inv=getInv(); let ex=inv.find(x=>x.nombre.toLowerCase()==n.toLowerCase());
  if(ex){ ex.precio=p; ex.unidad=u; msg.innerText='✅ Actualizado'; } else { inv.push({id:Date.now().toString(),nombre:n,precio:p,unidad:u}); msg.innerText='✅ Guardado'; }
  localStorage.setItem('inventarioMaestro',JSON.stringify(inv));
  document.getElementById('inv-nombre').value=''; document.getElementById('inv-precio').value=''; msg.className='mt-3 p-2 rounded-xl text-center font-bold bg-green-100'; msg.classList.remove('hidden'); setTimeout(()=>msg.classList.add('hidden'),1500);
  renderInventarioMaster();
}
function renderInventarioMaster(){
  let inv=getInv(); let q=(document.getElementById('buscInv')?.value||'').toLowerCase();
  let filtered=inv.filter(x=>x.nombre.toLowerCase().includes(q));
  let h=''; filtered.forEach(it=>{
    let idx=getInv().findIndex(x=>x.id==it.id);
    h+=`<div class="flex gap-2 items-center bg-gray-50 p-3 rounded-xl border"><div class="flex-1"><b class="text-[13px]">${it.nombre}</b><br><span class="text-[11px]">$${it.precio}/${it.unidad}</span></div><input type="number" value="${it.precio}" onchange="let inv=getInv(); inv[${idx}].precio=parseFloat(this.value)||0; localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); calc(); calc2();" class="w-20 border-2 border-black p-2 rounded-xl font-black text-[13px]"><button onclick="if(confirm('Borrar?')){let inv=getInv(); inv.splice(${idx},1); localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); renderInventarioMaster();}" class="text-red-400 font-black px-2">X</button></div>`;
  });
  document.getElementById('listaInvMaster').innerHTML=h;
}

// CLIENTES
function addCliente(){ let n=document.getElementById('cliNombre').value.trim(), t=document.getElementById('cliTel').value.trim(); if(!n) return; let cli=getCli(); cli.push({id:Date.now().toString(),nombre:n,tel:t}); localStorage.setItem('clientes',JSON.stringify(cli)); document.getElementById('cliNombre').value=''; document.getElementById('cliTel').value=''; renderClientes(); renderClientesSel(); }
function renderClientes(){ let cli=getCli(); let h=''; cli.forEach((c,i)=>{ let idx=getCli().findIndex(x=>x.id==c.id); h+=`<div class="flex justify-between items-center bg-gray-50 p-3 rounded-xl border"><div><b class="text-[13px]">${c.nombre}</b><br><span class="text-[11px]">${c.tel||''}</span></div><button onclick="let cl=getCli(); cl.splice(${idx},1); localStorage.setItem('clientes',JSON.stringify(cl)); renderClientes(); renderClientesSel();" class="text-red-400 font-black px-2">X</button></div>`; }); document.getElementById('listaClientes').innerHTML=h||'<p class="text-[11px] text-gray-400 text-center py-4">Sin clientes</p>'; }
function renderClientesSel(){ let cli=getCli(); let sel=document.getElementById('selCliente'); if(sel) sel.innerHTML='<option value="">Cliente mostrador</option>'+cli.map(c=>`<option value="${c.id}">${c.nombre}</option>`).join(''); }

// CREAR LOGICA
function addInsumo(d={}){
  let inv=getInv(); let opts=inv.map(it=>`<option value="${it.id}" ${d.invId==it.id?'selected':''} data-p="${it.precio}" data-u="${it.unidad}">${it.nombre} $${it.precio}/${it.unidad}</option>`).join('');
  let div=document.createElement('div'); div.className='bg-[#FFF8F0] p-3 rounded-[16px] border-2 border-orange-100'; div.dataset.t='ing';
  div.innerHTML=`<select class="in-n w-full bg-white border-2 border-black p-2 rounded-xl font-bold text-[13px]" onchange="cambiarInv(this)"><option value="">-- Elige ingrediente --</option>${opts}</select><div class="grid grid-cols-3 gap-2 mt-2 bg-white p-2 rounded-xl"><input type="number" value="${d.cu||''}" placeholder="¿Cuanto usas? Ej 250" class="in-cu col-span-2 border-2 border-black p-2 rounded-lg font-bold" oninput="calc()"><select class="in-uu border-2 border-black p-2 rounded-lg text-[11px]" onchange="calc()"><option>g</option><option>kg</option><option>ml</option><option>L</option><option>pza</option></select><div class="col-span-3 text-right font-black text-[12px] mt-1">Me sale: $<span class="in-sub">0.00</span> <span class="in-det text-[10px] text-gray-500 font-normal"></span></div></div><input type="hidden" class="in-cc" value="1"><input type="hidden" class="in-uc"><input type="hidden" class="in-pc"><button onclick="this.parentElement.remove();calc()" class="w-full mt-2 text-[10px] text-red-400 font-bold">Quitar</button>`;
  document.getElementById('insumos').appendChild(div); if(d.invId){ cambiarInv(div.querySelector('.in-n')); if(d.cu) div.querySelector('.in-cu').value=d.cu; }
}
function cambiarInv(sel){
  let row=sel.closest('div'); let id=sel.value; if(!id) return; let opt=sel.options[sel.selectedIndex]; let it=getInv().find(x=>x.id==id); if(!it) return;
  row.dataset.invId=id; row.querySelector('.in-pc').value=it.precio; row.querySelector('.in-uc').value=it.unidad; row.querySelector('.in-cc').value=1;
  let uu=row.querySelector('.in-uu'); if(it.unidad=='kg') uu.value='g'; if(it.unidad=='L') uu.value='ml'; calc();
}
function calc(){
  let inv=getInv(); let tot=0;
  document.querySelectorAll('#insumos > div').forEach(row=>{
    let sub=row.querySelector('.in-sub'); let det=row.querySelector('.in-det');
    let invId=row.dataset.invId||row.querySelector('.in-n')?.value; if(invId){ let it=inv.find(x=>x.id==invId); if(it){ row.querySelector('.in-pc').value=it.precio; row.querySelector('.in-uc').value=it.unidad; } }
    let pc=parseFloat(row.querySelector('.in-pc').value)||0, cu=parseFloat(row.querySelector('.in-cu').value)||0;
    let uc=row.querySelector('.in-uc').value, uu=row.querySelector('.in-uu').value;
    if(!pc||!cu){ sub.innerText='0.00'; return; }
    let cost=(pc/1000)*cu; if(uc=='kg'&&uu=='kg') cost=pc*cu; if(uc=='kg'&&uu=='g') cost=(pc/1000)*cu; if(uc=='L'&&uu=='L') cost=pc*cu; if(uc=='L'&&uu=='ml') cost=(pc/1000)*cu; if(uc=='pza') cost=pc*cu;
    if(uc=='g'&&uu=='g') cost=(pc/1000)*cu*1000; // fallback
    // simple: precio por kg / L -> gramos / ml /1000
    if((uc=='kg'||uc=='L') && (uu=='g'||uu=='ml')) cost=(pc/1000)*cu;
    if(uc==uu) cost=pc*cu;
    if(uc=='pza') cost=pc*cu;
    sub.innerText=cost.toFixed(2); if(det) det.innerText=`(${cu}${uu} de ${inv.find(x=>x.id==invId)?.nombre||''} a $${pc}/${uc})`; tot+=cost;
  });
  document.getElementById('c-ing').innerText=tot.toFixed(2);
  let gf=parseFloat(document.getElementById('c-fijos')?.innerText||'0')||0;
  document.getElementById('costo').innerText=(tot+gf).toFixed(2);
  let m=parseFloat(document.getElementById('margen').value)||0; let vm=document.getElementById('ventaManual').value;
  let ve=document.getElementById('venta'); if(ve){ if(vm&&parseFloat(vm)>0) ve.innerText=parseFloat(vm).toFixed(2); else ve.innerText=((tot+gf)*(1+m/100)).toFixed(2); }
}
function addBase(){
  let bases=getProd().filter(p=>getCats().find(c=>c.id==p.tipo)?.grupo=='recetario');
  if(!bases.length) return alert('Primero crea una BASE en la opcion 1');
  let div=document.createElement('div'); div.className='bg-white border-2 border-black p-2 rounded-xl flex gap-2 items-center';
  div.innerHTML=`<select class="b-sel flex-1 border-2 p-2 rounded-lg font-bold text-[12px]" onchange="calc2()">${bases.map(b=>`<option value="${b.id}" data-c="${b.costo}">${b.nombre} $${b.costo.toFixed(2)}</option>`).join('')}</select><input type="number" value="1" class="b-cant w-14 border-2 p-2 rounded-lg font-bold" oninput="calc2()"><button onclick="this.parentElement.remove();calc2()" class="text-red-400 font-black">X</button>`;
  document.getElementById('basesSel').appendChild(div); calc2();
}
function addExtra(){
  let inv=getInv(); let prods=getProd();
  let optsInv=inv.map(i=>`<option value="inv-${i.id}" data-c="${i.precio}" data-u="${i.unidad}">📦 ${i.nombre} $${i.precio}/${i.unidad}</option>`).join('');
  let optsProd=prods.map(p=>`<option value="prod-${p.id}" data-c="${p.venta}">🛍️ ${p.nombre} $${p.venta.toFixed(2)}</option>`).join('');
  let div=document.createElement('div'); div.className='bg-white border-2 p-2 rounded-xl flex gap-2 items-center';
  div.innerHTML=`<select class="e-sel flex-1 border-2 p-2 rounded-lg font-bold text-[11px]" onchange="calc2()"><optgroup label="Del inventario">${optsInv}</optgroup><optgroup label="Productos">${optsProd}</optgroup></select><input type="number" value="1" placeholder="Cant" class="e-cant w-14 border-2 p-2 rounded-lg font-bold text-[11px]" oninput="calc2()"><button onclick="this.parentElement.remove();calc2()" class="text-red-400 font-black">X</button>`;
  document.getElementById('extrasSel').appendChild(div); calc2();
}
function calc2(){
  let tot=0;
  document.querySelectorAll('#basesSel > div').forEach(r=>{
    let sel=r.querySelector('.b-sel'); if(!sel?.options[sel.selectedIndex]) return;
    let c=parseFloat(sel.options[sel.selectedIndex].dataset.c)||0; let cant=parseFloat(r.querySelector('.b-cant').value)||1; tot+=c*cant;
  });
  document.querySelectorAll('#extrasSel > div').forEach(r=>{
    let sel=r.querySelector('.e-sel'); if(!sel?.options[sel.selectedIndex]) return;
    let c=parseFloat(sel.options[sel.selectedIndex].dataset.c)||0; let cant=parseFloat(r.querySelector('.e-cant').value)||1;
    let val=sel.value; if(val.startsWith('inv-')){ // si es kg/L y cant es g/ml convertir simple: asumimos cant en gramos si base es kg
      let it=getInv().find(x=>x.id==val.replace('inv-','')); if(it && (it.unidad=='kg'||it.unidad=='L')) c=c/1000;
    }
    tot+=c*cant;
  });
  document.getElementById('c-ing2').innerText=tot.toFixed(2);
  let m=parseFloat(document.getElementById('margen2').value)||0; let vm=document.getElementById('ventaManual2').value;
  let ve=document.getElementById('venta2'); if(vm&&parseFloat(vm)>0) ve.innerText=parseFloat(vm).toFixed(2); else ve.innerText=(tot*(1+m/100)).toFixed(2);
}
function guardarProd(tipo){
  let isBase=tipo=='recetario';
  let nomEl=isBase?document.getElementById('nombre'):document.getElementById('nombreProd');
  let nom=nomEl.value.trim(); if(!nom) return alert('Pon nombre');
  let costo=parseFloat((isBase?document.getElementById('costo'):document.getElementById('c-ing2')).innerText);
  let venta=parseFloat((isBase?document.getElementById('venta'):document.getElementById('venta2')).innerText);
  let ings=[];
  if(isBase){
    document.querySelectorAll('#insumos > div').forEach(row=>{ let sel=row.querySelector('.in-n'); ings.push({tipo:'ing',invId:row.dataset.invId||sel.value,cu:row.querySelector('.in-cu').value,uu:row.querySelector('.in-uu').value}); });
  } else {
    document.querySelectorAll('#basesSel > div').forEach(r=>{ ings.push({tipo:'rec',id:r.querySelector('.b-sel').value.replace('prod-','').replace('inv-',''),cant:r.querySelector('.b-cant').value}); });
    document.querySelectorAll('#extrasSel > div').forEach(r=>{ let v=r.querySelector('.e-sel').value; ings.push({tipo:v.startsWith('inv-')?'invExtra':'cat',id:v,cant:r.querySelector('.e-cant').value}); });
  }
  let cats=getCats(); let tipoId=isBase?cats.find(c=>c.grupo=='recetario')?.id:cats.find(c=>c.grupo=='catalogo')?.id;
  let ps=getProd();
  if(editId){ let idx=ps.findIndex(x=>x.id==editId); if(idx>=0){ ps[idx].nombre=nom; ps[idx].costo=costo; ps[idx].venta=venta; ps[idx].tipo=tipoId; ps[idx].ingredientes=ings; } }
  else { ps.push({id:Date.now(),tipo:tipoId,nombre:nom,costo,venta,ingredientes:ings}); }
  localStorage.setItem('productosV2',JSON.stringify(ps)); cancelEdit(); renderInventario(); renderVenta(); setCrear('menu');
}
function renderInventario(){ let ps=getProd(); let cs=getCats(); let h=''; ps.forEach((p,i)=>{ let cat=cs.find(c=>c.id==p.tipo); let esBase=cat?.grupo=='recetario'; h+=`<div class="bg-white p-3 rounded-2xl flex gap-2 shadow-sm mt-3 border items-center"><span class="text-[8px] ${esBase?'bg-orange-100':'bg-black text-white'} px-2 py-1 rounded-full font-bold">${esBase?'BASE':'VENTA'}</span><div class="flex-1"><b class="text-[13px]">${p.nombre}</b><br><span class="text-[11px]">$${p.costo.toFixed(2)} → $${p.venta.toFixed(2)}</span></div><button onclick="editarProd(${p.id})" class="bg-blue-50 text-blue-600 px-3 py-1.5 rounded-full text-[11px] font-black">Editar</button><button onclick="if(confirm('Borrar?')){let pr=getProd(); pr.splice(${i},1); localStorage.setItem('productosV2',JSON.stringify(pr)); renderInventario(); renderVenta();}" class="text-red-400 ml-1 font-black">X</button></div>`; }); document.getElementById('listaInv').innerHTML=h||'<p class="text-[11px] text-gray-400 text-center py-4">Aún no tienes bases. Crea una arriba 👆</p>'; }
function editarProd(id){
  let p=getProd().find(x=>x.id==id); if(!p) return; editId=id;
  let esBase=getCats().find(c=>c.id==p.tipo)?.grupo=='recetario';
  if(esBase){
    setCrear('base'); document.getElementById('nombre').value=p.nombre; document.getElementById('insumos').innerHTML='';
    if(p.ingredientes){ p.ingredientes.forEach(ing=>{ if(ing.tipo=='ing') addInsumo({invId:ing.invId,cu:ing.cu}); }); }
    calc();
  } else {
    setCrear('producto'); document.getElementById('nombreProd').value=p.nombre;
    // simplificado: no recargamos ingredientes complejos en edicion
  }
  document.getElementById('btnCancel').classList.remove('hidden');
}
function cancelEdit(){ editId=null; document.getElementById('nombre').value=''; document.getElementById('nombreProd').value=''; document.getElementById('insumos').innerHTML=''; document.getElementById('ventaManual').value=''; document.getElementById('ventaManual2').value=''; document.getElementById('btnCancel').classList.add('hidden'); setCrear('menu'); }
function renderVenta(){ let cs=getCats(); let ids=cs.filter(c=>c.grupo=='catalogo').map(c=>c.id); let ps=getProd().filter(p=>ids.includes(p.tipo)); let h=''; ps.forEach(p=>{ h+=`<div class="bg-white rounded-2xl shadow-sm border overflow-hidden"><button onclick="addCart(${p.id})" class="w-full text-left p-3"><b class="text-[12px]">${p.nombre}</b><p class="text-green-600 font-black text-[12px]">$${p.venta.toFixed(2)}</p><p class="text-[9px] text-gray-400">Costo $${p.costo.toFixed(2)}</p></button></div>`; }); document.getElementById('listaVenta').innerHTML=h||'<p class="text-center text-gray-400 py-10 col-span-2">Crea productos en Crear → Producto para vender</p>'; }
function addCart(id){ let p=getProd().find(x=>x.id==id); let ex=carrito.find(x=>x.id==id); if(ex) ex.qty++; else carrito.push({...p,qty:1}); let t=0, html=''; carrito.forEach(x=>{ t+=x.venta*x.qty; html+=`<div class="flex justify-between py-1"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)}</span></div>`; }); document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('ticket').innerHTML=html||'Vacio'; }
function cobrar(){ if(!carrito.length) return alert('Vacio'); let tot=parseFloat(document.getElementById('c-total').innerText); let facts=getFacts(); let now=new Date(); let iso=now.toISOString().split('T')[0]; let cliId=document.getElementById('selCliente').value; let cli=getCli().find(c=>c.id==cliId); facts.push({id:Date.now(),concepto:'Venta'+(cli?' a '+cli.nombre:'')+': '+carrito.map(c=>c.nombre+' x'+c.qty).join(', '),monto:tot,fecha:iso,fechaObj:now.getTime(),tipo:'entrada'}); localStorage.setItem('facturas',JSON.stringify(facts)); carrito=[]; document.getElementById('c-total').innerText='0'; document.getElementById('ticket').innerHTML='Vacio'; finView='flujo'; showTab('finanzas'); }
function enviarWA(){ if(!carrito.length) return; let texto=`*PRESUPUESTO*%0A`; carrito.forEach(p=>texto+=`• ${p.nombre} x${p.qty} $${(p.venta*p.qty).toFixed(0)}%0A`); texto+=`*TOTAL $${document.getElementById('c-total').innerText}*`; window.open('https://wa.me/?text='+texto,'_blank'); }
function setFin(v){ finView=v; renderFinanzas(); }
function addCat(){ let n=document.getElementById('catNombre').value.trim(); if(!n) return; let cs=getCatG(); cs.push({id:Date.now().toString(),nombre:n}); localStorage.setItem('catGastos',JSON.stringify(cs)); document.getElementById('catNombre').value=''; renderFinanzas(); }
function addProv(){ let n=document.getElementById('provNombre').value.trim(); if(!n) return; let ps=getProv(); ps.push({id:Date.now().toString(),nombre:n}); localStorage.setItem('proveedores',JSON.stringify(ps)); document.getElementById('provNombre').value=''; renderFinanzas(); }
function openGasto(){ let cats=getCatG(); document.getElementById('g-cat').innerHTML='<option value="">Sin categoria</option>'+cats.map(c=>`<option value="${c.id}">${c.nombre}</option>`).join(''); document.getElementById('modalGasto').classList.remove('hidden'); }
function addMov(){ let concepto=document.getElementById('g-concepto').value.trim(), monto=parseFloat(document.getElementById('g-monto').value), fecha=document.getElementById('g-fecha').value; if(!concepto||!monto||!fecha) return alert('Faltan'); let facts=getFacts(); facts.push({id:Date.now(),concepto,monto,fecha,fechaObj:new Date(fecha+'T00:00:00').getTime(),tipo:document.getElementById('g-tipo').value,catGastoId:document.getElementById('g-cat').value}); localStorage.setItem('facturas',JSON.stringify(facts)); document.getElementById('modalGasto').classList.add('hidden'); document.getElementById('g-concepto').value=''; document.getElementById('g-monto').value=''; renderFinanzas(); }
function renderFinanzas(){
  let facts=getFacts(); let cats=getCatG(); let provs=getProv();
  ['flujo','facturas','proveedores','categorias','fijos'].forEach(v=>{ let el=document.getElementById('fin-'+v); if(el) el.classList.toggle('hidden',finView!=v); let b=document.getElementById('f-'+v); if(b) b.className=finView==v?'px-3 py-2 rounded-full text-[10px] font-black bg-white text-black':'px-3 py-2 rounded-full text-[10px] bg-white/20 text-white'; });
  let mesEl=document.getElementById('mesFlujo'); if(mesEl&&!mesEl.value) mesEl.value=new Date().toISOString().slice(0,7);
  let y=0,m=0; if(mesEl.value){ let p=mesEl.value.split('-'); y=parseInt(p[0]); m=parseInt(p[1]); }
  let start=new Date(y,m-1,1).getTime(), end=new Date(y,m,0,23,59,59).getTime();
  let filtrados=facts.filter(f=>{ let t=f.fechaObj||new Date(f.fecha+'T00:00:00').getTime(); return t>=start && t<=end; });
  let entradas=filtrados.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0);
  let salidas=filtrados.filter(f=>f.tipo=='salida').reduce((s,f)=>s+f.monto,0);
  document.getElementById('flu-e').innerText=entradas.toFixed(0); document.getElementById('flu-s').innerText=salidas.toFixed(0); document.getElementById('flu-g').innerText=(entradas-salidas).toFixed(0);
  let lista=document.getElementById('flu-lista'); let h=''; if(!filtrados.length) h='<p class="text-center text-[12px] text-gray-400 py-6">Sin movimientos</p>'; else filtrados.sort((a,b)=>b.fechaObj-a.fechaObj).forEach(f=>{ let isE=f.tipo=='entrada'; h+=`<div class="flex justify-between items-center py-2 border-b"><div><p class="text-[12px] font-bold">${f.concepto}</p><p class="text-[10px] text-gray-400">${f.fecha}</p></div><p class="font-black text-[13px] ${isE?'text-green-600':'text-red-600'}">${isE?'+':'-'}$${f.monto.toFixed(0)}</p></div>`; }); if(lista) lista.innerHTML=h;
  let fl=document.getElementById('f-lista'); if(fl){ let hh=''; filtrados.slice().reverse().forEach(f=>{ hh+=`<div class="flex justify-between py-2 border-b"><p class="text-[12px] font-bold">${f.concepto}</p><b class="${f.tipo=='entrada'?'text-green-600':'text-red-600'}">$${f.monto}</b></div>`; }); fl.innerHTML=hh||'Sin datos'; }
  let lc=document.getElementById('listaCat'); if(lc){ let hh=''; cats.forEach((c,i)=>{ hh+=`<div class="flex justify-between items-center bg-gray-50 p-3 rounded-xl mt-2 border"><b class="text-[13px]">${c.nombre}</b><button onclick="let cs=getCatG(); cs.splice(${i},1); localStorage.setItem('catGastos',JSON.stringify(cs)); renderFinanzas();" class="text-red-400 font-black">X</button></div>`; }); lc.innerHTML=hh; }
  let lp=document.getElementById('listaProv'); if(lp){ let hh=''; provs.forEach((p,i)=>{ hh+=`<div class="flex justify-between bg-gray-50 p-3 rounded-xl mt-2"><b>${p.nombre}</b><button onclick="let pr=getProv(); pr.splice(${i},1); localStorage.setItem('proveedores',JSON.stringify(pr)); renderFinanzas();" class="text-red-400">X</button></div>`; }); lp.innerHTML=hh; }
}
function addCatProd(){ let n=document.getElementById('newCat').value.trim(), g=document.getElementById('newCatTipo').value; if(!n) return; let cs=getCats(); cs.push({id:Date.now().toString(),nombre:n,grupo:g}); localStorage.setItem('categoriasV2',JSON.stringify(cs)); document.getElementById('newCat').value=''; renderCatsProd(); }
function renderCatsProd(){ let cs=getCats(); let h=''; cs.forEach((c,i)=>{ h+=`<div class="flex gap-2 items-center bg-gray-50 p-2 rounded-xl mt-2"><input value="${c.nombre}" onchange="let cs=getCats(); cs[${i}].nombre=this.value; localStorage.setItem('categoriasV2',JSON.stringify(cs)); renderCatsProd();" class="flex-1 bg-transparent font-bold text-sm"><span class="text-[9px] ${c.grupo=='recetario'?'bg-amber-200':'bg-black text-white'} px-2 py-0.5 rounded-full">${c.grupo}</span><button onclick="let cs=getCats(); cs.splice(${i},1); localStorage.setItem('categoriasV2',JSON.stringify(cs)); renderCatsProd();" class="text-red-400">x</button></div>`; }); let el=document.getElementById('listaCats'); if(el) el.innerHTML=h; }
function addFijo(d={}){ let div=document.createElement('div'); div.className='flex gap-2 items-center bg-gray-50 p-2 rounded-xl border'; div.innerHTML=`<input value="${d.nombre||''}" placeholder="Renta" class="f-n flex-1 bg-transparent font-bold text-[13px] p-2 outline-none" oninput="calcFijos()"><input type="number" value="${d.monto||''}" placeholder="$" class="f-m w-28 border-2 border-black p-2.5 rounded-xl font-black" oninput="calcFijos()"><button onclick="this.parentElement.remove();calcFijos()" class="text-red-400 w-8 h-8 bg-white rounded-full font-black">X</button>`; document.getElementById('gastosFijos').appendChild(div); }
function calcFijos(){ let tot=0,arr=[]; document.querySelectorAll('#gastosFijos > div').forEach(r=>{ let n=r.querySelector('.f-n')?.value||''; let m=parseFloat(r.querySelector('.f-m')?.value)||0; if(n||m){ arr.push({nombre:n,monto:m}); tot+=m; } }); localStorage.setItem('gastosFijos',JSON.stringify(arr)); let pm=parseFloat(document.getElementById('prodMes').value)||100; localStorage.setItem('prodMes',pm); let por=pm>0?tot/pm:0; document.getElementById('totMes').innerText=tot.toFixed(0); document.getElementById('porRec').innerText=por.toFixed(2); let cf=document.getElementById('c-fijos'); if(cf) cf.innerText=por.toFixed(2); calc(); calc2(); }

let gf=getFijos(); if(gf.length){ gf.forEach(g=>addFijo(g)); } else { addFijo({nombre:'Renta',monto:3000}); }
document.getElementById('prodMes').value=localStorage.getItem('prodMes')||100;
let today=new Date().toISOString().split('T')[0]; let gd=document.getElementById('g-fecha'); if(gd) gd.value=today;
let me=document.getElementById('mesFlujo'); if(me) me.value=new Date().toISOString().slice(0,7);
calcFijos(); renderInventario(); renderVenta(); renderFinanzas(); renderInventarioMaster(); renderClientes(); renderClientesSel(); showTab('costos');
</script></body></html>
"""
