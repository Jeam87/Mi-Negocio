from http.server import BaseHTTPRequestHandler
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        path_parts = parsed.path.split('/')
        user_id = path_parts[-1] if len(path_parts)>=3 else query.get('user_id',[''])[0]

        html = f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mi Tienda</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-50 p-4">
<div class="max-w-md mx-auto bg-white rounded-2xl shadow p-5">
<h1 class="font-black text-xl">🛒 Mi Tienda</h1>
<p class="text-xs text-gray-500 mb-4">Pide por WhatsApp - Jacona</p>
<div id="lista">Cargando...</div>
</div>
<script>
const USER_ID = "{user_id}";
async function cargar(){{
  const r = await fetch('/api/products?user_id='+USER_ID);
  const j = await r.json();
  const prods = j.products || j || [];
  document.getElementById('lista').innerHTML = prods.map(p=>`
    <div class="flex justify-between border p-4 rounded-xl mb-3">
      <div><b>${{p.name}}</b><br><span class="text-green-600 font-bold">$${{p.price}}</span></div>
      <a href="https://wa.me/523521009999?text=Quiero ${{encodeURIComponent(p.name)}}" target="_blank" class="bg-green-500 text-white px-4 py-2 rounded-full text-xs">Pedir</a>
    </div>`).join('') || 'Sin productos';
}}
cargar();
</script></body></html>
        """
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(html.encode())
