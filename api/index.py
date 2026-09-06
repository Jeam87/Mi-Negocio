from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 3.0</title><script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head><body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[80px]">

<div class="bg-white p-4 flex justify-between items-center sticky top-0 z-20 shadow-sm">
<div class="flex items-center gap-2"><label for="logoIn"><img id="logo" src="https://em-content.zobj.net/thumbs/120/apple/354/hamburger_1f354.png" class="w-9 h-9 rounded-full object-cover bg-gray-100"></label><input id="logoIn" type="file" hidden accept="image/*"><h1 class="font-black text-[17px]">Mi Negocio</h1></div>
<div class="text-[11px] bg-green-50 text-green-700 px-3 py-1 rounded-full font-bold"><span id="gananciaHoy">$0</span> hoy</div>
</div>

<!-- PAGINA 1 COSTOS -->
<div id="p-costos" class="p-3">
<div class="bg-white rounded-[24px] p-4 shadow-sm">
<input id="nombre" placeholder="Nombre receta: Salsa 1L" class="w-full border-2 p-3 rounded-xl font-bold text-[14px]">
<div id="insumos" class="mt-3 space-y-3"></div>
<button onclick="addInsumo()" class="mt-3 text-[11px] bg-orange-100 text-orange-700 px-4 py-2 rounded-full font-bold">+ Ingrediente</button>
<div class="mt-4 p-4 bg-gray-900 text-white rounded-[18px]">
<div class="flex justify-between text-sm"><span>Costo receta:</span><span class="font-bold">$<b id="costo">0.00</b></span></div>
<div class="flex gap-2 mt-3 items-center"><input id="margen" type="number" value="100" class="w-14 text-black p-2 rounded-lg text-sm font-bold text-center"><span class="text-[11px]">% ganancia</span><span class="ml-auto">Venta $<b id="venta" class="text-[20px]">0</b></span></div>
</div>
<button onclick="guardar()" class="w-full mt-3 bg-black text-white py-3 rounded-xl font-black text-sm">Guardar receta</button>
</div><div id="listaInv" class="mt-4"></div>
</div>

<!-- PAGINA 2 VENDER -->
<div id="p-vender" class="p-3 hidden">
<div id="listaVenta" class="grid grid-cols-2 gap-3"></div>
<div id="carrito" class="mt-6 bg-white rounded-[20px] p-4 shadow-xl border sticky bottom-[80px]">
<h3 class="font-bold text-sm">Carrito <span id="c-count">0</span></h3><div id="c-items" class="text-[13px] mt-2"></div>
<div class="flex justify-between font-black text-lg mt-3 border-t pt-3"><span>Total</span><span>$<span id="c-total">0</span></span></div>
<button onclick="cobrar()" class="w-full mt-3 bg-green-500 text-white py-3 rounded-xl font-black">COBRAR + REGISTRAR</button>
<button onclick="vaciar()" class="w-full mt-2 text-[11px] text-gray-400">Vaciar carrito</button>
</div>
</div>

<!-- PAGINA 3 FINANZAS -->
<div id="p-finanzas" class="p-3 hidden">
<div class="grid grid-cols-3 gap-2">
<div class="bg-green-500 text-white p-3 rounded-2xl"><p class="text-[10px]">ENTRADAS</p><p class="font-black text-lg">$<span id="f-entradas">0</span></p></div>
<div class="bg-red-500 text-white p-3 rounded-2xl"><p class="text-[10px]">SALIDAS</p><p class="font-black text-lg">$<span id="f-salidas">0</span></p></div>
<div class="bg-black text-white p-3 rounded-2xl"><p class="text-[10px]">GANANCIA</p><p class="font-black text-lg">$<span id="f-ganancia">0</span></p></div>
</div>

<div class="mt-4 bg-white rounded-2xl p-4 shadow-sm">
<h3 class="font-bold text-sm">Registrar movimiento</h3>
<div class="flex gap-2 mt-2"><select id="movTipo" class="border p-2.5 rounded-xl text-sm w-1/3"><option value="salida">Salida</option><option value="entrada">Entrada</option></select><input id="movConcepto" placeholder="Concepto: compra jitomate, luz..." class="border p-2.5 rounded-xl text-sm flex-1"></div>
<div class="flex gap-2 mt-2"><input id="movMonto" type="number" placeholder="$ monto" class="border p-2.5 rounded-xl text-sm flex-1"><button onclick="addMov()" class="bg-black text-white px-5 rounded-xl font-bold text-sm">Agregar</button></div>
</div>

<div class="mt-4 bg-white rounded-2xl p-4 shadow-sm">
<div class="flex justify-between items-center"><h3 class="font-bold text-sm">Historial</h3><button onclick="borrarHistorial()" class="text-[10px] text-red-400">Borrar todo</button></div>
<div id="f-lista" class="mt-3 space-y-2 max-h-[300px] overflow-auto"></div>
</div>
</div>

<!-- NAV ABAJO -->
<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto z-30">
<button onclick="tab('costos')" id="nav-costos" class="flex flex-col items-center px-4 py-1 text-black"><i class="fa-solid fa-calculator"></i><span class="text-[10px] font-bold">Costos</span></button>
<button onclick="tab('vender')" id="nav-vender" class="flex flex-col items-center px-4 py-1 text-gray-300"><i class="fa-solid fa-cash-register"></i><span class="text-[10px] font-bold">Vender</span></button>
<button onclick="tab('finanzas')" id="nav-finanzas" class="flex flex-col items-center px-4 py-1 text-gray-300"><i class="fa-solid fa-chart-line"></i><span class="text-[10px] font-bold">Finanzas</span></button>
</div>

</div>
<script>
let carrito=[]; const U=['kg','g','L','ml','galon','pza','cda'];
function baseFactor(u){ if(u=='kg'||u=='L') return 1000; if(u=='galon') return 3785; return 1;}
function addInsumo(d={}){let div=document.createElement('div'); div.className='bg-[#FFF8F0] p-3 rounded-[16px] border'; div.innerHTML=`<div class="flex justify-between"><input placeholder="Ingrediente" value="${d.n||''}" class="in-n bg-transparent font-bold text-sm w-2/3 outline-none"><button onclick="this.closest('div').parentElement.remove();calc()" class="text-red-300 text-xs">X</button></div><div class="mt-2 grid grid-cols-3 gap-1 text-[11px]"><div class="col-span-3 text-gray-400 font-bold">COMPRE:</div><input type="number" value="${d.cc||''}" placeholder="Cant" class="in-cc border p-2 rounded-lg" oninput="calc()"><select class="in-uc border p-2 rounded-lg" onchange="calc()">${U.map(x=>`<option ${d.uc==x?'selected':''}>${x}</option>`).join('')}</select><input type="number" value="${d.pc||''}" placeholder="$" class="in-pc border p-2 rounded-lg" oninput="calc()"><div class="col-span-3 text-gray-400 font-bold mt-1">USO:</div><input type="number" value="${d.cu||''}" placeholder="Cant" class="in-cu border p-2 rounded-lg" oninput="calc()"><select class="in-uu border p-2 rounded-lg" onchange="calc()">${U.map(x=>`<option ${d.uu==x?'selected':''}>${x}</option>`).join('')}</select><div class="p-2 bg-white rounded-lg text-center font-bold">$<span class="in-sub">0</span></div></div>`; document.getElementById('insumos').appendChild(div);}
addInsumo({n:'Cebolla',cc:1,uc:'kg',pc:40,cu:150,uu:'g'});
function calc(){let total=0; document.querySelectorAll('#insumos > div').forEach(row=>{let cc=parseFloat(row.querySelector('.in-cc').value)||0, pc=parseFloat(row.querySelector('.in-pc').value)||0, cu=parseFloat(row.querySelector('.in-cu').value)||0, uc=row.querySelector('.in-uc').value, uu=row.querySelector('.in-uu').value; if(!cc||!pc||!cu){row.querySelector('.in-sub').innerText='0'; return;} let bcc=cc*baseFactor(uc), bcu=cu*baseFactor(uu), cost=(pc/bcc)*bcu; if(uc!=uu && baseFactor(uc)!=baseFactor(uu) && ((uc=='pza')!== (uu=='pza'))) { if(uc==uu) cost=(pc/cc)*cu; else if(uc=='kg'&&uu=='g'||uc=='L'&&uu=='ml'){} else cost=(pc/cc)*cu; } row.querySelector('.in-sub').innerText=cost.toFixed(2); total+=cost;}); document.getElementById('costo').innerText=total.toFixed(2); let m=parseFloat(document.getElementById('margen').value)||0; document.getElementById('venta').innerText=(total+total*m/100).toFixed(2);}
document.getElementById('margen').oninput=calc;
function tab(t){['costos','vender','finanzas'].forEach(x=>{document.getElementById('p-'+x).classList.toggle('hidden',x!=t); document.getElementById('nav-'+x).classList.toggle('text-black',x==t); document.getElementById('nav-'+x).classList.toggle('text-gray-300',x!=t);}); if(t=='vender') mostrarVenta(); if(t=='finanzas') mostrarFinanzas();}
function getProd(){return JSON.parse(localStorage.getItem('productosV2')||'[]');}
function getMovs(){return JSON.parse(localStorage.getItem('movs')||'[]');}
function guardar(){let nombre=document.getElementById('nombre').value.trim(); if(!nombre) return alert('Pon nombre'); let costo=parseFloat(document.getElementById('costo').innerText), venta=parseFloat(document.getElementById('venta').innerText); let ingredientes=[]; document.querySelectorAll('#insumos > div').forEach(r=>ingredientes.push({n:r.querySelector('.in-n').value})); let p=getProd(); p.push({id:Date.now(),nombre,costo,venta}); localStorage.setItem('productosV2',JSON.stringify(p)); document.getElementById('nombre').value=''; mostrar(); tab('vender');}
function mostrar(){let prods=getProd(); let h='<h2 class="font-black text-sm">Recetas ('+prods.length+')</h2>'; prods.forEach((p,i)=>h+=`<div class="mt-2 bg-white p-3 rounded-xl flex justify-between items-center shadow-sm"><div><b class="text-[13px]">${p.nombre}</b><br><span class="text-[11px] text-gray-500">$${p.costo.toFixed(2)} → $${p.venta.toFixed(2)}</span></div><button onclick="let pr=getProd(); pr.splice(${i},1); localStorage.setItem('productosV2',JSON.stringify(pr)); mostrar();" class="text-[11px] bg-red-50 text-red-500 px-3 py-1 rounded-full">Borrar</button></div>`); document.getElementById('listaInv').innerHTML=h; mostrarVenta();}
function mostrarVenta(){let prods=getProd(); let h=''; prods.forEach(p=>h+=`<button onclick="addCart(${p.id})" class="bg-white p-3 rounded-2xl text-left shadow-sm border"><b class="text-[12px]">${p.nombre}</b><br><span class="text-[11px] text-green-600 font-bold">$${p.venta.toFixed(2)}</span></button>`); if(!prods.length) h='<p class="col-span-2 text-center text-sm text-gray-400 py-10">Crea recetas primero en Costos</p>'; document.getElementById('listaVenta').innerHTML=h;}
function addCart(id){let p=getProd().find(x=>x.id==id); let ex=carrito.find(x=>x.id==id); if(ex) ex.qty++; else carrito.push({...p,qty:1}); renderCart();}
function renderCart(){let t=0,c=0,html=''; carrito.forEach((x,i)=>{t+=x.venta*x.qty; c+=x.qty; html+=`<div class="flex justify-between py-1"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)} <button onclick="carrito.splice(${i},1);renderCart()" class="text-red-300 ml-1">x</button></span></div>`;}); document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('c-count').innerText=c; document.getElementById('c-items').innerHTML=html||'<span class="text-gray-400 text-xs">Vacío</span>';}
function vaciar(){carrito=[]; renderCart();}
function cobrar(){if(!carrito.length) return alert('Vacío'); let total=parseFloat(document.getElementById('c-total').innerText); let desc=carrito.map(c=>c.nombre+' x'+c.qty).join(', '); let movs=getMovs(); movs.unshift({tipo:'entrada',concepto:'Venta: '+desc,monto:total,fecha:new Date().toLocaleString()}); localStorage.setItem('movs',JSON.stringify(movs)); vaciar(); alert('Venta $'+total+' registrada en Finanzas!'); tab('finanzas');}
function addMov(){let tipo=document.getElementById('movTipo').value, concepto=document.getElementById('movConcepto').value.trim(), monto=parseFloat(document.getElementById('movMonto').value); if(!concepto||!monto) return alert('Llena concepto y monto'); let movs=getMovs(); movs.unshift({tipo,concepto,monto,fecha:new Date().toLocaleString()}); localStorage.setItem('movs',JSON.stringify(movs)); document.getElementById('movConcepto').value=''; document.getElementById('movMonto').value=''; mostrarFinanzas();}
function mostrarFinanzas(){let movs=getMovs(); let ent=0,sal=0; let h=''; movs.forEach(m=>{ if(m.tipo=='entrada') ent+=m.monto; else sal+=m.monto; h+=`<div class="flex justify-between items-center border-b py-2"><div><p class="text-[13px] font-bold">${m.tipo=='entrada'?'<span class=text-green-600>▲</span>':'<span class=text-red-500>▼</span>'} ${m.concepto}</p><p class="text-[10px] text-gray-400">${m.fecha}</p></div><div class="font-black text-[13px] ${m.tipo=='entrada'?'text-green-600':'text-red-500'}">${m.tipo=='entrada'?'+':'-'}$${m.monto.toFixed(2)}</div></div>`;}); document.getElementById('f-entradas').innerText=ent.toFixed(0); document.getElementById('f-salidas').innerText=sal.toFixed(0); document.getElementById('f-ganancia').innerText=(ent-sal).toFixed(0); document.getElementById('gananciaHoy').innerText='$'+(ent-sal).toFixed(0); document.getElementById('f-lista').innerHTML=h||'<p class="text-xs text-gray-400 text-center py-6">Aún no hay movimientos</p>';}
function borrarHistorial(){if(confirm('¿Borrar todo el historial?')){localStorage.removeItem('movs'); mostrarFinanzas();}}
document.getElementById('logoIn').onchange=e=>{let r=new FileReader(); r.onload=()=>{document.getElementById('logo').src=r.result; localStorage.setItem('logo',r.result);}; r.readAsDataURL(e.target.files[0]);}; if(localStorage.getItem('logo')) document.getElementById('logo').src=localStorage.getItem('logo');
calc(); mostrar(); mostrarFinanzas();
</script></body></html>
"""
