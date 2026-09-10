from flask import Flask, jsonify, send_file, request
import os, json
app = Flask(__name__)
BASE_DATA = '/tmp/data' if os.path.exists('/tmp') else 'data'
os.makedirs(BASE_DATA, exist_ok=True)
USERS_FILE = os.path.join(BASE_DATA, 'users.json')
def load_users():
 try:
  if os.path.exists(USERS_FILE):
   with open(USERS_FILE,'r') as f: return json.load(f)
 except: pass
 return {}
def save_users(u):
 try:
  with open(USERS_FILE,'w') as f: json.dump(u,f)
 except: pass
def get_user_file(nid):
 safe=nid.replace("@","_at_").replace(".","_")
 return os.path.join(BASE_DATA, f"{safe}.json")

 <!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Negocio 11.5 - Inventario Editable</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#f6f5f0] p-2">
<div class="max-w-[700px] mx-auto space-y-3" id="app"></div>
<script>
let prods = JSON.parse(localStorage.getItem('prods11')||'[]');
let editandoId = null;
function getProd(){return prods;}
function save(){localStorage.setItem('prods11', JSON.stringify(prods));}
function normalizarUnidad(u){u=(u||'').toString().toLowerCase().trim(); const m={g:['g','gr'],kg:['kg','kilo'],lb:['lb'],oz:['oz'],ml:['ml'],L:['l','lt','L','litro'],pza:['pz','pza','pieza']}; for(let k in m){if(m[k].includes(u)||k===u) return k;} return u||'g';}
function factorABase(u){u=normalizarUnidad(u); let f={g:1,kg:1000,lb:453.592,oz:28.3495,ml:1,L:1000,pza:1}; return f[u]||1;}
function convertir(c,de,a){de=normalizarUnidad(de); a=normalizarUnidad(a); if(de===a) return c; let peso=['g','kg','lb','oz'], vol=['ml','L']; if(peso.includes(de)&&peso.includes(a)) return c*factorABase(de)/factorABase(a); if(vol.includes(de)&&vol.includes(a)) return c*factorABase(de)/factorABase(a); if(a==='pza'||de==='pza') return c; return c;}
function parseCant(v){if(v==null||v==='') return 0; v=String(v).trim().replace(',','.').toLowerCase(); if(v.includes('/')){let p=v.split('/'); return (parseFloat(p[0])||0)/(parseFloat(p[1])||1);} return parseFloat(v)||0;}

function calcBase(){
 let costo=0;
 document.querySelectorAll('#ingSel>div').forEach(r=>{
   let c=parseCant(r.querySelector('.i-cant')?.value);
   let pu=parseFloat(r.querySelector('.i-precio')?.dataset.precio||0);
   if(c>0) costo+=c*pu;
 });
 let el=document.getElementById('costoBase'); if(el) el.innerText=costo.toFixed(2);
 let rend=parseCant(document.getElementById('rendCant')?.value)||1;
 let el2=document.getElementById('costoPorRend'); if(el2) el2.innerText=(rend>0?costo/rend:0).toFixed(4);
}
function addIng(d={}){
 let div=document.createElement('div');
 div.className='flex gap-2 items-center bg-white p-2 rounded-xl border-2 border-black mb-2';
 div.innerHTML=`<input class="i-nombre flex-1 border-2 border-black rounded-xl p-2" placeholder="Ing" value="${d.nombre||''}"><input class="i-cant w-[70px] border-2 border-black rounded-xl p-2" value="${d.cant||'1'}" oninput="calcBase()"><input class="i-precio w-[80px] border-2 border-black rounded-xl p-2" placeholder="$" data-precio="${d.precio||0}" value="${d.precio||''}" oninput="this.dataset.precio=this.value;calcBase()"><button onclick="this.parentElement.remove();calcBase()" class="text-red-600 font-black">X</button>`;
 document.getElementById('ingSel').appendChild(div);
}
function guardarBase(){
 let nombre=document.getElementById('nombreBase').value.trim(); if(!nombre) return alert('Pon nombre');
 let costo=parseFloat(document.getElementById('costoBase').innerText)||0;
 let rendCant=parseCant(document.getElementById('rendCant').value)||1;
 let rendUnit=document.getElementById('rendUnit').value||'g';
 if(editandoId){
   let b=prods.find(x=>x.id==editandoId); b.nombre=nombre; b.costo=costo; b.rendimiento={cant:rendCant,unit:rendUnit}; editandoId=null;
 }else{
   prods.push({id:Date.now().toString(),nombre:nombre,tipo:'base',costo:costo,rendimiento:{cant:rendCant,unit:rendUnit},venta:costo});
 }
 save(); render();
}
function editarBase(id){
 let b=prods.find(x=>x.id==id); editandoId=id; render();
 setTimeout(()=>{document.getElementById('nombreBase').value=b.nombre; document.getElementById('rendCant').value=b.rendimiento.cant; document.getElementById('rendUnit').value=b.rendimiento.unit; document.getElementById('costoBase').innerText=b.costo.toFixed(2); document.getElementById('btnBase').innerText='ACTUALIZAR BASE'; window.scrollTo(0,0);},50);
}
function borrarProd(id){if(!confirm('¿Borrar?')) return; prods=prods.filter(x=>x.id!=id); save(); render();}

function addBase(d={}){
 let bases=getProd().filter(x=>x.tipo==='base');
 if(bases.length===0){alert('Crea base primero'); return;}
 let opts=bases.map(b=>`<option value="${b.id}" ${d.id==b.id?'selected':''}>${b.nombre} $${b.costo.toFixed(2)} rinde ${b.rendimiento.cant} ${b.rendimiento.unit}</option>`).join('');
 let div=document.createElement('div');
 div.className='flex gap-2 items-center flex-wrap bg-yellow-50 p-2 rounded-xl border-2 border-black mb-2';
 div.innerHTML=`<select class="b-sel flex-1 min-w-[140px] border-2 border-black rounded-xl p-2" onchange="calc2()"><option value="">-- Receta --</option>${opts}</select><input class="b-cant w-[80px] border-2 border-black rounded-xl p-2" value="${d.cant||'200'}" oninput="calc2()"><select class="b-unit w-[80px] border-2 border-black rounded-xl p-2" onchange="calc2()"><option value="g" ${d.unit=='g'?'selected':''}>g</option><option value="kg" ${d.unit=='kg'?'selected':''}>kg</option><option value="lb">lb</option><option value="ml">ml</option><option value="L">L</option><option value="pza">pza</option></select><button onclick="this.parentElement.remove();calc2()" class="text-red-600 font-black">X</button>`;
 document.getElementById('basesSel').appendChild(div); calc2();
}
function calc2(){
 let tot=0;
 document.querySelectorAll('#basesSel>div').forEach(row=>{
  let id=row.querySelector('.b-sel')?.value; if(!id) return;
  let cant=parseCant(row.querySelector('.b-cant')?.value);
  let unit=row.querySelector('.b-unit')?.value||'g';
  let b=getProd().find(x=>String(x.id)==String(id)); if(!b) return;
  let rCant=parseCant(b.rendimiento?.cant)||1; let rUnit=normalizarUnidad(b.rendimiento?.unit||'g');
  let conv=convertir(cant,unit,rUnit); if(rCant>0) tot+=(b.costo/rCant)*conv;
 });
 document.getElementById('c-ing2').innerText=tot.toFixed(2);
 let m=parseFloat(document.getElementById('margen2')?.value)||0;
 let vm=document.getElementById('ventaManual2')?.value||'';
 let v=vm!==''?parseCant(vm):tot*(1+m/100);
 document.getElementById('venta2').innerText=v.toFixed(2);
}
function guardarProd(){
 let nombre=document.getElementById('nombre2').value.trim(); let cat=document.getElementById('categoria2').value||'General';
 if(!nombre) return alert('Pon nombre');
 let bases=[]; document.querySelectorAll('#basesSel>div').forEach(r=>{let id=r.querySelector('.b-sel')?.value; let cant=r.querySelector('.b-cant')?.value||0; let unit=r.querySelector('.b-unit')?.value||'g'; if(id) bases.push({id,cant,unit});});
 if(bases.length==0) return alert('Agrega receta');
 let costo=parseFloat(document.getElementById('c-ing2').innerText)||0; let venta=parseFloat(document.getElementById('venta2').innerText)||0;
 if(editandoId){
   let p=prods.find(x=>x.id==editandoId); p.nombre=nombre; p.categoria=cat; p.costo=costo; p.venta=venta; p.bases=bases; editandoId=null;
 }else{
   prods.push({id:Date.now().toString(),nombre:nombre,tipo:'secundario',categoria:cat,costo:costo,venta:venta,bases:bases,rendimiento:{cant:1,unit:'pza'}});
 }
 save(); render();
}
function editarProd(id){
 let p=prods.find(x=>x.id==id); editandoId=id; render();
 setTimeout(()=>{document.getElementById('nombre2').value=p.nombre; document.getElementById('categoria2').value=p.categoria||'General'; document.getElementById('basesSel').innerHTML=''; p.bases.forEach(b=>addBase(b)); calc2(); document.getElementById('btnProd').innerText='ACTUALIZAR PRODUCTO'; window.scrollTo(0,9999);},50);
}

function render(){
 let bases=getProd().filter(x=>x.tipo==='base'); let sec=getProd().filter(x=>x.tipo==='secundario');
 document.getElementById('app').innerHTML=`
 <div class="bg-white border-[3px] border-black rounded-[20px] p-3 shadow-[4px_4px_0_#000]">
  <h2 class="font-black">1) Base / Receta</h2>
  <input id="nombreBase" placeholder="Ej: Salsa BBQ" class="w-full mt-2 border-2 border-black rounded-xl p-3">
  <div id="ingSel" class="mt-2"></div>
  <button onclick="addIng()" class="w-full mt-2 border-2 border-black rounded-xl p-2 font-black">+ Ingrediente</button>
  <div class="flex gap-2 mt-2"><input id="rendCant" value="1" oninput="calcBase()" class="w-[80px] border-2 border-black rounded-xl p-2"><select id="rendUnit" class="w-[80px] border-2 border-black rounded-xl p-2"><option value="kg">kg</option><option value="g">g</option><option value="L">L</option><option value="ml">ml</option><option value="pza">pza</option></select><div class="flex-1 bg-black text-white rounded-xl p-2 text-xs">Costo: $<span id="costoBase">0</span> | $/u: $<span id="costoPorRend">0</span></div></div>
  <button id="btnBase" onclick="guardarBase()" class="w-full mt-2 bg-black text-white rounded-xl p-3 font-black">${editandoId?'ACTUALIZAR BASE':'GUARDAR BASE'}</button>
  <div class="mt-3 space-y-1">${bases.map(b=>`<div class="flex justify-between items-center bg-gray-100 p-2 rounded-xl border-2 border-black"><div class="text-xs"><b>${b.nombre}</b><br>$${b.costo.toFixed(2)} rinde ${b.rendimiento.cant} ${b.rendimiento.unit}</div><div class="flex gap-1"><button onclick="editarBase('${b.id}')" class="bg-yellow-300 border-2 border-black rounded-lg px-2 py-1 text-xs font-black">EDITAR</button><button onclick="borrarProd('${b.id}')" class="bg-red-500 text-white border-2 border-black rounded-lg px-2 py-1 text-xs font-black">X</button></div></div>`).join('')||'Sin bases'}</div>
 </div>
 <div class="bg-white border-[3px] border-black rounded-[20px] p-3 shadow-[4px_4px_0_#000]">
  <h2 class="font-black">2) Producto + Categoría (con gramos)</h2>
  <div class="flex gap-2 mt-2"><input id="nombre2" placeholder="Ej: Alitas 10 pzas" class="flex-1 border-2 border-black rounded-xl p-3"><select id="categoria2" class="w-[120px] border-2 border-black rounded-xl p-3"><option>Alitas</option><option>Burgers</option><option>Boneless</option><option>Bebidas</option><option>General</option></select></div>
  <div id="basesSel" class="mt-2"></div>
  <button onclick="addBase()" class="w-full mt-2 bg-yellow-300 border-2 border-black rounded-xl p-3 font-black">+ AGREGAR RECETA (elige g/kg)</button>
  <div class="bg-black text-white rounded-2xl p-4 mt-3"><div class="flex justify-between"><span>Costo:</span><b>$<span id="c-ing2">0.00</span></b></div><div class="flex justify-between text-yellow-300"><span>Venta:</span><b>$<span id="venta2">0.00</span></b></div><div class="flex gap-2 mt-3"><input id="margen2" value="100" type="number" oninput="calc2()" class="w-[70px] text-black rounded-xl p-2">%<input id="ventaManual2" placeholder="$ manual" oninput="calc2()" class="flex-1 text-black rounded-xl p-2"></div></div>
  <button id="btnProd" onclick="guardarProd()" class="w-full mt-3 p-4 bg-black text-white rounded-2xl font-black">${editandoId?'ACTUALIZAR PRODUCTO':'GUARDAR PRODUCTO'}</button>
  <div class="mt-3 space-y-1">${sec.map(p=>`<div class="flex justify-between items-center bg-yellow-50 p-2 rounded-xl border-2 border-black"><div class="text-xs"><b>${p.nombre}</b> [${p.categoria}]<br>$${p.costo.toFixed(2)} -> $${p.venta.toFixed(2)}<br><span class="text-[10px]">${p.bases.map(b=>{let rb=getProd().find(x=>x.id==b.id); return (rb?rb.nombre:'?')+' '+b.cant+' '+b.unit}).join(', ')}</span></div><div class="flex gap-1"><button onclick="editarProd('${p.id}')" class="bg-yellow-300 border-2 border-black rounded-lg px-2 py-1 text-xs font-black">EDITAR</button><button onclick="borrarProd('${p.id}')" class="bg-red-500 text-white border-2 border-black rounded-lg px-2 py-1 text-xs font-black">X</button></div></div>`).join('')||'Sin productos'}</div>
 </div>`;
 calcBase(); calc2();
}
render();
</script>
</body>
</html>


"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
