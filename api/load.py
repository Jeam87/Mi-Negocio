from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        user_id = (qs.get('user_id',[None])[0] or qs.get('negocio_id',[None])[0] or "esaul_1987@hotmail.com").lower()
        url = (os.environ.get('SUPABASE_URL') or "").strip().rstrip('/')
        key = (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or "").strip()
        data = {}
        if url and key:
            try:
                full = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id)}&select=data"
                req = urllib.request.Request(full, method='GET')
                req.add_header('apikey', key)
                req.add_header('Authorization', f'Bearer {key}')
                with urllib.request.urlopen(req, timeout=8) as r:
                    txt = r.read().decode()
                    arr = json.loads(txt) if txt else []
                    if arr and len(arr)>0:
                        data = arr[0].get('data',{}) or {}
            except Exception as e:
                pass
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"ok":True,"data":data,"user_id":user_id}).encode())
