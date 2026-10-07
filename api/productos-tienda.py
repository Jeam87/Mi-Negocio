from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def send_json(self, obj, code=200):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_json({"ok": True})

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            negocio_id = (qs.get('negocio_id', [''])[0] or '').strip()
            if not negocio_id:
                return self.send_json({"ok": False, "msg": "Falta negocio_id"}, 400)

            supa = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
            key = (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip()
            if not supa or not key:
                return self.send_json({"ok": False, "msg": "Faltan variables de Supabase en Vercel"}, 500)

            def get(path):
                req = urllib.request.Request(supa + path, method='GET')
                req.add_header('apikey', key)
                req.add_header('Authorization', 'Bearer ' + key)
                with urllib.request.urlopen(req, timeout=15) as r:
                    return json.loads(r.read().decode('utf-8') or '[]')

            # 1) Averiguar el user_id del negocio.
            negocios = get('/rest/v1/negocios?id=eq.' + urllib.parse.quote(negocio_id, safe='') + '&select=*')
            negocio = negocios[0] if negocios else {}
            owner_id = str(negocio.get('user_id') or '').strip().lower()

            # 2) Buscar negocio_data por el owner_id, pero también revisar todas las filas.
            #    Esto evita depender de que negocios.user_id y negocio_data.user_id sean iguales.
            rows = []
            if owner_id:
                rows = get('/rest/v1/negocio_data?user_id=eq.' + urllib.parse.quote(owner_id, safe='') + '&select=user_id,data')

            if not rows:
                rows = get('/rest/v1/negocio_data?select=user_id,data&limit=1000')

            wanted = 'productosV2_' + negocio_id
            found = None
            fuente = 'ninguna'
            found_user = None

            for row in rows:
                d = row.get('data') or {}
                if isinstance(d, str):
                    try: d = json.loads(d)
                    except: d = {}
                if not isinstance(d, dict):
                    continue
                raw = d.get(wanted)
                if raw is None:
                    raw = d.get('productosV2')
                if raw is not None:
                    if isinstance(raw, str):
                        try: raw = json.loads(raw)
                        except: raw = []
                    if isinstance(raw, list):
                        found = raw
                        found_user = row.get('user_id')
                        fuente = wanted if wanted in d else 'productosV2'
                        if raw:
                            break

            if not isinstance(found, list):
                found = []

            productos = []
            for p in found:
                if not isinstance(p, dict):
                    continue
                productos.append({
                    'id': p.get('id'),
                    'nombre': p.get('nombre') or 'Producto',
                    'precio': p.get('venta') if p.get('venta') is not None else 0,
                    'costo': p.get('costo') if p.get('costo') is not None else 0,
                    'stock': p.get('stock') if p.get('stock') is not None else None,
                    'categoria': p.get('categoria') or 'Otros',
                    'barcode': p.get('barcode') or '',
                    'foto': p.get('foto') or '',
                    'esBase': bool(p.get('esBase', False))
                })

            return self.send_json({
                'ok': True,
                'negocio_id': negocio_id,
                'productos': productos,
                'fuente': fuente,
                'filas_revisadas': len(rows)
            })
        except Exception as e:
            return self.send_json({'ok': False, 'msg': str(e)}, 500)
