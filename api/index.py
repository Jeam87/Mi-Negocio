from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 9.0 Inventario</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>input,select,textarea{color:#000!important;background:#fff!important}input::placeholder{color:#9CA3AF!important}</style></head>
<body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[100px]">
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><h1 class="font-black">Mi Negocio</h1><button onclick="showTab('config')" class="text-[10px] bg-gray-100 px-3 py-1 rounded-full">Config</button></div>

<div id="tab-costos" class="p-3 hidden">
<div class="bg-white rounded-[28px] p-4 shadow-sm">
<div class="flex gap-2 mb-2"><button id="bRec" onclick="setTipo('recetario')" class="flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white">RECETARIO</button><button id="bCat" onclick="setTipo('catalogo')" class="flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100">CATALOGO</button></div>
<input id="nombre" placeholder="Ej: Masa crepas" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[15px]">
<div id="insumos" class="mt-4 space-y-3"></div>
<div class="grid grid-cols-2 gap-2 mt-4"><button onclick="addInsumo()" class="text-[11px] bg-orange-100 py-3 rounded-full font-black">+ Ingrediente del inventario</button><button onclick="addSalsa()" class="text-[11px] bg-amber-200 py-3 rounded-full font-black">+ Del recetario</button></div>
<button id="btnComp" onclick="addComp()" class="hidden w-full mt-2 text-[11px] bg-blue-100 py-3 rounded-full font-black">+ Complemento</button>
<div class="mt-4 p-4 bg-[#0F172A] text-white rounded-[16px] text-[13px]"><div class="flex justify-between"><span>Ingredientes</span><b>$<span id="c-ing">0.00</span></b></div><div class="flex justify-between text-amber-300"><span>+ Fijos auto</span><b>$<span id="c-fijos">0.00</span></b></div><div class="flex justify-between font-black text-[15px] border-t border-white/20 mt-2 pt-2"><span>Costo $<span id="costo">0.00</span></span><span class="text-green-300">Venta $<span id="venta">0.00</span></span></div><div class="mt-2 flex gap-2 items-center"><span class="text-[10px]">Margen</span><input id="margen" type="number" value="100" class="w-14 text-black rounded-lg text-center font-black py-1" oninput="calc()"><input id="ventaManual" type="number" placeholder="$ final" class="ml-auto w-24 text-black rounded-lg px-2 py-1 font-black" oninput="calc()"></div></div>
<button onclick="guardarProd()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR</button><button id="btnCancel" onclick="cancelEdit()" class="hidden w-full mt-2 bg-gray-100 py-3 rounded-2xl text-[11px]">Cancelar</button>
</div><div id="listaInv" class="mt-5"></div>
</div>

<div id="tab-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div><div class="mt-6 bg-white rounded-[20px] p-4 shadow-xl border"><div id="ticket" class="text-[12px]">Vacio</div><div class="flex justify-between font-black text-lg mt-3">Total $<span id="c-total">0</span></div><button onclick="cobrar()" class="w-full mt-3 bg-black text-white py-3 rounded-xl font-black">COBRAR -> Flujo</button></div></div>

<!-- NUEVO INVENTARIO MAESTRO -->
<div id="tab-inventario" class="p-3 hidden">
<div class="bg-[#2D3748] rounded-[24px] p-4 text-white"><h2 class="font-black text-[15px]">📦 Inventario maestro</h2><p class="text-[11px] opacity-70 mt-1">Precios por kg, L, metro, pza. Si cambias precio aquí, todas las recetas se actualizan solas</p></div>
<div class="mt-3 bg-white rounded-[20px] p-4 shadow-sm">
<div class="grid grid-cols-5 gap-2">
<input id="inv-nombre" placeholder="Ej: Papas" class="col-span-2 border-2 border-black p-3 rounded-xl font-bold text-[13px]">
<input id="inv-precio" type="number" placeholder="$30" class="border-2 border-black p-3 rounded-xl font-black text-[13px]">
<select id="inv-unidad" class="border-2 border-black p-3 rounded-xl text-[11px] font-bold"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>galon</option><option>pza</option><option>m</option><option>cm</option></select>
<button onclick="addInventario()" class="bg-black text-white rounded-xl font-black text-xl">+</button>
</div>
<button onclick="addInventario()" class="w-full mt-2 bg-black text-white py-3 rounded-2xl font-black text-[13px]">GUARDAR EN INVENTARIO</button>
<div id="inv-msg" class="hidden mt-3 p-2 rounded-xl text-center font-bold text-[12px]"></div>
<input id="buscInv" placeholder="🔍 Buscar papa, jitomate..." class="w-full border-2 p-3 rounded-xl mt-3 text-[12px]" oninput="renderInventarioMaster()">
<div id="listaInvMaster" class="mt-4 space-y-2"></div>
</div>
</div>

<div id="tab-finanzas" class="p-3 hidden">
<div class="bg-[#2D3748] rounded-[24px] p-4 text-white"><div class="flex justify-between items-center"><h2 class="font-black">Finanzas</h2><button onclick="openGasto()" class="bg-[#4FD1C5] text-black w-10 h-10 rounded-xl font-black text-xl">+</button></div>
<div class="mt-3 flex gap-1 overflow-auto">
<button onclick="setFin('flujo')" id="f-flujo" class="px-3 py-2 rounded-full text-[10px] font-black bg-white text-black">📊 Flujo</button>
<button onclick="setFin('facturas')" id="f-facturas" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Facturas</button>
<button onclick="setFin('proveedores')" id="f-proveedores" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Provee.</button>
<button onclick="setFin('categorias')" id="f-categorias" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Cat.</button>
<button onclick="setFin('fijos')" id="f-fijos" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Fijos</button>
</div></div>
<div id="fin-flujo" class="mt-3 bg-white rounded-[20px] p-4 shadow-sm"><div class="flex justify-between items-center"><h3 class="font-black text-[14px]">Flujo de caja</h3><input id="mesFlujo" type="month" class="border-2 border-black rounded-xl px-2 py-1 text-[12px] font-bold" onchange="renderFinanzas()"></div>
<div class="grid grid-cols-3 gap-2 mt-4 text-center"><div class="bg-green-50 border-2 border-green-200 rounded-2xl p-3"><p class="text-[9px] font-black text-green-700">ENTRADAS</p><p class="font-black text-green-600">$<span id="flu-e">0</span></p></div><div class="bg-red-50 border-2 border-red-200 rounded-2xl p-3"><p class="text-[9px] font-black text-red-700">SALIDAS</p><p class="font-black text-red-600">$<span id="flu-s">0</span></p></div><div class="bg-black text-white rounded-2xl p-3"><p class="text-[9px] font-black opacity-60">GANANCIA</p><p class="font-black text-[#4FD1C5]">$<span id="flu-g">0</span></p><p class="text-[8px]" id="flu-g-p">0%</p></div></div>
<div class="w-full bg-gray-100 rounded-full h-3 flex overflow-hidden mt-4"><div id="bar-e" class="bg-green-500 h-3" style="width:50%"></div><div id="bar-s" class="bg-red-500 h-3" style="width:50%"></div></div><div id="flu-lista" class="mt-4 space-y-2"></div></div>
<div id="fin-facturas" class="hidden mt-3 bg-white rounded-2xl p-3"><div id="f-lista"></div></div>
<div id="fin-proveedores" class="hidden mt-3 bg-white rounded-2xl p-4"><div class="flex gap-2"><input id="provNombre" placeholder="Proveedor" class="flex-1 border-2 border-black p-3 rounded-xl font-bold"><button onclick="addProv()" class="bg-black text-white px-6 rounded-xl font-black">+</button></div><div id="listaProv" class="mt-3 space-y-2"></div></div>
<div id="fin-categorias" class="hidden mt-3 bg-white rounded-[20px] p-4"><div class="flex gap-2"><input id="catNombre" placeholder="Ej: Gasolina" class="flex-1 border-2 border-black p-4 rounded-2xl font-bold"><button onclick="addCat()" class="bg-black text-white px-6 rounded-2xl font-black">+</button></div><button onclick="addCat()" class="w-full mt-2 bg-black text-white py-3 rounded-2xl font-black">GUARDAR</button><div id="catMsg" class="hidden mt-3 p-2 rounded-xl text-center font-bold text-[12px]"></div><div id="listaCat" class="mt-4 space-y-2"></div></div>
<div id="fin-fijos" class="hidden mt-3 bg-white rounded-[20px] p-4"><input id="prodMes" type="number" value="100" class="w-full border-2 border-black p-3 rounded-xl mt-2 font-black" oninput="calcFijos()"><div id="gastosFijos" class="mt-3 space-y-2"></div><button onclick="addFijo()" class="w-full mt-3 bg-gray-100 py-3 rounded-full font-black text-[11px]">+ Agregar gasto fijo</button><div class="mt-4 bg-black text-white p-4 rounded-2xl text-center">Total mes $<span id="totMes">0</span> | Por receta $<span id="porRec">0.00</span></div></div>
<div id="modalGasto" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"><div class="bg-white w-full max-w-sm rounded-[24px] p-5"><select id="g-tipo" class="w-full border-2 p-3 rounded-xl mt-3 font-bold"><option value="salida">🔴 Salida</option><option value="entrada">🟢 Entrada</option></select><input id="g-concepto" placeholder="Concepto" class="w-full border-2 p-3 rounded-xl mt-2 font-bold"><input id="g-monto" type="number" placeholder="$" class="w-full border-2 p-3 rounded-xl mt-2 font-black"><select id="g-cat" class="w-full border-2 p-3 rounded-xl mt-2 text-[12px]"></select><input id="g-fecha" type="date" class="w-full border-2 p-3 rounded-xl mt-2 font-bold"><div class="flex gap-2 mt-4"><button onclick="document.getElementById('modalGasto').classList.add('hidden')" class="flex-1 bg-gray-100 py-3 rounded-xl">Cerrar</button><button onclick="addMov()" class="flex-1 bg-black text-white py-3 rounded-xl font-black">Guardar</button></div></div></div>
</div>

<div id="tab-clientes" class="p-3 hidden"><div id="listaClientes"></div></div>
<div id="tab-config" class="p-3 hidden"><div class="bg-white rounded-2xl p-4"><h3 class="font-black text-sm">Categorias productos</h3><div id="listaCats" class="mt-2"></div><input id="newCat" placeholder="Nueva" class="w-full border-2 p-3 rounded-xl mt-3"><select id="newCatTipo" class="w-full border-2 p-3 rounded-xl mt-2"><option value="recetario">Recetario</option><option value="catalogo">Catalogo</option></select><button onclick="addCatProd()" class="w-full mt-2 bg-black text-white py-3 rounded-xl">+ Agregar</button></div></div>

<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30">
<button onclick="showTab('costos')" id="n-costos" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-book"></i><span class="text-[8px]">Crear</span></button>
<button onclick="showTab('vender')" id="n-vender" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-store"></i><span class="text-[8px]">Catalogo</span></button>
<button onclick="showTab('inventario')" id="n-inventario" class="flex flex-col items-center text-black"><i class="fa-solid fa-boxes-stacked"></i><span class="text-[8px] font-bold">Inventario</span></button>
<button onclick="showTab('finanzas')" id="n-finanzas" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-chart-line"></i><span class="text-[8px]">Finanzas</span></button>
</div></div>

<script>
const U=['kg','g','L','ml','galon','pza','m','cm'];
let tipoAct='recetario', editId=null, carrito=[], finView='flujo';
function bf(u){ if(u=='kg'||u=='L'||u=='m') return 1000; if(u=='galon') return 3785; if(u=='g'||u=='ml'||u=='cm') return 1; return 1; }
function getCats(){ let c=JSON.parse(localStorage.getItem('categoriasV2')||'[]'); if(!c.length){ c=[{id:'recetario',nombre:'Masa base',grupo:'recetario'},{id:'catalogo',nombre:'Crepas',grupo:'catalogo'}]; localStorage.setItem('categoriasV2',JSON.stringify(c)); } return c; }
function getProd(){ return JSON.parse(localStorage.getItem('productosV2')||'[]'); }
function getFijos(){ return JSON.parse(localStorage.getItem('gastosFijos')||'[]'); }
function getFacts(){ return JSON.parse(localStorage.getItem('facturas')||'[]'); }
function getCatG(){ let c=JSON.parse(localStorage.getItem('catGastos')||'[]'); if(!c.length){ c=[{id:'renta',nombre:'Renta'}]; localStorage.setItem('catGastos',JSON.stringify(c)); } return c; }
function getProv(){ return JSON.parse(localStorage.getItem('proveedores')||'[]'); }
function getInv(){ let inv=JSON.parse(localStorage.getItem('inventarioMaestro')||'[]'); if(!inv.length){ inv=[{id:'1',nombre:'Papas',precio:30,unidad:'kg'},{id:'2',nombre:'Jitomate',precio:20,unidad:'kg'},{id:'3',nombre:'Leche',precio:40,unidad:'L'},{id:'4',nombre:'Harina',precio:25,unidad:'kg'}]; localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); } return inv; }

function showTab(t){
  ['costos','vender','inventario','finanzas','clientes','config'].forEach(x=>{
    let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hidden',x!=t);
    let nb=document.getElementById('n-'+x); if(nb){ nb.classList.toggle('text-black',x==t); nb.classList.toggle('text-gray-400',x!=t); }
  });
  if(t=='finanzas') renderFinanzas();
  if(t=='vender') renderVenta();
  if(t=='config') renderCatsProd();
  if(t=='inventario') renderInventarioMaster();
}
function setTipo(g){ let cs=getCats().filter(c=>c.grupo==g); if(cs.length) tipoAct=cs[0].id; renderBotones(); }
function renderBotones(){
  let cs=getCats(); let sel=cs.find(c=>c.id==tipoAct)||cs[0]; if(sel) tipoAct=sel.id;
  let isRec=sel?.grupo=='recetario';
  let bR=document.getElementById('bRec'), bC=document.getElementById('bCat');
  if(bR) bR.className=isRec?'flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white':'flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100';
  if(bC) bC.className=!isRec?'flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white':'flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100';
  let bc=document.getElementById('btnComp'); if(bc) bc.classList.toggle('hidden',isRec);
}

// INVENTARIO MAESTRO
function addInventario(){
  let n=document.getElementById('inv-nombre').value.trim(), p=parseFloat(document.getElementById('inv-precio').value), u=document.getElementById('inv-unidad').value;
  let msg=document.getElementById('inv-msg');
  if(!n||!p){ msg.className='mt-3 p-2 rounded-xl text-center font-bold bg-red-100 text-red-700'; msg.innerText='Pon nombre y precio'; msg.classList.remove('hidden'); return; }
  let inv=getInv();
  let exist=inv.find(x=>x.nombre.toLowerCase()==n.toLowerCase());
  if(exist){ exist.precio=p; exist.unidad=u; msg.className='mt-3 p-2 rounded-xl text-center font-bold bg-amber-100'; msg.innerText='✅ Actualizado: '+n+' $'+p+'/'+u+' - recetas actualizadas solas'; }
  else { inv.push({id:Date.now().toString(),nombre:n,precio:p,unidad:u}); msg.className='mt-3 p-2 rounded-xl text-center font-bold bg-green-100 text-green-700'; msg.innerText='✅ Guardado: '+n+' $'+p+'/'+u; }
  localStorage.setItem('inventarioMaestro',JSON.stringify(inv));
  document.getElementById('inv-nombre').value=''; document.getElementById('inv-precio').value='';
  msg.classList.remove('hidden'); setTimeout(()=>msg.classList.add('hidden'),2500);
  renderInventarioMaster(); calc();
}
function renderInventarioMaster(){
  let inv=getInv(); let q=(document.getElementById('buscInv')?.value||'').toLowerCase();
  let filtered=inv.filter(x=>x.nombre.toLowerCase().includes(q));
  let h=''; filtered.forEach((it,i)=>{
    let realIdx=getInv().findIndex(x=>x.id==it.id);
    h+=`<div class="flex gap-2 items-center bg-gray-50 p-3 rounded-xl border"><div class="flex-1"><b class="text-[13px]">${it.nombre}</b><br><span class="text-[11px] text-gray-500">$${it.precio} / ${it.unidad}</span></div><input type="number" value="${it.precio}" onchange="updateInvPrecio(${realIdx},this.value)" class="w-20 border-2 border-black p-2 rounded-xl font-black text-[13px]"><select onchange="updateInvUnidad(${realIdx},this.value)" class="border-2 p-2 rounded-xl text-[11px]"><option ${it.unidad=='kg'?'selected':''}>kg</option><option ${it.unidad=='g'?'selected':''}>g</option><option ${it.unidad=='L'?'selected':''}>L</option><option ${it.unidad=='ml'?'selected':''}>ml</option><option ${it.unidad=='pza'?'selected':''}>pza</option><option ${it.unidad=='m'?'selected':''}>m</option></select><button onclick="delInv(${realIdx})" class="text-red-400 font-black px-2">X</button></div>`;
  });
  document.getElementById('listaInvMaster').innerHTML=h||'<p class="text-center text-[11px] text-gray-400 py-4">Sin resultados</p>';
}
function updateInvPrecio(idx,val){ let inv=getInv(); inv[idx].precio=parseFloat(val)||0; localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); calc(); renderInventarioMaster(); }
function updateInvUnidad(idx,val){ let inv=getInv(); inv[idx].unidad=val; localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); calc(); }
function delInv(idx){ if(!confirm('¿Borrar?')) return; let inv=getInv(); inv.splice(idx,1); localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); renderInventarioMaster(); }

// RECETARIO CONECTADO A INVENTARIO
function addInsumo(d={}){
  let inv=getInv();
  let opts=inv.map(it=>`<option value="${it.id}" ${d.invId==it.id?'selected':''} data-p="${it.precio}" data-u="${it.unidad}">${it.nombre} $${it.precio}/${it.unidad}</option>`).join('');
  let div=document.createElement('div'); div.className='bg-[#FFF8F0] p-3 rounded-[16px] border-2 border-orange-100'; div.dataset.t='ing';
  div.innerHTML=`<div class="flex justify-between mb-2"><select class="in-n font-black text-[13px] w-full bg-white border-2 border-black p-2 rounded-xl" onchange="cambiarInv(this)"><option value="">-- Elige del inventario --</option>${opts}</select><button onclick="this.closest('div').parentElement.remove();calc()" class="ml-2 text-red-400 bg-white w-8 h-8 rounded-full font-black">x</button></div>
  <div class="bg-white rounded-xl p-2">
    <p class="text-[9px] font-black opacity-50">PRECIO MAESTRO (se actualiza solo)</p>
    <div class="grid grid-cols-3 gap-2 mt-1"><input type="number" value="${d.cc||1}" class="in-cc w-full border-2 p-2 rounded-lg font-bold" oninput="calc()"><input value="${d.uc||'kg'}" class="in-uc w-full border-2 p-2 rounded-lg text-[11px] font-bold" readonly><input type="number" value="${d.pc||''}" class="in-pc w-full border-2 border-amber-300 bg-amber-50 p-2 rounded-lg font-bold" oninput="calc()"></div>
    <div class="h-px bg-gray-100 my-2"></div>
    <p class="text-[9px] font-black opacity-50">CUANTO USAS</p>
    <div class="grid grid-cols-3 gap-2 mt-1"><input type="number" value="${d.cu||''}" placeholder="250" class="in-cu w-full border-2 border-black p-2 rounded-lg font-bold text-[13px]" oninput="calc()"><select class="in-uu w-full border-2 border-black p-2 rounded-lg text-[11px]" onchange="calc()"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>pza</option><option>m</option></select><div class="bg-black text-white rounded-lg p-2 text-center"><div class="text-[8px] opacity-70">ME SALE</div><div class="font-black text-[12px]">$<span class="in-sub">0.00</span></div></div></div>
  </div>`;
  document.getElementById('insumos').appendChild(div);
  if(d.invId){ let sel=div.querySelector('.in-n'); if(sel) cambiarInv(sel); }
}
function cambiarInv(sel){
  let row=sel.closest('div').parentElement; let id=sel.value; let opt=sel.options[sel.selectedIndex];
  if(!id){ return; }
  let p=parseFloat(opt.dataset.p)||0; let u=opt.dataset.u||'kg';
  row.querySelector('.in-pc').value=p; row.querySelector('.in-uc').value=u;
  row.dataset.invId=id;
  // auto sugerir unidad de uso
  let uu=row.querySelector('.in-uu'); if(u=='kg') uu.value='g'; if(u=='L') uu.value='ml'; if(u=='m') uu.value='cm';
  calc();
}
function addSalsa(){
  let bases=getCats().filter(c=>c.grupo=='recetario').map(c=>c.id); let ss=getProd().filter(p=>bases.includes(p.tipo));
  if(!ss.length) return alert('Primero crea algo en RECETARIO');
  let div=document.createElement('div'); div.className='bg-amber-50 p-3 rounded-[16px] border-2 border-amber-300'; div.dataset.t='rec';
  div.innerHTML=`<div class="flex justify-between"><span class="font-black text-[11px]">📖 Del recetario</span><button onclick="this.parentElement.parentElement.remove();calc()" class="text-red-400">x</button></div><div class="grid grid-cols-4 gap-2 mt-2 bg-white p-2 rounded-xl"><select class="in-sel col-span-3 border-2 p-2 rounded-lg text-[12px] font-bold" onchange="calc()">${ss.map(s=>`<option value="${s.id}" data-c="${s.costo}">${s.nombre} $${s.costo.toFixed(2)}</option>`).join('')}</select><input type="number" value="1" class="in-cant border-2 p-2 rounded-lg font-bold" oninput="calc()"><div class="col-span-4 text-right font-black text-[12px]">Me sale: $<span class="in-sub">0.00</span></div></div>`;
  document.getElementById('insumos').appendChild(div); calc();
}
function addComp(){
  let ps=getProd(); if(!ps.length) return alert('No hay productos');
  let div=document.createElement('div'); div.className='bg-blue-50 p-3 rounded-[16px] border-2 border-blue-200'; div.dataset.t='cat';
  div.innerHTML=`<div class="flex justify-between"><span class="font-black text-[11px]">🛒 Complemento</span><button onclick="this.parentElement.parentElement.remove();calc()" class="text-red-400">x</button></div><div class="grid grid-cols-4 gap-2 mt-2 bg-white p-2 rounded-xl"><select class="in-sel col-span-3 border-2 p-2 rounded-lg text-[12px] font-bold" onchange="calc()">${ps.map(s=>`<option value="${s.id}" data-c="${s.venta}">${s.nombre} $${s.venta.toFixed(2)}</option>`).join('')}</select><input type="number" value="1" class="in-cant border-2 p-2 rounded-lg font-bold" oninput="calc()"><div class="col-span-4 text-right font-black text-[12px]">$<span class="in-sub">0.00</span></div></div>`;
  document.getElementById('insumos').appendChild(div); calc();
}
function addFijo(d={}){ let div=document.createElement('div'); div.className='flex gap-2 items-center bg-gray-50 p-2 rounded-xl border'; div.innerHTML=`<input value="${d.nombre||''}" placeholder="Renta" class="f-n flex-1 bg-transparent font-bold text-[13px] p-2 outline-none" oninput="calcFijos()"><input type="number" value="${d.monto||''}" placeholder="$" class="f-m w-28 border-2 border-black p-2.5 rounded-xl font-black" oninput="calcFijos()"><button onclick="this.parentElement.remove();calcFijos()" class="text-red-400 w-8 h-8 bg-white rounded-full font-black">X</button>`; document.getElementById('gastosFijos').appendChild(div); }
function calcFijos(){ let tot=0,arr=[]; document.querySelectorAll('#gastosFijos > div').forEach(r=>{ let n=r.querySelector('.f-n')?.value||''; let m=parseFloat(r.querySelector('.f-m')?.value)||0; if(n||m){ arr.push({nombre:n,monto:m}); tot+=m; } }); localStorage.setItem('gastosFijos',JSON.stringify(arr)); let pm=parseFloat(document.getElementById('prodMes').value)||100; localStorage.setItem('prodMes',pm); let por=pm>0?tot/pm:0; document.getElementById('totMes').innerText=tot.toFixed(0); document.getElementById('porRec').innerText=por.toFixed(2); let cf=document.getElementById('c-fijos'); if(cf) cf.innerText=por.toFixed(2); calc(); }
function calc(){
  let tot=0;
  // actualizar precios desde inventario maestro si estan vinculados
  let inv=getInv();
  document.querySelectorAll('#insumos > div').forEach(row=>{
    let sub=row.querySelector('.in-sub'); if(!sub) return;
    if(row.dataset.t=='rec' || row.dataset.t=='cat'){
      let sel=row.querySelector('.in-sel'); if(!sel?.options[sel.selectedIndex]) return;
      let c=parseFloat(sel.options[sel.selectedIndex].dataset.c)||0;
      let cant=parseFloat(row.querySelector('.in-cant').value)||0;
      let s=c*cant; sub.innerText=s.toFixed(2); tot+=s;
    } else {
      // si tiene invId, tomar precio actual del maestro
      let invId=row.dataset.invId || row.querySelector('.in-n')?.value;
      if(invId){ let it=inv.find(x=>x.id==invId); if(it){ row.querySelector('.in-pc').value=it.precio; row.querySelector('.in-uc').value=it.unidad; } }
      let cc=parseFloat(row.querySelector('.in-cc').value)||1, pc=parseFloat(row.querySelector('.in-pc').value)||0, cu=parseFloat(row.querySelector('.in-cu').value)||0;
      let uc=row.querySelector('.in-uc').value, uu=row.querySelector('.in-uu').value;
      if(!pc||!cu){ sub.innerText='0.00'; return; }
      function bf2(u){ if(u=='kg'||u=='L'||u=='m') return 1000; if(u=='g'||u=='ml'||u=='cm'||u=='pza') return 1; return 1; }
      let cost=0;
      if(uc==uu) cost=(pc/cc)*cu;
      else if((uc=='kg'&&uu=='g')||(uc=='L'&&uu=='ml')||(uc=='m'&&uu=='cm')) cost=(pc/(cc*1000))*cu;
      else if((uc=='g'&&uu=='kg')||(uc=='ml'&&uu=='L')||(uc=='cm'&&uu=='m')) cost=(pc/(cc/1000))*cu;
      else cost=(pc/(cc*bf2(uc)))*(cu*bf2(uu));
      if(uc=='pza'||uu=='pza') cost=(pc/cc)*cu;
      sub.innerText=cost.toFixed(2); tot+=cost;
    }
  });
  document.getElementById('c-ing').innerText=tot.toFixed(2);
  let gf=parseFloat(document.getElementById('c-fijos')?.innerText||'0');
  document.getElementById('costo').innerText=(tot+gf).toFixed(2);
  let m=parseFloat(document.getElementById('margen').value)||0;
  let vm=document.getElementById('ventaManual').value;
  let ve=document.getElementById('venta'); if(ve){ if(vm&&parseFloat(vm)>0) ve.innerText=parseFloat(vm).toFixed(2); else ve.innerText=((tot+gf)*(1+m/100)).toFixed(2); }
}
function guardarProd(){
  let nom=document.getElementById('nombre').value.trim(); if(!nom) return alert('Nombre');
  let costo=parseFloat(document.getElementById('costo').innerText), venta=parseFloat(document.getElementById('venta').innerText);
  let ings=[]; document.querySelectorAll('#insumos > div').forEach(row=>{
    if(row.dataset.t=='rec'||row.dataset.t=='cat'){ ings.push({tipo:row.dataset.t,id:row.querySelector('.in-sel').value,cant:row.querySelector('.in-cant').value}); }
    else {
      let sel=row.querySelector('.in-n'); let invId=row.dataset.invId||sel.value;
      ings.push({tipo:'ing',invId:invId,n:sel.options[sel.selectedIndex]?.text||'',cc:row.querySelector('.in-cc').value,uc:row.querySelector('.in-uc').value,pc:row.querySelector('.in-pc').value,cu:row.querySelector('.in-cu').value,uu:row.querySelector('.in-uu').value});
    }
  });
  let ps=getProd();
  if(editId){ let idx=ps.findIndex(x=>x.id==editId); if(idx>=0){ ps[idx].nombre=nom; ps[idx].costo=costo; ps[idx].venta=venta; ps[idx].tipo=tipoAct; ps[idx].ingredientes=ings; } }
  else { ps.push({id:Date.now(),tipo:tipoAct,nombre:nom,costo,venta,ingredientes:ings}); }
  localStorage.setItem('productosV2',JSON.stringify(ps)); cancelEdit(); renderInventario(); renderVenta(); showTab('costos');
}
function renderInventario(){
  let ps=getProd(); let cs=getCats(); let h=''; ps.forEach((p,i)=>{
    let cat=cs.find(c=>c.id==p.tipo); h+=`<div class="bg-white p-3 rounded-2xl flex gap-2 shadow-sm mt-3 border items-center"><span class="text-[8px] bg-gray-100 px-2 py-1 rounded-full font-bold">${cat?cat.nombre:p.tipo}</span><div class="flex-1"><b class="text-[13px]">${p.nombre}</b><br><span class="text-[11px]">$${p.costo.toFixed(2)} → $${p.venta.toFixed(2)}</span></div><button onclick="editarProd(${p.id})" class="bg-blue-50 text-blue-600 px-3 py-1.5 rounded-full text-[11px] font-black">Editar</button><button onclick="if(confirm('¿Borrar?')){let pr=getProd(); pr.splice(${i},1); localStorage.setItem('productosV2',JSON.stringify(pr)); renderInventario(); renderVenta();}" class="text-red-400 ml-1 font-black">X</button></div>`;
  }); document.getElementById('listaInv').innerHTML=h;
}
function editarProd(id){ let p=getProd().find(x=>x.id==id); if(!p) return; editId=id; tipoAct=p.tipo; document.getElementById('nombre').value=p.nombre; document.getElementById('insumos').innerHTML=''; if(p.ingredientes){ p.ingredientes.forEach(ing=>{ if(ing.tipo=='ing') addInsumo({invId:ing.invId,n:ing.n,cc:ing.cc,uc:ing.uc,pc:ing.pc,cu:ing.cu,uu:ing.uu}); else if(ing.tipo=='rec'){ addSalsa(); let l=document.getElementById('insumos').lastElementChild; l.querySelector('.in-sel').value=ing.id; l.querySelector('.in-cant').value=ing.cant; } else if(ing.tipo=='cat'){ addComp(); let l=document.getElementById('insumos').lastElementChild; l.querySelector('.in-sel').value=ing.id; l.querySelector('.in-cant').value=ing.cant; } }); } showTab('costos'); renderBotones(); calc(); document.getElementById('btnCancel').classList.remove('hidden'); }
function cancelEdit(){ editId=null; document.getElementById('nombre').value=''; document.getElementById('insumos').innerHTML=''; document.getElementById('ventaManual').value=''; document.getElementById('btnCancel').classList.add('hidden'); addInsumo({}); calc(); }
function renderVenta(){ let cs=getCats(); let ids=cs.filter(c=>c.grupo=='catalogo').map(c=>c.id); let ps=getProd().filter(p=>ids.includes(p.tipo)); let h=''; ps.forEach(p=>{ h+=`<div class="bg-white rounded-2xl shadow-sm border overflow-hidden"><button onclick="addCart(${p.id})" class="w-full text-left p-3"><b class="text-[12px]">${p.nombre}</b><p class="text-green-600 font-black text-[12px]">$${p.venta.toFixed(2)}</p></button></div>`; }); document.getElementById('listaVenta').innerHTML=h||'<p class="text-center text-gray-400 py-10 col-span-2">Crea productos en CATALOGO</p>'; }
function addCart(id){ let p=getProd().find(x=>x.id==id); let ex=carrito.find(x=>x.id==id); if(ex) ex.qty++; else carrito.push({...p,qty:1}); let t=0, html=''; carrito.forEach(x=>{ t+=x.venta*x.qty; html+=`<div class="flex justify-between py-1"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)}</span></div>`; }); document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('ticket').innerHTML=html||'Vacio'; }
function cobrar(){ if(!carrito.length) return alert('Carrito vacio'); let tot=parseFloat(document.getElementById('c-total').innerText); let facts=getFacts(); let now=new Date(); let iso=now.toISOString().split('T')[0]; facts.push({id:Date.now(),concepto:'Venta: '+carrito.map(c=>c.nombre+' x'+c.qty).join(', '),monto:tot,fecha:iso,fechaObj:now.getTime(),tipo:'entrada',origen:'venta'}); localStorage.setItem('facturas',JSON.stringify(facts)); carrito=[]; document.getElementById('c-total').innerText='0'; document.getElementById('ticket').innerHTML='Vacio'; finView='flujo'; showTab('finanzas'); }
function setFin(v){ finView=v; renderFinanzas(); }
function addCat(){ let n=document.getElementById('catNombre').value.trim(); if(!n) return; let cs=getCatG(); cs.push({id:Date.now().toString(),nombre:n}); localStorage.setItem('catGastos',JSON.stringify(cs)); document.getElementById('catNombre').value=''; renderFinanzas(); }
function addProv(){ let n=document.getElementById('provNombre').value.trim(); if(!n) return; let ps=getProv(); ps.push({id:Date.now().toString(),nombre:n}); localStorage.setItem('proveedores',JSON.stringify(ps)); document.getElementById('provNombre').value=''; renderFinanzas(); }
function openGasto(){ let cats=getCatG(); document.getElementById('g-cat').innerHTML='<option value="">Sin categoria</option>'+cats.map(c=>`<option value="${c.id}">${c.nombre}</option>`).join(''); document.getElementById('modalGasto').classList.remove('hidden'); }
function addMov(){ let concepto=document.getElementById('g-concepto').value.trim(), monto=parseFloat(document.getElementById('g-monto').value), fecha=document.getElementById('g-fecha').value; if(!concepto||!monto||!fecha) return alert('Faltan datos'); let facts=getFacts(); facts.push({id:Date.now(),concepto,monto,fecha,fechaObj:new Date(fecha+'T00:00:00').getTime(),tipo:document.getElementById('g-tipo').value,catGastoId:document.getElementById('g-cat').value}); localStorage.setItem('facturas',JSON.stringify(facts)); document.getElementById('modalGasto').classList.add('hidden'); document.getElementById('g-concepto').value=''; document.getElementById('g-monto').value=''; renderFinanzas(); }
function renderFinanzas(){
  let facts=getFacts(); let cats=getCatG(); let provs=getProv();
  ['flujo','facturas','proveedores','categorias','fijos'].forEach(v=>{
    let el=document.getElementById('fin-'+v); if(el) el.classList.toggle('hidden',finView!=v);
    let b=document.getElementById('f-'+v); if(b) b.className=finView==v?'px-3 py-2 rounded-full text-[10px] font-black bg-white text-black':'px-3 py-2 rounded-full text-[10px] bg-white/20 text-white';
  });
  let mesEl=document.getElementById('mesFlujo'); if(mesEl&&!mesEl.value) mesEl.value=new Date().toISOString().slice(0,7);
  let y=0,m=0; if(mesEl.value){ let parts=mesEl.value.split('-'); y=parseInt(parts[0]); m=parseInt(parts[1]); }
  let start=new Date(y,m-1,1).getTime(), end=new Date(y,m,0,23,59,59).getTime();
  let filtrados=facts.filter(f=>{ let t=f.fechaObj||new Date(f.fecha+'T00:00:00').getTime(); return t>=start && t<=end; });
  let entradas=filtrados.filter(f=>f.tipo=='entrada').reduce((s,f)=>s+f.monto,0);
  let salidas=filtrados.filter(f=>f.tipo=='salida').reduce((s,f)=>s+f.monto,0);
  let gan=entradas-salidas;
  let porc=entradas>0?((gan/entradas)*100).toFixed(1):0;
  document.getElementById('flu-e').innerText=entradas.toFixed(0);
  document.getElementById('flu-s').innerText=salidas.toFixed(0);
  document.getElementById('flu-g').innerText=gan.toFixed(0);
  document.getElementById('flu-g-p').innerText=porc+'%';
  let tot=entradas+salidas||1; document.getElementById('bar-e').style.width=(entradas/tot*100)+'%'; document.getElementById('bar-s').style.width=(salidas/tot*100)+'%';
  let lista=document.getElementById('flu-lista'); let h='';
  if(!filtrados.length) h='<p class="text-center text-[12px] text-gray-400 py-6">Sin movimientos. Usa + o cobra en Catalogo</p>';
  else filtrados.sort((a,b)=>b.fechaObj-a.fechaObj).forEach(f=>{ let cat=cats.find(c=>c.id==f.catGastoId); let isE=f.tipo=='entrada'; h+=`<div class="flex justify-between items-center py-2 border-b"><div class="flex gap-2 items-center"><div class="w-8 h-8 rounded-full flex items-center justify-center ${isE?'bg-green-100':'bg-red-100'}">${isE?'💰':'💸'}</div><div><p class="text-[12px] font-bold">${f.concepto}</p><p class="text-[10px] text-gray-400">${f.fecha} ${cat?'• '+cat.nombre:''}</p></div></div><div class="text-right"><p class="font-black text-[13px] ${isE?'text-green-600':'text-red-600'}">${isE?'+':'-'}$${f.monto.toFixed(0)}</p><button onclick="let fs=getFacts(); fs=fs.filter(x=>x.id!=${f.id}); localStorage.setItem('facturas',JSON.stringify(fs)); renderFinanzas();" class="text-[9px] text-gray-300">Borrar</button></div></div>`; });
  if(lista) lista.innerHTML=h;
  let fl=document.getElementById('f-lista'); if(fl){ let hh=''; filtrados.slice().reverse().forEach(f=>{ hh+=`<div class="flex justify-between py-2 border-b"><div><p class="text-[12px] font-bold">${f.concepto}</p><p class="text-[10px] text-gray-400">${f.fecha}</p></div><b class="${f.tipo=='entrada'?'text-green-600':'text-red-600'}">$${f.monto}</b></div>`; }); fl.innerHTML=hh||'<p class="text-center py-6 text-gray-400">Sin datos</p>'; }
  let lc=document.getElementById('listaCat'); if(lc){ let hh=''; cats.forEach((c,i)=>{ hh+=`<div class="flex justify-between items-center bg-gray-50 p-3 rounded-xl mt-2 border"><b class="text-[13px]">${c.nombre}</b><button onclick="let cs=getCatG(); cs.splice(${i},1); localStorage.setItem('catGastos',JSON.stringify(cs)); renderFinanzas();" class="text-red-400 font-black">X</button></div>`; }); lc.innerHTML=hh; }
  let lp=document.getElementById('listaProv'); if(lp){ let hh=''; provs.forEach((p,i)=>{ hh+=`<div class="flex justify-between bg-gray-50 p-3 rounded-xl mt-2"><b>${p.nombre}</b><button onclick="let pr=getProv(); pr.splice(${i},1); localStorage.setItem('proveedores',JSON.stringify(pr)); renderFinanzas();" class="text-red-400">X</button></div>`; }); lp.innerHTML=hh||'<p class="text-[11px] text-gray-400">Sin proveedores</p>'; }
}
function addCatProd(){ let n=document.getElementById('newCat').value.trim(), g=document.getElementById('newCatTipo').value; if(!n) return; let cs=getCats(); cs.push({id:Date.now().toString(),nombre:n,grupo:g}); localStorage.setItem('categoriasV2',JSON.stringify(cs)); document.getElementById('newCat').value=''; renderCatsProd(); renderBotones(); }
function renderCatsProd(){ let cs=getCats(); let h=''; cs.forEach((c,i)=>{ h+=`<div class="flex gap-2 items-center bg-gray-50 p-2 rounded-xl mt-2"><input value="${c.nombre}" onchange="let cs=getCats(); cs[${i}].nombre=this.value; localStorage.setItem('categoriasV2',JSON.stringify(cs)); renderCatsProd(); renderBotones();" class="flex-1 bg-transparent font-bold text-sm"><span class="text-[9px] ${c.grupo=='recetario'?'bg-amber-200':'bg-black text-white'} px-2 py-0.5 rounded-full">${c.grupo}</span><button onclick="let cs=getCats(); cs.splice(${i},1); localStorage.setItem('categoriasV2',JSON.stringify(cs)); renderCatsProd(); renderBotones();" class="text-red-400">x</button></div>`; }); let el=document.getElementById('listaCats'); if(el) el.innerHTML=h; }

document.getElementById('margen').oninput=calc;
let gf=getFijos(); if(gf.length){ gf.forEach(g=>addFijo(g)); } else { addFijo({nombre:'Renta',monto:3000}); addFijo({nombre:'Luz',monto:800}); }
document.getElementById('prodMes').value=localStorage.getItem('prodMes')||100;
let today=new Date().toISOString().split('T')[0]; let gd=document.getElementById('g-fecha'); if(gd) gd.value=today;
let me=document.getElementById('mesFlujo'); if(me) me.value=new Date().toISOString().slice(0,7);
renderBotones(); calcFijos(); addInsumo({}); calc(); renderInventario(); renderVenta(); renderFinanzas(); renderInventarioMaster(); showTab('inventario');
</script></body></html>
"""
