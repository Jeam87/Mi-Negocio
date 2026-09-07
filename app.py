from flask import Flask, jsonify, send_file
app = Flask(__name__)

@app.route('/manifest.json')
def manifest():
    return jsonify({
      "name": "Mi Negocio 9.9.5",
      "short_name": "Mi Negocio",
      "start_url": "/",
      "display": "standalone",
      "background_color": "#FFF8F0",
      "theme_color": "#8a2be2",
      "icons": [{"src": "/logo.png", "sizes": "512x512", "type": "image/png"}]
    })

@app.route('/logo.png')
def logo_file():
    return send_file('logo.png', mimetype='image/png')

@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head>
<link rel="manifest" href="/manifest.json">
<link rel="icon" href="/logo.png">
<meta name="theme-color" content="#8a2be2">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 9.9.5</title><script src="https://cdn.tailwindcss.com"></script><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>input,select,textarea{color:#000!important;background:#fff!important}</style></head>
<body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto pb-[120px]">
<div class="bg-white p-3 flex justify-between items-center sticky top-0 z-20 shadow-sm"><h1 class="font-black">Mi Negocio 9.9.5 - Gastos Fijos</h1><button onclick="showTab('config')" class="text-[10px] bg-black text-white px-3 py-1 rounded-full">Config</button></div>

<div id="tab-costos" class="p-3">
<div id="crear-menu" class="space-y-3">
<div class="bg-white rounded-[28px] p-5 shadow-sm"><h2 class="font-black text-[16px]">💰 Gastos Fijos Mensuales</h2><p class="text-[11px] text-gray-500 mt-1">Luz, Renta, Empleados, Internet, etc. Se prorratean en tus costos</p><div class="grid grid-cols-5 gap-2 mt-3"><input id="fijoNombre" placeholder="Ej: Renta" class="col-span-2 border-2 border-black p-3 rounded-xl font-bold text-[12px]"><input id="fijoMonto" type="number" placeholder="$3000" class="col-span-2 border-2 border-black p-3 rounded-xl font-black text-[12px]"><button onclick="addFijo()" class="bg-black text-white rounded-xl font-black">+</button></div><div id="listaFijos" class="mt-3 space-y-2"></div><div class="mt-3 bg-black text-white p-3 rounded-xl flex justify-between font-black"><span>Total Fijos/mes</span><span>$<span id="totalFijos">0</span></span></div><div class="mt-2 bg-amber-50 border-2 border-amber-200 p-3 rounded-xl"><p class="text-[10px] font-bold">¿Cuantos lotes/bases produces al mes? (para prorratear)</p><input id="lotesMes" type="number" value="30" class="w-full border-2 border-black p-2 rounded-xl mt-1 font-black" oninput="guardarLotes(); renderFijos(); calc();"><p class="text-[9px] text-gray-500 mt-1">Ej: Si haces 30 veces salsa al mes, tu renta se divide entre 30</p></div></div>
<div class="bg-white rounded-[28px] p-5 shadow-sm text-center"><h2 class="font-black text-[16px]">Crear</h2><button onclick="setCrear('base')" class="w-full mt-4 bg-[#FFF8F0] border-2 border-black rounded-[20px] p-4 font-black">1. Crear BASE</button></div><div class="bg-white rounded-[20px] p-4"><div id="listaInv"></div></div>
</div>
<div id="crear-base" class="hidden"><button onclick="setCrear('menu')" class="mb-3 font-bold">← Volver</button><div class="bg-white rounded-[28px] p-4"><h2 class="font-black">BASE</h2><input id="nombre" placeholder="Ej: Salsa búfalo" class="w-full border-2 border-black p-3 rounded-xl font-bold mt-3"><div id="insumos" class="mt-3 space-y-2"></div><button onclick="addInsumo()" class="w-full mt-2 bg-orange-100 border-2 py-2 rounded-xl font-bold text-[12px]">+ Ingrediente</button><div class="mt-3 bg-amber-50 border-2 p-3 rounded-xl"><div class="flex gap-2"><input id="rendCant" type="number" value="10" class="flex-1 border-2 border-black p-2 rounded-xl font-black" oninput="calc()"><select id="rendUni" class="border-2 border-black p-2 rounded-xl" onchange="calc()"><option>L</option><option>ml</option><option>kg</option><option>g</option><option>pza</option></select></div></div><div class="mt-3 p-4 bg-[#0F172A] text-white rounded-[16px]"><div class="flex justify-between"><span>Ingredientes</span><b>$<span id="c-ing">0.00</span></b></div><div class="flex justify-between text-amber-300"><span>+ Fijos (luz, renta...)</span><b>$<span id="c-fijos">0.00</span></b></div><div class="font-black text-[16px] border-t border-white/20 mt-2 pt-2 flex justify-between"><span>Total</span><span>$<span id="costo">0.00</span></span></div><div class="text-[11px] text-green-300">Costo x 1 <span id="r-uni-label">L</span>: $<span id="costo-unit">0.00</span></div><div class="flex justify-between mt-2 text-[#4FD1C5] font-black"><span>Venta:</span><span>$<span id="venta">0.00</span></span></div><div class="mt-2 flex gap-2"><input id="margen" type="number" value="50" class="w-16 text-black rounded-lg text-center font-black" oninput="calc()"><input id="ventaManual" type="number" placeholder="$ final" class="flex-1 text-black rounded-lg px-2 font-black" oninput="calc()"></div></div><button onclick="guardarProd('recetario')" class="w-full mt-4 bg-black text-white py-3 rounded-xl font-black">GUARDAR BASE</button></div></div>
</div>

<div id="tab-clientes" class="p-3 hidden"><div class="bg-white rounded-[20px] p-4 shadow-sm"><h3 class="font-black">Clientes (<span id="cliCount">0</span>)</h3><div id="listaClientes" class="mt-3"></div></div></div>
<div id="tab-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div><div class="mt-4 bg-white p-4 rounded-2xl border-2 border-black"><div id="ticket">Vacío</div><div class="flex justify-between font-black text-xl mt-3">Total $ <span id="c-total">0</span></div><button onclick="abrirCobro()" class="w-full mt-3 bg-black text-white py-3 rounded-xl font-black">COBRAR</button></div></div>
<div id="tab-inventario" class="p-3 hidden"><div class="bg-white rounded-[20px] p-4"><div class="grid grid-cols-5 gap-2"><input id="inv-nombre" placeholder="Papas" class="col-span-2 border-2 border-black p-2 rounded-xl"><input id="inv-precio" type="number" placeholder="$30" class="border-2 border-black p-2 rounded-xl"><select id="inv-unidad" class="border-2 border-black p-2 rounded-xl"><option>kg</option><option>g</option><option>L</option><option>ml</option><option>pza</option></select><button onclick="addInventario()" class="bg-black text-white rounded-xl">+</button></div><div id="listaInvMaster" class="mt-4"></div></div></div>
<div id="tab-config" class="p-3 hidden"><div class="bg-white p-5 rounded-2xl"><h2 class="font-black">Config</h2><p class="text-[11px] text-gray-500">Aquí van tus gastos fijos arriba en Crear</p><button onclick="showTab('costos')" class="w-full mt-4 bg-black text-white py-3 rounded-xl font-bold">Ir a Gastos Fijos</button></div></div>

<div id="modalCobro" class="hidden fixed inset-0 bg-black/70 z-50 flex items-end justify-center"><div class="bg-white w-full max-w-md rounded-t-[28px] p-5"><h2 class="font-black">Cobrar $<span id="cobroTotal">0</span></h2><button onclick="confirmarCobro()" class="w-full mt-4 bg-black text-white py-3 rounded-xl font-black">CONFIRMAR</button><button onclick="cerrarCobro()" class="w-full mt-2 bg-gray-100 py-2 rounded-xl">Cerrar</button></div></div>
<div class="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 max-w-md mx-auto"><button onclick="showTab('costos')" class="flex flex-col items-center"><span class="text-[10px] font-bold">Crear</span></button><button onclick="showTab('vender')" class="flex flex-col items-center text-gray-400"><span class="text-[10px]">Vender</span></button><button onclick="showTab('inventario')" class="flex flex-col items-center text-gray-400"><span class="text-[10px]">Inv</span></button><button onclick="showTab('clientes')" class="flex flex-col items-center text-gray-400"><span class="text-[10px]">Clientes</span></button></div></div>
<script>
let carrito=[];
function getFijos(){ return JSON.parse(localStorage.getItem('gastosFijos')||'[]'); }
function getProd(){ return JSON.parse(localStorage.getItem('productosV2')||'[]'); }
function getInv(){ return JSON.parse(localStorage.getItem('inventarioMaestro')||'[]'); }
function getCli(){ return JSON.parse(localStorage.getItem('clientesV2')||'[]'); }
function getLotes(){ return parseInt(localStorage.getItem('lotesMes')||'30')||30; }
function guardarLotes(){ localStorage.setItem('lotesMes', document.getElementById('lotesMes').value); }
function addFijo(){ let n=document.getElementById('fijoNombre').value.trim(), m=parseFloat(document.getElementById('fijoMonto').value); if(!n||!m) return alert('Pon nombre y monto'); let f=getFijos(); f.push({id:Date.now().toString(), nombre:n, monto:m}); localStorage.setItem('gastosFijos', JSON.stringify(f)); document.getElementById('fijoNombre').value=''; document.getElementById('fijoMonto').value=''; renderFijos(); calc(); }
function renderFijos(){ let f=getFijos(); let total=f.reduce((s,x)=>s+x.monto,0); document.getElementById('totalFijos').innerText=total.toFixed(0); let lotes=getLotes(); document.getElementById('lotesMes').value=lotes; let costoPorLote = lotes>0? total/lotes : 0; let h=f.map(x=>`<div class="flex justify-between items-center bg-gray-50 p-3 rounded-xl border"><div><b class="text-[12px]">${x.nombre}</b><br><span class="text-[10px]">$${x.monto}/mes → $${(x.monto/lotes).toFixed(2)} por lote</span></div><button onclick="borrarFijo('${x.id}')" class="text-red-500 font-black px-2">X</button></div>`).join(''); document.getElementById('listaFijos').innerHTML=h||'<p class="text-[11px] text-gray-400 text-center">Agrega luz, renta, empleados...</p>'; window._costoFijoPorLote=costoPorLote; }
function borrarFijo(id){ let f=getFijos().filter(x=>x.id!=id); localStorage.setItem('gastosFijos', JSON.stringify(f)); renderFijos(); calc(); }
function showTab(t){ ['costos','vender','inventario','clientes','config'].forEach(x=>{ let el=document.getElementById('tab-'+x); if(el) el.classList.toggle('hidden',x!=t); }); if(t=='costos'){ renderFijos(); renderInventario(); } if(t=='vender') renderVenta(); if(t=='inventario') renderInventarioMaster(); if(t=='clientes') renderClientes(); }
function setCrear(v){ document.getElementById('crear-menu').classList.toggle('hidden',v!='menu'); document.getElementById('crear-base').classList.toggle('hidden',v!='base'); if(v=='base'){ document.getElementById('insumos').innerHTML=''; addInsumo(); calc(); } if(v=='menu') renderInventario(); }
function addInsumo(){ let inv=getInv(); let opts=inv.map(it=>`<option value="${it.id}">${it.nombre} $${it.precio}/${it.unidad}</option>`).join(''); let div=document.createElement('div'); div.className='bg-white border-2 p-2 rounded-xl flex gap-2'; div.innerHTML=`<select class="in-n flex-1 border-2 p-2 rounded-lg text-[12px]" onchange="calc()"><option value="">Ingrediente</option>${opts}</select><input type="number" placeholder="Cant" class="in-cu w-20 border-2 p-2 rounded-lg" oninput="calc()"><button onclick="this.parentElement.remove();calc()" class="text-red-400 font-black">X</button>`; document.getElementById('insumos').appendChild(div); }
function calc(){ try{ let tot=0; document.querySelectorAll('#insumos > div').forEach(row=>{ let sel=row.querySelector('.in-n'); let id=sel.value; let it=getInv().find(x=>x.id==id); let cu=parseFloat(row.querySelector('.in-cu').value)||0; if(it&&cu) tot+=(it.precio*cu); }); let fijos=window._costoFijoPorLote||0; document.getElementById('c-ing').innerText=tot.toFixed(2); document.getElementById('c-fijos').innerText=fijos.toFixed(2); let rc=parseFloat(document.getElementById('rendCant').value)||1; document.getElementById('r-uni-label').innerText=document.getElementById('rendUni').value; let total=tot+fijos; document.getElementById('costo').innerText=total.toFixed(2); document.getElementById('costo-unit').innerText=(total/rc).toFixed(2); let m=parseFloat(document.getElementById('margen').value)||0; let vm=document.getElementById('ventaManual').value; document.getElementById('venta').innerText= vm? parseFloat(vm).toFixed(2) : (total*(1+m/100)).toFixed(2); }catch(e){} }
function guardarProd(){ let n=document.getElementById('nombre').value.trim(); if(!n) return alert('Pon nombre'); let c=parseFloat(document.getElementById('costo').innerText)||0, v=parseFloat(document.getElementById('venta').innerText)||0; let ps=getProd(); ps.push({id:Date.now(), nombre:n, costo:c, venta:v}); localStorage.setItem('productosV2', JSON.stringify(ps)); alert('✅ Base guardada con gastos fijos incluidos'); setCrear('menu'); }
function renderInventario(){ let ps=getProd(); document.getElementById('listaInv').innerHTML=ps.map(p=>`<div class="bg-gray-50 p-3 rounded-xl border mt-2 flex justify-between"><div><b>${p.nombre}</b><br><span class="text-[11px]">Costo real $${p.costo.toFixed(2)} (con fijos) → Venta $${p.venta.toFixed(2)}</span></div><button onclick="let ps=getProd().filter(x=>x.id!=${p.id}); localStorage.setItem('productosV2',JSON.stringify(ps)); renderInventario(); renderVenta();" class="text-red-400">X</button></div>`).join('')||'<p class="text-center text-gray-400 text-[11px]">Sin bases</p>'; }
function renderInventarioMaster(){ let inv=getInv(); document.getElementById('listaInvMaster').innerHTML=inv.map(i=>`<div class="bg-gray-50 p-2 rounded-xl flex justify-between"><span>${i.nombre} $${i.precio}/${i.unidad}</span><button onclick="let inv=getInv().filter(x=>x.id!='${i.id}'); localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); renderInventarioMaster();" class="text-red-400">X</button></div>`).join(''); }
function addInventario(){ let n=document.getElementById('inv-nombre').value, p=parseFloat(document.getElementById('inv-precio').value); if(!n||!p) return; let inv=getInv(); inv.push({id:Date.now().toString(),nombre:n,precio:p,unidad:document.getElementById('inv-unidad').value}); localStorage.setItem('inventarioMaestro',JSON.stringify(inv)); document.getElementById('inv-nombre').value=''; document.getElementById('inv-precio').value=''; renderInventarioMaster(); }
function renderClientes(){ let cli=getCli(); document.getElementById('cliCount').innerText=cli.length; document.getElementById('listaClientes').innerHTML=cli.map(c=>`<div class="bg-gray-50 p-2 rounded-xl">${c.nombre} - ${c.tel}</div>`).join(''); }
function renderVenta(){ let ps=getProd(); document.getElementById('listaVenta').innerHTML=ps.map(p=>`<div class="bg-white rounded-xl border p-3"><b class="text-[12px]">${p.nombre}</b><br><span class="text-[11px]">Costo real $${p.costo.toFixed(2)}</span><br><button onclick="carrito.push({...getProd().find(x=>x.id==${p.id}),qty:1}); renderCarrito();" class="w-full mt-2 bg-black text-white py-2 rounded-xl text-[11px]">Agregar</button></div>`).join(''); }
function renderCarrito(){ let t=0; let h=''; carrito.forEach((x,i)=>{ t+=x.venta*x.qty; h+=`<div class="flex justify-between bg-gray-50 p-2 rounded-xl mt-1"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)} <button onclick="carrito.splice(${i},1); renderCarrito();" class="text-red-500">X</button></span></div>`; }); document.getElementById('ticket').innerHTML=h||'Vacío'; document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('cobroTotal').innerText=t.toFixed(0); }
function abrirCobro(){ if(!carrito.length) return alert('Vacío'); document.getElementById('modalCobro').classList.remove('hidden'); }
function cerrarCobro(){ document.getElementById('modalCobro').classList.add('hidden'); }
function confirmarCobro(){ alert('Venta $'+document.getElementById('c-total').innerText); carrito=[]; renderCarrito(); cerrarCobro(); }
showTab('costos'); renderFijos();
</script>
</body></html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
