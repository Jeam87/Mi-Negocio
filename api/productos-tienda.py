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
