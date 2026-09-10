<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 11.5 - Completo</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{font-family:system-ui;background:#f5f5f0}
.card{background:#fff;border:2.5px solid #000;border-radius:20px;padding:14px;box-shadow:4px 4px 0 #000}
</style>
</head>
<body class="p-3">
<div id="app" class="max-w-[600px] mx-auto"></div>
<script>
let prods = JSON.parse(localStorage.getItem('prods11')||'[]');
function getProd(){return prods;}
function saveProd(){localStorage.setItem('prods11', JSON.stringify(prods));}

// ===== CONVERSIONES NUEVAS =====
function normalizarUnidad(u){
 u=(u||'').toString().toLowerCase().trim();
 if(['g','gr','gramo','gramos'].includes(u)) return 'g';
 if(['kg','kilo','kilos','kilogramo'].includes(u)) return 'kg';
 if(['mg','miligramo'].includes(u)) return 'mg';
 if(['lb','libra','libras'].includes(u)) return 'lb';
 if(['oz','onza','onzas'].includes(u)) return 'oz';
 if(['l','lt','lts','litro','litros'].includes(u)) return 'L';
 if(['ml','mililitro','mililitros'].includes(u)) return 'ml';
 if(['cl'].includes(u)) return 'cl';
 if(['gal','galon','galones'].includes(u)) return 'gal';
 if(['m','mt','metro','metros'].includes(u)) return 'm';
 if(['cm','centimetro'].includes(u)) return 'cm';
 if(['mm'].includes(u)) return 'mm';
 if(['pz','pza','pzas','pieza','piezas'].includes(u)) return 'pza';
 return u||'g';
}
function factorABase(u){
 u=normalizarUnidad(u);
 let m={mg:0.001,g:1,kg:1000,lb:453.592,oz:28.3495,ml:1,cl:10,L:1000,gal:3785.41,m:100,cm:1,mm:0.1,pza:1,'':1};
 return m[u]||1;
}
function convertir(cant,de,a){
 de=normalizarUnidad(de); a=normalizarUnidad(a);
 if(de===a) return cant;
 let fd=factorABase(de), fa=factorABase(a);
 let peso=['mg','g','kg','lb','oz'];
 let vol=['ml','cl','L','gal'];
 let long=['mm','cm','m'];
 if(peso.includes(de)&&peso.includes(a)) return cant*fd/fa;
 if(vol.includes(de)&&vol.includes(a)) return cant*fd/fa;
 if(long.includes(de)&&long.includes(a)) return cant*fd/fa;
 if(a==='pza'||de==='pza') return cant;
 return cant;
}
function parseCant(v){
 if(v===null||v===undefined||v==='') return 0;
 v=String(v).trim().replace(',','.').toLowerCase();
 if(v.includes('/')){
   let p=v.split('/');
   let n=parseFloat(p[0])||0;
   let d=parseFloat(p[1])||1;
   if(d===0) d=1;
   return n/d;
 }
 return parseFloat(v)||0;
}
function actualizarRinde(sel){ calc2(); }

// ===== SECUNDARIOS =====
function addBase(){
 let bases = getProd().filter(x=>x.tipo==='base');
 if(bases.length===0){ alert('Primero crea una base'); return; }
 let opts = bases.map(b=>`<option value="${b.id}" data-rinde="${b.rendimiento?.cant||1} ${b.rendimiento?.unit||'g'}">${b.nombre} - $${(b.costo||0).toFixed(2)} - rinde ${b.rendimiento?.cant||1} ${b.rendimiento?.unit||'g'}</option>`).join('');
 let div=document.createElement('div');
 div.className='flex gap-2 items-center flex-wrap bg-yellow-50 p-2 rounded-xl border-2 border-black mb-2';
 div.innerHTML = `
  <select class="b-sel border-2 border-black rounded-xl p-2 flex-1 min-w-[130px]" onchange="actualizarRinde(this)">
   <option value="">-- Base --</option>${opts}
  </select>
  <input class="b-cant border-2 border-black rounded-xl p-2 w-[80px]" value="1" placeholder="1/2" oninput="calc2()">
  <select class="b-unit border-2 border-black rounded-xl p-2 w-[85px]" onchange="calc2()">
   <option value="g">g</option><option value="kg">kg</option><option value="lb">lb</option><option value="oz">oz</option>
   <option value="ml">ml</option><option value="L">L</option><option value="gal">gal</option>
   <option value="m">m</option><option value="cm">cm</option><option value="pza">pza</option>
  </select>
  <button onclick="this.parentElement.remove();calc2()" class="text-red-600 font-black text-xl px-2">X</button>
 `;
 document.getElementById('basesSel').appendChild(div);
 calc2();
}
function calc2(){
 let tot=0;
 document.querySelectorAll('#basesSel > div').forEach(row=>{
  let id=row.querySelector('.b-sel')?.value;
  if(!id) return;
  let cantUsada=parseCant(row.querySelector('.b-cant')?.value);
  let unitUsada=row.querySelector('.b-unit')?.value||'g';
  let b=getProd().find(x=>String(x.id)===String(id));
  if(!b) return;
  let rindeCant=parseCant(b.rendimiento?.cant)||1;
  let rindeUnit=normalizarUnidad(b.rendimiento?.unit||'g');
  let cantConvertida=convertir(cantUsada, unitUsada, rindeUnit);
  if(rindeCant>0 && cantConvertida>0){
    tot += (b.costo / rindeCant) * cantConvertida;
  }
 });
 let elCosto=document.getElementById('c-ing2');
 if(elCosto) elCosto.innerText=tot.toFixed(2);
 let margen=parseFloat(document.getElementById('margen2')?.value)||0;
 let ventaManual=document.getElementById('ventaManual2')?.value||'';
 let venta=0;
 if(ventaManual!==''){
   venta=parseCant(ventaManual);
 } else {
   venta=tot*(1+margen/100);
 }
 let elVenta=document.getElementById('venta2');
 if(elVenta) elVenta.innerText=venta.toFixed(2);
}
function guardarProd(tipo){
 let nombreEl=document.getElementById('nombre2') || document.getElementById('nombre');
 let nombre=nombreEl?.value?.trim();
 if(!nombre) return alert('Pon nombre');
 let bases=[];
 document.querySelectorAll('#basesSel > div').forEach(row=>{
  let id=row.querySelector('.b-sel')?.value;
  let cant=row.querySelector('.b-cant')?.value||0;
  let unit=row.querySelector('.b-unit')?.value||'g';
  if(id) bases.push({id:id, cant:cant, unit:unit});
 });
 if(bases.length===0) return alert('Agrega al menos 1 base');
 let costo=parseFloat(document.getElementById('c-ing2')?.innerText)||0;
 let venta=parseFloat(document.getElementById('venta2')?.innerText)||0;
 let id=Date.now().toString();
 let rendCant=1; let rendUnit='pza';
 prods.push({id:id, nombre:nombre, tipo:tipo, costo:costo, venta:venta, bases:bases, rendimiento:{cant:rendCant, unit:rendUnit}});
 saveProd();
 alert('Guardado: '+nombre+' Costo $'+costo.toFixed(2));
 render();
}
function render(){
 let html=`
 <div class="card">
  <h2 class="font-black text-xl mb-2">Crear Secundario / Producto Final</h2>
  <input id="nombre2" placeholder="Ej: Alitas 10 pzas" class="mb-2">
  <div class="font-bold mt-3">Bases que lleva:</div>
  <div id="basesSel" class="mt-2"></div>
  <button onclick="addBase()" class="w-full mt-2 bg-white text-black border-2 border-black rounded-xl p-3 font-black">+ AGREGAR BASE</button>
  <div class="bg-black text-white rounded-2xl p-4 mt-4">
   <div class="flex justify-between"><span>Costo ingredientes:</span><b>$<span id="c-ing2">0.00</span></b></div>
   <div class="flex justify-between text-yellow-300"><span>Precio venta:</span><b>$<span id="venta2">0.00</span></b></div>
   <div class="flex gap-2 mt-3">
    <input id="margen2" value="100" type="number" oninput="calc2()" class="w-[80px] text-black" placeholder="%"> <span class="pt-2">% margen</span>
    <input id="ventaManual2" placeholder="$ manual (ej 1/2)" oninput="calc2()" class="flex-1 text-black">
   </div>
   <div class="text-xs text-gray-400 mt-2">Puedes escribir 1/2, 1/4, 0.5 en cantidad. Elige kg, g, lb, L, ml, m, cm, pza y se convierte solo.</div>
  </div>
  <button onclick="guardarProd('secundario')" class="w-full mt-4 p-4 text-xl bg-black text-white border-2 border-black rounded-2xl font-black">GUARDAR PRODUCTO</button>
  <div class="mt-4 text-xs">
   <div class="font-bold">Productos guardados: ${prods.length}</div>
   <div class="mt-1">${prods.map(p=>p.nombre+' $'+(p.costo||0).toFixed(2)).join('<br>')||'ninguno'}</div>
  </div>
 </div>`;
 document.getElementById('app').innerHTML=html;
}
render();
</script>
</body>
</html>
