from http.server import BaseHTTPRequestHandler
import os, json, urllib.parse
from urllib import request as url_req

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        user_id = qs.get('user_id',[None])[0] or parsed.path.split('/')[-1].split('?')[0] or "eedfc281-71bb-4765-8883-8bec75ea3102"

        supa_url = os.environ.get('SUPABASE_URL')
        supa_key = os.environ.get('SUPABASE_ANON_KEY') or os.environ.get('SUPABASE_KEY')
        productos = []
        try:
            url = f"{supa_url}/rest/v1/products?user_id=eq.{user_id}&select=*"
            req = url_req.Request(url, headers={"apikey": supa_key, "Authorization": f"Bearer {supa_key}"})
            with url_req.urlopen(req, timeout=10) as r:
                productos = json.loads(r.read().decode())
        except: pass

        cards = ""
        for p in productos:
            nombre = p.get('name') or p.get('nombre') or 'Producto'
            precio = p.get('price') or p.get('precio') or 0
            desc = (p.get('description') or p.get('descripcion') or '')[:100]
            img = p.get('image_url') or p.get('imagen') or ''
            img_tag = f"<img src='{img}' class='w-full h-40 object-cover rounded-xl mb-3'/>" if img else ""
            wa = urllib.parse.quote(f"Hola! Quiero {nombre} - ${precio}")
            cards += f"<div class='bg-white rounded-2xl p-4 shadow mb-4'>{img_tag}<h3 class='font-bold text-lg'>{nombre}</h3><p class='text-sm text-gray-500'>{desc}</p><div class='flex justify-between items-center mt-3'><span class='text-green-600 font-black text-xl'>${precio}</span><a href='https://wa.me/523521009999?text={wa}' target='_blank' class='bg-green-500 text-white px-5 py-2 rounded-full font-bold text-sm'>Pedir WhatsApp</a></div></div>"

        if not cards:
            cards = "<div class='bg-white p-6 rounded-2xl text-center'>No hay productos</div>"

        html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Mi Tienda</title><script src='https://cdn.tailwindcss.com'></script></head><body class='bg-gray-100'><div class='max-w-md mx-auto p-4'><div class='bg-white rounded-2xl p-5 mb-4 text-center shadow'><h1 class='font-black text-2xl'>🛒 Mi Tienda Jacona</h1><p class='text-xs text-gray-500'>Tap para pedir por WhatsApp</p></div>{cards}</div></body></html>"
        self.send_response(200)
        self.send_header('Content-type','text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())
