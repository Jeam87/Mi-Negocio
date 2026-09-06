from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
 return """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Mi Negocio PRO</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#FFF8F0] min-h-screen"><div class="max-w-md mx-auto">
<div class="bg-white p-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
<div class="flex items-center gap-2"><label for="logoIn"><img id="logo" src="https://em-content.zobj.net/thumbs/120/apple/354/hamburger_1f354.png" class="w-10 h-10 rounded-full object-cover bg-gray-100"></label><input id="logoIn" type="file" hidden accept="image/*"><div><h1 class="font-black text-[18px] leading-none">Mi Negocio</h1><p class="text-[10px] text-gray-400">Toca el logo para cambiarlo</p></div></div>
<div class="flex gap-1 text-[11px]"><button onclick="tab('crear')" id="b-crear" class="px-3 py-2 rounded-full bg-black text-white font-bold">Crear</button><button onclick="tab('vender')" id="b-vender" class="px-3 py-2 rounded-full bg-gray-100 font-bold">Vender</button></div>
</div>

<div id="t-crear" class="p-3">
<div class="bg-white rounded-[24px] p-4 shadow-sm">
<input id="nombre" placeholder="Nombre: Ej Salsa verde para 1L" class="w-full border-2 p-3 rounded-xl font-bold text-[15px]">
<div id="insumos" class="mt-3 space-y-3"></div>
<button onclick="addInsumo()" class="mt-3 text-[12px] bg-orange-100 text-orange-700 px-4 py-2 rounded-full font-bold">+ Agregar ingrediente</button>
<div class="mt-4 p-4 bg-gray-900 text-white rounded-[18px]">
<div class="flex justify-between text-sm"><span>Costo real receta:</span><span class="font-bold">$<b id="costo">0.00</b></span></div>
<div class="flex gap-2 mt-3 items-center"><input id="margen" type="number" value="100" class="w-16 text-black p-2 rounded-lg text-sm font-bold text-center"> <span class="text-[12px]">% ganancia</span><span class="ml-auto text-right">Precio venta:<br>$<b id="venta" class="text-[22px]">0.00</b></span></div>
</div>
<button onclick="guardar()" class="w-full mt-3 bg-black text-white py-3.5 rounded-xl font-black">Guardar en inventario</button>
</div><div id="listaInv" class="mt-4 pb-20"></div>
</div>

<div id="t-vender" class="p-3 hidden"><div id="listaVenta" class="grid grid-cols-2 gap-3"></div><div id="carrito" class="mt-6 bg-white rounded-[20px] p-4 shadow-xl sticky bottom-4 border"><h3 class="font-bold">Carrito <span id="c-count">0</span></h3><div id="c-items" class="text-sm mt-2"></div><div class="flex justify-between font-black text-lg mt-3 border-t pt-3"><span>Total</span><span>$<span id="c-total">0</span></span></div><button onclick="cobrar()" class="w-full mt-3 bg-green-500 text-white py-3 rounded-xl font-black">COBRAR</button><button onclick="vaciar()" class="w-full mt-2 text-[11px] text-gray-400">Vaciar</button></div></div>
</div>

<script>
let carrito=[];
const U=['kg','g','L','ml','galon','pza','cda','cdita'];
function baseFactor(u){
 if(u=='kg'||u=='L') return 1000;
 if(u=='g'||u=='ml'||u=='cda'||u=='cdita'||u=='pza') return 1;
 if(u=='galon') return 3785;
 return 1;
}
function addInsumo(d={}){
 let div=document.createElement('div');
 div.className='bg-[#FFF8F0] p-3 rounded-[16px] border';
 div.innerHTML=`<div class="flex justify-between"><input placeholder="Ingrediente: Cebolla" value="${d.n||''}" class="in-n bg-transparent font-bold text-sm w-2/3 outline-none"><button onclick="this.closest('div').parentElement.remove();calc()" class="text-red-300 text-xs">X</button></div>
 <div class="mt-2 grid grid-cols-3 gap-1 text-[11px]"><div class="col-span-3 text-gray-500 font-bold">COMPRE:</div>
 <input type="number" value="${d.cc||''}" placeholder="Cant" class="in-cc border p-2 rounded-lg" oninput="calc()"><select class="in-uc border p-2 rounded-lg" onchange="calc()">${U.map(x=>`<option ${d.uc==x?'selected':''}>${x}</option>`).join('')}</select><input type="number" value="${d.pc||''}" placeholder="$ costo" class="in-pc border p-2 rounded-lg" oninput="calc()">
 <div class="col-span-3 text-gray-500 font-bold mt-1">USO EN RECETA:</div>
 <input type="number" value="${d.cu||''}" placeholder="Cant uso" class="in-cu border p-2 rounded-lg" oninput="calc()"><select class="in-uu border p-2 rounded-lg" onchange="calc()">${U.map(x=>`<option ${d.uu==x?'selected':''}>${x}</option>`).join('')}</select><div class="p-2 bg-white rounded-lg text-center font-bold">$<span class="in-sub">0</span></div></div>`;
 document.getElementById('insumos').appendChild(div);
}
addInsumo({n:'Cebolla',cc:1,uc:'kg',pc:40,cu:150,uu:'g'});
addInsumo({n:'Tomate',cc:1,uc:'kg',pc:30,cu:500,uu:'g'});

function calc(){
 let total=0;
 document.querySelectorAll('#insumos > div').forEach(row=>{
  let cc=parseFloat(row.querySelector('.in-cc').value)||0;
  let pc=parseFloat(row.querySelector('.in-pc').value)||0;
  let cu=parseFloat(row.querySelector('.in-cu').value)||0;
  let uc=row.querySelector('.in-uc').value;
  let uu=row.querySelector('.in-uu').value;
  if(!cc||!pc||!cu){ row.querySelector('.in-sub').innerText='0'; return; }
  let bcc=cc*baseFactor(uc); let bcu=cu*baseFactor(uu);
  let cost = (pc/bcc)*bcu;
  if((uc=='kg'||uc=='g') && (uu=='kg'||uu=='g')){} else if((uc=='L'||uc=='ml'||uc=='galon') && (uu=='L'||uu=='ml'||uu=='galon')){} else if(uc!=uu){ cost = (pc/cc)*cu; }
  row.querySelector('.in-sub').innerText=cost.toFixed(2);
  total+=cost;
 });
 document.getElementById('costo').innerText=total.toFixed(2);
 let m=parseFloat(document.getElementById('margen').value)||0;
 document.getElementById('venta').innerText=(total + total*m/100).toFixed(2);
}
document.getElementById('margen').oninput=calc;

function tab(t){
 document.getElementById('t-crear').classList.toggle('hidden',t!='crear');
 document.getElementById('t-vender').classList.toggle('hidden',t!='vender');
 document.getElementById('b-crear').className= t=='crear'?'px-3 py-2 rounded-full bg-black text-white font-bold':'px-3 py-2 rounded-full bg-gray-100 font-bold';
 document.getElementById('b-vender').className= t=='vender'?'px-3 py-2 rounded-full bg-black text-white font-bold':'px-3 py-2 rounded-full bg-gray-100 font-bold';
 if(t=='vender') mostrarVenta();
}
function getProd(){return JSON.parse(localStorage.getItem('productosV2')||'[]');}
function guardar(){
 let nombre=document.getElementById('nombre').value.trim(); if(!nombre) return alert('Pon nombre');
 let costo=parseFloat(document.getElementById('costo').innerText); let venta=parseFloat(document.getElementById('venta').innerText);
 let ingredientes=[]; document.querySelectorAll('#insumos > div').forEach(r=> ingredientes.push({n:r.querySelector('.in-n').value,cc:r.querySelector('.in-cc').value,uc:r.querySelector('.in-uc').value,pc:r.querySelector('.in-pc').value,cu:r.querySelector('.in-cu').value,uu:r.querySelector('.in-uu').value,c:r.querySelector('.in-sub').innerText}));
 let p=getProd(); p.push({id:Date.now(),nombre,costo,venta,ingredientes}); localStorage.setItem('productosV2',JSON.stringify(p)); mostrar(); alert('Guardado! Costo real $'+costo);
}
function mostrar(){
 let prods=getProd(); let h='<h2 class="font-black text-sm">Mis recetas ('+prods.length+')</h2>';
 prods.forEach((p,i)=> h+=`<div class="mt-2 bg-white p-3 rounded-xl flex justify-between items-center shadow-sm"><div><b class="text-[13px]">${p.nombre}</b><br><span class="text-[11px] text-gray-500">$${p.costo.toFixed(2)} costo → $${p.venta.toFixed(2)} venta</span></div><button onclick="borrar(${i})" class="text-[11px] bg-red-50 text-red-500 px-3 py-1 rounded-full">Borrar</button></div>`);
 document.getElementById('listaInv').innerHTML=h; mostrarVenta();
}
function borrar(i){let p=getProd(); p.splice(i,1); localStorage.setItem('productosV2',JSON.stringify(p)); mostrar();}
function mostrarVenta(){
 let prods=getProd(); let h=''; prods.forEach(p=> h+=`<button onclick="addCart(${p.id})" class="bg-white p-3 rounded-2xl text-left shadow"><b class="text-[12px]">${p.nombre}</b><br><span class="text-[11px] text-green-600 font-bold">$${p.venta.toFixed(2)}</span><br><span class="text-[10px] text-gray-400">${p.costo.toFixed(2)} costo</span></button>`);
 if(!prods.length) h='<p class="col-span-2 text-center text-sm text-gray-400 py-10">Crea tu primera salsa/receta arriba.</p>';
 document.getElementById('listaVenta').innerHTML=h;
}
function addCart(id){let p=getProd().find(x=>x.id==id); let ex=carrito.find(x=>x.id==id); if(ex) ex.qty++; else carrito.push({...p,qty:1}); renderCart();}
function renderCart(){let t=0,c=0,html=''; carrito.forEach((x,i)=>{t+=x.venta*x.qty; c+=x.qty; html+=`<div class="flex justify-between py-1"><span>${x.nombre} x${x.qty}</span><span>$${(x.venta*x.qty).toFixed(0)} <button onclick="carrito.splice(${i},1);renderCart()" class="text-red-300 ml-1">x</button></span></div>`;}); document.getElementById('c-total').innerText=t.toFixed(0); document.getElementById('c-count').innerText=c; document.getElementById('c-items').innerHTML=html||'<span class="text-gray-400">Vacío</span>';}
function vaciar(){carrito=[]; renderCart();} function cobrar(){if(!carrito.length) return alert('Vacío'); alert('TOTAL $'+document.getElementById('c-total').innerText); vaciar();}
document.getElementById('logoIn').onchange=e=>{let r=new FileReader(); r.onload=()=>{document.getElementById('logo').src=r.result; localStorage.setItem('logo',r.result);}; r.readAsDataURL(e.target.files[0]);};
if(localStorage.getItem('logo')) document.getElementById('logo').src=localStorage.getItem('logo');
calc(); mostrar();
</script></body></html>
""" 
