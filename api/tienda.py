from http.server import BaseHTTPRequestHandler
import os, json, urllib.parse
from urllib import request as url_req

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        user_id = qs.get('user_id',[None])[0] or parsed.path.split('/')[-1]
        if not user_id or len(user_id)<10:
            user_id = qs.get('user_id',[''])[0]

        supa_url = os.environ.get('SUPABASE_URL')
        supa_key = os.environ.get('SUPABASE_ANON_KEY') or os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_SERVICE_KEY')
        productos = []
        try:
            if supa_url and supa_key and user_id:
                url = f"{supa_url}/rest/v1/products?user_id=eq.{user_id}&select=*"
                req = url_req.Request(url, headers={"apikey": supa_key, "Authorization": f"Bearer {supa_key}"})
                with url_req.urlopen(req, timeout=5) as r:
                    productos = json.loads(r.read().decode())
        except Exception as e:
            print(e)

        cards = ""
        for p in productos:
            nombre = p.get('name','Producto')
            precio = p.get('price',0)
            desc = p.get('description','')[:80]
            img = p.get('image_url') or p.get('image') or ''
            img_tag = f"<img src='{img}' class='w-full h-28 object-cover rounded-xl mb-2'/>" if img else ""
            wa_msg = urllib.parse.quote(f"Hola! Quiero {nombre} - ${precio}")
            cards += f"""
            <div class="bg-white border rounded-2xl p-4 shadow-sm mb-3">
              {img_tag}
              <h3 class="font-bold">{nombre}</h3>
              <p class="text-xs text-gray-500">{desc}</p>
              <div class="flex justify-between items-center mt-3">
                <span class="text-green-600 font-black text-lg">${precio}</span>
                <a href="https://wa.me/523521009999?text={wa_msg}" target="_blank" class="bg-green-500 text-white px-5 py-2 rounded-full text-sm font-bold">Pedir por WhatsApp</a>
              </div>
            </div>"""

        if not cards:
            cards = "<div class='bg-white p-6 rounded-2xl text-center text-gray-400'>No hay productos todavía.<br>Agrega desde tu panel.</div>"

        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Mi Tienda - Jacona</title><script src="https://cdn.tailwindcss.com"></script></head>
        <body class="bg-gray-100 min-h-screen"><div class="max-w-md mx-auto p-3">
        <div class="bg-white rounded-2xl shadow p-5 mb-4 text-center">
          <h1 class="font-black text-2xl">🛒 Mi Tienda</h1>
          <p class="text-xs text-gray-500">Pide por WhatsApp - Entrega en Jacona</p>
          <p class="text-[10px] text-gray-400 mt-1">{user_id[:8]}...</p>
        </div>{cards}</div></body></html>"""

        self.send_response(200)
        self.send_header('Content-type','text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())
