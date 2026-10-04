import os,json,urllib.parse,urllib.request,urllib.error
from http.server import BaseHTTPRequestHandler
def sj(h,o,c=200):h.send_response(c);h.send_header('Access-Control-Allow-Origin','*');h.send_header('Access-Control-Allow-Methods','POST, OPTIONS');h.send_header('Access-Control-Allow-Headers','Content-Type');h.send_header('Content-Type','application/json');h.end_headers();h.wfile.write(json.dumps(o).encode())
def rj(h):
 try:n=int(h.headers.get('Content-Length','0'));return json.loads(h.rfile.read(n).decode() or '{}')
 except:return {}
def e(*x):
 for n in x:
  v=os.getenv(n,'').strip()
  if v:return v
 return ''
def data(n):
 u=e('SUPABASE_URL');k=e('SUPABASE_SERVICE_ROLE_KEY')
 if not u or not k:return {}
 q=urllib.parse.quote(str(n),safe='');r=urllib.request.Request(f'{u.rstrip("/")}/rest/v1/negocio_data?user_id=eq.{q}&select=data');r.add_header('apikey',k);r.add_header('Authorization','Bearer '+k)
 try:
  with urllib.request.urlopen(r,timeout=10) as x:a=json.loads(x.read().decode() or '[]');return (a[0].get('data') or {}) if a else {}
 except:return {}
class handler(BaseHTTPRequestHandler):
 def do_OPTIONS(self):sj(self,{})
 def do_POST(self):
  n=str(rj(self).get('negocio_id') or '').strip();d=data(n);a=d.get('stripe_account_id') or d.get('stripeAccountId') or '';sj(self,{'ok':True,'connected':bool(a and d.get('stripe_connected',True)),'account_id':a if a else ''})
