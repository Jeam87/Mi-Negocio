<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 11.5 - Completo con Gramos</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#f6f5f0] p-2">
<div class="max-w-[700px] mx-auto space-y-3" id="app"></div>
<script>
let prods = JSON.parse(localStorage.getItem('prods11')||'[]');
function getProd(){return prods;}
function save(){localStorage.setItem('prods11', JSON.stringify(prods));}
function normalizarUnidad(u){
 u=(u||'').toString().toLowerCase().trim();
 const map={g:['g','gr','gramo'],kg:['kg','kilo'],lb:['lb','libra'],oz:['oz','onza'],ml:['ml'],L:['l','lt','litro','L'],gal:['gal','galon'],m:['m','metro'],cm:['cm'],pza:['pz','pza','pieza']};
 for(let k in map){ if(map[k].includes(u)||k===u) return k; }
 return u||'g';
}
function factorABase(u){
 u=normalizarUnidad(u);
 let f={g:1,kg:1000,lb:453.592,oz:28.3495,ml:1,L:1000,gal:3785.41,m:100,cm:1,pza:1};
 return f[u]||1;
}
function convertir(cant,de,a){
 de=normalizarUnidad(de); a=normalizarUnidad(a);
 if(de===a) return cant;
 let peso=['g','kg','lb','oz'], vol=['ml','L','gal'], long=['mm','cm','m'];
 if(peso.includes(de)&&peso.includes(a)) return cant*factorABase(de)/factorABase(a);
 if(vol.includes(de)&&vol.includes(a)) return cant*factorABase(de)/factorABase(a);
 if(long.includes(de)&&long.includes(a)) return cant*factorABase(de)/factorABase(a);
 if(a==='pza'||de==='pza') return cant;
 return cant;
}
function parseCant(v){
 if(v==null||v==='') return 0;
 v=String(v).trim().replace(',','.').toLowerCase();
 if(v.includes('/')){ let p=v.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1); }
 return parseFloat(v)||0;
}
function calcBase(){
 let costo=0;
 document.querySelectorAll('#ingSel>div').forEach(r=>{
   let c=parseCant(r.querySelector('.i-cant')?.value);
   let pu=parseFloat(r.querySelector('.i-precio')?.dataset.precio||0);
   if(c>0) costo+=c*pu;
 });
 document.getElementById('costoBase').innerText=costo.toFixed(2);
 let rend=parseCant(document.getElementById('rendCant')?.value)||1;
 document.getElementById('costoPorRend').innerText=(rend>0?costo/rend:0).toFixed(4);
}
function addIng(){
 let div=document.createElement('div');
 div.className='flex gap-2 items-center bg-white p-2 rounded-xl border-2 border-black mb-2';
 div.innerHTML=`<input class="i-nombre flex-1 border-2 border-black rounded-xl p-2" placeholder="Ingrediente"><input class="i-cant w-[80px] border-2 border-black rounded-xl p-2" value="1" oninput="calcBase()"><select class="i-unit w-[70px] border-2 border-black rounded-xl p-2"><option>g</option><option>kg</option><option>ml</option><option>L</option><option>pza</option></select><input class="i-precio w-[80px] border-2 border-black rounded-xl p-2" placeholder="$/u" data-precio="0" oninput="this.dataset.precio=this.value;calcBase()"><button onclick="this.parentElement.remove();calcBase()" class="text-red-600 font-black">X</button>`;
 document.getElementById('ingSel').appendChild(div);
}
function guardarBase(){
 let nombre=document.getElementById('nombreBase')?.value.trim();
 if(!nombre) return alert('Nombre base');
 let costo=parseFloat(document.getElementById('costoBase').innerText)||0;
 let rendCant=parseCant(document.getElementById('rendCant').value)||1;
 let rendUnit=document.getElementById('rendUnit').value||'g';
 prods.push({id:Date.now().toString(),nombre:nombre,tipo:'base',costo:costo,rendimiento:{cant:rendCant,unit:rendUnit},venta:costo});
 save(); render();
}
function addBase(){
 let bases=getProd().filter(x=>x.tipo==='base');
 if(bases.length===0){ alert('Primero crea una base'); return; }
 let opts=bases.map(b=>`<option value="${b.id}">${b.nombre} - $${(b.costo||0).toFixed(2)} - rinde ${b.rendimiento?.cant||1} ${b.rendimiento?.unit||'g'}</option>`).join('');
 let div=document.createElement('div');
 div.className='flex gap-2 items-center flex-wrap bg-yellow-50 p-2 rounded-xl border-2 border-black mb-2';
 div.innerHTML=`
  <select class="b-sel flex-1 min-w-[140px] border-2 border-black rounded-xl p-2" onchange="calc2()">
   <option value="">-- Elige receta --</option>${opts}
  </select>
  <input class="b-cant w-[90px] border-2 border-black rounded-xl p-2" value="200" placeholder="1/2" oninput="calc2()">
  <select class="b-unit w-[90px] border-2 border-black rounded-xl p-2" onchange="calc2()">
   <option value="g">g</option><option value="kg">kg</option><option value="lb">lb</option><option value="oz">oz</option><option value="ml">ml</option><option value="L">L</option><option value="pza">pza</option>
  </select>
  <button onclick="this.parentElement.remove();calc2()" class="text-red-600 font-black text-xl">X</button>
 `;
 document.getElementById('basesSel').appendChild(div);
 calc2();
}
function calc2(){
 let tot=0;
 document.querySelectorAll('#basesSel>div').forEach(row=>{
  let id=row.querySelector('.b-sel')?.value;
  if(!id) return;
  let cantUsada=parseCant(row.querySelector('.b-cant')?.value);
  let unitUsada=row.querySelector('.b-unit')?.value||'g';
  let b=getProd().find(x=>String(x.id)===String(id));
  if(!b) return;
  let rindeCant=parseCant(b.rendimiento?.cant)||1;
  let rindeUnit=normalizarUnidad(b.rendimiento?.unit||'g');
  let cantConvertida=convertir(cantUsada,unitUsada,rindeUnit);
  if(rindeCant>0) tot+=(b.costo/rindeCant)*cantConvertida;
 });
 document.getElementById('c-ing2').innerText=tot.toFixed(2);
 let margen=parseFloat(document.getElementById('margen2')?.value)||0;
 let vm=document.getElementById('ventaManual2')?.value||'';
 let venta=vm!==''?parseCant(vm):tot*(1+margen/100);
 document.getElementById('venta2').innerText=venta.toFixed(2);
}
function guardarProd(){
 let nombre=document.getElementById('nombre2')?.value.trim();
 let cat=document.getElementById('categoria2')?.value||'General';
 if(!nombre) return alert('Pon nombre');
 let bases=[];
 document.querySelectorAll('#basesSel>div').forEach(row=>{
  let id=row.querySelector('.b-sel')?.value;
  let cant=row.querySelector('.b-cant')?.value||0;
  let unit=row.querySelector('.b-unit')?.value||'g';
  if(id) bases.push({id:id,cant:cant,unit:unit});
 });
 if(bases.length===0) return alert('Agrega 1 receta');
 let costo=parseFloat(document.getElementById('c-ing2')?.innerText)||0;
 let venta=parseFloat(document.getElementById('venta2')?.innerText)||0;
 prods.push({id:Date.now().toString(),nombre:nombre,tipo:'secundario',categoria:cat,costo:costo,venta:venta,bases:bases,rendimiento:{cant:1,unit:'pza'}});
 save(); render();
}
function render(){
 let bases=getProd().filter(x=>x.tipo==='base');
 let sec=getProd().filter(x=>x.tipo==='secundario');
 document.getElementById('app').innerHTML=`
 <div class="bg-white border-[3px] border-black rounded-[20px] p-3 shadow-[4px_4px_0_#000]">
  <h2 class="font-black">1) Crear Base / Receta</h2>
  <input id="nombreBase" placeholder="Ej: Salsa BBQ" class="w-full mt-2 border-2 border-black rounded-xl p-3">
  <div id="ingSel" class="mt-2"></div>
  <button onclick="addIng()" class="w-full mt-2 border-2 border-black rounded-xl p-2 font-black">+ Ingrediente</button>
  <div class="flex gap-2 mt-2"><input id="rendCant" value="1" oninput="calcBase()" class="w-[80px] border-2 border-black rounded-xl p-2"><select id="rendUnit" onchange="calcBase()" class="w-[80px] border-2 border-black rounded-xl p-2"><option value="kg">kg</option><option value="g">g</option><option value="L">L</option><option value="ml">ml</option><option value="pza">pza</option></select><div class="flex-1 bg-black text-white rounded-xl p-2">Costo: $<span id="costoBase">0</span> | $/u: $<span id="costoPorRend">0</span></div></div>
  <button onclick="guardarBase()" class="w-full mt-2 bg-black text-white rounded-xl p-3 font-black">GUARDAR BASE</button>
  <div class="text-xs mt-2">${bases.map(b=>b.nombre+' $'+b.costo.toFixed(2)+' rinde '+b.rendimiento.cant+' '+b.rendimiento.unit).join('<br>')||'Sin bases'}</div>
 </div>
 <div class="bg-white border-[3px] border-black rounded-[20px] p-3 shadow-[4px_4px_0_#000]">
  <h2 class="font-black">2) Crear Producto + Categoría (con gramos)</h2>
  <div class="flex gap-2 mt-2"><input id="nombre2" placeholder="Ej: Alitas 10 pzas" class="flex-1 border-2 border-black rounded-xl p-3"><select id="categoria2" class="w-[120px] border-2 border-black rounded-xl p-3"><option>Alitas</option><option>Burgers</option><option>Boneless</option><option>Bebidas</option><option>General</option></select></div>
  <div class="font-bold mt-3">Recetas que lleva:</div>
  <div id="basesSel" class="mt-2"></div>
  <button onclick="addBase()" class="w-full mt-2 bg-yellow-300 border-2 border-black rounded-xl p-3 font-black">+ AGREGAR RECETA</button>
  <div class="bg-black text-white rounded-2xl p-4 mt-3">
   <div class="flex justify-between"><span>Costo:</span><b>$<span id="c-ing2">0.00</span></b></div>
   <div class="flex justify-between text-yellow-300"><span>Venta:</span><b>$<span id="venta2">0.00</span></b></div>
   <div class="flex gap-2 mt-3"><input id="margen2" value="100" type="number" oninput="calc2()" class="w-[70px] text-black rounded-xl p-2">%<input id="ventaManual2" placeholder="$ manual" oninput="calc2()" class="flex-1 text-black rounded-xl p-2"></div>
  </div>
  <button onclick="guardarProd()" class="w-full mt-3 p-4 bg-black text-white rounded-2xl font-black">GUARDAR PRODUCTO</button>
  <div class="text-xs mt-3">${sec.map(p=>p.nombre+' ['+p.categoria+'] $'+p.costo.toFixed(2)).join('<br>')||'Sin productos'}</div>
 </div>`;
 calc2();
}
render();
</script>
</body>
</html> 
