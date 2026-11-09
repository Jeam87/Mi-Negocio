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
        self.wfile.write(
            json.dumps(obj, ensure_ascii=False).encode('utf-8')
        )

    def do_OPTIONS(self):
        self.send_json({"ok": True})

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            negocio_id = ( qs.get('negocio_id', [''])[0] or '' ).strip()
            
            if not negocio_id:
                return self.send_json({
                    "ok": False,
                    "msg": "Falta negocio_id"
                }, 400)

            supa = ( os.environ.get('SUPABASE_URL') or '' ).strip().rstrip('/')
            key = ( os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '' ).strip()
            
            if not supa or not key:
                return self.send_json({
                    "ok": False,
                    "msg": "Faltan variables de Supabase en Vercel"
                }, 500)

            # -------------------------------------------------
            # DICCIONARIO DE TRADUCCIÓN DE CATEGORÍAS
            # Modifica los números y nombres según los tuyos de la Base de Datos
            # -------------------------------------------------
            MAPA_CATEGORIAS = {
                "1": "Abarrotes",
                "2": "Bebidas",
                "3": "Limpieza",
                "4": "Lácteos",
                "5": "Snacks",
                1: "Abarrotes",   # Soporta si viene como número entero
                2: "Bebidas",
                3: "Limpieza",
                4: "Lácteos",
                5: "Snacks"
            }

            def get(path):
                req = urllib.request.Request(
                    supa + path,
                    method='GET'
                )
                req.add_header('apikey', key)
                req.add_header(
                    'Authorization', 'Bearer ' + key
                )
                with urllib.request.urlopen(
                    req, timeout=15
                ) as r:
                    return json.loads(
                        r.read().decode('utf-8') or '[]'
                    )

            # -------------------------------------------------
            # 1. Buscar el negocio
            # -------------------------------------------------
            negocios = get(
                '/rest/v1/negocios?id=eq.' + 
                urllib.parse.quote( negocio_id, safe='' ) + 
                '&select=*'
            )
            negocio = negocios[0] if negocios else {}
            owner_id = str( negocio.get('user_id') or '' ).strip().lower()

            # -------------------------------------------------
            # 2. Buscar los datos del dueño
            # -------------------------------------------------
            rows = []
            if owner_id:
                rows = get(
                    '/rest/v1/negocio_data?user_id=eq.' + 
                    urllib.parse.quote( owner_id, safe='' ) + 
                    '&select=user_id,data'
                )

            if not rows:
                rows = get(
                    '/rest/v1/negocio_data'
                    '?select=user_id,data&limit=1000'
                )

            # -------------------------------------------------
            # 3. Obtener productos
            # -------------------------------------------------
            wanted = 'productosV2_' + negocio_id
            merged = {}

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
                    candidates.append( d.get(wanted) )
                if d.get('productosV2') is not None:
                    candidates.append( d.get('productosV2') )

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

                        pid = str( p.get('id') or '' ).strip()
                        if not pid:
                            pid = ( 'sin_id_' + str(len(merged) + 1) )

                        anterior = merged.get( pid, {} )
                        combinado = dict(anterior)
                        combinado.update(p)
                        merged[pid] = combinado

            # -------------------------------------------------
            # 4. Preparar productos para la tienda y Traducir Categorías
            # -------------------------------------------------
            productos = []
            for p in merged.values():
                if not isinstance(p, dict):
                    continue

                # Extraer la categoría cruda (puede ser id numérico, string o None)
                cat_original = p.get('categoria')
                
                # Traducir usando el mapa. Si no se encuentra en el mapa, conserva el valor original o pone 'Otros'
                cat_nombre = MAPA_CATEGORIAS.get(cat_original, cat_original or 'Otros')
                
                # Forzar que si el resultado sigue siendo un número (por no estar mapeado), se devuelva texto limpio o 'Otros'
                if str(cat_nombre).isdigit():
                    cat_nombre = f"Categoría {cat_nombre}"

                productos.append({
                    'id': p.get('id'),
                    'nombre': ( p.get('nombre') or 'Producto' ),
                    'precio': ( p.get('venta') if p.get('venta') is not None else 0 ),
                    'costo': ( p.get('costo') if p.get('costo') is not None else 0 ),
                    'stock': ( p.get('stock') if p.get('stock') is not None else None ),
                    'categoria': cat_nombre,
                    'barcode': ( p.get('barcode') or '' ),
                    'foto': ( p.get('foto') or '' ),
                    'descripcion': ( 
                        p.get('descripcion') or p.get('descripcion_producto') or 
                        p.get('descripcionProducto') or p.get('detalle') or '' 
                    ),
                    'esBase': bool( p.get( 'esBase', False ) )
                })

            # -------------------------------------------------
            # 5. No mostrar productos base
            # -------------------------------------------------
            productos = [ p for p in productos if not p.get('esBase') ]

            # -------------------------------------------------
            # 6. Respuesta para la tienda
            # -------------------------------------------------
            return self.send_json({
                'ok': True,
                'negocio_id': negocio_id,
                'productos': productos,
                'fuente': wanted,
                'filas_revisadas': len(rows)
            })

        except Exception as e:
            return self.send_json({
                'ok': False,
                'msg': str(e)
            }, 500)
