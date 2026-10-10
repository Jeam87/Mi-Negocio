from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def send(self, obj, code=200):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def supabase(self):
        return ((os.environ.get('SUPABASE_URL') or '').strip().rstrip('/'),
                (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip())

    def get_rows(self, user_id):
        url, key = self.supabase()
        if not url or not key:
            raise RuntimeError('Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Vercel')
        full = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id, safe='')}&select=user_id,data"
        req = urllib.request.Request(full, method='GET')
        req.add_header('apikey', key); req.add_header('Authorization', 'Bearer ' + key)
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode() or '[]')

    @staticmethod
    def as_dict(value):
        if isinstance(value, str):
            try: value = json.loads(value)
            except Exception: return {}
        return value if isinstance(value, dict) else {}

    @staticmethod
    def as_list(value):
        if isinstance(value, str):
            try: value = json.loads(value or '[]')
            except Exception: return None
        return value if isinstance(value, list) else None

    @staticmethod
    def inv_stamp(data):
        try: return int(float(data.get('inventarioMaestro_updatedAt') or 0))
        except Exception: return 0

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            user_id = (qs.get('user_id', [None])[0] or qs.get('email', [None])[0] or '').strip().lower()
            if not user_id: return self.send({'ok': False, 'msg': 'falta user_id'}, 400)
            rows = self.get_rows(user_id)
            data = {}
            for row in rows:
                data.update(self.as_dict(row.get('data')))
            return self.send({'ok': True, 'data': data, 'user_id': user_id})
        except Exception as e:
            return self.send({'ok': False, 'msg': str(e)}, 500)

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8') if length else '{}')
            user_id = (body.get('user_id') or body.get('email') or '').strip().lower()
            incoming = body.get('data') or {}
            if not user_id: return self.send({'ok': False, 'msg': 'falta user_id'}, 400)
            if not isinstance(incoming, dict): return self.send({'ok': False, 'msg': 'data debe ser un objeto'}, 400)
            url, key = self.supabase()
            if not url or not key: return self.send({'ok': False, 'msg': 'Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Vercel'}, 500)

            rows = self.get_rows(user_id)
            existing = {}
            for row in rows: existing.update(self.as_dict(row.get('data')))
            merged = dict(existing)
            # Mantener el comportamiento de guardado de las demás claves.
            for k, v in incoming.items():
                if k == 'inventarioMaestro' or k.startswith('inventarioMaestro_') or k == 'productosV2' or k.startswith('productosV2_'):
                    continue
                merged[k] = v

            # Inventario de materias primas: sincronizar clave general y específica.
            # La marca de tiempo permite rechazar una copia más vieja de otro dispositivo.
            incoming_stamp = self.inv_stamp(incoming)
            existing_stamp = self.inv_stamp(existing)
            id_negocio = ''
            # Inferir la clave específica del inventario que venga en el payload.
            inv_keys = [k for k in list(existing.keys()) + list(incoming.keys()) if k.startswith('inventarioMaestro_') and k != 'inventarioMaestro_updatedAt']
            for k in incoming.keys():
                if k.startswith('inventarioMaestro_') and k != 'inventarioMaestro_updatedAt':
                    id_negocio = k[len('inventarioMaestro_'):]
                    break
            candidatos_in = []
            if id_negocio and 'inventarioMaestro_' + id_negocio in incoming:
                candidatos_in.append(incoming.get('inventarioMaestro_' + id_negocio))
            candidatos_in.append(incoming.get('inventarioMaestro'))
            candidatos_old = []
            if id_negocio and 'inventarioMaestro_' + id_negocio in existing:
                candidatos_old.append(existing.get('inventarioMaestro_' + id_negocio))
            candidatos_old.append(existing.get('inventarioMaestro'))
            inv_in = next((self.as_list(v) for v in candidatos_in if self.as_list(v) is not None and len(self.as_list(v)) > 0), None)
            inv_old = next((self.as_list(v) for v in candidatos_old if self.as_list(v) is not None and len(self.as_list(v)) > 0), None)
            raw_in = next((self.as_list(v) for v in candidatos_in if self.as_list(v) is not None), None)
            raw_old = next((self.as_list(v) for v in candidatos_old if self.as_list(v) is not None), None)
            if incoming_stamp and incoming_stamp >= existing_stamp:
                chosen = raw_in if raw_in is not None else (inv_in if inv_in is not None else inv_old)
                chosen_stamp = incoming_stamp
            elif existing_stamp > incoming_stamp:
                chosen = raw_old if raw_old is not None else inv_old
                chosen_stamp = existing_stamp
            else:
                # Compatibilidad con datos anteriores que aún no tenían marca de tiempo.
                chosen = inv_in if inv_in is not None else (raw_in if raw_in is not None and len(raw_in) > 0 else inv_old)
                chosen_stamp = max(incoming_stamp, existing_stamp)
            if chosen is not None:
                merged['inventarioMaestro'] = chosen
                if id_negocio:
                    merged['inventarioMaestro_' + id_negocio] = chosen
                # Mantener alineadas las claves específicas existentes para este usuario.
                for k in inv_keys:
                    merged[k] = chosen
                merged['inventarioMaestro_updatedAt'] = str(chosen_stamp or incoming_stamp or existing_stamp or 0)
            elif 'inventarioMaestro' in existing or any(k.startswith('inventarioMaestro_') for k in existing):
                # Si no se pudo interpretar el valor recibido, conservar lo que ya estaba guardado.
                pass

            # Productos de venta: conservar el comportamiento previo de no borrar listas con datos por [] accidental.
            def product_lists(d):
                out=[]
                for k,v in d.items():
                    if k == 'productosV2' or k.startswith('productosV2_'):
                        arr=self.as_list(v)
                        if arr is not None: out.append(arr)
                return out
            in_products=next((a for a in product_lists(incoming) if a), None)
            old_products=next((a for a in product_lists(existing) if a), None)
            chosen_products=in_products if in_products is not None else (old_products if old_products is not None else [])
            if chosen_products or old_products is not None:
                merged['productosV2']=chosen_products
                for k in set([x for x in existing if x.startswith('productosV2_')] + [x for x in incoming if x.startswith('productosV2_')]):
                    merged[k]=chosen_products

            payload=json.dumps({'user_id': user_id, 'data': merged}, ensure_ascii=False).encode('utf-8')
            if rows:
                target=f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id, safe='')}"
                req=urllib.request.Request(target, data=payload, method='PATCH')
                req.add_header('Prefer', 'return=minimal')
            else:
                target=f'{url}/rest/v1/negocio_data'
                req=urllib.request.Request(target, data=payload, method='POST')
                req.add_header('Prefer', 'return=minimal')
            req.add_header('apikey', key); req.add_header('Authorization', 'Bearer ' + key); req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=30) as r: r.read()
            return self.send({'ok': True, 'user_id': user_id, 'filas_encontradas': len(rows), 'inventario_materias_primas': len(chosen) if isinstance(chosen, list) else 0, 'data': merged})
        except Exception as e:
            return self.send({'ok': False, 'msg': str(e)}, 500)
