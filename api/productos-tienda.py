from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs


def parse_json_value(value, fallback=None):
    """Convierte valores JSON guardados como texto sin perder valores válidos."""
    if fallback is None:
        fallback = []
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return fallback
    return value if value is not None else fallback


def extraer_categorias(rows, negocio_id):
    """
    Recupera las definiciones de categorías guardadas por Mi Negocio.
    Prioriza la clave específica del negocio y conserva los IDs originales.
    """
    claves = ['categoriasVenta_' + negocio_id, 'categoriasVenta']
    encontradas = {}

    for row in rows:
        data = parse_json_value(row.get('data'), {})
        if not isinstance(data, dict):
            continue

        for clave in claves:
            raw = parse_json_value(data.get(clave), [])
            if not isinstance(raw, list):
                continue

            for cat in raw:
                if not isinstance(cat, dict):
                    continue
                cid = str(cat.get('id') or '').strip()
                nombre = str(cat.get('nombre') or cat.get('name') or '').strip()
                if not cid or not nombre:
                    continue
                # No reemplazar una definición específica ya encontrada
                # con una copia general potencialmente antigua.
                if cid not in encontradas or clave.endswith('_' + negocio_id):
                    encontradas[cid] = {
                        'id': cid,
                        'nombre': nombre,
                        'parentId': cat.get('parentId') or cat.get('parent_id') or None
                    }

    return list(encontradas.values())

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

            negocios = get('/rest/v1/negocios?id=eq.' + urllib.parse.quote(negocio_id, safe='') + '&select=*')
            negocio = negocios[0] if negocios else {}
            owner_id = str(negocio.get('user_id') or '').strip().lower()

            rows = []
            if owner_id:
                rows = get('/rest/v1/negocio_data?user_id=eq.' + urllib.parse.quote(owner_id, safe='') + '&select=user_id,data')

            if not rows:
                rows = get('/rest/v1/negocio_data?select=user_id,data&limit=1000')

            categorias = extraer_categorias(rows, negocio_id)

            wanted = 'productosV2_' + negocio_id
            merged = {}

            # Revisamos TODAS las filas y TODAS las listas disponibles.
            # Así una fila antigua no puede ocultar un producto nuevo.
            for row in rows:
                d = row.get('data') or {}
                if isinstance(d, str):
                    try:
                        d = json.loads(d)
                    except Exception:
                        d = {}
                if not isinstance(d, dict):
                    continue

                candidates = []
                if d.get(wanted) is not None:
                    candidates.append(d.get(wanted))
                if d.get('productosV2') is not None:
                    candidates.append(d.get('productosV2'))

                for raw in candidates:
                    if isinstance(raw, str):
                        try:
                            raw = json.loads(raw)
                        except Exception:
                            raw = []
                    if not isinstance(raw, list):
                        continue

                    for p in raw:
                        if not isinstance(p, dict):
                            continue
                        pid = str(p.get('id') or '').strip()
                        if not pid:
                            pid = 'sin_id_' + str(len(merged) + 1)
                        old = merged.get(pid, {})
                        item = dict(old)
                        item.update(p)
                        merged[pid] = item

            productos = []
            for p in merged.values():
                if not isinstance(p, dict):
                    continue
                # Productos antiguos sin destinoVenta permanecen visibles en ambas tiendas.
                destino = str(p.get('destinoVenta') or 'ambas').strip().lower()
                if destino not in ('online', 'ambas'):
                    continue
                productos.append({
                    'id': p.get('id'),
                    'nombre': p.get('nombre') or 'Producto',
                    'precio': p.get('venta') if p.get('venta') is not None else 0,
                    'costo': p.get('costo') if p.get('costo') is not None else 0,
                    'stock': p.get('stock') if p.get('stock') is not None else None,
                    # categoria conserva el ID que usa Mi Negocio.
                    'categoria': p.get('categoria') or 'Otros',
                    'categoria_id': p.get('categoria') or 'Otros',
                    'barcode': p.get('barcode') or '',
                    'foto': p.get('foto') or '',
                    'descripcion': p.get('descripcion') or p.get('descripcion_producto') or p.get('descripcionProducto') or p.get('detalle') or '',
                    'esBase': bool(p.get('esBase', False)),
                    'destinoVenta': destino
                })

            productos = [p for p in productos if not p.get('esBase')]

            return self.send_json({
                'ok': True,
                'negocio_id': negocio_id,
                'productos': productos,
                'categorias': categorias,
                'fuente': wanted,
                'filas_revisadas': len(rows)
            })

        except Exception as e:
            return self.send_json({'ok': False, 'msg': str(e)}, 500)
