from flask import Flask
app = Flask(__name__)

HTML = r'''
<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 11.5 Fix</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{background:#fdf6f0}
.bg-snoopy{background-image:url('https://i.imgur.com/8Km9tLL.png');background-size:cover;background-position:center;opacity:0.15;position:fixed;inset:0;z-index:0}
</style>
</head><body class="relative">
<div class="bg-snoopy"></div>
<div class="relative z-10 max-w-[440px] mx-auto min-h-screen bg-white/90 border-x-2 border-black flex flex-col">
<!-- HEADER -->
<div class="bg-white border-b-2 border-black p-3 flex items-center gap-3">
<img src="https://i.imgur.com/Q3a6n1H.png" class="w-16 h-16 rounded-full border-2 border-black object-cover">
<div class="flex-1"><p class="font-black text-[18px]">Mi Negocio 11.5</p><p class="text-[11px] opacity-60">esaul_1987@hotmail.com</p><p class="text-[11px] text-green-600 font-bold">10/09/2026, 12:32:49 p.m.</p></div>
<button class="bg-black text-white px-4 py-2 rounded-full text-[12px] font-bold">Config</button><button class="bg-red-100 text-red-600 px-3 py-2 rounded-full text-[12px] font-bold ml-1">Salir</button>
</div>

<div class="p-3">
<div class="bg-black text-white rounded-full p-4 flex items-center gap-2 font-black text-[18px]"><span>📦</span> Inventario</div>
<div class="bg-white border-2 border-black rounded-[20px] p-3 mt-3 shadow-[4px_4px_0px_#000]">
<div class="flex gap-2">
<input id="inv-nombre" placeholder="Papas" class="flex-1 border-2 border-black rounded-full px-3 py-2 text-[14px] font-bold">
<input id="inv-costo" placeholder="$30" class="w-[70px] border-2 border-black rounded-full px-2 py-2 text-[14px] font-bold text-center">
<input id="inv-stock" placeholder="500 g" class="w-[90px] border-2 border-black rounded-full px-2 py-2 text-[14px] font-bold text-center">
<select id="inv-cat" class="w-[55px] border-2 border-black rounded-full px-1 py-2 text-[12px]"><option>Otros</option><option>Papas</option><option>Proteina</option><option>Salsas</option><option>Bebidas</option></select>
<button onclick="agregarInventario()" class="bg-black text-white w-12 h-12 rounded-full font-black text-[20px]">+</button>
</div>
<div class="mt-3 bg-white border-2 border-yellow-400 rounded-full p-2 flex items-center gap-2">
<span class="pl-2">🔍</span><input id="buscInv" oninput="renderInventario()" placeholder="Buscar producto..." class="flex-1 outline-none text-[14px]"><button onclick="document.getElementById('buscInv').value='';renderInventario()" class="border-2 border-black rounded-full w-8 h-8 font-black">X</button>
</div>
</div>

<div id="listaInventario" class="mt-4 flex flex-col gap-2"></div>

<div class="mt-6 border-2 border-black rounded-xl p-3 bg-yellow-50">
<p class="font-black text-[12px] mb-2">CREAR PRODUCTO - RECETA CON FRACCION (0.2L)</p>
<input id="nombre2" placeholder="Ej: Burger BBQ" class="w-full border-2 border-black p-2 rounded-lg font-bold text-[12px] mb-2">
<div class="flex gap-1 mb-2"><select id="cat2" class="border-2 border-black p-2 rounded text-[10px] font-bold"><option>Hamburguesas</option><option>Papas</option><option>Salsas/Bases</option></select><input id="margen2" type="number" value="30" class="w-[60px] border-2 border-black p-2 rounded text-[10px]"><input id="ventaManual2" placeholder="Venta $" class="flex-1 border-2 border-black p-2 rounded text-[10px]" oninput="calc2()"></div>
<div class="bg-white border-2 border-dashed border-black rounded-lg p-2 mb-2"><div class="flex justify-between mb-1"><b class="text-[10px]">BASES - cuanto usas</b><button onclick="addBase({})" class="bg-black text-white px-2 py-1 rounded text-[10px]">+ BASE</button></div><div id="basesSel"></div><div class="flex justify-between font-black text-[11px] mt-2 border-t-2 border-black pt-1"><span>Costo: $<span id="c-ing2">0.00</span></span><span>Venta: $<span id="v2">0.00</span></span></div></div>
<div class="flex gap-2"><button onclick="guardarProd('normal')" class="flex-1 bg-black text-white py-2 rounded-lg font-black text-[11px]">GUARDAR PRODUCTO</button><button onclick="guardarProd('base')" class="flex-1 bg-yellow-300 border-2 border-black py-2 rounded-lg font-black text-[11px]">GUARDAR BASE</button></div>
</div>
</div>
</div>

<!-- BOTTOM NAV -->
<div class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[440px] bg-white border-t-2 border-black flex justify-around py-2 z-50">
<button class="flex flex-col items-center text-[10px] font-black"><span>📄</span>Crear</button>
<button class="flex flex-col items-center text-[10px] opacity-40"><span>🏪</span>Catalogo</button>
<button class="flex flex-col items-center text-[10px] opacity-40"><span>📦</span>Invent</button>
<button class="flex flex-col items-center text-[10px] opacity-40"><span>📈</span>Finanzas</button>
<button class="flex flex-col items-center text-[10px] opacity-40"><span>👥</span>Clientes</button>
<button class="flex flex-col items-center text-[10px] opacity-40"><span>🚚</span>Prov</button>
</div>
</div>

<script>
let editId=null;
function g(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}} function s(k,v){localStorage.setItem(k,JSON.stringify(v))}
function getInv(){let a=g('pro_inv_v1',[]); if(!a.length){let o=g('inv',[]); if(o.length) a=o; s('pro_inv_v1',a)} return a}
function getProd(){return g('pro_prod_v1',[])}
function parseCant(v){v=String(v||'').trim().replace(',','.'); if(!v) return 0; if(v.includes('/')){let p=v.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1)} return parseFloat(v)||0}
function conv(c,de,a){de=(de||'kg').toLowerCase(); a=(a||'kg').toLowerCase(); if(de==a) return c; let m={g:1,kg:1000,mg:0.001,ml:1,l:1000,lt:1000,pza:1}; if(m[de]!=null&&m[a]!=null) return c*m[de]/m[a]; return c}

function agregarInventario(){
 let nEl=document.getElementById('inv-nombre');
 let cEl=document.getElementById('inv-costo');
 let sEl=document.getElementById('inv-stock');
 let catEl=document.getElementById('inv-cat');
 let nombre=(nEl?.value||'').trim(); if(!nombre) return alert('Pon nombre Ej: Papas');
 let cTxt=String(cEl?.value||'0').replace(/[^0-9.,\/\-]/g,'').replace(',','.'); let sTxt=String(sEl?.value||'0').replace(/[^0-9.,\/\-]/g,'').replace(',','.');
 let costo=0; if(cTxt.includes('/')){let p=cTxt.split('/'); costo=(parseFloat(p[0])||0)/(parseFloat(p[1])||1)} else costo=parseFloat(cTxt)||0;
 let stock=0; if(sTxt.includes('/')){let p=sTxt.split('/'); stock=(parseFloat(p[0])||0)/(parseFloat(p[1])||1)} else stock=parseFloat(sTxt)||0;
 if(stock<=0) stock=1;
 let inv=getInv();
 if(editId){let b=inv.find(x=>String(x.id)==String(editId)); if(b){b.nombre=nombre; b.costo=costo; b.stock=stock; b.categoria=catEl?.value||'Otros'} editId=null; document.querySelector('button[onclick="agregarInventario()"]').innerText='+';}
 else inv.push({id:Date.now().toString(), nombre:nombre, costo:costo, stock:stock, categoria:catEl?.value||'Otros'});
 s('pro_inv_v1',inv); s('inv',inv);
 if(nEl) nEl.value=''; if(cEl) cEl.value=''; if(sEl) sEl.value='';
 renderInventario();
}
function editarInv(id){let inv=getInv(); let b=inv.find(x=>String(x.id)==String(id)); if(!b) return; editId=id; document.getElementById('inv-nombre').value=b.nombre; document.getElementById('inv-costo').value=b.costo; document.getElementById('inv-stock').value=b.stock; document.querySelector('button[onclick="agregarInventario()"]').innerText='✓'; window.scrollTo({top:0,behavior:'smooth'});}
function borrarInv(id){if(!confirm('Borrar?')) return; s('pro_inv_v1', getInv().filter(x=>String(x.id)!=String(id))); renderInventario();}
function mermaInv(id){let c=prompt('Cuanto de merma? Ej: 0.5 o 1/2'); if(!c) return; let v=parseCant(c); let inv=getInv(); let b=inv.find(x=>String(x.id)==String(id)); if(b){b.stock=Math.max(0,(b.stock||0)-v); s('pro_inv_v1',inv); s('inv',inv); renderInventario();}}
function renderInventario(){
 let q=(document.getElementById('buscInv')?.value||'').toLowerCase();
 let inv=getInv().filter(i=>i.nombre.toLowerCase().includes(q));
 document.getElementById('listaInventario').innerHTML=inv.length? inv.map(i=>`<div class="bg-white border-2 border-black rounded-xl p-2 flex justify-between items-center shadow-[2px_2px_0px_#000]"><div><p class="font-black text-[13px]">${i.nombre}</p><p class="text-[10px] opacity-60">Stock: ${i.stock} | $${(i.costo||0).toFixed(2)} | ${i.categoria||''}</p></div><div class="flex gap-1"><button onclick="editarInv('${i.id}')" class="bg-yellow-300 border-2 border-black w-8 h-8 rounded-lg">✏️</button><button onclick="mermaInv('${i.id}')" class="bg-orange-200 border-2 border-black w-8 h-8 rounded-full text-[10px] font-black">M</button><button onclick="borrarInv('${i.id}')" class="bg-white border-2 border-black w-8 h-8 rounded-full">X</button></div></div>`).join(''):'<p class="text-center opacity-30 text-[12px] mt-10">Sin productos. Escribe Papas 30 500 y dale +</p>';
}
function addBase(d={}){
 let inv=getInv(); let bases=getProd().filter(p=>p.esBase);
 let lista=[...inv.map(i=>({id:'inv_'+i.id,nombre:i.nombre+' (Insumo)',costo:i.costo,stock:i.stock})),...bases];
 if(!lista.length){alert('Primero agrega un insumo'); return;}
 let opts=lista.map(b=>`<option value="${b.id}" ${String(d.baseId||d.id)==String(b.id)?'selected':''}>${b.nombre} $${(b.costo||0).toFixed(2)}</option>`).join('');
 let div=document.createElement('div'); div.className='bg-white border-2 border-black rounded-xl p-2 flex gap-1 items-center flex-wrap mb-2';
 div.innerHTML=`<select class="b-sel flex-1 border-2 p-1 rounded font-bold text-[11px] min-w-[100px]" onchange="calc2()"><option value="">-- Base --</option>${opts}</select><input class="b-cant w-[60px] border-2 border-black p-1 rounded text-center font-black text-[11px]" value="${d.cant||'0.2'}" oninput="calc2()"><select class="b-unit w-[55px] border-2 p-1 rounded font-bold text-[10px]" onchange="calc2()"><option value="kg">kg</option><option value="g">g</option><option value="L" selected>L</option><option value="ml">ml</option><option value="pza">pza</option></select><button onclick="this.parentElement.remove();calc2()" class="text-red-500 font-black">X</button>`;
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
  tot+=costoUnit*conv(cant,unit,'kg');
 });
 document.getElementById('c-ing2').innerText=tot.toFixed(2);
 let m=parseFloat(document.getElementById('margen2').value)||0; let vm=document.getElementById('ventaManual2').value;
 document.getElementById('v2').innerText= vm? parseFloat(vm).toFixed(2) : (tot*(1+m/100)).toFixed(2);
}
function guardarProd(tipo){
 let n=document.getElementById('nombre2').value.trim(); if(!n) return alert('Pon nombre producto');
 let receta=[]; document.querySelectorAll('#basesSel > div').forEach(r=>{let id=r.querySelector('.b-sel')?.value; if(id) receta.push({id:id,baseId:id,cant:r.querySelector('.b-cant').value||'0.2',unit:r.querySelector('.b-unit').value||'L'})});
 let prods=getProd(); prods.push({id:Date.now().toString(),nombre:n,categoria:document.getElementById('cat2').value,esBase:tipo=='base',bases:receta}); s('pro_prod_v1',prods); alert('Guardado '+n+' con '+(receta.length?'0.2L':'sin receta')); document.getElementById('nombre2').value=''; document.getElementById('basesSel').innerHTML=''; calc2();
}
renderInventario();
</script>
</body></html>
'''

@app.route('/')
def index(): return HTML
@app.route('/<path:path>')
def catch_all(path): return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
