import os,json,urllib.parse,urllib.request,urllib.error,base64
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
def get(n):
 u=e('SUPABASE_URL');k=e('SUPABASE_SERVICE_ROLE_KEY');q=urllib.parse.quote(str(n),safe='');r=urllib.request.Request(f'{u.rstrip("/")}/rest/v1/negocio_data?user_id=eq.{q}&select=data');r.add_header('apikey',k);r.add_header('Authorization','Bearer '+k)
 with urllib.request.urlopen(r,timeout=10) as x:a=json.loads(x.read().decode() or '[]');return (a[0].get('data') or {}) if a else {}
def save(n,d):
 u=e('SUPABASE_URL');k=e('SUPABASE_SERVICE_ROLE_KEY');body=json.dumps({'user_id':str(n).lower(),'data':d}).encode();r=urllib.request.Request(u.rstrip('/')+'/rest/v1/negocio_data',data=body,method='POST');r.add_header('apikey',k);r.add_header('Authorization','Bearer '+k);r.add_header('Content-Type','application/json');r.add_header('Prefer','resolution=merge-duplicates')
 with urllib.request.urlopen(r,timeout=10) as x:x.read()
def stripe_deauth(a):
 key=e('STRIPE_SECRET_KEY');cid=e('STRIPE_CONNECT_CLIENT_ID','STRIPE_CLIENT_ID');data=urllib.parse.urlencode({'client_id':cid,'stripe_user_id':a}).encode();r=urllib.request.Request('https://connect.stripe.com/oauth/deauthorize',data=data,method='POST');r.add_header('Authorization','Basic '+base64.b64encode((key+':').encode()).decode());r.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(r,timeout=20) as x:return json.loads(x.read().decode() or '{}')
class handler(BaseHTTPRequestHandler):
 def do_OPTIONS(self):sj(self,{})
 def do_POST(self):
  try:
   n=str(rj(self).get('negocio_id') or '').strip();d=get(n);a=d.get('stripe_account_id') or d.get('stripeAccountId') or ''
   if a:stripe_deauth(a)
   d.update({'stripe_account_id':'','stripe_connected':False});save(n,d);sj(self,{'ok':True})
  except Exception as ex:sj(self,{'ok':False,'msg':str(ex)},500)
