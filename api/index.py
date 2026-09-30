from flask import Flask, jsonify, send_file, request, redirect, Response
import os, json, secrets, urllib.parse
from datetime import datetime
from supabase import create_client

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

BASE_DATA = '/tmp/data' if os.path.exists('/tmp') else 'data'
os.makedirs(BASE_DATA, exist_ok=True)

def _stripe_file(nid):
    safe=str(nid or '').replace('@','_at_').replace('.','_').replace('/','_')
    return os.path.join(BASE_DATA, f"{safe}_stripe.json")
def _stripe_data(nid):
    if not nid: return {}
    try:
        ruta=_stripe_file(nid)
        if os.path.exists(ruta):
            with open(ruta,'r') as f: return json.load(f)
    except: pass
    return {}
def _save_stripe_data(nid, data):
    try:
        with open(_stripe_file(nid),'w') as f: json.dump(data,f)
    except: pass
def _stripe_connect_url(negocio_id):
    client_id=os.environ.get('STRIPE_CONNECT_CLIENT_ID','').strip()
    if not client_id: return None, 'Falta STRIPE_CONNECT_CLIENT_ID'
    state=secrets.token_urlsafe(32)
    sd=_stripe_data(negocio_id); sd['stripe_oauth_state']=state; _save_stripe_data(negocio_id,sd)
    redirect_uri=os.environ.get('STRIPE_CONNECT_REDIRECT_URI','').strip() or (request.url_root.rstrip('/')+'/api/stripe/callback')
    params={'response_type':'code','client_id':client_id,'scope':'read_write','redirect_uri':redirect_uri,'state':state}
    return 'https://connect.stripe.com/oauth/authorize?'+urllib.parse.urlencode(params), None
def _email_respaldo(e): return str(e or "").lower().strip() or None

@app.route('/manifest.json')
def manifest():
    return jsonify({"name":"Mi Negocio 11.5","short_name":"Mi Negocio","start_url":"/","display":"standalone","icons":[{"src":"/logo.png","sizes":"512x512","type":"image/png"}]})

@app.route('/logo.png')
@app.route('/api/logo.png')
def logo_file():
    for ruta in ['logo.png','api/logo.png', os.path.join(os.path.dirname(__file__), '..', 'logo.png')]:
        try:
            if os.path.exists(ruta): return send_file(ruta, mimetype='image/png')
        except: pass
    return "",204

@app.route('/api/stripe/connect', methods=['POST'])
def stripe_connect():
    d=request.get_json(silent=True) or {}
    url,msg=_stripe_connect_url(d.get('negocio_id'))
    if not url: return jsonify({'ok':False,'msg':msg}),400
    return jsonify({'ok':True,'url':url})

@app.route('/api/stripe/callback')
def stripe_callback():
    try:
        code=request.args.get('code',''); state=request.args.get('state','')
        if request.args.get('error'): return redirect('/?stripe=cancelled')
        if not code or not state: return redirect('/?stripe=error')
        negocio_id=None; sd={}
        for nombre in os.listdir(BASE_DATA):
            if not nombre.endswith('_stripe.json'): continue
            try:
                with open(os.path.join(BASE_DATA,nombre),'r') as f:
                    datos=json.load(f)
                    if datos.get('stripe_oauth_state')==state:
                        negocio_id=nombre[:-12]; sd=datos; break
            except: continue
        if not negocio_id: return redirect('/?stripe=invalid_state')
        secret=os.environ.get('STRIPE_SECRET_KEY','').strip()
        client_id=os.environ.get('STRIPE_CONNECT_CLIENT_ID','').strip()
        import stripe; stripe.api_key=secret
        tok=stripe.OAuth.token(grant_type='authorization_code', code=code)
        acct=tok.get('stripe_user_id')
        if not acct: return redirect('/?stripe=error')
        sd['stripe_account_id']=acct; sd['stripe_connected']=True
        sd['stripe_connected_at']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sd.pop('stripe_oauth_state',None); _save_stripe_data(negocio_id,sd)
        return redirect('/?stripe=connected')
    except: return redirect('/?stripe=error')

@app.route('/api/stripe/status', methods=['POST'])
def stripe_status():
    d=request.get_json(silent=True) or {}; nid=str(d.get('negocio_id') or '').strip()
    sd=_stripe_data(nid)
    return jsonify({'ok':True,'connected':bool(sd.get('stripe_account_id')),'account_id':sd.get('stripe_account_id','')})

@app.route('/api/stripe/disconnect', methods=['POST'])
def stripe_disconnect():
    d=request.get_json(silent=True) or {}; nid=str(d.get('negocio_id') or '').strip()
    sd=_stripe_data(nid); sd.pop('stripe_account_id',None); _save_stripe_data(nid,sd)
    return jsonify({'ok':True})

@app.route('/api/crear-link-cobro', methods=['POST'])
def crear_link_cobro():
    import stripe; stripe.api_key=os.environ.get("STRIPE_SECRET_KEY","").strip()
    d=request.get_json(silent=True) or {}; nid=str(d.get('negocio_id') or '').strip()
    sd=_stripe_data(nid); acct=sd.get('stripe_account_id') if sd else ''
    if not acct: return jsonify({'ok':False,'msg':'Conecta Stripe primero'}),400
    monto=int(round(float(d.get('monto',0))*100))
    if monto<=0: return jsonify({'ok':False,'msg':'Monto invalido'}),400
    fee=int(round(monto*0.015))
    link=stripe.PaymentLink.create(
        line_items=[{"price_data":{"currency":"mxn","product_data":{"name":d.get('concepto','Cobro')},"unit_amount":monto},"quantity":1}],
        application_fee_amount=fee, stripe_account=acct
    )
    return jsonify({"ok":True,"url":link.url})

@app.route('/api/register', methods=['POST'])
def api_register():
    d=request.get_json(silent=True) or {}; email=str(d.get('email') or '').lower().strip(); pwd=str(d.get('password') or '')
    if not email or not pwd: return jsonify({"ok":False,"msg":"Pon correo y contraseña"}),400
    res=supabase.auth.sign_up({"email":email,"password":pwd})
    if not res.user: return jsonify({"ok":False,"msg":"No se creo"}),400
    return jsonify({"ok":True,"email":email,"negocio_id":str(res.user.id)})

@app.route('/api/login', methods=['POST'])
def api_login():
    d=request.get_json(silent=True) or {}; email=str(d.get('email') or '').lower().strip(); pwd=str(d.get('password') or '')
    res=supabase.auth.sign_in_with_password({"email":email,"password":pwd})
    if not res.user: return jsonify({"ok":False,"msg":"Credenciales incorrectas"}),401
    return jsonify({"ok":True,"email":email,"negocio_id":str(res.user.id)})

@app.route('/api/load', methods=['GET'])
def api_load():
    negocio_id=str(request.args.get('negocio_id') or '').strip(); email=_email_respaldo(request.args.get('email'))
    res=supabase.table("respaldo").select("datos").eq("email",email).limit(1).execute()
    rows=res.data or []; data=rows[0].get("datos") if rows else {}
    return jsonify({"ok":True,"data":data if isinstance(data,dict) else {}})

@app.route('/api/save', methods=['POST'])
def api_save():
    d=request.get_json(silent=True) or {}; negocio_id=str(d.get('negocio_id') or '').strip(); email=_email_respaldo(d.get('email')); data=d.get('data') or {}
    supabase.table("respaldo").upsert({"email":email,"datos":data}, on_conflict="email").execute()
    return jsonify({"ok":True})

@app.route('/api/entregas', methods=['GET'])
def api_entregas():
    negocio_id=str(request.args.get('negocio_id') or '').strip()
    res=supabase.table('entregas_programadas').select('*').eq('negocio_id',negocio_id).order('fecha_entrega').execute()
    return jsonify({'ok':True,'entregas':res.data or []})

@app.route('/api/entregas', methods=['POST'])
def api_crear_entrega():
    d=request.get_json(silent=True) or {}; negocio_id=str(d.get('negocio_id') or '').strip()
    registro={
        'negocio_id':negocio_id,
        'fecha_venta':d.get('fecha_venta'),
        'fecha_entrega':d.get('fecha_entrega'),
        'hora_entrega':d.get('hora_entrega'),
        'contenido':d.get('contenido'),
        'observaciones':d.get('observaciones'),
        'quien_ordena':d.get('quien_ordena'),
        'telefono_ordena':d.get('telefono_ordena'),
        'entregar_a':d.get('entregar_a'),
        'estado':d.get('estado') or 'pendiente'
    }
    res=supabase.table('entregas_programadas').insert(registro).execute()
    return jsonify({'ok':True,'entrega':(res.data or [None])[0]})

@app.route('/api/entregas/<entrega_id>', methods=['PATCH'])
def api_actualizar_entrega(entrega_id):
    negocio_id=str(request.args.get('negocio_id') or '').strip()
    d=request.get_json(silent=True) or {}
    res=supabase.table('entregas_programadas').update({'estado':d.get('estado')}).eq('id',entrega_id).eq('negocio_id',negocio_id).execute()
    return jsonify({'ok':True})

@app.route('/')
def home():
    # CORRECCIÓN 404: como está en api/, el index.html está un nivel arriba
    base_dir = os.path.dirname(__file__)
    index_path = os.path.join(base_dir, '..', 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    return send_file(os.path.join(base_dir, 'index.html')) if os.path.exists(os.path.join(base_dir, 'index.html')) else ("index.html no encontrado",404)

@app.route('/api/autoguardado')
def autoguardado():
    js = """setInterval(()=>{ let e=localStorage.getItem("session_email"); if(!e) return; let all={}; for(let i=0;i<localStorage.length;i++){let k=localStorage.key(i); try{all[k]=JSON.parse(localStorage.getItem(k))}catch{all[k]=localStorage.getItem(k)}} fetch("/api/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({negocio_id:localStorage.getItem("session_negocio"),email:e,data:all})}); },15000);"""
    return Response(js, mimetype='application/javascript')
