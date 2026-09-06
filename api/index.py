from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 7.0</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>input,select,textarea{color:#000!important; background:#fff!important;} input::placeholder{color:#9CA3AF!important;}</style></head>
<body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[95px]">
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><h1 class="font-black">Mi Negocio</h1><button onclick="tab('config')" class="text-[10px] bg-gray-100 px-3 py-1 rounded-full">Config</button></div>

<div id="p-costos" class="p-3">
<div class="bg-white rounded-[28px] p-4 shadow-sm">
<div class="flex gap-2 mb-2"><button id="bRec" onclick="setTipoCat('recetario')" class="flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white">📖 RECETARIO</button><button id="bCat" onclick="setTipoCat('catalogo')" class="flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100">🛒 CATALOGO</button></div>
<p id="ayudaTipo" class="text-[10px] text-gray-500 mb-3"></p>
<input id="nombre" placeholder="Ej: Masa de crepas / Combo crepa + refresco" class="w-full border-2 border-black p-4 rounded-2xl font-bold text-[15px]">
<textarea id="descripcion" placeholder="Descripcion para catalogo" class="w-full border-2 p-3 rounded-2xl text-[12px] mt-2 h-12"></textarea>
<input id="prodImg" type="file" accept="image/*" class="text-[11px] mt-2"><img id="prevImg" class="w-24 h-24 rounded-2xl object-cover mt-2 hidden border-2">
<div id="insumos" class="mt-4 space-y-3"></div>
<div class="flex flex-col gap-2 mt-4">
<div class="grid grid-cols-2 gap-2"><button onclick="addInsumo()" class="text-[11px] bg-orange-100 py-3 rounded-full font-black">+ Ingrediente suelto</button><button id="btnBase" onclick="addInsumoSalsa()" class="text-[11px] bg-amber-200 py-3 rounded-full font-black">+ Del recetario</button></div>
<button id="btnComplemento" onclick="addInsumoCatalogo()" class="hidden text-[11px] bg-blue-100 py-3 rounded-full font-black">+ Complemento (refresco, topping)</button>
</div>
<div class="mt-4 p-4 bg-[#0F172A] text-white rounded-[16px] text-[13px]">
<div class="flex justify-between"><span class="opacity-70">Costo ingredientes</span><b>$<span id="c-ing">0.00</span></b></div>
<div class="flex justify-between text-amber-300"><span class="opacity-70">+ Gastos fijos</span><b>$<span id="c-fijos">0.00</span></b></div>
<div class="flex justify-between font-black text-[15px] border-t border-white/20 mt-2 pt-2"><span>COSTO TOTAL $<span id="costo">0.00</span></span><span class="text-green-300">VENTA $<span id="venta">0.00</span></span></div>
<div class="mt-3 flex items-center gap-2"><span class="text-[11px] opacity-70">Margen</span><input id="margen" type="number" value="100" class="w-14 text-black rounded-lg text-center font-black py-1">% <span class="ml-auto text-[10px] opacity-60">Precio manual combo:</span><input id="ventaManual" type="number" placeholder="$ final" class="w-20 text-black rounded-lg px-2 py-1 font-black text-[12px]" oninput="calc()"></div>
</div>
<button id="btnGuardar" onclick="guardar()" class="w-full mt-4 bg-black text-white py-4 rounded-2xl font-black text-[15px]">Guardar en RECETARIO</button><button id="btnCancelarEdit" onclick="cancelarEdit()" class="hidden w-full mt-2 bg-gray-100 py-3 rounded-2xl text-[11px] font-bold">Cancelar edición</button>
</div><div id="listaInv" class="mt-5"></div>
</div>

<div id="p-vender" class="p-3 hidden"><div id="filtrosCat" class="flex gap-2 overflow-auto pb-2"></div><div id="listaVenta" class="grid grid-cols-2 gap-3"></div>
<div class="mt-6 bg-white rounded-[20px] p-4 shadow-xl border"><h3 class="font-bold text-sm">Presupuesto <span id="c-count">0</span></h3><div id="c-items" class="text-[12px] mt-2"></div><div class="flex justify-between font-black text-lg mt-3">Total $<span id="c-total">0</span></div><button onclick="enviarPresupuesto()" class="w-full mt-3 bg-green-500 text-white py-3 rounded-xl font-black">WhatsApp</button><button onclick="cobrar()" class="w-full mt-2 bg-black text-white py-2 rounded-xl">Cobrar</button></div></div>

<div id="p-finanzas" class="p-3 hidden">
<div class="bg-[#2D3748] rounded-[20px] p-4 text-white"><div class="flex justify-between"><h2 class="font-black">Finanzas</h2><button onclick="openModalGasto()" class="bg-[#4FD1C5] text-black w-8 h-8 rounded-lg font-black">+</button></div><div class="mt-3 flex gap-1"><button onclick="vistaFin='facturas';mostrarFinanzas()" id="vf-facturas" class="text-[10px] px-3 py-1.5 rounded-full bg-white/20">Facturas</button><button onclick="vistaFin='proveedores';mostrarFinanzas()" id="vf-proveedores" class="text-[10px] px-3 py-1.5 rounded-full bg-white/20">Proveedores</button><button onclick="vistaFin='categorias';mostrarFinanzas()" id="vf-categorias" class="text-[10px] px-3 py-1.5 rounded-full bg-white text-black font-bold">Cat. gastos</button></div></div>
<div id="view-facturas" class="hidden"><div id="f-lista" class="mt-3 bg-white rounded-2xl p-3 shadow-sm"></div></div>
<div id="view-proveedores" class="hidden"><div class="mt-3 bg-white rounded-2xl p-4 shadow-sm"><div class="flex gap-2"><input id="provNombre" placeholder="Proveedor" class="flex-1 border-2 p-3 rounded-xl font-bold"><button onclick="addProveedorFix()" class="bg-black text-white px-5 rounded-xl font-black">+</button></div><div id="listaProveedores" class="mt-3"></div></div></div>
<div id="view-categorias"><div class="mt-3 bg-white rounded-[20px] p-4 shadow-sm"><h3 class="font-black text-[14px]">Categorías - ILIMITADAS</h3><p class="text-[11px] text-gray-500 mb-3">Escribe en negro y dale Guardar</p><div class="flex gap-2"><input id="catGastoNombre" type="text" placeholder="Ej: Gasolina, Gas" class="flex-1 border-2 border-black p-4 rounded-2xl font-bold text-[16px]" style="color:#000!important;"><button onclick="addCatGastoFix()" class="bg-black text-white px-6 rounded-2xl font-black text-xl">+</button></div><button onclick="addCatGastoFix()" class="w-full mt-2 bg-black text-white py-3 rounded-2xl font-black">GUARDAR CATEGORÍA</button><div id="catMsg" class="hidden mt-3 p-3 rounded-xl text-center font-bold text-[13px]"></div><div id="listaCatGastos" class="mt-4 space-y-2"></div></div></div>
<div id="modalGasto" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"><div class="bg-white w-full max-w-sm rounded-[24px] p-5"><input id="g-concepto" placeholder="Concepto" class="w-full border-2 p-3 rounded-xl mt-2"><input id="g-monto" type="number" placeholder="$" class="w-full border-2 p-3 rounded-xl mt-2"><select id="g-proveedor" class="w-full border-2 p-3 rounded-xl mt-2"></select><select id="g-catGasto" class="w-full border-2 p-3 rounded-xl mt-2"></select><input id="g-fecha" type="date" class="w-full border-2 p-3 rounded-xl mt-2"><select id="g-tipo" class="w-full border-2 p-3 rounded-xl mt-2"><option value="salida">Salida</option><option value="entrada">Entrada</option></select><div class="flex gap-2 mt-3"><button onclick="document.getElementById('modalGasto').classList.add('hidden')" class="flex-1 bg-gray-100 py-3 rounded-xl">Cerrar</button><button onclick="addFactura()" class="flex-1 bg-black text-white py-3 rounded-xl font-black">Guardar</button></div></div></div>
</div>

<div id="p-clientes" class="p-3 hidden"><div id="listaClientes"></div></div>
<div id="p-config" class="p-3 hidden"><div id="listaCats"></div><input id="newCat" placeholder="Nueva categoria" class="w-full border-2 p-3 rounded-xl mt-2"><select id="newCatTipo" class="w-full border-2 p-3 rounded-xl mt-2"><option value="recetario">Recetario</option><option value="catalogo">Catalogo</option></select><button onclick="addCategoria()" class="w-full mt-2 bg-black text-white py-3 rounded-xl">+ Agregar</button><div id="gastosFijos" class="mt-4"></div><input id="prodMes" type="number" value="100" class="w-full border-2 p-3 rounded-xl mt-2"><div class="bg-black text-white p-3 rounded-xl mt-2 text-center">$<span id="cfg-porReceta">0</span> por receta</div></div>

<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30">
<button onclick="tab('costos')" id="nav-costos" class="flex flex-col items-center text-black"><i class="fa-solid fa-book"></i><span class="text-[8px] font-bold">Crear</span></button>
<button onclick="tab('vender')" id="nav-vender" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-store"></i><span class="text-[8px]">Catalogo</span></button>
<button onclick="tab('finanzas')" id="nav-finanzas" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-chart-line"></i><span class="text-[8px]">Finanzas</span></button>
<button onclick="tab('clientes')" id="nav-clientes" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-users"></i><span class="text-[8px]">Clientes</span></button>
</div></div>

<script>
let tipoActual='recetario', editId=null, carrito=[], prodImgBase='', vistaFin='categorias'; const U=['kg','g','L','ml','galon','pza','cda'];
function baseFactor(u){ if(u=='kg'||u=='L') return 1000; if(u=='galon') return 3785; return 1;}
document.getElementById('prodImg')?.addEventListener('change',e=>{let r=new FileReader(); r.onload=()=>{prodImgBase=r.result; let im=document.getElementById('prevImg'); im.src=r.result; im.classList.remove('hidden');}; r.readAsDataURL(e.target.files[0]);});
function getCats(){let c=JSON.parse(localStorage.getItem('categoriasV2')||'[]'); if(!c.length||!c[0].grupo){c=[{id:'recetario',nombre:'Masa base',grupo:'recetario'},{id:'guisado',nombre:'Guisados',grupo:'recetario'},{id:'catalogo',nombre:'Crepas dulces',grupo:'catalogo'},{id:'combos',nombre:'Combos',grupo:'catalogo'}]; localStorage.setItem('categoriasV2',JSON.stringify(c));} return c;}
function saveCats(c){localStorage.setItem('categoriasV2',JSON.stringify(c)); renderCats(); renderCatBotones();}
function renderCats(){let cats=getCats(); let h=''; cats.forEach((cat,i)=>{h+=`<div class="flex gap-2 items-center bg-gray-50 p-2 rounded-xl mt-2"><input value="${cat.nombre}" onchange="let cs=getCats(); cs[${i}].nombre=this.value; saveCats(cs);" class="flex-1 bg-transparent font-bold text-sm"><span class="text-[9px] ${cat.grupo=='recetario'?'bg-amber-200':'bg-black text-white'} px-2 py-0.5 rounded-full">${cat.grupo}</span><button onclick="let cs=getCats(); cs.splice(${i},1); saveCats(cs);" class="text-red-400">x</button></div>`;}); let el=document.getElementById('listaCats'); if(el) el.innerHTML=h;}
function renderCatBotones(){let cats=getCats(); let sel=cats.find(c=>c.id==tipoActual)||cats[0]; if(sel) tipoActual=sel.id; let isRec=sel?.grupo=='recetario'; let bR=document.getElementById('bRec'), bC=document.getElementById('bCat'); if(bR) bR.className=isRec?'flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white':'flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100'; if(bC) bC.className=!isRec?'flex-1 py-3 rounded-2xl text-[11px] font-black bg-black text-white':'flex-1 py-3 rounded-2xl text-[11px] font-black bg-gray-100'; let btnC=document.getElementById('btnComplemento'); if(btnC) btnC.classList.toggle('hidden',isRec); let ayuda=document.getElementById('ayudaTipo'); if(ayuda) ayuda.innerText=isRec?'RECETARIO: Ingredientes sueltos con precio por unidad y cuanto usas':'CATALOGO: Tomas del recetario + complementos y pones precio final'; let btnG=document.getElementById('btnGuardar'); if(btnG) btnG.innerText=editId?'Actualizar '+(sel?.nombre||''):'Guardar en '+(sel?.nombre?.toUpperCase()||'');}
function setTipoCat(g){let cats=getCats().filter(c=>c.grupo==g); if(cats.length) tipoActual=cats[0].id; renderCatBotones();}

// RECETARIO COMPLETO - PRECIO POR UNIDADES
function addInsumo(d={}){
  let div=document.createElement('div');
  div.className='bg-[#FFF8F0] p-3 rounded-[16px] border-2 border-orange-100 text-[11px]';
  div.dataset.tipo='ing';
  div.innerHTML=`
  <div class="flex justify-between items-center mb-2"><input placeholder="Nombre ingrediente: Leche, Harina..." value="${d.n||''}" class="in-n font-black text-[13px] w-full bg-transparent outline-none placeholder-gray-400"><button onclick="this.closest('div').parentElement.remove();calc()" class="ml-2 text-red-400 bg-white w-6 h-6 rounded-full">x</button></div>
  <div class="bg-white rounded-xl p-2">
    <p class="text-[9px] font-black opacity-50">PRECIO DE COMPRA</p>
    <div class="grid grid-cols-3 gap-2 mt-1">
      <div><label class="text-[8px]">Cant. compro</label><input type="number" step="0.01" value="${d.cc||''}" placeholder="1" class="in-cc w-full border-2 p-2 rounded-lg font-bold text-[13px]" oninput="calc()"></div>
      <div><label class="text-[8px]">Unidad</label><select class="in-uc w-full border-2 p-2 rounded-lg text-[11px]" onchange="calc()">${U.map(x=>`<option ${d.uc==x?'selected':''}>${x}</option>`).join('')}</select></div>
      <div><label class="text-[8px]">$ pagué</label><input type="number" step="0.01" value="${d.pc||''}" placeholder="40" class="in-pc w-full border-2 p-2 rounded-lg font-bold text-[13px]" oninput="calc()"></div>
    </div>
    <div class="h-[1px] bg-gray-100 my-2"></div>
    <p class="text-[9px] font-black opacity-50">CUANTO VOY A USAR EN ESTA RECETA</p>
    <div class="grid grid-cols-3 gap-2 mt-1">
      <div><label class="text-[8px]">Uso</label><input type="number" step="0.01" value="${d.cu||''}" placeholder="250" class="in-cu w-full border-2 p-2 rounded-lg font-bold text-[13px] border-black" oninput="calc()"></div>
      <div><label class="text-[8px]">Unidad uso</label><select class="in-uu w-full border-2 p-2 rounded-lg text-[11px] border-black" onchange="calc()">${U.map(x=>`<option ${d.uu==x?'selected':''}>${x}</option>`).join('')}</select></div>
      <div class="bg-black text-white rounded-lg p-2 text-center"><label class="text-[8px] opacity-70">ME SALE EN</label><div class="font-black text-[13px]">$<span class="in-sub">0.00</span></div></div>
    </div>
  </div>`;
  document.getElementById('insumos').appendChild(div);
}
function addInsumoSalsa(){
  let bases=getCats().filter(c=>c.grupo=='recetario').map(c=>c.id);
  let salsas=getProd().filter(p=>bases.includes(p.tipo));
  if(!salsas.length) return alert('Primero crea algo en RECETARIO (ej: Masa de crepas)');
  let div=document.createElement('div'); div.className='bg-amber-50 p-3 rounded-[16px] border-2 border-amber-300 text-[11px]'; div.dataset.tipo='receta';
  div.innerHTML=`<div class="flex justify-between"><span class="font-black text-amber-800 text-[11px]">📖 Del recetario</span><button onclick="this.parentElement.parentElement.remove();calc()" class="text-red-400">x</button></div>
  <div class="grid grid-cols-4 gap-2 mt-2 bg-white p-2 rounded-xl"><select class="in-salsa col-span-3 border-2 p-2 rounded-lg text-[12px] font-bold" onchange="calc()">${salsas.map(s=>`<option value="${s.id}" data-costo="${s.costo}">${s.nombre} - costo $${s.costo.toFixed(2)}</option>`).join('')}</select><input type="number" value="1" step="0.1" class="in-salsaCant border-2 p-2 rounded-lg font-bold" oninput="calc()"><div class="col-span-4 text-right font-black">Me sale: $<span class="in-sub">0.00</span></div></div>`;
  document.getElementById('insumos').appendChild(div); calc();
}
function addInsumoCatalogo(){
  let prods=getProd(); if(!prods.length) return alert('No hay productos');
  let div=document.createElement('div'); div.className='bg-blue-50 p-3 rounded-[16px] border-2 border-blue-200 text-[11px]'; div.dataset.tipo='catalogo';
  div.innerHTML=`<div class="flex justify-between"><span class="font-black text-blue-800">🛒 Complemento</span><button onclick="this.parentElement.parentElement.remove();calc()" class="text-red-400">x</button></div><div class="grid grid-cols-4 gap-2 mt-2 bg-white p-2 rounded-xl"><select class="in-salsa col-span-3 border-2 p-2 rounded-lg text-[12px] font-bold" onchange="calc()">${prods.map(s=>`<option value="${s.id}" data-costo="${s.costo}" data-venta="${s.venta}">${s.nombre} - $${s.venta.toFixed(2)}</option>`).join('')}</select><input type="number" value="1" class="in-salsaCant border-2 p-2 rounded-lg font-bold" oninput="calc()"><div class="col-span-4 text-right font-black">Me sale: $<span class="in-sub">0.00</span></div></div>`;
  document.getElementById('insumos').appendChild(div); calc();
}
function getProd(){return JSON.parse(localStorage.getItem('productosV2')||'[]');}
function calcGastosFijos(){let total=0; document.querySelectorAll('#gastosFijos > div').forEach(r=>{let m=r.querySelector('.gf-m'); if(m) total+=parseFloat(m.value)||0;}); let pm=parseFloat(document.getElementById('prodMes')?.value)||100; localStorage.setItem('prodMes',pm); let por=pm>0?total/pm:0; let el=document.getElementById('cfg-porReceta'); if(el) el.innerText=por.toFixed(2); let cf=document.getElementById('c-fijos'); if(cf) cf.innerText=por.toFixed(2); calc();}
function calc(){
  let tot=0;
  document.querySelectorAll('#insumos > div').forEach(row=>{
    let subEl=row.querySelector('.in-sub'); if(!subEl) return;
    if(row.dataset.tipo=='receta' || row.dataset.tipo=='catalogo'){
      let sel=row.querySelector('.in-salsa'); if(!sel?.options[sel.selectedIndex]) return;
      let costo=parseFloat(sel.options[sel.selectedIndex].dataset.costo)||0;
      if(row.dataset.tipo=='catalogo') costo=parseFloat(sel.options[sel.selectedIndex].dataset.venta)||costo;
      let cant=parseFloat(row.querySelector('.in-salsaCant').value)||0;
      let sub=costo*cant; subEl.innerText=sub.toFixed(2); tot+=sub;
    }else{
      let cc=parseFloat(row.querySelector('.in-cc').value)||0, pc=parseFloat(row.querySelector('.in-pc').value)||0, cu=parseFloat(row.querySelector('.in-cu').value)||0;
      let uc=row.querySelector('.in-uc').value, uu=row.querySelector('.in-uu').value;
      if(!cc||!pc||!cu){subEl.innerText='0.00'; return;}
      let costoCompraPorBase = pc / (cc*baseFactor(uc));
      let usoEnBase = cu*baseFactor(uu);
      let cost = costoCompraPorBase * usoEnBase;
      if(uc=='pza' || uu=='pza'){ cost = (pc/cc)*cu; }
      if(uc=='kg' && uu=='g'){ cost = (pc/(cc*1000))*cu; }
      if(uc=='L' && uu=='ml'){ cost = (pc/(cc*1000))*cu; }
      if(uc=='L' && uu=='L'){ cost = (pc/cc)*cu; }
      if(uc=='kg' && uu=='kg'){ cost = (pc/cc)*cu; }
      subEl.innerText=cost.toFixed(2); tot+=cost;
    }
  });
  let ci=document.getElementById('c-ing'); if(ci) ci.innerText=tot.toFixed(2);
  let gf=parseFloat(document.getElementById('c-fijos')?.innerText||'0');
  let ce=document.getElementById('costo'); if(ce) ce.innerText=(tot+gf).toFixed(2);
  let m=parseFloat(document.getElementById('margen').value)||0;
  let vm=document.getElementById('ventaManual').value;
  let ve=document.getElementById('venta'); if(ve){ if(vm&&parseFloat(vm)>0) ve.innerText=parseFloat(vm).toFixed(2); else ve.innerText=((tot+gf)*(1+m/100)).toFixed(2); }
}
document.getElementById('margen').oninput=calc;
function tab(t){['costos','vender','finanzas','clientes','config'].forEach(x=>{let el=document.getElementById('p-'+x); if(el) el.classList.toggle('hidden',x!=t); let nav=document.getElementById('nav-'+x); if(nav){nav.classList.toggle('text-black',x==t); nav.classList.toggle('text-gray-400',x!=t);}}); if(t=='vender') mostrarVenta(); if(t=='finanzas') mostrarFinanzas();}
function getMovs(){return JSON.parse(localStorage.getItem('movs')||'[]');}
function getClientes(){return JSON.parse(localStorage.getItem('clientes')||'[]');}
function getFacturas(){return JSON.parse(localStorage.getItem('facturas')||'[]');}
function getProveedores(){return JSON.parse(localStorage.getItem('proveedores')||'[]');}
function getCatGastos(){let c=JSON.parse(localStorage.getItem('catGastos')||'[]'); if(!c.length){c=[{id:'renta',nombre:'Renta'},{id:'luz',nombre:'Luz / Agua'},{id:'insumos',nombre:'Insumos'},{id:'sueldos',nombre:'Sueldos'}]; localStorage.setItem('catGastos',JSON.stringify(c));} return c;}
function guardar(){let nombre=document.getElementById('nombre').value.trim(); if(!nombre) return alert('Pon nombre Ej: Masa de crepas'); let desc=document.getElementById('descripcion')?.value||''; let costo=parseFloat(document.getElementById('costo').innerText), venta=parseFloat(document.getElementById('venta').innerText); let ings=[]; document.querySelectorAll('#insumos > div').forEach(row=>{if(row.dataset.tipo=='receta'||row.dataset.tipo=='catalogo'){ings.push({tipo:row.dataset.tipo,id:row.querySelector('.in-salsa').value,cant:row.querySelector('.in-salsaCant').value});} else {ings.push({tipo:'ing',n:row.querySelector('.in-n').value,cc:row.querySelector('.in-cc').value,uc:row.querySelector('.in-uc').value,pc:row.querySelector('.in-pc').value,cu:row.querySelector('.in-cu').value,uu:row.querySelector('.in-uu').value});}}); let p=getProd(); if(editId){let idx=p.findIndex(x=>x.id==editId); if(idx>=0){p[idx].nombre=nombre; p[idx].descripcion=desc; p[idx].costo=costo; p[idx].venta=venta; p[idx].tipo=tipoActual; p[idx].ingredientes=ings; if(prodImgBase) p[idx].img=prodImgBase;}} else {p.push({id:Date.now(),tipo:tipoActual,nombre,descripcion:desc,costo,venta,img:prodImgBase,ingredientes:ings});} localStorage.setItem('productosV2',JSON.stringify(p)); cancelarEdit(); mostrar(); tab('costos');}
function editarProd(id){let p=getProd().find(x=>x.id==id); if(!p) return; editId=id; tipoActual=p.tipo; document.getElementById('nombre').value=p.nombre; document.getElementById('descripcion').value=p.descripcion||''; if(p.img){prodImgBase=p.img; let pi=document.getElementById('prevImg'); pi.src=p.img; pi.classList.remove('hidden');} document.getElementById('insumos').innerHTML=''; if(p.ingredientes){p.ingredientes.forEach(ing=>{if(ing.tipo=='ing') addInsumo({n:ing.n,cc:ing.cc,uc:ing.uc,pc:ing.pc,cu:ing.cu,uu:ing.uu}); else if(ing.tipo=='receta'){addInsumoSalsa(); let l=document.getElementById('insumos').lastElementChild; l.querySelector('.in-salsa').value=ing.id; l.querySelector('.in-salsaCant').value=ing.cant;} else if(ing.tipo=='catalogo'){addInsumoCatalogo(); let l=document.getElementById('insumos').lastElementChild; l.querySelector('.in-salsa').value=ing.id; l.querySelector('.in-salsaCant').value=ing.cant;}});} tab('costos'); renderCatBotones(); calc(); document.getElementById('btnCancelarEdit').classList.remove('hidden'); window.scrollTo(0,0);}
function cancelarEdit(){editId=null; prodImgBase=''; document.getElementById('nombre').value=''; document.getElementById('descripcion').value=''; let pi=document.getElementById('prevImg'); if(pi) pi.classList.add('hidden'); document.getElementById('insumos').innerHTML=''; document.getElementById('ventaManual').value=''; document.getElementById('btnCancelarEdit').classList.add('hidden'); addInsumo({}); calc(); mostrar();}
function mostrar(){let prods=getProd(); let cats=getCats(); let h=''; prods.forEach((p,i)=>{let cat=cats.find(c=>c.id==p.tipo); h+=`<div class="bg-white p-3 rounded-2xl flex gap-3 shadow-sm mt-3 items-center border"><span class="text-[8px] bg-gray-100 px-2 py-1 rounded-full font-bold">${cat?cat.nombre:p.tipo}</span><img src="${p.img||''}" class="w-12 h-12 rounded-xl object-cover bg-gray-100"><div class="flex-1"><b class="text-[13px]">${p.nombre}</b><br><span class="text-[11px]">Costo $${p.costo.toFixed(2)} → Venta $${p.venta.toFixed(2)}</span></div><button onclick="editarProd(${p.id})" class="bg-blue-50 text-blue-600 px-3 py-1.5 rounded-full text-[11px] font-black">Editar</button><button onclick="if(confirm('¿Borrar?')){let pr=getProd(); pr.splice(${i},1); localStorage.setItem('productosV2',JSON.stringify(pr)); mostrar();}" class="text-red-300 font-black">X</button></div>`;}); document.getElementById('listaInv').innerHTML=h; mostrarVenta();}
function mostrarVenta(){let cats=getCats(); let catalogoIds=cats.filter(c=>c.grupo=='catalogo').map(c=>c.id); let prods=getProd().filter(p=>catalogoIds.includes(p.tipo)); let h=''; prods.forEach(p=>{h+=`<div class="bg-white rounded-2xl shadow-sm border overflow-hidden"><button onclick="addCart(${p.id})" class="w-full text-left"><img src="${p.img||'https://via.placeholder.com/200'}" class="w-full h-28 object-cover"><div class="p-2"><b class="text-[12px]">${p.nombre}</b><p class="text-[12px] text-green-600 font-black">$${p.venta.toFixed(2)}</p></div></button><button onclick="editarProd(${p.id})" class="w-full text-[10px] bg-blue-50 py-2 font-bold">Editar precio</button></div>`;}); let lv=document.getElementById('listaVenta'); if(lv) lv.innerHTML=h||'<p class="text-sm text-gray-400 col-span-2 text-center py-10">Crea productos en CATALOGO</p>';}
function addCart(id){let p=getProd().find(x=>x.id==id); let ex=carrito.find(x=>x.id==id); if(ex) ex.qty++; else carrito.push({...p,qty:1}); renderCart();}
function renderCart(){let t=0,c=0,html=''; carrito.forEach(x=>{t+=x.venta*x.qty; c+=x.qty; html+=`<div class="flex justify-between py-1 text-[12px]"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)}</span></div>`;}); document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('c-count').innerText=c; document.getElementById('c-items').innerHTML=html||'Vacío';}
function cobrar(){if(!carrito.length) return; let total=parseFloat(document.getElementById('c-total').innerText); let movs=getMovs(); movs.unshift({tipo:'entrada',concepto:'Venta',monto:total,fecha:new Date().toLocaleDateString()}); localStorage.setItem('movs',JSON.stringify(movs)); carrito=[]; renderCart(); tab('finanzas');}
function enviarPresupuesto(){if(!carrito.length) return; let texto=`*PRESUPUESTO*%0A`; carrito.forEach(p=>texto+=`• ${p.nombre} x${p.qty} $${(p.venta*p.qty).toFixed(2)}%0A`); texto+=`*TOTAL $${document.getElementById('c-total').innerText}*`; window.open('https://wa.me/?text='+texto,'_blank');}
function addCatGastoFix(){let input=document.getElementById('catGastoNombre'); let n=input.value.trim(); let msg=document.getElementById('catMsg'); if(!n){msg.className='mt-3 p-3 rounded-xl text-center font-bold bg-red-100 text-red-700'; msg.innerText='Escribe categoria primero'; msg.classList.remove('hidden'); return;} let cats=getCatGastos(); if(cats.some(c=>c.nombre.toLowerCase()===n.toLowerCase())){msg.className='mt-3 p-3 rounded-xl text-center font-bold bg-yellow-100 text-yellow-700'; msg.innerText='Ya existe'; msg.classList.remove('hidden'); return;} cats.push({id:Date.now().toString(),nombre:n}); localStorage.setItem('catGastos',JSON.stringify(cats)); input.value=''; msg.className='mt-3 p-3 rounded-xl text-center font-bold bg-green-100 text-green-700'; msg.innerText='✅ '+n+' guardada'; msg.classList.remove('hidden'); setTimeout(()=>msg.classList.add('hidden'),2000); mostrarFinanzas();}
function addProveedorFix(){let n=document.getElementById('provNombre').value.trim(); if(!n) return alert('Nombre'); let provs=getProveedores(); provs.push({id:Date.now().toString(),nombre:n,tel:document.getElementById('provTel')?.value||''}); localStorage.setItem('proveedores',JSON.stringify(provs)); document.getElementById('provNombre').value=''; let pt=document.getElementById('provTel'); if(pt) pt.value=''; mostrarFinanzas();}
function mostrarFinanzas(){let facts=getFacturas(); let provs=getProveedores(); let cats=getCatGastos(); let vfF=document.getElementById('view-facturas'), vp=document.getElementById('view-proveedores'), vc=document.getElementById('view-categorias'); if(vfF) vfF.classList.toggle('hidden',vistaFin!='facturas'); if(vp) vp.classList.toggle('hidden',vistaFin!='proveedores'); if(vc) vc.classList.toggle('hidden',vistaFin!='categorias'); let bF=document.getElementById('vf-facturas'), bP=document.getElementById('vf-proveedores'), bC=document.getElementById('vf-categorias'); if(bF) bF.className=vistaFin=='facturas'?'text-[10px] bg-white text-black px-3 py-1.5 rounded-full font-bold':'text-[10px] bg-white/20 text-white px-3 py-1.5 rounded-full'; if(bP) bP.className=vistaFin=='proveedores'?'text-[10px] bg-white text-black px-3 py-1.5 rounded-full font-bold':'text-[10px] bg-white/20 text-white px-3 py-1.5 rounded-full'; if(bC) bC.className=vistaFin=='categorias'?'text-[10px] bg-white text-black px-3 py-1.5 rounded-full font-bold':'text-[10px] bg-white/20 text-white px-3 py-1.5 rounded-full'; if(vistaFin=='categorias'){let h=''; cats.forEach((c,i)=>{h+=`<div class="flex justify-between items-center bg-gray-50 p-3 rounded-xl mt-2 border"><div><b class="text-[13px]">${c.nombre}</b></div><div class="flex gap-2"><button onclick="let cs=getCatGastos(); let n=prompt('Editar:',cs[${i}].nombre); if(n){cs[${i}].nombre=n.trim(); localStorage.setItem('catGastos',JSON.stringify(cs)); mostrarFinanzas();}" class="text-blue-600 text-[11px] font-bold">Editar</button><button onclick="if(confirm('Borrar?')){let cs=getCatGastos(); cs.splice(${i},1); localStorage.setItem('catGastos',JSON.stringify(cs)); mostrarFinanzas();}" class="text-red-400">X</button></div></div>`;}); document.getElementById('listaCatGastos').innerHTML=h;} if(vistaFin=='proveedores'){let h=''; provs.forEach((p,i)=>{h+=`<div class="flex justify-between bg-gray-50 p-3 rounded-xl mt-2"><b>${p.nombre}</b><button onclick="let pr=getProveedores(); pr.splice(${i},1); localStorage.setItem('proveedores',JSON.stringify(pr)); mostrarFinanzas();" class="text-red-400">X</button></div>`;}); document.getElementById('listaProveedores').innerHTML=h||'<p class="text-[11px] text-gray-400">Sin proveedores</p>';} if(vistaFin=='facturas'){let h=''; facts.slice().reverse().forEach(f=>{let cat=cats.find(c=>c.id==f.catGastoId); h+=`<div class="flex justify-between py-2 border-b"><div><p class="text-[12px] font-bold">${f.concepto}</p><p class="text-[10px] text-gray-400">${cat?cat.nombre:''} • ${f.fecha}</p></div><b>$${f.monto}</b></div>`;}); document.getElementById('f-lista').innerHTML=h||'<p class="text-center text-gray-400 py-6">Sin facturas</p>';}}
function openModalGasto(){let provs=getProveedores(); let cats=getCatGastos(); document.getElementById('g-proveedor').innerHTML='<option value="">Sin proveedor</option>'+provs.map(p=>`<option value="${p.id}">${p.nombre}</option>`).join(''); document.getElementById('g-catGasto').innerHTML='<option value="">Sin categoria</option>'+cats.map(c=>`<option value="${c.id}">${c.nombre}</option>`).join(''); document.getElementById('modalGasto').classList.remove('hidden');}
function addFactura(){let concepto=document.getElementById('g-concepto').value.trim(), monto=parseFloat(document.getElementById('g-monto').value), fecha=document.getElementById('g-fecha').value; if(!concepto||!monto||!fecha) return alert('Faltan datos'); let facts=getFacturas(); facts.push({id:Date.now(),concepto,monto,fecha,fechaObj:new Date(fecha+'T00:00:00').getTime(),tipo:document.getElementById('g-tipo').value,proveedorId:document.getElementById('g-proveedor').value,catGastoId:document.getElementById('g-catGasto').value,estado:'pendiente'}); localStorage.setItem('facturas',JSON.stringify(facts)); document.getElementById('modalGasto').classList.add('hidden'); mostrarFinanzas();}
function addCategoria(){let n=document.getElementById('newCat').value.trim(), g=document.getElementById('newCatTipo').value; if(!n) return; let cats=getCats(); cats.push({id:Date.now().toString(),nombre:n,grupo:g}); document.getElementById('newCat').value=''; saveCats(cats);}
document.getElementById('catGastoNombre').addEventListener('keydown',e=>{ if(e.key==='Enter'){ e.preventDefault(); addCatGastoFix(); } });
let today=new Date().toISOString().split('T')[0]; let gf=document.getElementById('g-fecha'); if(gf) gf.value=today;
renderCats(); renderCatBotones(); calcGastosFijos(); addInsumo({n:'Leche',cc:1,uc:'L',pc:40,cu:250,uu:'ml'}); calc(); mostrar(); mostrarFinanzas();
</script></body></html>
"""
