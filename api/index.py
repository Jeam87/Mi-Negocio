<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{background:#FEF8EF;font-family:system-ui}.card{border:2px solid #000;border-radius:20px}.tab-active{font-weight:900;opacity:1!important;border-bottom:3px solid #000}</style>
</head>
<body class="pb-[95px]">
<div id="app" class="max-w-[500px] mx-auto p-3"></div>
<nav class="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-black flex justify-around py-2 max-w-[500px] mx-auto z-50">
 <button onclick="setTab('crear')" id="t-crear" class="tab-active flex flex-col items-center opacity-40"><span>📝</span><span class="text-[11px]">Crear</span></button>
 <button onclick="setTab('catalogo')" id="t-catalogo" class="flex flex-col items-center opacity-40"><span>🏪</span><span class="text-[11px]">Catalogo</span></button>
 <button onclick="setTab('invent')" id="t-invent" class="flex flex-col items-center opacity-40"><span>📦</span><span class="text-[11px]">Invent</span></button>
 <button onclick="setTab('finanzas')" id="t-finanzas" class="flex flex-col items-center opacity-40"><span>📈</span><span class="text-[11px]">Finanzas</span></button>
 <button onclick="setTab('clientes')" id="t-clientes" class="flex flex-col items-center opacity-40"><span>👥</span><span class="text-[11px]">Clientes</span></button>
</nav>

<script>
let prods; try{prods=JSON.parse(localStorage.getItem('prods11')||'[]')}catch(e){prods=[]}
let cats; try{cats=JSON.parse(localStorage.getItem('cats11')||'["Todas","Alitas","Boneless","Burgers","Papas","Salsas"]')}catch(e){cats=["Todas","Alitas","Boneless","Burgers","Papas","Salsas"]}
let tab='crear'; let editBaseId=null; let editProdId=null;

function save(){localStorage.setItem('prods11',JSON.stringify(prods)); localStorage.setItem('cats11',JSON.stringify(cats));}
function getProd(){return prods}
function parseCant(v){ v=String(v||'').trim().replace(',','.').toLowerCase(); if(v.includes('/')){let p=v.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1);} return parseFloat(v)||0; }
function convertir(c,de,a){ de=(de||'l').toLowerCase(); a=(a||'l').toLowerCase(); if(de==a) return c; let m={g:1,kg:1000,lb:453.592,oz:28.3495,mg:0.001,ml:1,l:1000,lt:1000,cl:10,pza:1}; if(m[de]!=null&&m[a]!=null) return c*m[de]/m[a]; return c; }

function setTab(t){ tab=t; render(); }

function calc2(){
 let tot=0;
 document.querySelectorAll('#basesSel > div').forEach(row=>{
  let sel=row.querySelector('.b-sel'); if(!sel||!sel.value) return;
  let b=getProd().find(x=>String(x.id)==String(sel.value)); if(!b) return;
  let cant=parseCant(row.querySelector('.b-cant').value||'0');
  let rCant=parseCant(b.rendimiento?.cant||1)||1;
  let rUnit=(b.rendimiento?.unit||'L'); let uUsada=row.querySelector('.b-unit').value||rUnit;
  let cantConv=convertir(cant,uUsada,rUnit);
  let costo=parseFloat(b.costo)||0;
  if(rCant>0) tot+=(costo/rCant)*cantConv;
 });
 document.getElementById('costoTxt').innerText='$'+tot.toFixed(2);
 document.getElementById('c-ing2').innerText=tot.toFixed(2);
 let margen=parseFloat(document.getElementById('margenInput').value)||100;
 let venta=tot*(1+margen/100);
 let f=document.getElementById('finalInput').value; if(f!==''){let mv=parseCant(f); if(mv>0) venta=mv;}
 document.getElementById('ventaTxt').innerText='$'+venta.toFixed(2);
}

function addBaseRow(d){
 d=d||{}; let bases=getProd().filter(x=>x.tipo==='base'||x.esBase);
 if(!bases.length){alert('Ve a Inventario y crea tu Salsa o Papas primero'); setTab('invent'); return;}
 let opts=bases.map(b=>`<option value="${b.id}" ${String(d.id)==String(b.id)?'selected':''}>${b.nombre} $${(b.costo||0).toFixed(2)} rinde ${b.rendimiento.cant}${b.rendimiento.unit}</option>`).join('');
 let div=document.createElement('div'); div.className='bg-white border-2 border-black rounded-[16px] p-2 flex gap-2 items-center mb-2';
 div.innerHTML=`<select class="b-sel flex-1 border-2 border-black rounded-xl p-3 font-bold bg-white" onchange="calc2()"><option value="">-- Elige Salsa / Papa / Base --</option>${opts}</select>
 <input class="b-cant w-[75px] border-2 border-black rounded-xl p-3 text-center font-black" value="${d.cant||'0.2'}" oninput="calc2()" placeholder="0.2">
 <select class="b-unit w-[60px] border-2 border-black rounded-xl p-2 font-bold" onchange="calc2()"><option value="L">L</option><option value="ml">ml</option><option value="kg">kg</option><option value="g">g</option><option value="pza">pza</option></select>
 <button onclick="this.parentElement.remove();calc2()" class="text-red-500 font-black px-2">X</button>
 <div class="text-[10px] opacity-60 w-full hidden">Tip: puedes poner 1/4, 0.5, 150</div>`;
 document.getElementById('basesSel').appendChild(div); calc2();
}

// INVENTARIO
function guardarBase(){
 let nombre=document.getElementById('ib-nombre').value.trim(); if(!nombre) return alert('Nombre');
 let costo=parseCant(document.getElementById('ib-costo').value);
 let rCant=parseCant(document.getElementById('ib-rinde-cant').value)||10;
 let rUnit=document.getElementById('ib-rinde-unit').value||'L';
 let stock=parseCant(document.getElementById('ib-stock').value)||0;
 let cat=document.getElementById('ib-cat').value||'Salsas';
 if(editBaseId){
  let b=prods.find(x=>x.id==editBaseId); b.nombre=nombre; b.costo=costo; b.rendimiento={cant:rCant,unit:rUnit}; b.stock=stock; b.categoria=cat;
  editBaseId=null;
 }else{
  prods.push({id:Date.now().toString(),nombre:nombre,categoria:cat,tipo:'base',esBase:true,costo:costo,venta:costo,stock:stock,rendimiento:{cant:rCant,unit:rUnit},bases:[]});
 }
 save(); render(); alert('Inventario guardado. Ahora puedes usar 0.2L, 150g etc.');
}
function editarBase(id){
 let b=prods.find(x=>x.id==id); if(!b) return;
 editBaseId=id; setTab('invent');
 setTimeout(()=>{
  document.getElementById('ib-nombre').value=b.nombre;
  document.getElementById('ib-costo').value=b.costo;
  document.getElementById('ib-rinde-cant').value=b.rendimiento.cant;
  document.getElementById('ib-rinde-unit').value=b.rendimiento.unit;
  document.getElementById('ib-stock').value=b.stock||0;
  document.getElementById('ib-cat').value=b.categoria||'Salsas';
 },100);
}
function borrarBase(id){ if(!confirm('Borrar base?')) return; prods=prods.filter(x=>x.id!=id); save(); render(); }

function guardarProdFinal(){
 let nombre=document.getElementById('nombreProd').value.trim(); if(!nombre) return alert('Nombre');
 let lista=[]; document.querySelectorAll('#basesSel > div').forEach(r=>{
  let id=r.querySelector('.b-sel').value; let cant=r.querySelector('.b-cant').value; let unit=r.querySelector('.b-unit').value;
  if(id) lista.push({id:id,cant:cant,unit:unit});
 });
 if(!lista.length) return alert('Agrega al menos una base (ej: 0.2L salsa)');
 let costo=parseFloat((document.getElementById('costoTxt').innerText||'0').replace('$',''))||0;
 let venta=parseFloat((document.getElementById('ventaTxt').innerText||'0').replace('$',''))||0;
 let cat=document.getElementById('catSelect').value||'Todas';
 if(editProdId){
  let p=prods.find(x=>x.id==editProdId); p.nombre=nombre; p.categoria=cat; p.costo=costo; p.venta=venta; p.bases=lista; editProdId=null;
 }else{
  prods.push({id:Date.now().toString(),nombre:nombre,categoria:cat,tipo:'secundario',costo:costo,venta:venta,bases:lista,rendimiento:{cant:1,unit:'pza'}});
 }
 save(); setTab('catalogo');
}

function editarProd(id){ let p=prods.find(x=>x.id==id); if(!p) return; editProdId=id; setTab('crear'); setTimeout(()=>{ document.getElementById('nombreProd').value=p.nombre; document.getElementById('catSelect').value=p.categoria; document.getElementById('basesSel').innerHTML=''; p.bases.forEach(b=>addBaseRow(b)); calc2(); },100); }

function crearCat(){ let v=document.getElementById('nuevaCat').value.trim(); if(!v) return; if(cats.indexOf(v)===-1) cats.push(v); save(); render(); }

function render(){
 let catsOpt=cats.map(c=>`<option ${c==cats[0]?'selected':''}>${c}</option>`).join('');
 let bases=prods.filter(x=>x.tipo==='base'||x.esBase);
 let secund=prods.filter(x=>!x.esBase&&x.tipo!=='base');

 let html='';
 if(tab==='crear'){
  html+=`<div class="card p-3 bg-[#E8F4FF]"><div class="font-black mb-2">📁 Categoria del producto final</div><select id="catSelect" class="w-full border-2 border-black rounded-[16px] p-4 font-bold bg-white mb-2">${catsOpt}</select><div class="flex gap-2"><input id="nuevaCat" placeholder="Nueva cat" class="flex-1 border-2 border-black rounded-[16px] p-3 bg-white"><button onclick="crearCat()" class="bg-black text-white rounded-[16px] px-6 font-black">Crear</button></div></div>
  <div class="card p-3 bg-[#FFFBE6] mt-3"><div class="font-black mb-1">Bases que lleva (usa solo una parte):</div><div class="text-[11px] mb-2 opacity-70">Ej: Salsa BBQ rinde 10L $284.28 → si pones 0.2L te cobra $5.68. Puedes poner 1/4, 0.5, 150g, 200ml</div><div id="basesSel"></div><button onclick="addBaseRow()" class="w-full border-2 border-black rounded-[16px] p-3 bg-white font-bold mt-2">+ Agregar Salsa / Papa</button></div>
  <div class="card p-4 bg-black text-white mt-3"><div class="flex justify-between text-[18px] mb-1"><span>Costo ingredientes</span><b id="costoTxt">$0.00</b><span id="c-ing2" class="hidden">0</span></div><div class="flex justify-between text-[22px] font-black mb-3"><span>Venta</span><b id="ventaTxt" class="text-[#5CFFC0]">$0.00</b></div><div class="flex gap-2"><div class="bg-white rounded-xl flex items-center px-2"><input id="margenInput" value="100" type="number" oninput="calc2()" class="w-[55px] p-2 font-black text-black text-center outline-none"><span class="font-black text-black">%</span></div><input id="finalInput" placeholder="$ final opcional" oninput="calc2()" class="flex-1 rounded-xl p-3 text-black font-bold"></div></div>
  <input id="nombreProd" placeholder="Nombre ej: Alitas BBQ 10pzs" class="w-full border-2 border-black rounded-[16px] p-4 font-bold bg-white mt-3">
  <button onclick="guardarProdFinal()" class="w-full bg-black text-white rounded-[20px] p-5 font-black text-xl mt-3">${editProdId?'ACTUALIZAR':'GUARDAR'}</button>`;
 }
 if(tab==='invent'){
  html+=`<div class="card p-3 bg-[#E8FFEF]"><div class="font-black text-lg mb-2">📦 ${editBaseId?'Editar':'Nueva'} Base / Insumo</div>
  <input id="ib-nombre" placeholder="Nombre ej: Salsa BBQ, Papas" class="w-full border-2 border-black rounded-[16px] p-3 font-bold mb-2 bg-white">
  <div class="flex gap-2 mb-2"><input id="ib-costo" placeholder="Costo total ej: 284.28" class="flex-1 border-2 border-black rounded-[16px] p-3 font-bold bg-white" type="text"><input id="ib-stock" placeholder="Stock ej: 2" class="w-[90px] border-2 border-black rounded-[16px] p-3 font-bold bg-white" type="text"></div>
  <div class="flex gap-2 mb-2"><input id="ib-rinde-cant" placeholder="Rinde ej: 10" value="10" class="flex-1 border-2 border-black rounded-[16px] p-3 font-bold bg-white"><select id="ib-rinde-unit" class="w-[90px] border-2 border-black rounded-[16px] p-3 font-bold bg-white"><option value="L">L</option><option value="ml">ml</option><option value="kg">kg</option><option value="g">g</option><option value="pza">pza</option></select></div>
  <select id="ib-cat" class="w-full border-2 border-black rounded-[16px] p-3 font-bold bg-white mb-2">${catsOpt}</select>
  <button onclick="guardarBase()" class="w-full bg-black text-white rounded-[16px] p-4 font-black">${editBaseId?'ACTUALIZAR BASE':'GUARDAR BASE'}</button>
  ${editBaseId?'<button onclick="editBaseId=null;render()" class="w-full mt-2 p-2 font-bold">Cancelar edición</button>':''}
  </div>
  <div class="mt-4 space-y-2">${bases.length?bases.map(b=>`<div class="bg-white border-2 border-black rounded-[16px] p-3 flex justify-between items-center"><div><div class="font-black">${b.nombre} <span class="text-[11px] bg-black text-white rounded px-2">${b.categoria}</span></div><div class="text-[12px]">$${(b.costo||0).toFixed(2)} rinde ${b.rendimiento.cant}${b.rendimiento.unit} → $${(b.rendimiento.cant>0?(b.costo/b.rendimiento.cant):0).toFixed(2)}/${b.rendimiento.unit} | Stock: ${b.stock||0}</div></div><div class="flex gap-2"><button onclick="editarBase('${b.id}')" class="border-2 border-black rounded-xl px-3 py-1 font-black bg-yellow-200">Editar</button><button onclick="borrarBase('${b.id}')" class="text-red-500 font-black px-2">X</button></div></div>`).join(''):'<div class="opacity-60 text-center mt-4">No hay bases aún. Crea tu Salsa BBQ aquí.</div>'}</div>`;
 }
 if(tab==='catalogo'){
  html+=`<div class="font-black text-xl mb-2">🏪 Catalogo (${secund.length})</div><div class="space-y-2">${secund.length?secund.map(p=>{
   let detalle=p.bases.map(bb=>{
    let base=prods.find(x=>x.id==bb.id); if(!base) return '';
    return `${base.nombre} ${bb.cant}${bb.unit}`;
   }).join(' + ');
   return `<div class="bg-white border-2 border-black rounded-[16px] p-3"><div class="flex justify-between"><b>${p.nombre}</b><b class="text-green-600">$${(p.venta||0).toFixed(2)}</b></div><div class="text-[11px] opacity-70">Costo $${(p.costo||0).toFixed(2)} | ${detalle} | ${p.categoria}</div><div class="flex gap-2 mt-2"><button onclick="editarProd('${p.id}')" class="border-2 border-black rounded-xl px-3 py-1 text-[12px] font-black bg-yellow-200">Editar</button><button onclick="if(confirm('borrar?')){prods=prods.filter(x=>x.id!='${p.id}'); save(); render();}" class="text-red-500 font-black text-[12px]">Borrar</button></div></div>`;
  }).join(''):'<div class="opacity-60">Aún no creas productos</div>'}</div>`;
 }
 if(tab==='finanzas'){ let total=prods.reduce((a,b)=>a+(b.stock||0)*(b.costo||0),0); html+=`<div class="card p-4"><div class="font-black">Finanzas</div><div>Valor inventario: $${total.toFixed(2)}</div></div>`; }
 if(tab==='clientes'){ html+=`<div class="card p-4"><div class="font-black">Clientes</div><div class="opacity-60">Próximamente</div></div>`; }
 document.getElementById('app').innerHTML=html;
 if(tab==='crear') calc2();
 document.querySelectorAll('nav button').forEach(b=>b.classList.remove('tab-active')); document.getElementById('t-'+tab).classList.add('tab-active');
}
render();
</script>
</body>
</html>
