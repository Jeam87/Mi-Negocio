from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Costeo Pro - POS</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-pink-50 min-h-screen p-4">
<div class="max-w-md mx-auto bg-white rounded-2xl shadow-lg p-5">
  <h1 class="text-2xl font-bold text-center">Costeo Pro 💐</h1>
  <p class="text-center text-xs text-gray-500">Calcula costo + precio + inventario</p>
  
  <div class="mt-5">
    <input id="nombre" placeholder="Nombre producto (Ej: Ramo 12 rosas)" class="w-full border p-3 rounded-xl">
    <div id="insumos" class="mt-3 space-y-2"></div>
    <button onclick="addInsumo()" class="mt-2 text-sm bg-pink-100 text-pink-700 px-3 py-2 rounded-xl">+ Agregar costo</button>
    
    <div class="mt-4 p-3 bg-gray-50 rounded-xl">
      <p class="text-sm">Costo total: $<span id="costo">0</span></p>
      <div class="flex gap-2 mt-2">
        <input id="margen" type="number" value="150" class="w-20 border p-2 rounded-lg"> <span class="text-sm py-2">% ganancia</span>
      </div>
      <p class="mt-2 font-bold text-lg">Precio venta: $<span id="venta">0</span></p>
    </div>
    
    <button onclick="guardar()" class="w-full mt-4 bg-black text-white py-3 rounded-xl font-bold">Guardar producto</button>
  </div>

  <div id="lista" class="mt-6"></div>
</div>

<script>
let insumosCount = 0;
function addInsumo(nombre='', costo=''){
  insumosCount++;
  let div = document.createElement('div');
  div.className='flex gap-2';
  div.innerHTML = `<input placeholder="Ej: Rosa" value="${nombre}" class="insumo-nombre flex-1 border p-2 rounded-lg text-sm"><input type="number" placeholder="$" value="${costo}" class="insumo-costo w-20 border p-2 rounded-lg text-sm" oninput="calc()"><button onclick="this.parentElement.remove();calc()" class="text-red-400">x</button>`;
  document.getElementById('insumos').appendChild(div);
}
addInsumo('Rosa','10');
addInsumo('Papel','5');

function calc(){
  let total=0;
  document.querySelectorAll('.insumo-costo').forEach(i=> total+= parseFloat(i.value)||0);
  document.getElementById('costo').innerText= total.toFixed(2);
  let margen = parseFloat(document.getElementById('margen').value)||0;
  let venta = total + (total*margen/100);
  document.getElementById('venta').innerText= venta.toFixed(2);
}
document.getElementById('margen').oninput=calc;
calc();

function guardar(){
  let nombre=document.getElementById('nombre').value;
  if(!nombre) return alert('Pon nombre');
  let costo=parseFloat(document.getElementById('costo').innerText);
  let venta=parseFloat(document.getElementById('venta').innerText);
  let productos=JSON.parse(localStorage.getItem('productos')||'[]');
  productos.push({nombre,costo,venta, fecha: new Date().toLocaleDateString()});
  localStorage.setItem('productos', JSON.stringify(productos));
  mostrar();
  document.getElementById('nombre').value='';
}

function mostrar(){
  let productos=JSON.parse(localStorage.getItem('productos')||'[]');
  let html='<h2 class="font-bold">Inventario ('+productos.length+')</h2>';
  productos.forEach((p,i)=>{
    html+=`<div class="mt-2 p-3 border rounded-xl flex justify-between"><div><b>${p.nombre}</b><br><span class="text-xs text-gray-500">Costo $${p.costo} | Venta $${p.venta}</span></div><button onclick="borrar(${i})" class="text-xs text-red-500">Borrar</button></div>`;
  });
  document.getElementById('lista').innerHTML=html;
}
function borrar(i){
  let productos=JSON.parse(localStorage.getItem('productos')||'[]');
  productos.splice(i,1);
  localStorage.setItem('productos', JSON.stringify(productos));
  mostrar();
}
mostrar();
</script>
</body>
</html>
"""
