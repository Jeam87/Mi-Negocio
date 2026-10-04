import os,json,urllib.parse,urllib.request,urllib.error,base64
from http.server import BaseHTTPRequestHandler
def sj(h,o,c=200):h.send_response(c);h.send_header('Access-Control-Allow-Origin','*');h.send_header('Access-Control-Allow-Methods','POST, OPTIONS');h.send_header('Access-Control-Allow-Headers','Content-Type');h.send_header('Content-Type','application/json');h.end_headers();h.wfile.write(json.dumps(o,ensure_ascii=False).encode())
def rj(h):
 try:n=int(h.headers.get('Content-Length','0'));return json.loads(h.rfile.read(n).decode() or '{}')
 except:return {}
def e(n):return os.getenv(n,'').strip()
def get(n):
 u=e('SUPABASE_URL');k=e('SUPABASE_SERVICE_ROLE_KEY');q=urllib.parse.quote(str(n),safe='');r=urllib.request.Request(f'{u.rstrip("/")}/rest/v1/negocio_data?user_id=eq.{q}&select=data');r.add_header('apikey',k);r.add_header('Authorization','Bearer '+k)
 with urllib.request.urlopen(r,timeout=10) as x:a=json.loads(x.read().decode() or '[]');return (a[0].get('data') or {}) if a else {}
def stripe(path,form,account):
 key=e('STRIPE_SECRET_KEY');body=urllib.parse.urlencode(form).encode();r=urllib.request.Request('https://api.stripe.com'+path,data=body,method='POST');r.add_header('Authorization','Basic '+base64.b64encode((key+':').encode()).decode());r.add_header('Content-Type','application/x-www-form-urlencoded');r.add_header('Stripe-Account',account)
 try:
  with urllib.request.urlopen(r,timeout=20) as x:return json.loads(x.read().decode() or '{}')
 except urllib.error.HTTPError as ex:
  raw=ex.read().decode() if ex.fp else ''
  try:msg=json.loads(raw).get('error',{}).get('message') or raw
  except:msg=raw
  raise RuntimeError(msg or 'Error de Stripe')
class handler(BaseHTTPRequestHandler):
 def do_OPTIONS(self):sj(self,{})
 def do_POST(self):
  try:
   d=rj(self);n=str(d.get('negocio_id') or '').strip();m=float(d.get('monto') or 0);concepto=str(d.get('concepto') or 'Compra').strip()[:120]
   if not n:return sj(self,{'ok':False,'msg':'Falta negocio_id.'},400)
   if m<=0:return sj(self,{'ok':False,'msg':'El monto debe ser mayor que 0.'},400)
   b=get(n);a=b.get('stripe_account_id') or b.get('stripeAccountId') or ''
   if not a:return sj(self,{'ok':False,'msg':'Este negocio todavía no tiene Stripe conectado.'},400)
   cents=int(round(m*100));form={'line_items[0][price_data][currency]':'mxn','line_items[0][price_data][unit_amount]':str(cents),'line_items[0][price_data][product_data][name]':concepto or 'Compra','line_items[0][quantity]':'1'}
   p=stripe('/v1/payment_links',form,a);url=p.get('url')
   if not url:raise RuntimeError('Stripe no devolvió el enlace de pago.')
   sj(self,{'ok':True,'url':url,'id':p.get('id','')})
  except Exception as ex:sj(self,{'ok':False,'msg':str(ex)},500)
