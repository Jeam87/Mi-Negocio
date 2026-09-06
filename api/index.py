from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 6.2</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>input,select,textarea{color:#000!important; background:#fff!important;} input::placeholder{color:#9CA3AF!important;}</style></head>
<body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[90px]">
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><h1 class="font-black">Mi Negocio</h1><button onclick="tab('config')" class="text-[10px] bg-gray-100 px-3 py-1 rounded-full">Config</button></div>

<div id="p-costos" class="p-3 hidden"><div class="bg-white rounded-[24px] p-4 shadow-sm"><div class="flex gap-2 mb-2"><button onclick="setTipoCat('recetario')" class="flex-1 py-2.5 rounded-xl text-[11px] font-black bg-black text-white">RECETARIO</button><button onclick="setTipoCat('catalogo')" class="flex-1 py-2.5 rounded-xl text-[11px] font-black bg-gray-100">CATALOGO</button></div><input id="nombre" placeholder="Nombre" class="w-full border-2 p-3 rounded-xl font-bold text-sm"><div id="insumos" class="mt-3"></div><div class="flex gap-2 mt-2"><button onclick="addInsumo()" class="flex-1 text-[11px] bg-orange-100 py-2 rounded-full">+ Ingrediente</button><button onclick="addInsumoSalsa()" class="flex-1 text-[11px] bg-amber-100 py-2 rounded-full">+ Del recetario</button></div><div class="mt-3 p-3 bg-gray-900 text-white rounded-xl text-[12px]">Costo $<span id="costo">0</span> | Venta $<span id="venta">0</span> <input id="margen" type="number" value="100" class="w-10 text-black rounded text-center ml-2">%</div><button onclick="guardar()" class="w-full mt-3 bg-black text-white py-3 rounded-xl font-black">Guardar</button><button id="btnCancelarEdit" onclick="cancelarEdit()" class="hidden w-full mt-2 bg-gray-100 py-2 rounded-xl text-[11px]">Cancelar</button></div><div id="listaInv" class="mt-4"></div></div>
<div id="p-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div></div>

<div id="p-finanzas" class="p-3">
<div class="bg-[#2D3748] rounded-[20px] p-4 text-white"><div class="flex justify-between"><h2 class="font-black">Finanzas</h2><button onclick="openModalGasto()" class="bg-[#4FD1C5] text-black w-8 h-8 rounded-lg font-black">+</button></div><div class="mt-3 flex gap-1"><button onclick="vistaFin='facturas';mostrarFinanzas()" id="vf-facturas" class="text-[10px] bg-white/20 px-3 py-1.5 rounded-full">Facturas</button><button onclick="vistaFin='proveedores';mostrarFinanzas()" id="vf-proveedores" class="text-[10px] bg-white/20 px-3 py-1.5 rounded-full">Proveedores</button><button onclick="vistaFin='categorias';mostrarFinanzas()" id="vf-categorias" class="text-[10px] bg-white text-black px-3 py-1.5 rounded-full font-bold">Cat. gastos</button></div></div>

<div id="view-categorias"><div class="mt-3 bg-white rounded-[20px] p-4 shadow-sm">
<h3 class="font-black text-[14px]">Categorías de gastos - ILIMITADAS</h3><p class="text-[11px] text-gray-500 mb-3">Escribe aquí abajo, en negro, y dale +</p>

<div class="relative">
<input id="catGastoNombre" type="text" inputmode="text" autocomplete="off" placeholder="Ej: Gasolina"
class="w-full border-2 border-black p-4 rounded-2xl text-[16px] font-bold outline-none focus:border-blue-500"
style="color:#000!important; background:#FFFFFF!important; -webkit-text-fill-color:#000!important;">
<button onclick="addCatGastoFix()" class="absolute right-2 top-2 bottom-2 bg-black text-white px-6 rounded-xl font-black text-xl">+</button>
</div>

<div class="mt-2 flex gap-2">
<button onclick="addCatGastoFix()" class="w-full bg-[#111] text-white py-4 rounded-2xl font-black text-[14px]">GUARDAR CATEGORÍA</button>
</div>

<div id="catMsg" class="hidden mt-3 p-3 rounded-xl text-center font-bold text-[13px]"></div>
<div id="listaCatGastos" class="mt-4 space-y-2"></div>
</div></div>

<div id="view-proveedores" class="hidden"><div class="mt-3 bg-white rounded-2xl p-4 shadow-sm">
<input id="provNombre" type="text" placeholder="Proveedor" class="w-full border-2 border-black p-3 rounded-xl text-[16px] font-bold" style="color:#000!important;"><div class="flex gap-2 mt-2"><input id="provTel" type="text" placeholder="Tel" class="flex-1 border-2 p-3 rounded-xl text-[14px]"><button onclick="addProveedorFix()" class="bg-black text-white px-6 rounded-xl font-black">+</button></div>
<div id="listaProveedores" class="mt-3"></div></div></div>

<div id="view-facturas" class="hidden"><div id="f-lista" class="mt-3 bg-white rounded-2xl p-3 shadow-sm"></div></div>
<div id="modalGasto" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"><div class="bg-white w-full max-w-sm rounded-[24px] p-5"><input id="g-concepto" placeholder="Concepto" class="w-full border-2 p-3 rounded-xl text-[16px] mt-2"><input id="g-monto" type="number" placeholder="$" class="w-full border-2 p-3 rounded-xl text-[16px] mt-2"><select id="g-proveedor" class="w-full border-2 p-3 rounded-xl mt-2"></select><select id="g-catGasto" class="w-full border-2 p-3 rounded-xl mt-2"></select><input id="g-fecha" type="date" class="w-full border-2 p-3 rounded-xl mt-2"><select id="g-tipo" class="w-full border-2 p-3 rounded-xl mt-2"><option value="salida">Salida</option><option value="entrada">Entrada</option></select><div class="flex gap-2 mt-3"><button onclick="document.getElementById('modalGasto').classList.add('hidden')" class="flex-1 bg-gray-100 py-3 rounded-xl">Cerrar</button><button onclick="addFactura()" class="flex-1 bg-black text-white py-3 rounded-xl font-black">Guardar</button></div></div></div>
</div>

<div id="p-clientes" class="p-3 hidden"><div id="listaClientes"></div></div>
<div id="p-config" class="p-3 hidden"><div id="listaCats"></div><input id="newCat" placeholder="Nueva" class="w-full border-2 p-3 rounded-xl mt-2"><div id="gastosFijos"></div><input id="prodMes" type="number" value="100" class="w-full border-2 p-3 rounded-xl mt-2"><span id="cfg-porReceta">0</span><span id="c-fijos">0</span></div>

<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30">
<button onclick="tab('costos')" id="nav-costos" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-book"></i><span class="text-[8px]">Crear</span></button>
<button onclick="tab('vender')" id="nav-vender" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-store"></i><span class="text-[8px]">Catalogo</span></button>
<button onclick="tab('finanzas')" id="nav-finanzas" class="flex flex-col items-center text-black"><i class="fa-solid fa-chart-line"></i><span class="text-[8px]">Finanzas</span></button>
<button onclick="tab('clientes')" id="nav-clientes" class="flex flex-col items-center text-gray-400"><i class="fa-solid fa-users"></i><span class="text-[8px]">Clientes</span></button>
</div></div>

<script>
let tipoActual='recetario', editId=null, carrito=[], prodImgBase='', vistaFin='categorias'; const U=['kg','g','L','ml','galon','pza','cda'];
function baseFactor(u){ if(u=='kg'||u=='L') return 1000; if(u=='galon') return 3785; return 1;}
function getCats(){let c=JSON.parse(localStorage.getItem('categoriasV2')||'[]'); if(!c.length){c=[{id:'recetario',nombre:'Recetario',grupo:'recetario'},{id:'catalogo',nombre:'Catalogo',grupo:'catalogo'}]; localStorage.setItem('categoriasV2',JSON.stringify(c));} return c;}
function getProd(){return JSON.parse(localStorage.getItem('productosV2')||'[]');}
function getFacturas(){return JSON.parse(localStorage.getItem('facturas')||'[]');}
function getProveedores(){return JSON.parse(localStorage.getItem('proveedores')||'[]');}
function getCatGastos(){let c=JSON.parse(localStorage.getItem('catGastos')||'[]'); if(!c.length){c=[{id:'renta',nombre:'Renta'},{id:'luz',nombre:'Luz / Agua'},{id:'insumos',nombre:'Insumos'},{id:'sueldos',nombre:'Sueldos'}]; localStorage.setItem('catGastos',JSON.stringify(c));} return c;}
function addInsumo(d={}){let div=document.createElement('div'); div.className='bg-[#FFF8F0] p-2 rounded-xl border text-[11px]'; div.dataset.tipo='ing'; div.innerHTML=`<input placeholder="Ingrediente" value="${d.n||''}" class="in-n font-bold w-full bg-transparent"><div class="grid grid-cols-3 gap-1 mt-1"><input type="number" value="${d.cc||''}" class="in-cc border p-2 rounded-lg"><select class="in-uc border p-2 rounded-lg">${U.map(x=>`<option>${x}</option>`).join('')}</select><input type="number" value="${d.pc||''}" class="in-pc border p-2 rounded-lg"></div>`; document.getElementById('insumos').appendChild(div);}
addInsumo({});
function calc(){}
function tab(t){['costos','vender','finanzas','clientes','config'].forEach(x=>{let el=document.getElementById('p-'+x); if(el) el.classList.toggle('hidden',x!=t);}); if(t=='finanzas') mostrarFinanzas();}
function addCatGastoFix(){
  let input=document.getElementById('catGastoNombre');
  let raw=input.value;
  let n=raw.trim();
  console.log('intentando guardar:', raw, 'trim:', n);
  let msg=document.getElementById('catMsg');
  if(!n){
    msg.className='mt-3 p-3 rounded-xl text-center font-bold text-[13px] bg-red-100 text-red-700';
    msg.innerText='❌ No escribiste nada. Toca el campo y escribe: Gasolina';
    msg.classList.remove('hidden');
    input.focus();
    return;
  }
  let cats=getCatGastos();
  if(cats.some(c=>c.nombre.toLowerCase()===n.toLowerCase())){
    msg.className='mt-3 p-3 rounded-xl text-center font-bold text-[13px] bg-yellow-100 text-yellow-700';
    msg.innerText='⚠️ Ya existe: '+n;
    msg.classList.remove('hidden');
    return;
  }
  cats.push({id:Date.now().toString(), nombre:n});
  localStorage.setItem('catGastos', JSON.stringify(cats));
  input.value='';
  msg.className='mt-3 p-3 rounded-xl text-center font-bold text-[13px] bg-green-100 text-green-700';
  msg.innerText='✅ Guardado: '+n+' - Ya puedes usarla en gastos';
  msg.classList.remove('hidden');
  setTimeout(()=>msg.classList.add('hidden'),2500);
  mostrarFinanzas();
}
function addProveedorFix(){
  let n=document.getElementById('provNombre').value.trim();
  if(!n) return alert('Escribe nombre');
  let provs=getProveedores();
  provs.push({id:Date.now().toString(), nombre:n, tel:document.getElementById('provTel').value});
  localStorage.setItem('proveedores', JSON.stringify(provs));
  document.getElementById('provNombre').value=''; document.getElementById('provTel').value='';
  mostrarFinanzas();
}
function mostrarFinanzas(){
  let facts=getFacturas(); let provs=getProveedores(); let cats=getCatGastos();
  let vfF=document.getElementById('view-facturas'), vp=document.getElementById('view-proveedores'), vc=document.getElementById('view-categorias');
  if(vfF) vfF.classList.toggle('hidden',vistaFin!='facturas');
  if(vp) vp.classList.toggle('hidden',vistaFin!='proveedores');
  if(vc) vc.classList.toggle('hidden',vistaFin!='categorias');
  document.getElementById('vf-facturas').className=vistaFin=='facturas'?'text-[10px] bg-white text-black px-3 py-1.5 rounded-full font-bold':'text-[10px] bg-white/20 text-white px-3 py-1.5 rounded-full';
  document.getElementById('vf-proveedores').className=vistaFin=='proveedores'?'text-[10px] bg-white text-black px-3 py-1.5 rounded-full font-bold':'text-[10px] bg-white/20 text-white px-3 py-1.5 rounded-full';
  document.getElementById('vf-categorias').className=vistaFin=='categorias'?'text-[10px] bg-white text-black px-3 py-1.5 rounded-full font-bold':'text-[10px] bg-white/20 text-white px-3 py-1.5 rounded-full';
  if(vistaFin=='categorias'){
    let h=''; cats.forEach((c,i)=>{
      let total=facts.filter(f=>f.catGastoId==c.id).reduce((s,f)=>s+f.monto,0);
      h+=`<div class="flex justify-between items-center bg-gray-50 p-3 rounded-xl mt-2 border"><div><b class="text-[14px] text-black">${c.nombre}</b><br><span class="text-[11px] text-gray-500">Gastado: $${total.toFixed(0)}</span></div><div class="flex gap-2"><button onclick="let cs=getCatGastos(); let n=prompt('Nuevo nombre:',cs[${i}].nombre); if(n&&n.trim()){cs[${i}].nombre=n.trim(); localStorage.setItem('catGastos',JSON.stringify(cs)); mostrarFinanzas();}" class="bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-[11px] font-bold">Editar</button><button onclick="if(confirm('¿Borrar ${c.nombre}?')){let cs=getCatGastos(); cs.splice(${i},1); localStorage.setItem('catGastos',JSON.stringify(cs)); mostrarFinanzas();}" class="text-red-400 font-black px-2">X</button></div></div>`;
    });
    document.getElementById('listaCatGastos').innerHTML=h;
  }
  if(vistaFin=='proveedores'){
    let h=''; provs.forEach((p,i)=>{h+=`<div class="flex justify-between bg-gray-50 p-3 rounded-xl mt-2"><b>${p.nombre}</b><button onclick="let pr=getProveedores(); pr.splice(${i},1); localStorage.setItem('proveedores',JSON.stringify(pr)); mostrarFinanzas();" class="text-red-400">X</button></div>`;});
    document.getElementById('listaProveedores').innerHTML=h||'<p class="text-[11px] text-gray-400">Sin proveedores</p>';
  }
}
function openModalGasto(){let provs=getProveedores(); let cats=getCatGastos(); document.getElementById('g-proveedor').innerHTML='<option value="">Sin proveedor</option>'+provs.map(p=>`<option value="${p.id}">${p.nombre}</option>`).join(''); document.getElementById('g-catGasto').innerHTML='<option value="">Sin categoria</option>'+cats.map(c=>`<option value="${c.id}">${c.nombre}</option>`).join(''); document.getElementById('modalGasto').classList.remove('hidden');}
function addFactura(){let concepto=document.getElementById('g-concepto').value.trim(), monto=parseFloat(document.getElementById('g-monto').value), fecha=document.getElementById('g-fecha').value; if(!concepto||!monto||!fecha) return alert('Faltan datos'); let facts=getFacturas(); facts.push({id:Date.now(),concepto,monto,fecha,fechaObj:new Date(fecha+'T00:00:00').getTime(),tipo:document.getElementById('g-tipo').value,proveedorId:document.getElementById('g-proveedor').value,catGastoId:document.getElementById('g-catGasto').value,estado:'pendiente'}); localStorage.setItem('facturas',JSON.stringify(facts)); document.getElementById('modalGasto').classList.add('hidden'); mostrarFinanzas();}
document.getElementById('catGastoNombre').addEventListener('keydown',function(e){ if(e.key==='Enter'){ e.preventDefault(); addCatGastoFix(); } });
document.getElementById('catGastoNombre').addEventListener('input',function(){ console.log('escribiendo:', this.value); });
let today=new Date().toISOString().split('T')[0]; let gf=document.getElementById('g-fecha'); if(gf) gf.value=today;
mostrarFinanzas();
</script></body></html>
"""
