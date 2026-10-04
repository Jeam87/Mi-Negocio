import os, json, urllib.parse, urllib.request, urllib.error, hmac, hashlib, base64, time
from http.server import BaseHTTPRequestHandler

def send_json(h,o,c=200):
 h.send_response(c); h.send_header('Access-Control-Allow-Origin','*'); h.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS'); h.send_header('Access-Control-Allow-Headers','Content-Type, Authorization'); h.send_header('Content-Type','application/json; charset=utf-8'); h.end_headers(); h.wfile.write(json.dumps(o,ensure_ascii=False).encode())
def read_json(h):
 try:
  n=int(h.headers.get('Content-Length','0')); return json.loads(h.rfile.read(n).decode() or '{}') if n else {}
 except: return {}
def env(*ns):
 for n in ns:
  v=(os.environ.get(n) or '').strip()
  if v:return v
 return ''
def sk(): return env('STRIPE_SECRET_KEY')
def cid(): return env('STRIPE_CONNECT_CLIENT_ID','STRIPE_CLIENT_ID')
def baseurl(h):
 v=env('APP_URL','NEXT_PUBLIC_APP_URL','SITE_URL','VERCEL_URL')
 if v:return ('https://'+v if not v.startswith('http') else v).rstrip('/')
 return ('https://'+(h.headers.get('x-forwarded-host') or h.headers.get('host') or '')).rstrip('/')
def redirect_uri(h): return baseurl(h)+'/api/stripe/connect'
def state_make(n):
 raw=json.dumps({'n':str(n),'t':int(time.time())},separators=(',',':')).encode(); sig=hmac.new(sk().encode(),raw,hashlib.sha256).digest(); return base64.urlsafe_b64encode(raw+b'.'+sig).decode().rstrip('=')
def state_read(s):
 try:
  b=base64.urlsafe_b64decode(s+'='*(-len(s)%4)); raw,sig=b.rsplit(b'.',1)
  if not hmac.compare_digest(sig,hmac.new(sk().encode(),raw,hashlib.sha256).digest()):return None
  x=json.loads(raw.decode()); return x['n'] if int(time.time())-int(x['t'])<=900 else None
 except:return None
def stripe(path,method='GET',form=None):
 if not sk():raise RuntimeError('Falta STRIPE_SECRET_KEY en Vercel.')
 data=urllib.parse.urlencode(form).encode() if form is not None else None
 r=urllib.request.Request('https://api.stripe.com'+path,data=data,method=method); r.add_header('Authorization','Basic '+base64.b64encode((sk()+':').encode()).decode())
 if data:r.add_header('Content-Type','application/x-www-form-urlencoded')
 try:
  with urllib.request.urlopen(r,timeout=20) as x:return json.loads(x.read().decode() or '{}')
 except urllib.error.HTTPError as e:
  raw=e.read().decode() if e.fp else ''
  try:msg=json.loads(raw).get('error',{}).get('message') or raw
  except:msg=raw
  raise RuntimeError(msg or 'Error de Stripe')
def save(n,patch):
 u=env('SUPABASE_URL'); k=env('SUPABASE_SERVICE_ROLE_KEY')
 if not u or not k:raise RuntimeError('Falta SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY.')
 q=urllib.parse.quote(str(n),safe=''); req=urllib.request.Request(f'{u.rstrip("/")}/rest/v1/negocio_data?user_id=eq.{q}&select=data'); req.add_header('apikey',k); req.add_header('Authorization','Bearer '+k)
 try:
  with urllib.request.urlopen(req,timeout=10) as r:a=json.loads(r.read().decode() or '[]')
 except:a=[]
 d=(a[0].get('data') or {}) if a else {}; d.update(patch); body=json.dumps({'user_id':str(n).lower(),'data':d}).encode(); req=urllib.request.Request(u.rstrip('/')+'/rest/v1/negocio_data',data=body,method='POST'); req.add_header('apikey',k); req.add_header('Authorization','Bearer '+k); req.add_header('Content-Type','application/json'); req.add_header('Prefer','resolution=merge-duplicates')
 with urllib.request.urlopen(req,timeout=10) as r:r.read()
class handler(BaseHTTPRequestHandler):
 def do_OPTIONS(self):send_json(self,{})
 def do_POST(self):
  d=read_json(self); n=str(d.get('negocio_id') or '').strip()
  if not n:return send_json(self,{'ok':False,'msg':'Falta negocio_id.'},400)
  if not cid() or not sk():return send_json(self,{'ok':False,'msg':'Falta STRIPE_CONNECT_CLIENT_ID o STRIPE_SECRET_KEY en Vercel.'},500)
  u='https://connect.stripe.com/oauth/authorize?'+urllib.parse.urlencode({'response_type':'code','client_id':cid(),'scope':'read_write','redirect_uri':redirect_uri(self),'state':state_make(n)})
  return send_json(self,{'ok':True,'url':u})
 def do_GET(self):
  q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
  if q.get('error'):return self.redir('/?stripe=cancelled')
  code=(q.get('code',[''])[0] or '').strip(); n=state_read((q.get('state',[''])[0] or '').strip())
  if not code or not n:return self.redir('/?stripe=invalid_state')
  try:
   r=stripe('/v1/oauth/token','POST',{'client_secret':sk(),'code':code,'grant_type':'authorization_code'}); aid=r.get('stripe_user_id') or r.get('stripe_account_id')
   if not aid:raise RuntimeError('Stripe no devolvió la cuenta conectada.')
   save(n,{'stripe_account_id':aid,'stripe_connected':True}); return self.redir('/?stripe=connected')
  except:return self.redir('/?stripe=error')
 def redir(self,u):self.send_response(302);self.send_header('Location',u);self.send_header('Cache-Control','no-store');self.end_headers()
