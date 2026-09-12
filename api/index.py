import os
import json
from datetime import datetime
from flask import Flask, request, redirect, session, url_for, render_template_string
import bcrypt

app = Flask(__name__)
app.secret_key = 'la-piedad-2024-carpinteria-secreto'

# --- FIX VERCEL: esto es lo que hacía que no entraras ---
BASE_DATA = '/tmp/data'
os.makedirs(BASE_DATA, exist_ok=True)
USERS_FILE = os.path.join(BASE_DATA, 'users.json')
PRESUP_FILE = os.path.join(BASE_DATA, 'presupuestos.json')
VENTAS_FILE = os.path.join(BASE_DATA, 'ventas.json')

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ESTO TE ARREGLA EL LOGIN - Siempre crea tu cuenta si se borró
def ensure_default_user():
    users = load_json(USERS_FILE)
    if "esaul_1987@hotmail.com" not in users:
        hashed = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
        users["esaul_1987@hotmail.com"] = {
            "password": hashed,
            "nombre": "Esaul",
            "rol": "admin"
        }
        save_json(USERS_FILE, users)
    return users

ensure_default_user()

# --- HTML BASE ---
BASE_HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial; background:#f5f5f5; padding:15px}
.card{background:#fff; padding:15px; border-radius:12px; margin-bottom:12px; box-shadow:0 2px 5px #0001}
input,textarea{width:100%; padding:12px; margin:6px 0; border:1px solid #ccc; border-radius:8px; box-sizing:border-box}
button{padding:12px 16px; border:none; border-radius:8px; font-weight:bold; cursor:pointer}
.btn-black{background:#111; color:#fff; width:100%}
.btn-orange{background:orange; color:#fff}
.btn-green{background:#25D366; color:#fff}
.btn-red{background:#ff4444; color:#fff}
</style>
</head>
<body>
{% if user %}<div style="display:flex;justify-content:space-between"><b>{{user}}</b><a href="/logout">Salir</a></div>{% endif %}
{{content|safe}}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    ensure_default_user()
    error = ""
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        pwd = request.form.get('password','')
        users = load_json(USERS_FILE)
        if email in users and bcrypt.checkpw(pwd.encode(), users[email]['password'].encode()):
            session['user'] = email
            return redirect('/dashboard')
        else:
            error = "Correo o contraseña incorrectos. Usa: esaul_1987@hotmail.com / 123456"

    content = f"""
    <div class="card" style="max-width:400px;margin:60px auto">
        <h2>Mi Negocio - Entrar</h2>
        <p style="color:red">{error}</p>
        <form method="post">
            <input name="email" placeholder="Correo" value="esaul_1987@hotmail.com">
            <input name="password" type="password" placeholder="Contraseña" value="123456">
            <button class="btn-black">ENTRAR</button>
        </form>
        <p style="font-size:13px;margin-top:15px">Si no te dejaba entrar era porque Vercel borró el archivo. Con este código ya se vuelve a crear solo.</p>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, user=None)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    presup = load_json(PRESUP_FILE)
    lista = ""
    for pid, p in presup.items():
        estado_color = "orange" if p['estado']=="pendiente" else "green" if p['estado']=="autorizado" else "red"
        lista += f"""
        <div class="card">
            <b>{p['cliente']}</b> - {p['concepto']} - ${p['total']}<br>
            <small>{p['fecha']} | Estado: <span style="color:{estado_color}">{p['estado']}</span></small><br><br>
            <a href="https://wa.me/52{p['telefono']}?text={p['mensaje']}" target="_blank"><button class="btn-green">📲 Mandar WhatsApp</button></a>
            <a href="/autorizar/{pid}"><button class="btn-black">✓ Autorizar y pasar a producción</button></a>
            <a href="/borrar/{pid}"><button class="btn-red">Borrar</button></a>
        </div>
        """

    content = f"""
    <div class="card">
        <h3>Nuevo Presupuesto (No cobra hasta autorizar)</h3>
        <form method="post" action="/nuevo_presupuesto">
            <input name="cliente" placeholder="Nombre cliente" required>
            <input name="telefono" placeholder="WhatsApp 10 digitos" required>
            <input name="concepto" placeholder="Ej: Closet 2 puertas" required>
            <input name="total" type="number" placeholder="Total $" required>
            <button class="btn-orange">📄 Guardar Presupuesto</button>
        </form>
    </div>
    <h3>Presupuestos pendientes</h3>
    {lista if lista else "<div class='card'>No hay presupuestos aún</div>"}
    """
    return render_template_string(BASE_HTML, content=content, user=session['user'])

@app.route('/nuevo_presupuesto', methods=['POST'])
def nuevo_presupuesto():
    if 'user' not in session:
        return redirect('/login')
    presup = load_json(PRESUP_FILE)
    pid = str(int(datetime.now().timestamp()))
    cliente = request.form['cliente']
    telefono = request.form['telefono']
    concepto = request.form['concepto']
    total = request.form['total']
    mensaje = f"*PRESUPUESTO - {concepto}*%0ACliente: {cliente}%0ATotal: ${total}%0A%0AValido por 3 dias.%0AResponde SI para autorizar."
    presup[pid] = {
        "cliente": cliente,
        "telefono": telefono,
        "concepto": concepto,
        "total": total,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "estado": "pendiente",
        "mensaje": mensaje
    }
    save_json(PRESUP_FILE, presup)
    return redirect('/dashboard')

@app.route('/autorizar/<pid>')
def autorizar(pid):
    presup = load_json(PRESUP_FILE)
    ventas = load_json(VENTAS_FILE)
    if pid in presup:
        presup[pid]['estado'] = "autorizado"
        ventas[pid] = presup[pid]
        save_json(PRESUP_FILE, presup)
        save_json(VENTAS_FILE, ventas)
    return redirect('/dashboard')

@app.route('/borrar/<pid>')
def borrar(pid):
    presup = load_json(PRESUP_FILE)
    if pid in presup:
        del presup[pid]
        save_json(PRESUP_FILE, presup)
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Para Vercel
if __name__ == '__main__':
    app.run(debug=True)
