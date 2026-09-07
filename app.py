from flask import Flask, jsonify, send_file, request
import os, json
from datetime import datetime

app = Flask(__name__)

# VERCEL FIX: en Vercel solo /tmp es escribible
BASE_DATA = '/tmp/data' if os.path.exists('/tmp') else 'data'
os.makedirs(BASE_DATA, exist_ok=True)
USERS_FILE = os.path.join(BASE_DATA, 'users.json')

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE,'r') as f:
                return json.load(f)
    except: pass
    return {}

def save_users(u):
    try:
        with open(USERS_FILE,'w') as f:
            json.dump(u,f)
    except Exception as e:
        print("Error save:", e)

def get_user_file(negocio_id):
    safe = negocio_id.replace("@","_at_").replace(".","_")
    return os.path.join(BASE_DATA, f"{safe}.json")

@app.route('/manifest.json')
def manifest():
    return jsonify({"name": "Mi Negocio 10.0","short_name": "Mi Negocio","start_url": "/","display": "standalone"})

@app.route('/logo.png')
def logo_file():
    try:
        if os.path.exists('logo.png'):
            return send_file('logo.png', mimetype='image/png')
        return "", 204
    except:
        return "", 204

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        d=request.json
        email=d.get('email','').lower().strip()
        pwd=d.get('password','')
        if not email or not pwd:
            return jsonify({"ok":False,"msg":"Falta correo"}),400
        users=load_users()
        if email in users:
            return jsonify({"ok":False,"msg":"Ya existe, dale Entrar"}),400
        users[email]={"password":pwd,"negocio_id":email,"rol":"owner"}
        save_users(users)
        with open(get_user_file(email),'w') as f:
            json.dump({},f)
        return jsonify({"ok":True,"email":email,"negocio_id":email})
    except Exception as e:
        print(e)
        return jsonify({"ok":False,"msg":"Error servidor: "+str(e)}),500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        d=request.json
        email=d.get('email','').lower().strip()
        pwd=d.get('password','')
        users=load_users()
        if email not in users or users[email]['password']!=pwd:
            return jsonify({"ok":False,"msg":"Correo o contraseña incorrecta"}),401
        return jsonify({"ok":True,"email":email,"negocio_id":users[email]['negocio_id'],"rol":users[email]['rol']})
    except Exception as e:
        return jsonify({"ok":False,"msg":str(e)}),500

@app.route('/api/invite', methods=['POST'])
def api_invite():
    try:
        d=request.json
        owner=d.get('owner_email','').lower().strip()
        owner_pwd=d.get('owner_password','')
        colab=d.get('colab_email','').lower().strip()
        colab_pwd=d.get('colab_password','') or '1234'
        users=load_users()
        if owner not in users or users[owner]['password']!=owner_pwd:
            return jsonify({"ok":False,"msg":"No autorizado"}),403
        users[colab]={"password":colab_pwd,"negocio_id":users[owner]['negocio_id'],"rol":"colab"}
        save_users(users)
        return jsonify({"ok":True,"msg":f"Colaborador {colab} agregado"})
    except Exception as e:
        return jsonify({"ok":False,"msg":str(e)}),500

@app.route('/api/load', methods=['GET'])
def api_load():
    try:
        email=request.args.get('email','').lower().strip()
        users=load_users()
        if email not in users:
            return jsonify({"ok":False,"msg":"No existe"}),404
        negocio_id=users[email]['negocio_id']
        fname=get_user_file(negocio_id)
        if os.path.exists(fname):
            with open(fname,'r') as f: data=json.load(f)
        else: data={}
        return jsonify({"ok":True,"data":data,"negocio_id":negocio_id})
    except Exception as e:
        return jsonify({"ok":False,"msg":str(e)}),500

@app.route('/api/save', methods=['POST'])
def api_save():
    try:
        d=request.json
        email=d.get('email','').lower().strip()
        data=d.get('data',{})
        users=load_users()
        if email not in users:
            return jsonify({"ok":False}),404
        negocio_id=users[email]['negocio_id']
        fname=get_user_file(negocio_id)
        with open(fname,'w') as f: json.dump(data,f)
        return jsonify({"ok":True})
    except Exception as e:
        return jsonify({"ok":False,"msg":str(e)}),500

@app.route('/')
def home():
 #... PEGA AQUÍ TODO TU HTML DE LA VERSIÓN 10.0 QUE YA TENÍAS (el que tiene login)...
 # Para no hacerte copiar 800 lineas, usa el mismo HTML del archivo anterior
 return """<!DOCTYPE html><html><head>...TU HTML COMPLETO DE LA VERSION 10 AQUI...</head></html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
