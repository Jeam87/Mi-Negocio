from http.server import BaseHTTPRequestHandler
import json, os, urllib.request
class handler(BaseHTTPRequestHandler):
 def send_json(self,o,c=200):
  self.send_response(c); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type, Authorization"); self.send_header("Content-Type","application/json; charset=utf-8"); self.end_headers(); self.wfile.write(json.dumps(o,ensure_ascii=False).encode())
 def do_OPTIONS(self): self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type, Authorization"); self.end_headers()
 def do_POST(self):
  try:
   n=int(self.headers.get("Content-Length",0)); b=json.loads(self.rfile.read(n).decode() if n else "{}"); t=(b.get("access_token") or "").strip(); p=b.get("password") or ""
   if not t:return self.send_json({"ok":False,"msg":"El enlace de recuperación no es válido o ya venció."},401)
   if len(p)<6:return self.send_json({"ok":False,"msg":"La contraseña debe tener al menos 6 caracteres."},400)
   u=(os.environ.get("SUPABASE_URL") or "").strip().rstrip("/"); k=(os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
   if not u or not k:return self.send_json({"ok":False,"msg":"Faltan las variables de Supabase en Vercel."},500)
   req=urllib.request.Request(u+"/auth/v1/user",data=json.dumps({"password":p}).encode(),method="PUT"); req.add_header("apikey",k); req.add_header("Authorization","Bearer "+t); req.add_header("Content-Type","application/json")
   with urllib.request.urlopen(req,timeout=15) as r:r.read()
   return self.send_json({"ok":True})
  except urllib.error.HTTPError as x:
   d=x.read().decode(errors="replace"); return self.send_json({"ok":False,"msg":"Supabase rechazó el cambio de contraseña: "+d[:500]},502)
  except Exception as x:return self.send_json({"ok":False,"msg":"Error al cambiar la contraseña: "+str(x)},500)
