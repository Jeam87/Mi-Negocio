from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 3.1</title><script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head><body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[90px]">

<div class="bg-white p-4 flex justify-between items-center sticky top-0 z-20 shadow-sm">
<div class="flex items-center gap-2"><label for="logoIn"><img id="logo" src="https://em-content.zobj.net/thumbs/120/apple/354/hamburger_1f354.png" class="w-8 h-8 rounded-full object-cover bg-gray-100"></label><input id="logoIn" type="file" hidden><h1 class="font-black text-[16px]">Mi Negocio</h1></div>
<div class="text-[10px] bg-black text-white px-3 py-1 rounded-full">Ganancia: <b id="gananciaHoy">$0</b></div>
</div>

<div id="p-costos" class="p-3">
<div class="bg-white rounded-[24px] p-4 shadow-sm">
<input id="nombre" placeholder="Ej: Salsa verde 1L" class="w-full border-2 p-3 rounded-xl font-bold text-sm">
<div id="insumos" class="mt-3 space-y-3"></div>
<button onclick="addInsumo()" class="mt-3 text-[11px] bg-orange-100 text-orange-700 px-4 py-2 rounded-full font-bold">+ Ingrediente</button>

<div class="mt-4 p-3 bg-amber-50 rounded-[16px] border border-amber-200">
<p class="text-[11px] font-black text-amber-800"><i class="fa-solid fa-building"></i> GASTOS FIJOS POR RECETA</p>
<div class="flex justify-between text-[11px] mt-1"><span>Gasto fijo mensual total: $<span id="gf-total">0</span> / <span id="gf-produccion">1</span> recetas al mes</span></div>
<div class="flex justify-between text-[12px] mt-1 font-bold"><span>= Costo fijo por receta:</span><span class="bg-amber-200 px-2 rounded-full">$<span id="gf-porReceta">0</span></span></div>
<p class="text-[10px] text-amber-700 mt-2">*Se suma automático al costo. Configúralo en Config</p>
</div>

<div class="mt-3 p-4 bg-gray-900 text-white rounded-[18px]">
<div class="text-[11px] space-y-1">
<div class="flex justify-between"><span>Costo ingredientes:</span><span>$<span id="c-ing">0</span></span></div>
<div class="flex justify-between text-amber-300"><span>+ Gastos fijos:</span><span>$<span id="c-fijos">0</span></span></div>
<div class="flex justify-between font-bold border-t border-gray-700 pt-2 mt-2"><span>Costo TOTAL real:</span><span>$<span id="costo">0</span></span></div>
</div>
<div class="flex gap-2 mt-3 items-center"><input id="margen" type="number" value="100" class="w-14 text-black p-2 rounded-lg text-sm font-bold text-center"><span class="text-[11px]">% ganancia</span><span class="ml-auto font-black">Venta $<b id="venta" class="text-[20px]">0</b></span></div>
</div>
<button onclick="guardar()" class="w-full mt-3 bg-black text-white py-3 rounded-xl font-black text-sm">Guardar receta</button>
</div><div id="listaInv" class="mt-4"></div>
</div>

<div id="p-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div>
<div class="mt-6 bg-white rounded-[20px] p-4 shadow-xl border sticky bottom-[90px]"><h3 class="font-bold text-sm">Carrito <span id="c-count">0</span></h3><div id="c-items" class="text-[13px] mt-2"></div><div class="flex justify-between font-black text-lg mt-3 border-t pt-3"><span>Total</span><span>$<span id="c-total">0</span></span></div><button onclick="cobrar()" class="w-full mt-3 bg-green-500 text-white py-3 rounded-xl font-black">COBRAR</button></div></div>

<div id="p-finanzas" class="p-3 hidden">
<div class="grid grid-cols-3 gap-2">
<div class="bg-green-500 text-white p-3 rounded-2xl"><p class="text-[9px]">ENTRADAS</p><p class="font-black text-[16px]">$<span id="f-entradas">0</span></p></div>
<div class="bg-red-500 text-white p-3 rounded-2xl"><p class="text-[9px]">SALIDAS</p><p class="font-black text-[16px]">$<span id="f-salidas">0</span></p></div>
<div class="bg-black text-white p-3 rounded-2xl"><p class="text-[9px]">GANANCIA</p><p class="font-black text-[16px]">$<span id="f-ganancia">0</span></p></div>
</div>
<div class="mt-4 bg-white rounded-2xl p-4 shadow-sm"><h3 class="font-bold text-sm">Registrar salida manual</h3><div class="flex gap-2 mt-2"><input id="movConcepto" placeholder="Concepto" class="border p-2.5 rounded-xl text-sm flex-1"><input id="movMonto" type="number" placeholder="$" class="border w-24 p-2.5 rounded-xl text-sm"><button onclick="addMov()" class="bg-black text-white px-4 rounded-xl text-sm">+</button></div></div>
<div id="f-lista" class="mt-3 bg-white rounded-2xl p-3"></div>
</div>

<div id="p-config" class="p-3 hidden">
<div class="bg-white rounded-[24px] p-5 shadow-sm">
<h2 class="font-black text-lg"><i class="fa-solid fa-gear"></i> Gastos fijos mensuales</h2><p class="text-[11px] text-gray-400 mt-1">Estos se reparten entre todo lo que produces al mes. Ej: $3000 renta / 100 salsas = $30 por salsa</p>
<div id="gastosFijos" class="mt-4 space-y-2"></div>
<button onclick="addGastoFijo()" class="mt-3 text-[11px] bg-gray-100 px-4 py-2 rounded-full font-bold w-full">+ Agregar gasto fijo (luz, renta, empleado...)</button>
<div class="mt-5 border-t pt-4"><label class="text-[11px] font-bold">¿Cuántas recetas/productos haces al mes aprox?</label><input id="prodMes" type="number" value="100" class="w-full border-2 p-3 rounded-xl mt-2 font-bold" oninput="calcGastosFijos()"></div>
<div class="mt-4 p-4 bg-black text-white rounded-2xl text-center"><p class="text-[11px]">Cada receta pagará</p><p class="font-black text-2xl">$<span id="cfg-porReceta">0</span> <span class="text-[12px] font-normal">de gastos fijos</span></p></div>
</div>
</div>

<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30">
<button onclick="tab('costos')" id="nav-costos" class="flex flex-col items-center px-3 py-1 text-black"><i class="fa-solid fa-calculator text-sm"></i><span class="text-[9px] font-bold">Costos</span></button>
<button onclick="tab('vender')" id="nav-vender" class="flex flex-col items-center px-3 py-1 text-gray-300"><i class="fa-solid fa-cash-register text-sm"></i><span class="text-[9px]">Vender</span></button>
<button onclick="tab('finanzas')" id="nav-finanzas" class="flex flex-col items-center px-3 py-1 text-gray-300"><i class="fa-solid fa-chart-line text-sm"></i><span class="text-[9px]">Finanzas</span></button>
<button onclick="tab('config')" id="nav-config" class="flex flex-col items-center px-3 py-1 text-gray-300"><i class="fa-solid fa-gear text-sm"></i><span class="text-[9px]">Fijos</span></button>
</div>

</div>
<script>
let carrito=[]; const U=['kg','g','L','ml','galon','pza','cda'];
function baseFactor(u){ if(u=='kg'||u=='L') return 1000; if(u=='galon') return 3785; return 1;}
function addInsumo(d={}){let div=document.createElement('div'); div.className='bg-[#FFF8F0] p-3 rounded-[16px] border'; div.innerHTML=`<div class="flex justify-between"><input placeholder="Ingrediente" value="${d.n||''}" class="in-n bg-transparent font-bold text-sm w-2/3 outline-none"><button onclick="this.closest('div').parentElement.remove();calc()" class="text-red-300 text-xs">X</button></div><div class="mt-2 grid grid-cols-3 gap-1 text-[11px]"><input type="number" value="${d.cc||''}" placeholder="Cant" class="in-cc border p-2 rounded-lg" oninput="calc()"><select class="in-uc border p-2 rounded-lg" onchange="calc()">${U.map(x=>`<option ${d.uc==x?'selected':''}>${x}</option>`).join('')}</select><input type="number" value="${d.pc||''}" placeholder="$" class="in-pc border p-2 rounded-lg" oninput="calc()"><input type="number" value="${d.cu||''}" placeholder="Uso" class="in-cu border p-2 rounded-lg" oninput="calc()"><select class="in-uu border p-2 rounded-lg" onchange="calc()">${U.map(x=>`<option ${d.uu==x?'selected':''}>${x}</option>`).join('')}</select><div class="p-2 bg-white rounded-lg text-center font-bold">$<span class="in-sub">0</span></div></div>`; document.getElementById('insumos').appendChild(div);}
addInsumo({n:'Cebolla',cc:1,uc:'kg',pc:40,cu:150,uu:'g'});
function getGF(){return JSON.parse(localStorage.getItem('gastosFijos')||'[]');}
function getProdMes(){return parseFloat(localStorage.getItem('prodMes')||'100')||100;}
function addGastoFijo(d={}){let div=document.createElement('div'); div.className='flex gap-2'; div.innerHTML=`<input placeholder="Concepto: Renta" value="${d.nombre||''}" class="gf-n flex-1 border p-2.5 rounded-xl text-sm"><input type="number" value="${d.monto||''}" placeholder="$" class="gf-m w-24 border p-2.5 rounded-xl text-sm" oninput="calcGastosFijos()"><button onclick="this.parentElement.remove();calcGastosFijos()" class="text-red-300">x</button>`; document.getElementById('gastosFijos').appendChild(div);}
function calcGastosFijos(){
 let total=0; document.querySelectorAll('#gastosFijos > div').forEach(r=>{total+=parseFloat(r.querySelector('.gf-m').value)||0;});
 let prodMes=parseFloat(document.getElementById('prodMes').value)||100; localStorage.setItem('prodMes',prodMes);
 let arr=[]; document.querySelectorAll('#gastosFijos > div').forEach(r=> arr.push({nombre:r.querySelector('.gf-n').value,monto:parseFloat(r.querySelector('.gf-m').value)||0})); localStorage.setItem('gastosFijos',JSON.stringify(arr));
 let porReceta= prodMes>0? total/prodMes : 0;
 document.getElementById('gf-total').innerText=total.toFixed(0); document.getElementById('gf-produccion').innerText=prodMes; document.getElementById('gf-porReceta').innerText=porReceta.toFixed(2); document.getElementById('cfg-porReceta').innerText=porReceta.toFixed(2); document.getElementById('c-fijos').innerText=porReceta.toFixed(2);
 calc();
}
function calc(){let totalIng=0; document.querySelectorAll('#insumos > div').forEach(row=>{let cc=parseFloat(row.querySelector('.in-cc').value)||0, pc=parseFloat(row.querySelector('.in-pc').value)||0, cu=parseFloat(row.querySelector('.in-cu').value)||0, uc=row.querySelector('.in-uc').value, uu=row.querySelector('.in-uu').value; if(!cc||!pc||!cu){row.querySelector('.in-sub').innerText='0'; return;} let bcc=cc*baseFactor(uc), bcu=cu*baseFactor(uu), cost=(pc/bcc)*bcu; if(uc!=uu && U.indexOf(uc)>4) cost=(pc/cc)*cu; row.querySelector('.in-sub').innerText=cost.toFixed(2); totalIng+=cost;}); document.getElementById('c-ing').innerText=totalIng.toFixed(2); let gf=parseFloat(document.getElementById('gf-porReceta').innerText)||0; document.getElementById('costo').innerText=(totalIng+gf).toFixed(2); let m=parseFloat(document.getElementById('margen').value)||0; document.getElementById('venta').innerText=((totalIng+gf)*(1+m/100)).toFixed(2);}
document.getElementById('margen').oninput=calc;
function tab(t){['costos','vender','finanzas','config'].forEach(x=>{document.getElementById('p-'+x).classList.toggle('hidden',x!=t); document.getElementById('nav-'+x).classList.toggle('text-black',x==t); document.getElementById('nav-'+x).classList.toggle('text-gray-300',x!=t);}); if(t=='vender') mostrarVenta(); if(t=='finanzas') mostrarFinanzas();}
function getProd(){return JSON.parse(localStorage.getItem('productosV2')||'[]');}
function getMovs(){return JSON.parse(localStorage.getItem('movs')||'[]');}
function guardar(){let nombre=document.getElementById('nombre').value.trim(); if(!nombre) return alert('Nombre'); let costo=parseFloat(document.getElementById('costo').innerText), venta=parseFloat(document.getElementById('venta').innerText); let p=getProd(); p.push({id:Date.now(),nombre,costo,venta}); localStorage.setItem('productosV2',JSON.stringify(p)); mostrar(); alert('Guardado con gastos fijos incluidos: $'+costo);}
function mostrar(){let prods=getProd(); let h='<h2 class="font-black text-sm">Recetas ('+prods.length+')</h2>'; prods.forEach((p,i)=>h+=`<div class="mt-2 bg-white p-3 rounded-xl flex justify-between shadow-sm"><div><b class="text-[13px]">${p.nombre}</b><br><span class="text-[11px] text-gray-500">Total $${p.costo.toFixed(2)} → Venta $${p.venta.toFixed(2)}</span></div><button onclick="let pr=getProd(); pr.splice(${i},1); localStorage.setItem('productosV2',JSON.stringify(pr)); mostrar();" class="text-[11px] bg-red-50 text-red-500 px-3 py-1 rounded-full">X</button></div>`); document.getElementById('listaInv').innerHTML=h; mostrarVenta();}
function mostrarVenta(){let prods=getProd(); let h=''; prods.forEach(p=>h+=`<button onclick="addCart(${p.id})" class="bg-white p-3 rounded-2xl text-left shadow-sm border"><b class="text-[12px]">${p.nombre}</b><br><span class="text-[11px] text-green-600 font-bold">$${p.venta.toFixed(2)}</span></button>`); document.getElementById('listaVenta').innerHTML=h||'<p class="text-center text-sm text-gray-400 py-10">Crea recetas primero</p>';}
function addCart(id){let p=getProd().find(x=>x.id==id); let ex=carrito.find(x=>x.id==id); if(ex) ex.qty++; else carrito.push({...p,qty:1}); renderCart();}
function renderCart(){let t=0,c=0,html=''; carrito.forEach((x,i)=>{t+=x.venta*x.qty; c+=x.qty; html+=`<div class="flex justify-between py-1"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)}</span></div>`;}); document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('c-count').innerText=c; document.getElementById('c-items').innerHTML=html||'<span class="text-gray-400 text-xs">Vacío</span>';}
function vaciar(){carrito=[]; renderCart();}
function cobrar(){if(!carrito.length) return alert('Vacío'); let total=parseFloat(document.getElementById('c-total').innerText); let movs=getMovs(); movs.unshift({tipo:'entrada',concepto:'Venta: '+carrito.map(c=>c.nombre+' x'+c.qty).join(', '),monto:total,fecha:new Date().toLocaleString()}); localStorage.setItem('movs',JSON.stringify(movs)); vaciar(); tab('finanzas');}
function addMov(){let concepto=document.getElementById('movConcepto').value, monto=parseFloat(document.getElementById('movMonto').value); if(!concepto||!monto) return; let movs=getMovs(); movs.unshift({tipo:'salida',concepto,monto,fecha:new Date().toLocaleString()}); localStorage.setItem('movs',JSON.stringify(movs)); document.getElementById('movConcepto').value=''; document.getElementById('movMonto').value=''; mostrarFinanzas();}
function mostrarFinanzas(){let movs=getMovs(); let ent=0,sal=0,h=''; movs.forEach(m=>{if(m.tipo=='entrada') ent+=m.monto; else sal+=m.monto; h+=`<div class="flex justify-between py-2 border-b"><div><p class="text-[12px] font-bold">${m.concepto}</p><p class="text-[10px] text-gray-400">${m.fecha}</p></div><div class="font-black text-[12px] ${m.tipo=='entrada'?'text-green-600':'text-red-500'}">${m.tipo=='entrada'?'+':'-'}$${m.monto}</div></div>`;}); document.getElementById('f-entradas').innerText=ent.toFixed(0); document.getElementById('f-salidas').innerText=sal.toFixed(0); document.getElementById('f-ganancia').innerText=(ent-sal).toFixed(0); document.getElementById('gananciaHoy').innerText='$'+(ent-sal).toFixed(0); document.getElementById('f-lista').innerHTML=h||'<p class="text-xs text-center text-gray-400">Sin movimientos</p>';}
let savedGF=getGF(); if(savedGF.length){savedGF.forEach(g=>addGastoFijo(g));} else {addGastoFijo({nombre:'Renta',monto:3000}); addGastoFijo({nombre:'Luz',monto:800}); addGastoFijo({nombre:'Gas',monto:500}); addGastoFijo({nombre:'Empleado',monto:4000});} document.getElementById('prodMes').value=getProdMes(); calcGastosFijos(); calc(); mostrar(); mostrarFinanzas();
</script></body></html>
""" 
