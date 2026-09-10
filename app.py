<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{background:#fef9f1;font-family:system-ui}
.card{border:2px solid #000;border-radius:20px;background:#fff}
</style>
</head>
<body>
<div id="app" class="max-w-[500px] mx-auto p-2 pb-[90px]"></div>

<nav class="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-black flex justify-around py-2 max-w-[500px] mx-auto">
 <button class="font-bold">📝 Crear</button>
 <button class="opacity-40">🏪 Catalogo</button>
 <button class="opacity-40">📦 Invent</button>
 <button class="opacity-40">📈 Finanzas</button>
 <button class="opacity-40">👥 Clientes</button>
</nav>

<script>
let prods = JSON.parse(localStorage.getItem('prods11')||'[]');
let categorias = JSON.parse(localStorage.getItem('cats11')||'["Todas","Alitas","Boneless","Burgers"]');
let editandoId=null;

function getProd(){return prods;}
function save(){localStorage.setItem('prods11', JSON.stringify(prods)); localStorage.setItem('cats11', JSON.stringify(categorias));}

function parseCant(v){
 if(v==null||v==='') return 0;
 v=String(v).trim().replace(',','.').toLowerCase();
 if(v.includes('/')){let p=v.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1);}
 return parseFloat(v)||0;
}
function convertir(c,de,a){
 de=(de||'').toLowerCase(); a=(a||'').toLowerCase();
 if(de==a) return c;
 let m={g:1,kg:1000,lb:453.592,oz:28.3495,mg:0.001,ml:1,l:1000,lt:1000,cl:10};
 if(m[de]&&m[a]) return c*m[de]/m[a];
 return c;
}

function calc2(){
 let tot=0;
 document.querySelectorAll('#basesSel>div').forEach(row=>{
  let sel=row.querySelector('.b-sel'); if(!sel||!sel.value) return;
  let b=getProd().find(x=>String(x.id)==String(sel.value)); if(!b) return;
  let cantInput=row.querySelector('.b-cant'); let cant=parseCant(cantInput?.value||1);
  let rCant=parseCant(b.rendimiento?.cant||1); let rUni=(b.rendimiento?.unit||b.rendimiento?.uni||'L').toLowerCase();
  let uSel=row.querySelector('.b-unit'); let uUsada=(uSel?.value||rUni).toLowerCase();
  let cantConv=convertir(cant,uUsada,rUni);
  let costo=parseFloat(b.costo)||0;
  if(rCant>0) tot+=(costo/rCant)*cantConv;
 });
 document.getElementById('costoTxt').innerText='$'+tot.toFixed(2);
 let margen=parseFloat(document.getElementById('margenInput')?.value)||100;
 let venta=tot*(1+margen/100);
 let manual=document.getElementById('finalInput')?.value;
 if(manual!==''){ venta=parseCant(manual); }
 document.getElementById('ventaTxt').innerText='$'+venta.toFixed(2);
}

function addBase(d={}){
 let bases=getProd().filter(x=>x.tipo==='base' || x.esBase);
 if(bases.length==0){alert('Primero crea una base en Inventario'); return;}
 let opts=bases.map(b=>{
   let rCant=b.rendimiento?.cant||b.rinde||1;
   let rUni=b.rendimiento?.unit||b.rendimiento?.uni||'L';
   return `<option value="${b.id}" ${String(d.id)==String(b.id)?'selected':''}>${b.nombre} $${(parseFloat(b.costo)||0).toFixed(2)} (rinde ${rCant}${rUni})</option>`;
 }).join('');
 let div=document.createElement('div');
 div.className='border-2 border-black rounded-[16px] p-2 bg-white flex gap-2 items-center mb-2';
 div.innerHTML=`
  <select class="b-sel flex-1 border-2 border-black rounded-xl p-3 bg-white" onchange="calc2()"><option value="">-- Base --</option>${opts}</select>
  <input class="b-cant w-[70px] border-2 border-black rounded-xl p-3 text-center font-bold" value="${d.cant||'1'}" oninput="calc2()">
  <select class="b-unit w-[70px] border-2 border-black rounded-xl p-2 hidden sm:block" onchange="calc2()">
    <option value="L" ${d.unit=='L'?'selected':''}>L</option><option value="ml">ml</option><option value="kg">kg</option><option value="g">g</option><option value="pza">pza</option>
  </select>
  <button onclick="this.parentElement.remove();calc2()" class="font-black text-red-500 text-xl px-2">✕</button>
 `;
 document.getElementById('basesSel').appendChild(div);
 calc2();
}

function crearCat(){
 let input=document.getElementById('nuevaCat'); let val=input.value.trim();
 if(!val) return; if(!categorias.includes(val)) categorias.push(val);
 save(); render();
}

function guardar(){
 let nombre=document.getElementById('nombreProd')?.value.trim();
 if(!nombre) return alert('Pon nombre al producto');
 let bases=[];
 document.querySelectorAll('#basesSel>div').forEach(r=>{
   let id=r.querySelector('.b-sel')?.value;
   let cant=r.querySelector('.b-cant')?.value||1;
   let unit=r.querySelector('.b-unit')?.value||'L';
   if(id) bases.push({id,cant,unit});
 });
 if(bases.length==0) return alert('Agrega al menos una base');
 let costoTxt=document.getElementById('costoTxt').innerText.replace('$','');
 let ventaTxt=document.getElementById('ventaTxt').innerText.replace('$','');
 let costo=parseFloat(costoTxt)||0; let venta=parseFloat(ventaTxt)||0;
 let cat=document.getElementById('catSelect')?.value||'Todas';

 if(editandoId){
   let p=prods.find(x=>x.id==editandoId);
   p.nombre=nombre; p.categoria=cat; p.costo=costo; p.venta=venta; p.bases=bases;
   editandoId=null;
 } else {
   prods.push({id:Date.now().toString(),nombre:nombre,categoria:cat,tipo:'secundario',esBase:false,costo:costo,venta:venta,bases:bases,rendimiento:{cant:1,unit:'pza'}});
 }
 save(); render(); alert('Guardado '+nombre+' Costo $'+costo.toFixed(2));
}

function render(){
 let cats=categorias.map(c=>`<option ${c=='Todas'?'selected':''}>${c}</option>`).join('');
 document.getElementById('app').innerHTML=`
  <div class="card p-3 bg-[#e8f4ff]">
    <div class="font-black mb-2">📁 Categoria</div>
    <select id="catSelect" class="w-full border-2 border-black rounded-[16px] p-4 font-bold bg-white mb-2">${cats}</select>
    <div class="flex gap-2">
      <input id="nuevaCat" placeholder="Nueva cat" class="flex-1 border-2 border-black rounded-[16px] p-3 bg-white">
      <button onclick="crearCat()" class="bg-black text-white rounded-[16px] px-6 font-black">Crear</button>
    </div>
  </div>

  <div class="mt-3">
    <input type="file" id="fileInput" class="mb-2">
    <div class="card p-3 bg-[#fffbe6]">
      <div class="font-black mb-2">Bases que lleva:</div>
      <div id="basesSel"></div>
      <button onclick="addBase()" class="w-full border-2 border-black rounded-[16px] p-3 bg-white font-bold mt-2">+ Base</button>
    </div>

    <div class="card p-4 bg-black text-white mt-3">
      <div class="flex justify-between text-xl mb-1"><span>Costo</span><b id="costoTxt">$0.00</b></div>
      <div class="flex justify-between text-xl mb-3"><span class="font-black">Venta</span><b id="ventaTxt" class="text-[#5cffc0]">$0.00</b></div>
      <div class="flex gap-2">
        <input id="margenInput" value="100" type="number" oninput="calc2()" class="w-[80px] rounded-xl p-3 text-black font-black text-center">
        <input id="finalInput" placeholder="$ final" oninput="calc2()" class="flex-1 rounded-xl p-3 text-black font-bold">
      </div>
    </div>

    <div class="mt-3">
      <input id="nombreProd" placeholder="Nombre del producto ej: Alitas BBQ 10pzs" class="w-full border-2 border-black rounded-[16px] p-4 font-bold">
    </div>

    <button onclick="guardar()" class="w-full bg-black text-white rounded-[20px] p-5 font-black text-xl mt-3">GUARDAR</button>

    <div class="mt-4 text-xs space-y-1">
      ${getProd().filter(x=>!x.esBase && x.tipo!='base').map(p=>`<div class="bg-white border-2 border-black rounded-xl p-2 flex justify-between"><span>${p.nombre} [$${p.costo.toFixed(2)}]</span><button onclick="if(confirm('borrar?')){prods=prods.filter(z=>z.id!='${p.id}'); save(); render();}" class="text-red-500 font-black">X</button></div>`).join('')||''}
    </div>
  </div>
 `;
}
render();
</script>
</body>
</html>
