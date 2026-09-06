from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 8.1 FIX</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>input,select,textarea{color:#000!important;background:#fff!important}input::placeholder{color:#9CA3AF!important}</style></head>
<body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[100px]">
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><h1 class="font-black">Mi Negocio</h1><button onclick="showTab('config')" class="text-[10px] bg-gray-100 px-3 py-1 rounded-full">Config</button></div>

<div id="tab-costos" class="p-3">
<div class="bg-white rounded-[28px] p-4 shadow-sm">
<div class="flex gap-2 mb-2"><button id="bRec" onclick="setTipo('recetario')" class="flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white">RECETARIO</button><button id="bCat" onclick="setTipo('catalogo')" class="flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100">CATALOGO</button></div>
<p id="ayuda" class="text-[10px] text-gray-500 mb-2">Recetario: precio por unidad y cuanto usas + fijos automaticos</p>
<input id="nombre" placeholder="Ej: Masa crepas" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[15px]">
<div id="insumos" class="mt-4 space-y-3"></div>
<div class="grid grid-cols-2 gap-2 mt-4"><button onclick="addInsumo()" class="text-[11px] bg-orange-100 py-3 rounded-full font-black">+ Ingrediente</button><button onclick="addSalsa()" class="text-[11px] bg-amber-200 py-3 rounded-full font-black">+ Del recetario</button></div>
<button id="btnComp" onclick="addComp()" class="hidden w-full mt-2 text-[11px] bg-blue-100 py-3 rounded-full font-black">+ Complemento</button>
<div class="mt-4 p-4 bg-[#0F172A] text-white rounded-[16px] text-[13px]">
<div class="flex justify-between"><span>Ingredientes</span><b>$<span id="c-ing">0.00</span></b></div>
<div class="flex justify-between text-amber-300"><span>+ Fijos auto</span><b>$<span id="c-fijos">0.00</span></b></div>
<div class="flex justify-between font-black text-[15px] border-t border-white/20 mt-2 pt-2"><span>Costo $<span id="costo">0.00</span></span><span class="text-green-300">Venta $<span id="venta">0.00</span></span></div>
<div class="mt-2 flex gap-2 items-center"><span class="text-[10px]">Margen</span><input id="margen" type="number" value="100" class="w-14 text-black rounded-lg text-center font-black py-1" oninput="calc()"><span class="text-[10px]">%</span><input id="ventaManual" type="number" placeholder="$ final" class="ml-auto w-24 text-black rounded-lg px-2 py-1 font-black" oninput="calc()"></div>
</div>
<button onclick="guardarProd()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black">GUARDAR</button>
<button id="btnCancel" onclick="cancelEdit()" class="hidden w-full mt-2 bg-gray-100 py-3 rounded-2xl text-[11px] font-bold">Cancelar edicion</button>
</div><div id="listaInv" class="mt-5"></div>
</div>

<div id="tab-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div>
<div class="mt-6 bg-white rounded-[20px] p-4 shadow-xl border"><h3 class="font-bold">Ticket</h3><div id="ticket" class="text-[12px] mt-2">Vacio</div><div class="flex justify-between font-black text-lg mt-3">Total $<span id="c-total">0</span></div><button onclick="cobrar()" class="w-full mt-3 bg-black text-white py-3 rounded-xl font-black">COBRAR -> Va a Flujo</button></div></div>

<div id="tab-finanzas" class="p-3 hidden">
<div class="bg-[#2D3748] rounded-[24px] p-4 text-white">
<div class="flex justify-between items-center"><h2 class="font-black">Finanzas</h2><button onclick="openGasto()" class="bg-[#4FD1C5] text-black w-10 h-10 rounded-xl font-black text-xl">+</button></div>
<div class="mt-3 flex gap-1 overflow-auto">
<button onclick="setFin('flujo')" id="f-flujo" class="px-3 py-2 rounded-full text-[10px] font-black bg-white text-black">📊 Flujo</button>
<button onclick="setFin('facturas')" id="f-facturas" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Facturas</button>
<button onclick="setFin('proveedores')" id="f-proveedores" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Provee.</button>
<button onclick="setFin('categorias')" id="f-categorias" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Cat.</button>
<button onclick="setFin('fijos')" id="f-fijos" class="px-3 py-2 rounded-full text-[10px] bg-white/20">Fijos</button>
</div>
</div>

<div id="fin-flujo" class="mt-3 bg-white rounded-[20px] p-4 shadow-sm">
<div class="flex justify-between items-center"><h3 class="font-black text-[14px]">Flujo de caja</h3><input id="mesFlujo" type="month" class="border-2 border-black rounded-xl px-2 py-1 text-[12px] font-bold" onchange="renderFinanzas()"></div>
<div class="grid grid-cols-3 gap-2 mt-4 text-center">
<div class="bg-green-50 border-2 border-green-200 rounded-2xl p-3"><p class="text-[9px] font-black text-green-700">ENTRADAS</p><p class="font-black text-[16px] text-green-600">$<span id="flu-e">0</span></p><p class="text-[8px]" id="flu-e-d">0 mov</p></div>
<div class="bg-red-50 border-2 border-red-200 rounded-2xl p-3"><p class="text-[9px] font-black text-red-700">SALIDAS</p><p class="font-black text-[16px] text-red-600">$<span id="flu-s">0</span></p><p class="text-[8px]" id="flu-s-d">0 mov</p></div>
<div class="bg-black text-white rounded-2xl p-3"><p class="text-[9px] font-black opacity-60">GANANCIA</p><p class="font-black text-[16px] text-[#4FD1C5]">$<span id="flu-g">0</span></p><p class="text-[8px]" id="flu-g-p">0%</p></div>
</div>
<div class="w-full bg-gray-100 rounded-full h-3 flex overflow-hidden mt-4"><div id="bar-e" class="bg-green-500 h-3" style="width:50%"></div><div id="bar-s" class="bg-red-500 h-3" style="width:50%"></div></div>
<div id="flu-lista" class="mt-4 space-y-2"></div>
</div>

<div id="fin-facturas" class="hidden mt-3 bg-white rounded-2xl p-3"><div id="f-lista"></div></div>
<div id="fin-proveedores" class="hidden mt-3 bg-white rounded-2xl p-4"><div class="flex gap-2"><input id="provNombre" placeholder="Proveedor" class="flex-1 border-2 border-black p-3 rounded-xl font-bold"><button onclick="addProv()" class="bg-black text-white px-6 rounded-xl font-black">+</button></div><div id="listaProv" class="mt-3 space-y-2"></div></div>
<div id="fin-categorias" class="hidden mt-3 bg-white rounded-[20px] p-4"><div class="flex gap-2"><input id="catNombre" placeholder="Ej: Gasolina, Gas" class="flex-1 border-2 border-black p-4 rounded-2xl font-bold text-[16px]"><button onclick="addCat()" class="bg-black text-white px-6 rounded-2xl font-black text-xl">+</button></div><button onclick="addCat()" class="w-full mt-2 bg-black text-white py-3 rounded-2xl font-black">GUARDAR CATEGORIA</button><div id="catMsg" class="hidden mt-3 p-3 rounded-xl text-center font-bold text-[12px]"></div><div id="listaCat" class="mt-4 space-y-2"></div></div>
<div id="fin-fijos" class="hidden mt-3 bg-white rounded-[20px] p-4"><h3 class="font-black text-[14px]">Gastos fijos mensuales</h3><p class="text-[11px] text-gray-500">Renta, luz, gas... se reparte en cada receta automaticamente</p><div class="bg-amber-50 border-2 border-amber-200 rounded-xl p-3 mt-3"><label class="text-[10px] font-black">¿Cuantas recetas vendes al mes?</label><input id="prodMes" type="number" value="100" class="w-full border-2 border-black p-3 rounded-xl mt-1 font-black text-[16px]" oninput="calcFijos()"></div><div id="gastosFijos" class="mt-3 space-y-2"></div><button onclick="addFijo()" class="w-full mt-3 bg-gray-100 py-3 rounded-full font-black text-[11px]">+ Agregar gasto fijo</button><div class="mt-4 bg-black text-white p-4 rounded-2xl text-center">Total mes $<span id="totMes">0</span> | Por receta $<span id="porRec">0.00</span></div></div>

<div id="modalGasto" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"><div class="bg-white w-full max-w-sm rounded-[24px] p-5"><h3 class="font-black">Nuevo movimiento</h3><select id="g-tipo" class="w-full border-2 p-3 rounded-xl mt-3 font-bold"><option value="salida">🔴 Salida - Gasto</option><option value="entrada">🟢 Entrada - Ingreso</option></select><input id="g-concepto" placeholder="Concepto" class="w-full border-2 p-3 rounded-xl mt-2 font-bold"><input id="g-monto" type="number" placeholder="$ Monto" class="w-full border-2 p-3 rounded-xl mt-2 font-black text-[16px]"><select id="g-cat" class="w-full border-2 p-3 rounded-xl mt-2 text-[12px]"></select><input id="g-fecha" type="date" class="w-full border-2 p-3 rounded-xl mt-2 font-bold"><div class="flex gap-2 mt-4"><button onclick="document.getElementById('modalGasto').classList.add('hidden')" class="flex-1 bg-gray-100 py-3 rounded-xl font-bold">Cerrar</button><button onclick="addMov()" class="flex-1 bg-black text-white py-3 rounded-xl font-black">Guardar</button></div></div></div>
</div>

<div id="tab-clientes" class="p-3 hidden"><div id="listaClientes" class="space-y-2"></div></div>
<div id="tab-config" class="p-3 hidden"><div class="bg-white rounded-2xl p-4"><h3 class="font-black text-sm">Categorias productos</h3><div id="listaCats" class="mt-2"></div><input id="newCat" placeholder="Nueva" class="w-full border-2 p-3 rounded-xl mt-3"><select id="newCatTipo" class="w-full border-2 p-3 rounded-xl mt-2"><option value="recetario">Recetario</option><option value="catalogo">Catalogo</option></select><button onclick="addCatProd()" class="w-full mt-2 bg-black text-white py-3 rounded-xl font-black">+ Agregar</button></div></div>

<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30">
<button onclick="showTab('costos')" id="n-costos" class="flex flex-col items-center text-black"><i class="fa-solid fa-book"></i><span class="text-[8px] font-bold">Crear</span></button>
<button onclick="showTab('vender')" id="n-vender" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-store"></i><span class="text-[8px]">Catalogo</span></button>
<button onclick="showTab('finanzas')" id="n-finanzas" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-chart-line"></i><span class="text-[8px]">Finanzas</span></button>
<button onclick="showTab('clientes')" id="n-clientes" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-users"></i><span class="text-[8px]">Clientes</span></button>
</div></div>

<script>
const U=['kg','g','L','ml','galon','pza','cda'];
let tipoAct='recetario', editId=null, carrito=[], finView='flujo';
function bf(u){ if(u=='kg'||u=='L') return 1000; if(u=='galon') return 3785; return 1; }
function getCats(){ let c=JSON.parse(localStorage.getItem('categoriasV2')||'[]'); if(!c.length){ c=[{id:'recetario',nombre:'Masa base',grupo:'recetario'},{id:'catalogo',nombre:'Crepas',grupo:'catalogo'}]; localStorage.setItem('categoriasV2',JSON.stringify(c)); } return c; }
function getProd(){ return JSON.parse(localStorage.getItem('productosV2')||'[]'); }
function getFijos(){ return JSON.parse(localStorage.getItem('gastosFijos')||'[]'); }
function getFacts(){ return JSON.parse(localStorage.getItem('facturas')||'[]'); }
function getCatG(){ let c=JSON.parse(localStorage.getItem('catGastos')||'[]'); if(!c.length){ c=[{id:'renta',nombre:'Renta'},{id:'luz',nombre:'Luz / Agua'},{id:'insumos',nombre:'Insumos'}]; localStorage.setItem('catGastos',JSON.stringify(c)); } return c; }
function getProv(){ return JSON.parse(localStorage.getItem('proveedores')||'[]'); }

function showTab(t){
  ['costos','vender','finanzas','clientes','config'].forEach(x=>{
    let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hidden',x!=t);
    let nb=document.getElementById('n-'+x); if(nb){ nb.classList.toggle('text-black',x==t); nb.classList.toggle('text-gray-400',x!=t); }
  });
  if(t=='finanzas') renderFinanzas();
  if(t=='vender') renderVenta();
  if(t=='config') renderCatsProd();
}
function setTipo(g){ let cs=getCats().filter(c=>c.grupo==g); if(cs.length) tipoAct=cs[0].id; renderBotones(); }
function renderBotones(){
  let cs=getCats(); let sel=cs.find(c=>c.id==tipoAct)||cs[0]; if(sel) tipoAct=sel.id;
  let isRec=sel?.grupo=='recetario';
  let bR=document.getElementById('bRec'), bC=document.getElementById('bCat');
  if(bR) bR.className=isRec?'flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white':'flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100';
  if(bC) bC.className=!isRec?'flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white':'flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100';
  let bc=document.getElementById('btnComp'); if(bc) bc.classList.toggle('hidden',isRec);
  let ay=document.getElementById('ayuda'); if(ay) ay.innerText=isRec?'RECETARIO: precio por unidad y cuanto usas + fijos':'CATALOGO: del recetario + complementos';
}
function addInsumo(d={}){
  let div=document.createElement('div'); div.className='bg-[#FFF8F0] p-3 rounded-[16px] border-2 border-orange-100'; div.dataset.t='ing';
  div.innerHTML=`<div class="flex justify-between mb-2"><input placeholder="Ej: Leche" value="${d.n||''}" class="in-n font-black text-[13px] w-full bg-transparent outline-none"><button onclick="this.closest('div').parentElement.remove();calc()" class="text-red-400 ml-2 bg-white w-6 h-6 rounded-full">x</button></div><div class="bg-white rounded-xl p-2"><p class="text-[9px] font-black opacity-50">PRECIO COMPRA</p><div class="grid grid-cols-3 gap-2 mt-1"><input type="number" value="${d.cc||''}" placeholder="Cant" class="in-cc w-full border-2 p-2 rounded-lg font-bold" oninput="calc()"><select class="in-uc w-full border-2 p-2 rounded-lg text-[11px]" onchange="calc()">${U.map(x=>`<option ${d.uc==x?'selected':''}>${x}</option>`).join('')}</select><input type="number" value="${d.pc||''}" placeholder="$" class="in-pc w-full border-2 p-2 rounded-lg font-bold" oninput="calc()"></div><div class="h-px bg-gray-100 my-2"></div><p class="text-[9px] font-black opacity-50">CUANTO USO</p><div class="grid grid-cols-3 gap-2 mt-1"><input type="number" value="${d.cu||''}" placeholder="Uso" class="in-cu w-full border-2 border-black p-2 rounded-lg font-bold" oninput="calc()"><select class="in-uu w-full border-2 border-black p-2 rounded-lg text-[11px]" onchange="calc()">${U.map(x=>`<option ${d.uu==x?'selected':''}>${x}</option>`).join('')}</select><div class="bg-black text-white rounded-lg p-2 text-center"><div class="text-[8px] opacity-70">ME SALE</div><div class="font-black">$<span class="in-sub">0.00</span></div></div></div></div>`;
  document.getElementById('insumos').appendChild(div);
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
function addFijo(d={}){
  let div=document.createElement('div'); div.className='flex gap-2 items-center bg-gray-50 p-2 rounded-xl border';
  div.innerHTML=`<input value="${d.nombre||''}" placeholder="Renta" class="f-n flex-1 bg-transparent font-bold text-[13px] p-2 outline-none" oninput="calcFijos()"><input type="number" value="${d.monto||''}" placeholder="$" class="f-m w-28 border-2 border-black p-2.5 rounded-xl font-black" oninput="calcFijos()"><button onclick="this.parentElement.remove();calcFijos()" class="text-red-400 w-8 h-8 bg-white rounded-full font-black">X</button>`;
  document.getElementById('gastosFijos').appendChild(div);
}
function calcFijos(){
  let tot=0, arr=[]; document.querySelectorAll('#gastosFijos > div').forEach(r=>{ let n=r.querySelector('.f-n')?.value||''; let m=parseFloat(r.querySelector('.f-m')?.value)||0; if(n||m){ arr.push({nombre:n,monto:m}); tot+=m; } });
  localStorage.setItem('gastosFijos',JSON.stringify(arr));
  let pm=parseFloat(document.getElementById('prodMes').value)||100; localStorage.setItem('prodMes',pm);
  let por=pm>0?tot/pm:0;
  document.getElementById('totMes').innerText=tot.toFixed(0);
  document.getElementById('porRec').innerText=por.toFixed(2);
  let cf=document.getElementById('c-fijos'); if(cf) cf.innerText=por.toFixed(2);
  calc();
}
function calc(){
  let tot=0;
  document.querySelectorAll('#insumos > div').forEach(row=>{
    let sub=row.querySelector('.in-sub'); if(!sub) return;
    if(row.dataset.t=='rec' || row.dataset.t=='cat'){
      let sel=row.querySelector('.in-sel'); if(!sel?.options[sel.selectedIndex]) return;
      let c=parseFloat(sel.options[sel.selectedIndex].dataset.c)||0;
      let cant=parseFloat(row.querySelector('.in-cant').value)||0;
      let s=c*cant; sub.innerText=s.toFixed(2); tot+=s;
    } else {
      let cc=parseFloat(row.querySelector('.in-cc').value)||0, pc=parseFloat(row.querySelector('.in-pc').value)||0, cu=parseFloat(row.querySelector('.in-cu').value)||0;
      let uc=row.querySelector('.in-uc').value, uu=row.querySelector('.in-uu').value;
      if(!cc||!pc||!cu){ sub.innerText='0.00'; return; }
      let cost=(pc/(cc*bf(uc)))*(cu*bf(uu)); if(uc=='pza'||uu=='pza') cost=(pc/cc)*cu;
      if(uc=='kg'&&uu=='g') cost=(pc/(cc*1000))*cu; if(uc=='L'&&uu=='ml') cost=(pc/(cc*1000))*cu;
      sub.innerText=cost.toFixed(2); tot+=cost;
    }
  });
  let ci=document.getElementById('c-ing'); if(ci) ci.innerText=tot.toFixed(2);
  let gf=parseFloat(document.getElementById('c-fijos')?.innerText||'0');
  let ce=document.getElementById('costo'); if(ce) ce.innerText=(tot+gf).toFixed(2);
  let m=parseFloat(document.getElementById('margen').value)||0;
  let vm=document.getElementById('ventaManual').value;
  let ve=document.getElementById('venta'); if(ve){ if(vm&&parseFloat(vm)>0) ve.innerText=parseFloat(vm).toFixed(2); else ve.innerText=((tot+gf)*(1+m/100)).toFixed(2); }
}
function guardarProd(){
  let nom=document.getElementById('nombre').value.trim(); if(!nom) return alert('Nombre');
  let costo=parseFloat(document.getElementById('costo').innerText), venta=parseFloat(document.getElementById('venta').innerText);
  let ings=[]; document.querySelectorAll('#insumos > div').forEach(row=>{
    if(row.dataset.t=='rec'||row.dataset.t=='cat'){ ings.push({tipo:row.dataset.t,id:row.querySelector('.in-sel').value,cant:row.querySelector('.in-cant').value}); }
    else { ings.push({tipo:'ing',n:row.querySelector('.in-n').value,cc:row.querySelector('.in-cc').value,uc:row.querySelector('.in-uc').value,pc:row.querySelector('.in-pc').value,cu:row.querySelector('.in-cu').value,uu:row.querySelector('.in-uu').value}); }
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
function editarProd(id){ let p=getProd().find(x=>x.id==id); if(!p) return; editId=id; tipoAct=p.tipo; document.getElementById('nombre').value=p.nombre; document.getElementById('insumos').innerHTML=''; if(p.ingredientes){ p.ingredientes.forEach(ing=>{ if(ing.tipo=='ing') addInsumo({n:ing.n,cc:ing.cc,uc:ing.uc,pc:ing.pc,cu:ing.cu,uu:ing.uu}); else if(ing.tipo=='rec'){ addSalsa(); let l=document.getElementById('insumos').lastElementChild; l.querySelector('.in-sel').value=ing.id; l.querySelector('.in-cant').value=ing.cant; } else if(ing.tipo=='cat'){ addComp(); let l=document.getElementById('insumos').lastElementChild; l.querySelector('.in-sel').value=ing.id; l.querySelector('.in-cant').value=ing.cant; } }); } showTab('costos'); renderBotones(); calc(); document.getElementById('btnCancel').classList.remove('hidden'); }
function cancelEdit(){ editId=null; document.getElementById('nombre').value=''; document.getElementById('insumos').innerHTML=''; document.getElementById('ventaManual').value=''; document.getElementById('btnCancel').classList.add('hidden'); addInsumo({}); calc(); }
function renderVenta(){ let cs=getCats(); let ids=cs.filter(c=>c.grupo=='catalogo').map(c=>c.id); let ps=getProd().filter(p=>ids.includes(p.tipo)); let h=''; ps.forEach(p=>{ h+=`<div class="bg-white rounded-2xl shadow-sm border overflow-hidden"><button onclick="addCart(${p.id})" class="w-full text-left p-3"><b class="text-[12px]">${p.nombre}</b><p class="text-green-600 font-black text-[12px]">$${p.venta.toFixed(2)}</p></button></div>`; }); document.getElementById('listaVenta').innerHTML=h||'<p class="text-center text-gray-400 py-10 col-span-2">Crea productos en CATALOGO</p>'; }
function addCart(id){ let p=getProd().find(x=>x.id==id); let ex=carrito.find(x=>x.id==id); if(ex) ex.qty++; else carrito.push({...p,qty:1}); let t=0, html=''; carrito.forEach(x=>{ t+=x.venta*x.qty; html+=`<div class="flex justify-between py-1"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)}</span></div>`; }); document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('ticket').innerHTML=html||'Vacio'; }
function cobrar(){ if(!carrito.length) return alert('Carrito vacio'); let tot=parseFloat(document.getElementById('c-total').innerText); let facts=getFacts(); let now=new Date(); let iso=now.toISOString().split('T')[0]; facts.push({id:Date.now(),concepto:'Venta: '+carrito.map(c=>c.nombre+' x'+c.qty).join(', '),monto:tot,fecha:iso,fechaObj:now.getTime(),tipo:'entrada',origen:'venta'}); localStorage.setItem('facturas',JSON.stringify(facts)); carrito=[]; document.getElementById('c-total').innerText='0'; document.getElementById('ticket').innerHTML='Vacio'; finView='flujo'; showTab('finanzas'); }

// Finanzas
function setFin(v){ finView=v; renderFinanzas(); }
function addCat(){
  let input=document.getElementById('catNombre'); let n=input.value.trim(); let msg=document.getElementById('catMsg');
  if(!n){ msg.className='mt-3 p-3 rounded-xl text-center font-bold bg-red-100 text-red-700'; msg.innerText='Escribe categoria'; msg.classList.remove('hidden'); return; }
  let cs=getCatG(); if(cs.some(c=>c.nombre.toLowerCase()==n.toLowerCase())){ msg.className='mt-3 p-3 rounded-xl text-center font-bold bg-yellow-100'; msg.innerText='Ya existe'; msg.classList.remove('hidden'); return; }
  cs.push({id:Date.now().toString(),nombre:n}); localStorage.setItem('catGastos',JSON.stringify(cs)); input.value=''; msg.className='mt-3 p-3 rounded-xl text-center font-bold bg-green-100 text-green-700'; msg.innerText='✅ '+n+' guardada'; msg.classList.remove('hidden'); setTimeout(()=>msg.classList.add('hidden'),2000); renderFinanzas();
}
function addProv(){ let n=document.getElementById('provNombre').value.trim(); if(!n) return alert('Nombre'); let ps=getProv(); ps.push({id:Date.now().toString(),nombre:n}); localStorage.setItem('proveedores',JSON.stringify(ps)); document.getElementById('provNombre').value=''; renderFinanzas(); }
function openGasto(){ let cats=getCatG(); document.getElementById('g-cat').innerHTML='<option value="">Sin categoria</option>'+cats.map(c=>`<option value="${c.id}">${c.nombre}</option>`).join(''); document.getElementById('modalGasto').classList.remove('hidden'); }
function addMov(){ let concepto=document.getElementById('g-concepto').value.trim(), monto=parseFloat(document.getElementById('g-monto').value), fecha=document.getElementById('g-fecha').value; if(!concepto||!monto||!fecha) return alert('Faltan datos'); let facts=getFacts(); facts.push({id:Date.now(),concepto,monto,fecha,fechaObj:new Date(fecha+'T00:00:00').getTime(),tipo:document.getElementById('g-tipo').value,catGastoId:document.getElementById('g-cat').value,estado:'pendiente'}); localStorage.setItem('facturas',JSON.stringify(facts)); document.getElementById('modalGasto').classList.add('hidden'); document.getElementById('g-concepto').value=''; document.getElementById('g-monto').value=''; renderFinanzas(); }
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
  document.getElementById('flu-e-d').innerText=filtrados.filter(f=>f.tipo=='entrada').length+' movs';
  document.getElementById('flu-s-d').innerText=filtrados.filter(f=>f.tipo=='salida').length+' movs';
  document.getElementById('flu-g-p').innerText=porc+'% margen';
  let tot=entradas+salidas||1; document.getElementById('bar-e').style.width=(entradas/tot*100)+'%'; document.getElementById('bar-s').style.width=(salidas/tot*100)+'%';
  let lista=document.getElementById('flu-lista'); let h='';
  if(!filtrados.length) h='<p class="text-center text-[12px] text-gray-400 py-6">Sin movimientos este mes. Usa + o cobra en Catalogo</p>';
  else filtrados.sort((a,b)=>b.fechaObj-a.fechaObj).forEach(f=>{ let cat=cats.find(c=>c.id==f.catGastoId); let isE=f.tipo=='entrada'; h+=`<div class="flex justify-between items-center py-2 border-b"><div class="flex gap-2 items-center"><div class="w-8 h-8 rounded-full flex items-center justify-center ${isE?'bg-green-100':'bg-red-100'}">${isE?'💰':'💸'}</div><div><p class="text-[12px] font-bold">${f.concepto}</p><p class="text-[10px] text-gray-400">${f.fecha} ${cat?'• '+cat.nombre:''}</p></div></div><div class="text-right"><p class="font-black text-[13px] ${isE?'text-green-600':'text-red-600'}">${isE?'+':'-'}$${f.monto.toFixed(0)}</p><button onclick="let fs=getFacts(); fs=fs.filter(x=>x.id!=${f.id}); localStorage.setItem('facturas',JSON.stringify(fs)); renderFinanzas();" class="text-[9px] text-gray-300">Borrar</button></div></div>`; });
  if(lista) lista.innerHTML=h;
  let fl=document.getElementById('f-lista'); if(fl){ let hh=''; filtrados.slice().reverse().forEach(f=>{ hh+=`<div class="flex justify-between py-2 border-b"><div><p class="text-[12px] font-bold">${f.concepto}</p><p class="text-[10px] text-gray-400">${f.fecha} ${f.tipo}</p></div><b class="${f.tipo=='entrada'?'text-green-600':'text-red-600'}">$${f.monto}</b></div>`; }); fl.innerHTML=hh||'<p class="text-center py-6 text-gray-400">Sin datos</p>'; }
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
renderBotones(); calcFijos(); addInsumo({n:'Leche',cc:1,uc:'L',pc:40,cu:250,uu:'ml'}); calc(); renderInventario(); renderVenta(); renderFinanzas(); showTab('finanzas');
</script></body></html>
"""
