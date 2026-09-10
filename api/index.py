<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Mi Negocio</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{background:#FEF8EF;font-family:system-ui}
.card{border:2px solid #000;border-radius:20px}
</style>
</head>
<body class="pb-[90px]">
<div id="app" class="max-w-[500px] mx-auto p-3"></div>

<nav class="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-black flex justify-around py-2 max-w-[500px] mx-auto">
 <button class="flex flex-col items-center font-black"><span>📝</span><span class="text-[11px]">Crear</span></button>
 <button class="flex flex-col items-center opacity-40"><span>🏪</span><span class="text-[11px]">Catalogo</span></button>
 <button class="flex flex-col items-center opacity-40"><span>📦</span><span class="text-[11px]">Invent</span></button>
 <button class="flex flex-col items-center opacity-40"><span>📈</span><span class="text-[11px]">Finanzas</span></button>
 <button class="flex flex-col items-center opacity-40"><span>👥</span><span class="text-[11px]">Clientes</span></button>
</nav>

<script>
let prods; try{ prods=JSON.parse(localStorage.getItem('prods11')||'[]'); }catch(e){ prods=[]; }
let cats; try{ cats=JSON.parse(localStorage.getItem('cats11')||'["Todas","Alitas","Boneless","Burgers"]'); }catch(e){ cats=["Todas"]; }

function getProd(){return prods;}
function save(){localStorage.setItem('prods11',JSON.stringify(prods)); localStorage.setItem('cats11',JSON.stringify(cats));}

function parseCant(v){
 v=String(v||'').replace(',','.').toLowerCase();
 if(v.includes('/')){let p=v.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1);}
 return parseFloat(v)||0;
}
function convertir(c,de,a){
 de=(de||'l').toLowerCase(); a=(a||'l').toLowerCase();
 if(de==a) return c;
 let m={g:1,kg:1000,lb:453.592,oz:28.3495,ml:1,l:1000,lt:1000};
 if(m[de]&&m[a]) return c*m[de]/m[a];
 return c;
}
function calc2(){
 let tot=0;
 document.querySelectorAll('#basesSel > div').forEach(function(row){
  let sel=row.querySelector('.b-sel'); if(!sel||!sel.value) return;
  let b=getProd().find(function(x){return String(x.id)==String(sel.value)}); if(!b) return;
  let cant=parseCant(row.querySelector('.b-cant').value||1);
  let rCant=parseCant(b.rendimiento?.cant||10)||10;
  let rUnit=b.rendimiento?.unit||'L';
  let u=row.querySelector('.b-unit')?.value||rUnit;
  let cantConv=convertir(cant,u,rUnit);
  let costo=parseFloat(b.costo)||0;
  if(rCant>0) tot+=(costo/rCant)*cantConv;
 });
 document.getElementById('costoTxt').innerText='$'+tot.toFixed(2);
 document.getElementById('c-ing2').innerText=tot.toFixed(2);
 let margen=parseFloat(document.getElementById('margenInput').value)||100;
 let venta=tot*(1+margen/100);
 let finalV=document.getElementById('finalInput').value;
 if(finalV!==''){ let mv=parseCant(finalV); if(mv>0) venta=mv; }
 document.getElementById('ventaTxt').innerText='$'+venta.toFixed(2);
 document.getElementById('venta2').innerText=venta.toFixed(2);
}
function addBase(d){
 d=d||{};
 let bases=getProd().filter(function(x){return x.tipo==='base'||x.esBase});
 if(bases.length==0){alert('Primero crea base en Inventario'); return;}
 let opts=bases.map(function(b){
  return '<option value="'+b.id+'" '+(String(d.id)==String(b.id)?'selected':'')+'>'+b.nombre+' $'+(parseFloat(b.costo)||0).toFixed(2)+' (rinde '+(b.rendimiento?.cant||10)+(b.rendimiento?.unit||'L')+')</option>';
 }).join('');
 let div=document.createElement('div');
 div.className='bg-white border-2 border-black rounded-[16px] p-2 flex gap-2 items-center mb-2';
 div.innerHTML='<select class="b-sel flex-1 border-2 border-black rounded-xl p-3 font-bold" onchange="calc2()"><option value="">-- Base --</option>'+opts+'</select><input class="b-cant w-[65px] border-2 border-black rounded-xl p-3 text-center font-black" value="'+(d.cant||1)+'" oninput="calc2()"><select class="b-unit w-[55px] border-2 border-black rounded-xl p-2 text-[12px] font-bold" onchange="calc2()"><option value="L">L</option><option value="ml">ml</option><option value="g">g</option></select><button onclick="this.parentElement.remove();calc2()" class="text-red-500 font-black">X</button>';
 document.getElementById('basesSel').appendChild(div); calc2();
}
function crearCat(){ let v=document.getElementById('nuevaCat').value.trim(); if(!v) return; if(cats.indexOf(v)===-1) cats.push(v); save(); render(); }
function guardar(){
 let nombre=document.getElementById('nombreProd').value.trim(); if(!nombre) return alert('Pon nombre');
 let lista=[]; document.querySelectorAll('#basesSel > div').forEach(function(r){
  let id=r.querySelector('.b-sel').value; let cant=r.querySelector('.b-cant').value; let unit=r.querySelector('.b-unit').value;
  if(id) lista.push({id:id,cant:cant,unit:unit});
 });
 if(!lista.length) return alert('Agrega base');
 let costo=parseFloat(document.getElementById('costoTxt').innerText.replace('$',''))||0;
 let venta=parseFloat(document.getElementById('ventaTxt').innerText.replace('$',''))||0;
 let cat=document.getElementById('catSelect').value||'Todas';
 prods.push({id:Date.now().toString(),nombre:nombre,categoria:cat,tipo:'secundario',costo:costo,venta:venta,bases:lista,rendimiento:{cant:1,unit:'pza'}});
 save(); render(); alert('Guardado '+nombre+' $'+costo.toFixed(2));
}
function render(){
 document.getElementById('app').innerHTML='<div class="card p-3 bg-[#E8F4FF]"><select id="catSelect" class="w-full border-2 border-black rounded-[16px] p-4 font-bold bg-white mb-2">'+cats.map(function(c){return '<option>'+c+'</option>'}).join('')+'</select><div class="flex gap-2"><input id="nuevaCat" placeholder="Nueva cat" class="flex-1 border-2 border-black rounded-[16px] p-3 bg-white"><button onclick="crearCat()" class="bg-black text-white rounded-[16px] px-6 font-black">Crear</button></div></div><div class="card p-3 bg-[#FFFBE6] mt-3"><div id="basesSel"></div><button onclick="addBase()" class="w-full border-2 border-black rounded-[16px] p-3 bg-white font-bold">+ Base</button></div><div class="card p-4 bg-black text-white mt-3"><div class="flex justify-between"><span>Costo</span><b id="costoTxt">$0.00</b><span id="c-ing2" class="hidden">0</span></div><div class="flex justify-between font-black text-xl"><span>Venta</span><b id="ventaTxt" class="text-[#5CFFC0]">$0.00</b><span id="venta2" class="hidden">0</span></div><div class="flex gap-2 mt-2"><input id="margenInput" value="100" type="number" oninput="calc2()" class="w-[70px] rounded-xl p-3 text-black font-black text-center"><input id="finalInput" placeholder="$ final" oninput="calc2()" class="flex-1 rounded-xl p-3 text-black"></div></div><div class="mt-3"><input id="nombreProd" placeholder="Nombre ej: Alitas BBQ" class="w-full border-2 border-black rounded-[16px] p-4 font-bold"></div><button onclick="guardar()" class="w-full bg-black text-white rounded-[20px] p-5 font-black text-xl mt-3">GUARDAR</button>';
}
render();
</script>
</body>
</html>
