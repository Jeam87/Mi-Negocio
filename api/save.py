from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
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
        req.add_header('apikey', key)
        req.add_header('Authorization', 'Bearer ' + key)
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

    @staticmethod
    def merge_inventory(old_list, new_list):
        """Une por id: conserva elementos previos y aplica los campos entrantes al mismo id.
        No propaga borrados implícitos por listas vacías; es intencional para proteger datos.
        """
        result = []
        positions = {}
        for source in (old_list or [], new_list or []):
            if not isinstance(source, list):
                continue
            for item in source:
                if not isinstance(item, dict):
                    continue
                item_id = item.get('id')
                key = str(item_id) if item_id is not None else None
                if key is not None and key in positions:
                    # Los datos entrantes van después y actualizan campos del mismo artículo.
                    result[positions[key]].update(item)
                else:
                    copied = dict(item)
                    result.append(copied)
                    if key is not None:
                        positions[key] = len(result) - 1
        return result

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            user_id = (qs.get('user_id', [None])[0] or qs.get('email', [None])[0] or '').strip().lower()
            if not user_id:
                return self.send({'ok': False, 'msg': 'falta user_id'}, 400)
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
            if not user_id:
                return self.send({'ok': False, 'msg': 'falta user_id'}, 400)
            if not isinstance(incoming, dict):
                return self.send({'ok': False, 'msg': 'data debe ser un objeto'}, 400)

            url, key = self.supabase()
            if not url or not key:
                return self.send({'ok': False, 'msg': 'Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Vercel'}, 500)

            rows = self.get_rows(user_id)
            existing = {}
            for row in rows:
                existing.update(self.as_dict(row.get('data')))

            merged = dict(existing)
            # Las demás claves mantienen el comportamiento de guardado existente.
            for k, v in incoming.items():
                if k == 'inventarioMaestro' or k.startswith('inventarioMaestro_') or k == 'productosV2' or k.startswith('productosV2_'):
                    continue
                merged[k] = v

            # Materias primas: preferir los datos que acaba de enviar este dispositivo,
            # pero unir por id con la nube para no perder elementos que no llegaron.
            specific_key = next((k for k in incoming if k.startswith('inventarioMaestro_') and k != 'inventarioMaestro_updatedAt'), None)
            if not specific_key:
                specific_key = next((k for k in existing if k.startswith('inventarioMaestro_') and k != 'inventarioMaestro_updatedAt'), None)
            incoming_candidates = []
            if specific_key and specific_key in incoming:
                incoming_candidates.append(incoming.get(specific_key))
            incoming_candidates.append(incoming.get('inventarioMaestro'))
            old_candidates = []
            if specific_key and specific_key in existing:
                old_candidates.append(existing.get(specific_key))
            old_candidates.append(existing.get('inventarioMaestro'))

            new_inventory = next((a for a in (self.as_list(v) for v in incoming_candidates) if a is not None and len(a) > 0), None)
            if new_inventory is None:
                # Si el cliente manda una lista vacía, no borrar inventario existente.
                new_inventory = next((a for a in (self.as_list(v) for v in incoming_candidates) if a is not None), None)
            old_inventory = next((a for a in (self.as_list(v) for v in old_candidates) if a is not None and len(a) > 0), None)
            if old_inventory is None:
                old_inventory = next((a for a in (self.as_list(v) for v in old_candidates) if a is not None), None)

            if new_inventory is not None or old_inventory is not None:
                # Una lista vacía entrante no elimina la lista ya guardada.
                if new_inventory is not None and len(new_inventory) == 0 and old_inventory:
                    chosen = old_inventory
                else:
                    chosen = self.merge_inventory(old_inventory, new_inventory)
                merged['inventarioMaestro'] = chosen
                # Alinear claves específicas del inventario existentes y recibidas.
                inv_keys = {k for k in list(existing) + list(incoming)
                            if k.startswith('inventarioMaestro_') and k != 'inventarioMaestro_updatedAt'}
                if specific_key:
                    inv_keys.add(specific_key)
                for k in inv_keys:
                    merged[k] = chosen
                merged['inventarioMaestro_updatedAt'] = str(max(self.inv_stamp(incoming), self.inv_stamp(existing)))

            # Productos de venta: no borrar listas existentes por una lista vacía accidental.
            def product_lists(d):
                out = []
                for k, v in d.items():
                    if k == 'productosV2' or k.startswith('productosV2_'):
                        arr = self.as_list(v)
                        if arr is not None:
                            out.append(arr)
                return out
            incoming_products = next((a for a in product_lists(incoming) if a), None)
            old_products = next((a for a in product_lists(existing) if a), None)
            chosen_products = incoming_products if incoming_products is not None else (old_products if old_products is not None else [])
            if chosen_products or old_products is not None:
                merged['productosV2'] = chosen_products
                for k in set([x for x in existing if x.startswith('productosV2_')] + [x for x in incoming if x.startswith('productosV2_')]):
                    merged[k] = chosen_products

            payload = json.dumps({'user_id': user_id, 'data': merged}, ensure_ascii=False).encode('utf-8')
            if rows:
                target = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id, safe='')}"
                req = urllib.request.Request(target, data=payload, method='PATCH')
            else:
                target = f'{url}/rest/v1/negocio_data'
                req = urllib.request.Request(target, data=payload, method='POST')
            req.add_header('apikey', key)
            req.add_header('Authorization', 'Bearer ' + key)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Prefer', 'return=minimal')
            with urllib.request.urlopen(req, timeout=30) as r:
                r.read()

            return self.send({'ok': True, 'user_id': user_id,
                              'filas_encontradas': len(rows),
                              'inventario_materias_primas': len(merged.get('inventarioMaestro', [])) if isinstance(merged.get('inventarioMaestro'), list) else 0,
                              'data': merged})
        except Exception as e:
            return self.send({'ok': False, 'msg': str(e)}, 500)
