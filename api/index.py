from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi Negocio 10.1</title>
<style>
body{font-family:system-ui;background:#fff7ed;margin:0}
header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:white;border-bottom:1px solid #eee}
h1{font-size:22px;margin:0}
.card{background:white;border-radius:16px;padding:16px;margin:12px;box-shadow:0 2px 10px rgba(0,0,0,.06)}
input{width:100%;padding:12px;border-radius:12px;border:2px solid #000;margin:6px 0;font-size:16px;box-sizing:border-box}
.btn{width:100%;padding:14px;border-radius:12px;border:0;background:black;color:white;font-weight:bold;font-size:16px}
.pay-box{background:black;color:white;border-radius:16px;padding:16px}
</style>
</head>
<body>
<header>
  <div style="display:flex;align-items:center;gap:8px">
    <img src="https://i.imgur.com/8Km9tLL.png" width="36" style="border-radius:50%">
    <h1>Mi Negocio 10.1 Pagos Auto</h1>
  </div>
  <button style="background:black;color:white;border-radius:20px;padding:8px 14px;border:0">Config</button>
</header>

<div class="card pay-box">
  <h3>💳 Conectar pagos - Mercado Pago</h3>
  <p style="opacity:.8;font-size:13px">Pega tu Access Token de Mercado Pago y se guardará automático.</p>
  <input id="mp_token" placeholder="APP_USR-xxxxxxxxxxxxxxxx" style="background:#222;color:white;border-color:#444">
  <button class="btn" style="background:white;color:black;margin-top:8px" onclick="guardarToken()">Conectar pagos</button>
  <p id="status" style="font-size:13px;margin-top:8px"></p>
</div>

<div class="card">
  <h2>⚙️ Config Ticket + Logo</h2>
  <label>📷 Logo</label>
  <input type="file">
  <div style="margin:8px 0">Vista previa - Snoopy</div>
  <input value="Mi Negocio">
  <input value="La que sea">
  <div style="display:flex;gap:8px">
    <input value="5966666">
    <input value="3510000000">
  </div>
</div>

<script>
function guardarToken(){
  const token = document.getElementById('mp_token').value;
  if(!token){ alert('Pega tu token'); return; }
  fetch('/api/save_token',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})})
  .then(r=>r.json()).then(d=>{
    document.getElementById('status').innerText = d.message;
  });
}
</script>
</body>
</html>
"""

TOKEN_FILE = "/tmp/mp_token.txt"

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/save_token', methods=['POST'])
def save_token():
    data = request.get_json()
    token = data.get('token','').strip()
    if not token.startswith('APP_USR-'):
        return jsonify({"message": "❌ Token no válido, debe empezar con APP_USR-"}), 400
    # Guardar token
    with open(TOKEN_FILE,'w') as f:
        f.write(token)
    # Probar token con Mercado Pago
    try:
        r = requests.get("https://api.mercadopago.com/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if r.status_code == 200:
            return jsonify({"message": "✅ Conectado a Mercado Pago correctamente"})
        else:
            return jsonify({"message": f"⚠️ Token guardado pero MP respondió {r.status_code}: {r.text[:100]}"})
    except Exception as e:
        return jsonify({"message": f"✅ Token guardado (no se pudo validar: {e})"})

# Vercel necesita esto
if __name__ == '__main__':
    app.run()
