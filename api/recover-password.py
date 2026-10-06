from http.server import BaseHTTPRequestHandler
import json, os, urllib.request
class handler(BaseHTTPRequestHandler):
 def send_json(self,o,c=200):
  self.send_response(c); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.send_header("Content-Type","application/json; charset=utf-8"); self.end_headers(); self.wfile.write(json.dumps(o,ensure_ascii=False).encode())
 def do_OPTIONS(self): self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
 def do_POST(self):
  try:
   n=int(self.headers.get("Content-Length",0)); b=json.loads(self.rfile.read(n).decode() if n else "{}"); e=(b.get("email") or "").strip().lower()
   if not e:return self.send_json({"ok":False,"msg":"Falta el correo."},400)
   u=(os.environ.get("SUPABASE_URL") or "").strip().rstrip("/"); k=(os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip(); app=(os.environ.get("NEXTAUTH_URL") or "").strip().rstrip("/")
   if not u or not k:return self.send_json({"ok":False,"msg":"Faltan las variables de Supabase en Vercel."},500)
   if not app:return self.send_json({"ok":False,"msg":"Falta NEXTAUTH_URL en Vercel."},500)
   req=urllib.request.Request(u+"/auth/v1/recover",data=json.dumps({"email":e,"redirect_to":app+"/reset-password.html"}).encode(),method="POST"); req.add_header("apikey",k); req.add_header("Authorization","Bearer "+k); req.add_header("Content-Type","application/json")
   with urllib.request.urlopen(req,timeout=15) as r:r.read()
   return self.send_json({"ok":True})
  except urllib.error.HTTPError as x:
   d=x.read().decode(errors="replace"); return self.send_json({"ok":False,"msg":"Supabase rechazó la recuperación: "+d[:500]},502)
  except Exception as x:return self.send_json({"ok":False,"msg":"Error al solicitar recuperación: "+str(x)},500)
