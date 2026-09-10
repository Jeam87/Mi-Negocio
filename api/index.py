from flask import Flask
app = Flask(__name__)

HTML = r'''
<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 12.1 Fix</title>
<script src="https://cdn.tailwindcss.com"></script>
</head><body class="bg-[#f6f5f0]">
<div class="max-w-[440px] mx-auto min-h-screen bg-white border-x-2 border-black flex flex-col">
<div class="bg-black text-white p-4 flex justify-between items-center sticky top-0 z-50">
<b>MI NEGOCIO 🍈 V12.1</b><span class="text-[9px] bg-yellow-300 text-black px-2 py-1 rounded-full font-black">FIX EDITAR + 0.2L</span>
</div>
<div class="flex gap-1 p-2 bg-zinc-100 border-b-2 border-black overflow-x-auto text-[10px]">
<button onclick="tab('crear')" id="t-crear" class="tab bg-black text-white px-3 py-2 rounded-lg font-black">CREAR</button>
<button onclick="tab('cat')" id="t-cat" class="tab bg-white border-2 border-black px-3 py-2 rounded-lg font-black">CATALOGO</button>
<button onclick="tab('inv')" id="t-inv" class="tab bg-white border-2 border-black px-3 py-2 rounded-lg font-black">INVENTARIO</button>
<button onclick="tab('fin')" id="t-fin" class="tab bg-white border-2 border-black px-3 py-2 rounded-lg font-black">FINANZAS</button>
<button onclick="tab('cli')" id="t-cli" class="tab bg-white border-2 border-black px-3 py-2 rounded-lg font-black">CLIENTES</button>
<button onclick="tab('prov')" id="t-prov" class="tab bg-white border-2 border-black px-3 py-2 rounded-lg font-black">PROV</button>
</div>

<div id="sec-crear" class="p-3">
<div class="border-2 border-black rounded-xl p-3">
<input id="nombre2" placeholder="Nombre Producto Ej: Burger BBQ" class="w-full border-2 border-black p-2 rounded-lg font-black mb-2 text-[13px]">
<div class="flex gap-2 mb-2">
<select id="cat2" class="border-2 border-black p-2 rounded-lg text-[11px] font-bold"><option>Hamburguesas</option><option>Papas</option><option>Bebidas</option><option>Salsas/Bases</option><option>Otros</option></select>
<input id="costo2" type="number" placeholder="Costo Extra" class="flex-1 border-2 border-black p-2 rounded-lg text-[11px]">
</div>
<div class="flex gap-2 mb-2">
<input id="margen2" type="number" value="30" class="w-[70px] border-2 border-black p-2 rounded-lg text-[11px]"><span class="text-[10px] font-bold pt-2">% margen</span>
<input id="ventaManual2" type="number" placeholder="Venta manual $" class="flex-1 border-2 border-black p-2 rounded-lg text-[11px]" oninput="calc2()">
</div>
<div class="bg-zinc-50 border-2 border-dashed border-black rounded-lg p-2 mb-2">
<div class="flex justify-between items-center mb-1"><b class="text-[11px]">RECETA - Cuanto usas (0.2L, 1/2kg)</b><button onclick="addBase({})" class="bg-black text-white px-2 py-1 rounded text-[10px] font-black">+ BASE</button></div>
<div id="basesSel"></div>
<div class="flex justify-between font-black text-[12px] mt-2 pt-2 border-t-2 border-black"><span>Costo: $<span id="c-ing2">0.00</span></span><span>Venta: $<span id="v2">0.00</span></span></div>
</div>
<input id="foto2" placeholder="URL Foto (opcional)" class="w-full border-2 border-black p-2 rounded-lg text-[11px] mb-2">
<div class="flex gap-2">
<button onclick="guardarProd('normal')" class="flex-1 bg-black text-white py-2 rounded-lg font-black text-[12px]">GUARDAR PRODUCTO</button>
<button onclick="guardarProd('base')" class="flex-1 bg-yellow-300 border-2 border-black py-2 rounded-lg font-black text-[12px]">GUARDAR COMO BASE</button>
</div>
</div>
</div>

<div id="sec-inv" class="p-3 hidden">
<div class="bg-yellow-50 border-2 border-black rounded-xl p-3 mb-3">
<p class="font-black text-[11px] mb-2" id="lblInv">NUEVO INSUMO</p>
<input id="inv-nombre" placeholder="Ej: Papas" class="w-full border-2 border-black p-2 rounded-lg mb-2 font-bold text-[13px]">
<div class="flex gap-2">
<input id="inv-costo" type="number" placeholder="Costo $ total" class="flex-1 border-2 border-black p-2 rounded-lg text-[12px]">
<input id="inv-stock" type="number" placeholder="Stock kg/L/pza" class="flex-1 border-2 border-black p-2 rounded-lg text-[12px]">
</div>
<button id="btnInv" onclick="addInv()" class="w-full bg-black text-white mt-2 py-2 rounded-lg font-black text-[13px]">+ GUARDAR INSUMO</button>
<button id="btnCancel" onclick="cancelEdit()" class="w-full bg-white border-2 border-black mt-2 py-1 rounded-lg font-bold text-[11px] hidden">Cancelar edición</button>
</div>
<div id="contInv" class="flex flex-col gap-2"></div>
</div>

<div id="sec-cat" class="p-3 hidden"><div id="contCat" class="grid grid-cols-2 gap-2"></div></div>
<div id="sec-fin" class="p-3 hidden"><div class="border-2 border-black rounded-xl p-3"><b class="text-[12px]">FINANZAS</b><p class="text-[11px] opacity-60 mt-2">Ventas: $<span id="f-ventas">0</span> | Costo: $<span id="f-costo">0</span> | Ganancia: $<span id="f-gan">0</span></p><div id="f-lista" class="mt-2 text-[10px]"></div></div></div>
<div id="sec-cli" class="p-3 hidden"><div class="border-2 border-black rounded-xl p-3"><b class="text-[12px]">CLIENTES</b><input id="cli-n" placeholder="Nombre cliente" class="w-full border-2 border-black p-2 rounded-lg text-[11px] mt-2"><button onclick="addCli()" class="w-full bg-black text-white py-2 rounded-lg font-black text-[11px] mt-2">+ CLIENTE</button><div id="contCli" class="mt-2"></div></div></div>
<div id="sec-prov" class="p-3 hidden"><div class="border-2 border-black rounded-xl p-3"><b class="text-[12px]">PROVEEDORES</b><input id="prov-n" placeholder="Nombre proveedor" class="w-full border-2 border-black p-2 rounded-lg text-[11px] mt-2"><button onclick="addProv()" class="w-full bg-black text-white py-2 rounded-lg font-black text-[11px] mt-2">+ PROVEEDOR</button><div id="contProv" class="mt-2"></div></div></div>

</div>
<script>
let editId=null;
function g(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}} function s(k,v){localStorage.setItem(k,JSON.stringify(v))}
function getInv(){let a=g('pro_inv_v1',[]); if(!a.length){let o=g('inv',[]); if(o.length) a=o.map(x=>({id:x.id||Date.now().toString(),nombre:x.nombre||x.name,costo:parseFloat(x.costo||x.price)||0,stock:parseFloat(x.stock||x.cantidad)||0})); s('pro_inv_v1',a)} return a}
function getProd(){return g('pro_prod_v1',[])}
function parseCant(v){v=String(v||'').trim().replace(',','.'); if(!v) return 0; if(v.includes('/')){let p=v.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1)} return parseFloat(v)||0}
function conv(c,de,a){de=(de||'kg').toLowerCase(); a=(a||'kg').toLowerCase(); if(de==a) return c; let m={g:1,kg:1000,mg:0.001,ml:1,l:1000,lt:1000,pza:1,pz:1}; if(m[de]!=null&&m[a]!=null) return c*m[de]/m[a]; return c}

function tab(t){document.querySelectorAll('[id^="sec-"]').forEach(x=>x.classList.add('hidden')); document.getElementById('sec-'+t).classList.remove('hidden'); document.querySelectorAll('.tab').forEach(b=>b.className='tab bg-white border-2 border-black px-3 py-2 rounded-lg font-black'); document.getElementById('t-'+t).className='tab bg-black text-white px-3 py-2 rounded-lg font-black'; if(t=='inv') renderInv(); if(t=='cat') renderCat(); if(t=='fin') renderFin(); if(t=='cli') renderCli(); if(t=='prov') renderProv();}

function addInv(){
let n=document.getElementById('inv-nombre').value.trim(); if(!n) return alert('Nombre');
let c=parseFloat(document.getElementById('inv-costo').value)||0; let st=parseFloat(document.getElementById('inv-stock').value)||0;
let inv=getInv();
if(editId){let b=inv.find(x=>String(x.id)==String(editId)); if(b){b.nombre=n; b.costo=c; b.stock=st} editId=null; document.getElementById('lblInv').innerText='NUEVO INSUMO'; document.getElementById('btnInv').innerText='+ GUARDAR INSUMO'; document.getElementById('btnCancel').classList.add('hidden');}
else inv.push({id:Date.now().toString(),nombre:n,costo:c,stock:st});
s('pro_inv_v1',inv); document.getElementById('inv-nombre').value=''; document.getElementById('inv-costo').value=''; document.getElementById('inv-stock').value=''; renderInv();
}
function cancelEdit(){editId=null; document.getElementById('inv-nombre').value=''; document.getElementById('inv-costo').value=''; document.getElementById('inv-stock').value=''; document.getElementById('lblInv').innerText='NUEVO INSUMO'; document.getElementById('btnInv').innerText='+ GUARDAR INSUMO'; document.getElementById('btnCancel').classList.add('hidden');}
function editarInv(id){let inv=getInv(); let b=inv.find(x=>String(x.id)==String(id)); if(!b) return; editId=id; document.getElementById('inv-nombre').value=b.nombre; document.getElementById('inv-costo').value=b.costo; document.getElementById('inv-stock').value=b.stock||''; document.getElementById('lblInv').innerText='EDITANDO: '+b.nombre; document.getElementById('btnInv').innerText='ACTUALIZAR'; document.getElementById('btnCancel').classList.remove('hidden'); window.scrollTo({top:0,behavior:'smooth'});}
function delInv(id){if(!confirm('Borrar?')) return; s('pro_inv_v1', getInv().filter(x=>String(x.id)!=String(id))); renderInv();}
function merma(id){let c=prompt('Merma? Ej: 0.5 o 1/2'); if(!c) return; let v=parseCant(c); let inv=getInv(); let b=inv.find(x=>String(x.id)==String(id)); if(b){b.stock=Math.max(0,(b.stock||0)-v); s('pro_inv_v1',inv); renderInv();}}
function renderInv(){let inv=getInv(); document.getElementById('contInv').innerHTML=inv.length? inv.map(b=>`<div class="bg-white border-2 border-black rounded-xl p-2 flex justify-between items-center"><div><p class="font-black text-[13px]">${b.nombre}</p><p class="text-[10px] opacity-60">Stock:${b.stock} | $${(b.costo||0).toFixed(2)}</p></div><div class="flex gap-1"><button onclick="editarInv('${b.id}')" class="bg-yellow-300 border-2 border-black w-8 h-8 rounded-lg">✏️</button><button onclick="merma('${b.id}')" class="bg-orange-200 border-2 border-black w-8 h-8 rounded-lg text-[10px] font-black">M</button><button onclick="delInv('${b.id}')" class="bg-red-100 border-2 border-black w-8 h-8 rounded-lg">🗑️</button></div></div>`).join(''):'<p class="text-center opacity-30 text-[11px] mt-10">Sin insumos</p>'}

function addBase(d={}){
let inv=getInv(); let prod=getProd().filter(p=>p.esBase);
let lista=[...inv.map(i=>({id:'inv_'+i.id,nombre:i.nombre+' (Insumo)',costo:i.costo,stock:i.stock})),...prod];
if(!lista.length){alert('Primero crea un insumo'); return;}
let opts=lista.map(b=>`<option value="${b.id}" ${String(d.baseId||d.id)==String(b.id)?'selected':''}>${b.nombre} $${(b.costo||0).toFixed(2)}</option>`).join('');
let div=document.createElement('div'); div.className='bg-white border-2 border-black rounded-xl p-2 flex gap-1 items-center flex-wrap mb-2';
div.innerHTML=`<select class="b-sel flex-1 border-2 p-1 rounded font-bold text-[11px] min-w-[110px]" onchange="calc2()"><option value="">-- Base --</option>${opts}</select><input class="b-cant w-[60px] border-2 border-black p-1 rounded text-center font-black text-[11px]" value="${d.cant||'0.2'}" oninput="calc2()"><select class="b-unit w-[50px] border-2 p-1 rounded font-bold text-[10px]" onchange="calc2()"><option value="L">L</option><option value="ml">ml</option><option value="kg" selected>kg</option><option value="g">g</option><option value="pza">pza</option></select><button onclick="this.parentElement.remove();calc2()" class="text-red-500 font-black px-1">X</button>`;
document.getElementById('basesSel').appendChild(div); calc2();
}
function calc2(){
let tot=0;
document.querySelectorAll('#basesSel > div').forEach(r=>{
let id=r.querySelector('.b-sel')?.value; if(!id) return;
let cant=parseCant(r.querySelector('.b-cant')?.value||'1'); let unit=r.querySelector('.b-unit')?.value||'kg';
let inv=getInv(); let prod=getProd();
let b=prod.find(x=>String(x.id)==String(id)) || inv.find(x=>String('inv_'+x.id)==String(id));
if(!b) return;
let costoUnit=(parseFloat(b.costo)||0)/Math.max(0.0001, parseFloat(b.stock||1)||1);
tot+=costoUnit*conv(cant, unit, 'kg');
});
document.getElementById('c-ing2').innerText=tot.toFixed(2);
let m=parseFloat(document.getElementById('margen2').value)||0; let vm=document.getElementById('ventaManual2').value;
document.getElementById('v2').innerText= vm? parseFloat(vm).toFixed(2) : (tot*(1+m/100)).toFixed(2);
}
function guardarProd(tipo){
let n=document.getElementById('nombre2').value.trim(); if(!n) return alert('Nombre');
let receta=[]; document.querySelectorAll('#basesSel > div').forEach(r=>{let id=r.querySelector('.b-sel')?.value; if(id) receta.push({id:id,baseId:id,cant:r.querySelector('.b-cant').value||'0.2',unit:r.querySelector('.b-unit').value||'kg'})});
let prods=getProd(); prods.push({id:Date.now().toString(),nombre:n,categoria:document.getElementById('cat2').value,esBase:tipo=='base',bases:receta,foto:document.getElementById('foto2').value||''}); s('pro_prod_v1',prods); alert('Guardado '+n); document.getElementById('nombre2').value=''; document.getElementById('basesSel').innerHTML=''; calc2(); renderCat();
}
function renderCat(){let prods=getProd(); document.getElementById('contCat').innerHTML=prods.map(p=>`<div class="border-2 border-black rounded-xl p-2 bg-white"><p class="font-black text-[11px]">${p.nombre} ${p.esBase?'(BASE)':''}</p><p class="text-[9px] opacity-60">${(p.bases||[]).map(b=>b.cant+b.unit).join(', ')||'Sin receta'}</p></div>`).join('')||'<p class="opacity-30 text-[11px]">Sin productos</p>'}
function renderFin(){let prods=getProd(); document.getElementById('f-lista').innerHTML=prods.length+' productos guardados';}
function addCli(){let n=document.getElementById('cli-n').value.trim(); if(!n) return; let c=g('clientes',[]); c.push({id:Date.now(),nombre:n}); s('clientes',c); renderCli();}
function renderCli(){let c=g('clientes',[]); document.getElementById('contCli').innerHTML=c.map(x=>`<div class="border p-2 rounded mt-1 text-[11px]">${x.nombre}</div>`).join('')}
function addProv(){let n=document.getElementById('prov-n').value.trim(); if(!n) return; let c=g('provs',[]); c.push({id:Date.now(),nombre:n}); s('provs',c); renderProv();}
function renderProv(){let c=g('provs',[]); document.getElementById('contProv').innerHTML=c.map(x=>`<div class="border p-2 rounded mt-1 text-[11px]">${x.nombre}</div>`).join('')}
renderInv();
</script>
</body></html>
'''

@app.route('/')
def index():
    return HTML

@app.route('/<path:path>')
def catch_all(path):
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
