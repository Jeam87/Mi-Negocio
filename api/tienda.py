from http.server import BaseHTTPRequestHandler
import os, json, urllib.parse
from urllib import request as url_req

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        uid = qs.get('user_id',[None])[0] or parsed.path.split('/')[-1].split('?')[0] or "eedfc281-71bb-4765-8883-8bec75ea3102"

        surl = os.environ.get('SUPABASE_URL','NO HAY URL')
        skey = os.environ.get('SUPABASE_ANON_KEY') or os.environ.get('SUPABASE_KEY') or 'NO HAY KEY'

        msg = f"ID buscado: {uid}<br><br>"
        msg += f"URL en Vercel: {surl}<br>"
        msg += f"URL corta: {surl[:45]}...<br>"
        msg += f"KEY existe: {'SI' if 'NO HAY' not in skey else 'NO'} - empieza con: {skey[:20]}...<br><br>"

        try:
            url = f"{surl}/rest/v1/products?user_id=eq.{uid}&select=*"
            msg += f"Consultando: {url}<br><br>"
            req = url_req.Request(url, headers={"apikey": skey, "Authorization": f"Bearer {skey}"})
            with url_req.urlopen(req, timeout=10) as r:
                data = r.read().decode()
                productos = json.loads(data)
                msg += f"Respuesta cruda: {data[:1000]}<br><br>"
                msg += f"Total productos encontrados: {len(productos)}"
        except Exception as e:
            msg += f"<b style='color:red'>ERROR EXACTO: {e}</b><br>"
            import traceback
            msg += f"<pre>{traceback.format_exc()}</pre>"

        html = f"<html><body style='font-family:monospace;padding:15px;word-break:break-all'><h2>DEBUG TIENDA</h2>{msg}</body></html>"
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(html.encode())
