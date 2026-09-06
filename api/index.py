from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Mi Negocio - POS</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#FFF5F7] min-h-screen">
<div class="max-w-md mx-auto">

<div class="bg-white p-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
  <h1 class="font-black text-xl">Mi Negocio 💐</h1>
  <div class="flex gap-2 text-xs">
    <button onclick="tab('crear')" id="b-crear" class="px-3 py-2 rounded-full bg-black text-white">Crear</button>
    <button onclick="tab('vender')" id="b-vender" class="px-3 py-2 rounded-full bg-gray-100">Vender</button>
  </div>
</div>

<div id="t-crear" class="p-4">
  <div class="bg-white rounded-[20px] p-5 shadow">
    <input id="nombre" placeholder="Nombre producto (Ramo 12 rosas)" class="w-full border-2 p-3 rounded-xl font-bold">
    <div id="insumos" class="mt-3 space-y-2"></div>
    <button onclick="addInsumo()" class="mt-2 text-xs bg-pink-100 text-pink-700 px-3 py-2 rounded-full">+ costo material</button>
    <div class="mt-4 p-4 bg-gray-900 text-white rounded-2xl">
      <div class="flex justify-between text-sm"><span>Costo:</span><span>$<b id="costo">0</b></span></div>
      <div class="flex gap-2 mt-2 items-center"><input id="margen" type="number" value="150" class="w-16 text-black p-2 rounded-lg text-sm"> <span class="text-sm">% ganancia</span><span class="ml-auto">Venta: $<b id="venta" class="text-lg">0</b></span></div>
    </div>
    <button onclick="guardar()" class="w-full mt-4 bg-black text-white py-3.5 rounded-xl font-black">Guardar en inventario</button>
  </div>
  <div id="listaInv" class="mt-6"></div>
</div>

<div id="t-vender" class="p-4 hidden">
  <div id="listaVenta" class="grid grid-cols-2 gap-3"></div>
  <div id="carrito" class="mt-6 bg-white rounded-[20px] p-4 shadow sticky bottom-4">
    <h3 class="font-bold">Carrito <span id="c-count">0</span></h3>
    <div id="c-items" class="text-sm mt-2"></div>
    <div class="flex justify-between font-black text-lg mt-3 border-t pt-3"><span>Total</span><span>$<span id="c-total">0</span></span></div>
    <button onclick="cobrar()" class="w-full mt-3 bg-green-500 text-white py-3 rounded-xl font-black">COBRAR Y TICKET</button>
    <button onclick="whats()" class="w-full mt-2 bg-white border-2 py-3 rounded-xl font-bold">Enviar WhatsApp</button>
    <button onclick="vaciar()" class="w-full mt-2 text-xs text-gray-400">Vaciar carrito</button>
  </div>
</div>

</div>

<script>
let carrito=[]
let insumosCount=0;
function addInsumo(n='', c=''){
  let div=document.createElement('div');
  div.className='flex gap-2';
  div.innerHTML=`<input placeholder="Material" value="${n}" class="insumo-nombre flex-1 border p-2.5 rounded-xl text-sm"><input type="number" placeholder="$" value="${c}" class="insumo-costo w-20 border p-2.5 rounded-xl text-sm" oninput="calc()"><button onclick="this.parentElement.remove();calc()" class="text-red-300">x</button>`;
  document.getElementById('insumos').appendChild(div);
}
addInsumo('Rosa','10'); addInsumo('Papel coreano','8');

function calc(){
  let total=0; document.querySelectorAll('.insumo-costo').forEach(i=> total+=parseFloat(i.value)||0);
  document.getElementById('costo').innerText=total.toFixed(2);
  let m=parseFloat(document.getElementById('margen').value)||0;
  document.getElementById('venta').innerText=(total + total*m/100).toFixed(2);
}
document.getElementById('margen').oninput=calc; calc();

function tab(t){
  document.getElementById('t-crear').classList.toggle('hidden', t!='crear');
  document.getElementById('t-vender').classList.toggle('hidden', t!='vender');
  document.getElementById('b-crear').className= t=='crear'? 'px-3 py-2 rounded-full bg-black text-white' : 'px-3 py-2 rounded-full bg-gray-100';
  document.getElementById('b-vender').className= t=='vender'? 'px-3 py-2 rounded-full bg-black text-white' : 'px-3 py-2 rounded-full bg-gray-100';
  if(t=='vender') mostrarVenta();
}

function guardar(){
  let nombre=document.getElementById('nombre').value.trim();
  if(!nombre) return alert('Pon nombre');
  let costo=parseFloat(document.getElementById('costo').innerText);
  let venta=parseFloat(document.getElementById('venta').innerText);
  let prod=JSON.parse(localStorage.getItem('productos')||'[]');
  prod.push({id:Date.now(), nombre,costo,venta});
  localStorage.setItem('productos',JSON.stringify(prod));
  document.getElementById('nombre').value=''; mostrar(); alert('Guardado!');
}
function getProd(){ return JSON.parse(localStorage.getItem('productos')||'[]'); }

function mostrar(){
  let prods=getProd();
  let h='<h2 class="font-black">Inventario ('+prods.length+')</h2>';
  prods.forEach((p,i)=> h+=`<div class="mt-2 bg-white p-3 rounded-xl flex justify-between items-center shadow-sm"><div><b class="text-sm">${p.nombre}</b><br><span class="text-xs text-gray-500">$${p.costo} costo → $${p.venta} venta</span></div><button onclick="borrar(${i})" class="text-xs bg-red-50 text-red-500 px-3 py-1 rounded-full">Borrar</button></div>`);
  document.getElementById('listaInv').innerHTML=h;
  mostrarVenta();
}
function borrar(i){ let p=getProd(); p.splice(i,1); localStorage.setItem('productos',JSON.stringify(p)); mostrar(); }
function mostrarVenta(){
  let prods=getProd();
  let h=''; prods.forEach(p=> h+=`<button onclick="addCart(${p.id})" class="bg-white p-3 rounded-2xl text-left shadow"><b class="text-sm">${p.nombre}</b><br><span class="text-xs text-green-600 font-bold">$${p.venta}</span></button>`);
  if(!prods.length) h='<p class="col-span-2 text-center text-sm text-gray-400 py-10">Aún no hay productos. Crea uno en Crear.</p>';
  document.getElementById('listaVenta').innerHTML=h;
}
function addCart(id){
  let p=getProd().find(x=>x.id==id);
  let ex=carrito.find(x=>x.id==id);
  if(ex) ex.qty++; else carrito.push({...p, qty:1});
  renderCart();
}
function renderCart(){
  let total=0, count=0, html='';
  carrito.forEach((c,i)=>{ total+=c.venta*c.qty; count+=c.qty; html+=`<div class="flex justify-between py-1"><span>${c.nombre} x${c.qty}</span><span>$${(c.venta*c.qty).toFixed(0)} <button onclick="carrito.splice(${i},1);renderCart()" class="text-red-300 ml-2">x</button></span></div>`; });
  document.getElementById('c-total').innerText=total.toFixed(0);
  document.getElementById('c-count').innerText=count;
  document.getElementById('c-items').innerHTML= html || '<span class="text-gray-400">Vacío</span>';
}
function vaciar(){ carrito=[]; renderCart(); }
function cobrar(){
  if(!carrito.length) return alert('Carrito vacío');
  let total=document.getElementById('c-total').innerText;
  let ticket='TICKET - Mi Negocio\\n'+carrito.map(c=>`${c.nombre} x${c.qty} - $${c.venta*c.qty}`).join('\\n')+'\\nTOTAL: $'+total;
  alert(ticket); vaciar();
}
function whats(){
  if(!carrito.length) return alert('Carrito vacío');
  let total=document.getElementById('c-total').innerText;
  let msg='Hola! Tu pedido Mi Negocio:%0A'+carrito.map(c=>`- ${c.nombre} x${c.qty} $${c.venta*c.qty}`).join('%0A')+'%0A%0ATOTAL: $'+total;
  window.open('https://wa.me/?text='+msg,'_blank');
}
mostrar();
</script>
</body>
</html>
""" 
