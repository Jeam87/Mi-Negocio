from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs


def _como_dict(valor):
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except Exception:
            return {}
    return valor if isinstance(valor, dict) else {}


def _como_lista(valor):
    if isinstance(valor, str):
        try:
            valor = json.loads(valor or "[]")
        except Exception:
            return None
    return valor if isinstance(valor, list) else None


class handler(BaseHTTPRequestHandler):

    def send_json(self, obj, code=200):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_json({"ok": True})

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            negocio_id = (qs.get('negocio_id', ['']) or '').strip()

            if not negocio_id:
                return self.send_json({"ok": False, "msg": "Falta negocio_id"}, 400)

            supa = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
            key = (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip()

            if not supa or not key:
                return self.send_json(
                    {"ok": False, "msg": "Faltan variables de Supabase en Vercel"}, 500)

            def get(path):
                req = urllib.request.Request(supa + path, method='GET')
                req.add_header('apikey', key)
                req.add_header('Authorization', 'Bearer ' + key)
                with urllib.request.urlopen(req, timeout=15) as r:
                    return json.loads(r.read().decode('utf-8') or '[]')

            # 1. Negocio
            negocios = get('/rest/v1/negocios?id=eq.'
                           + urllib.parse.quote(negocio_id, safe='') + '&select=*')
            negocio = negocios[0] if negocios else {}
            if not negocio:
                return self.send_json({"ok": False, "msg": "No se encontró el negocio"}, 404)

            owner_id = str(negocio.get('user_id') or '').strip().lower()
            # Respaldo de los dos nombres comunes que puede tener el campo de correo electrónico
            owner_email = str(negocio.get('correo') or negocio.get('email') or '').strip().lower()

            # 2. Datos del dueño (Búsqueda por user_id o por Correo)
            data = {}
            rows = []
            
            # Intento 1: Buscar por el user_id de la cuenta
            if owner_id:
                rows = get('/rest/v1/negocio_data?user_id=eq.'
                           + urllib.parse.quote(owner_id, safe='')
                           + '&select=user_id,data')
            
            # Intento 2: Si no regresó filas, buscamos usando el correo en la columna user_id
            if not rows and owner_email:
                rows = get('/rest/v1/negocio_data?user_id=eq.'
                           + urllib.parse.quote(owner_email, safe='')
                           + '&select=user_id,data')

            for row in rows:
                data.update(_como_dict(row.get('data')))

            # 3. Productos: misma lógica que la app
            especifica = _como_lista(data.get('productosV2_' + negocio_id))
            general = _como_lista(data.get('productosV2'))
            if especifica:
                fuente, lista = 'productosV2_' + negocio_id, especifica
            elif general:
                fuente, lista = 'productosV2', general
            else:
                fuente, lista = 'productosV2_' + negocio_id, especifica or []

            productos = []
            vistos = set()
            for p in lista:
                if not isinstance(p, dict) or p.get('esBase'):
                    continue
                pid = str(p.get('id') or '').strip()
                if not pid or pid in vistos:
                    continue
                vistos.add(pid)
                productos.append({
                    'id': p.get('id'),
                    'nombre': p.get('nombre') or 'Producto',
                    'precio': p.get('venta') if p.get('venta') is not None else 0,
                    'costo': p.get('costo') if p.get('costo') is not None else 0,
                    'stock': p.get('stock') if p.get('stock') is not None else None,
                    'categoria': p.get('categoria') or 'otros',
                    'barcode': p.get('barcode') or '',
                    'foto': p.get('foto') or '',
                    'descripcion': (p.get('descripcion') or p.get('descripcion_producto')
                                    or p.get('descripcionProducto') or p.get('detalle') or ''),
                    'esBase': False
                })

            # 4. Categorías de la app
            categorias = (_como_lista(data.get('categoriasVenta_' + negocio_id))
                          or _como_lista(data.get('categoriasVenta')) or [])
            categorias = [
                {'id': str(c.get('id')), 'nombre': c.get('nombre') or '',
                 'parentId': c.get('parentId')}
                for c in categorias if isinstance(c, dict) and c.get('id') is not None
            ]

            # 5. Logo y datos del negocio
            empresa = (_como_dict(data.get('empresaConfig_' + negocio_id))
                       or _como_dict(data.get('empresaConfig')))
            logo = (empresa.get('logo') or data.get('logo_url')
                    or data.get('logoUrl') or '')
            nombre_tienda = (negocio.get('nombre_negocio') or negocio.get('nombre')
                             or empresa.get('nombre') or '')
            whatsapp = negocio.get('whatsapp') or empresa.get('whatsapp') or ''

            return self.send_json({
                'ok': True,
                'negocio_id': negocio_id,
                'productos': productos,
                'categorias': categorias,
                'logo': logo if isinstance(logo, str) else '',
                'nombre_tienda': nombre_tienda,
                'whatsapp': whatsapp,
                'fuente': fuente
            })

        except Exception as e:
            return self.send_json({"ok": False, "msg": str(e)}, 500)
