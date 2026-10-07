import os
import json
import urllib.parse
import urllib.request
import urllib.error
import hmac
import hashlib
import base64
import time

from http.server import BaseHTTPRequestHandler


# =========================================================
# CONFIGURACIÓN
# =========================================================

FIXED_APP_URL = "https://mi-negocio-mauve.vercel.app/api/stripe/connect"


# =========================================================
# RESPUESTAS JSON
# =========================================================

def send_json(h, obj, code=200):
    h.send_response(code)
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.end_headers()
    h.wfile.write(json.dumps(obj, ensure_ascii=False).encode())


def read_json(h):
    try:
        n = int(h.headers.get("Content-Length", "0"))
        if not n:
            return {}
        return json.loads(h.rfile.read(n).decode() or "{}")
    except Exception:
        return {}


# =========================================================
# VARIABLES DE VERCEL
# =========================================================

def env(*names):
    for name in names:
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    return ""


def stripe_secret_key():
    return env("STRIPE_SECRET_KEY")


def stripe_client_id():
    return env(
        "STRIPE_CONNECT_CLIENT_ID",
        "STRIPE_CLIENT_ID"
    )


# =========================================================
# URL FIJA DE LA APLICACIÓN
# =========================================================

def base_url(h):
    return FIXED_APP_URL


def redirect_uri(h):
    return FIXED_APP_URL + "/api/stripe/connect"


# =========================================================
# STATE DE STRIPE CONNECT
# =========================================================

def state_make(negocio_id):

    raw = json.dumps(
        {
            "n": str(negocio_id),
            "t": int(time.time())
        },
        separators=(",", ":")
    ).encode()

    signature = hmac.new(
        stripe_secret_key().encode(),
        raw,
        hashlib.sha256
    ).digest()

    token = raw + b"." + signature

    return base64.urlsafe_b64encode(
        token
    ).decode().rstrip("=")


def state_read(state):

    try:

        padded = state + "=" * (-len(state) % 4)

        decoded = base64.urlsafe_b64decode(padded)

        raw, signature = decoded.rsplit(b".", 1)

        expected = hmac.new(
            stripe_secret_key().encode(),
            raw,
            hashlib.sha256
        ).digest()

        if not hmac.compare_digest(
            signature,
            expected
        ):
            return None

        data = json.loads(raw.decode())

        if int(time.time()) - int(data["t"]) > 900:
            return None

        return data["n"]

    except Exception:
        return None


# =========================================================
# STRIPE API
# =========================================================

def stripe_request(path, method="GET", form=None):

    key = stripe_secret_key()

    if not key:
        raise RuntimeError(
            "Falta STRIPE_SECRET_KEY en Vercel."
        )

    data = (
        urllib.parse.urlencode(form).encode()
        if form is not None
        else None
    )

    request = urllib.request.Request(
        "https://api.stripe.com" + path,
        data=data,
        method=method
    )

    request.add_header(
        "Authorization",
        "Basic " +
        base64.b64encode(
            (key + ":").encode()
        ).decode()
    )

    if data:
        request.add_header(
            "Content-Type",
            "application/x-www-form-urlencoded"
        )

    try:

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            return json.loads(
                response.read().decode() or "{}"
            )

    except urllib.error.HTTPError as error:

        raw = (
            error.read().decode()
            if error.fp
            else ""
        )

        try:

            message = (
                json.loads(raw)
                .get("error", {})
                .get("message")
                or raw
            )

        except Exception:

            message = raw

        raise RuntimeError(
            message or "Error de Stripe"
        )


# =========================================================
# SUPABASE - LEER DATOS
# =========================================================

def get_data(negocio_id):

    url = env("SUPABASE_URL")
    key = env("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Falta SUPABASE_URL o "
            "SUPABASE_SERVICE_ROLE_KEY."
        )

    q = urllib.parse.quote(
        str(negocio_id),
        safe=""
    )

    request = urllib.request.Request(
        f"{url.rstrip('/')}/rest/v1/negocio_data"
        f"?user_id=eq.{q}&select=data"
    )

    request.add_header("apikey", key)
    request.add_header(
        "Authorization",
        "Bearer " + key
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode() or "[]"
            )

            return (
                data[0].get("data") or {}
                if data
                else {}
            )

    except Exception:

        return {}


# =========================================================
# SUPABASE - GUARDAR DATOS
# =========================================================

def save_data(negocio_id, data):

    url = env("SUPABASE_URL")
    key = env("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Falta SUPABASE_URL o "
            "SUPABASE_SERVICE_ROLE_KEY."
        )

    body = json.dumps(
        {
            "user_id": str(negocio_id).lower(),
            "data": data
        }
    ).encode()

    request = urllib.request.Request(
        url.rstrip("/") +
        "/rest/v1/negocio_data",
        data=body,
        method="POST"
    )

    request.add_header("apikey", key)
    request.add_header(
        "Authorization",
        "Bearer " + key
    )
    request.add_header(
        "Content-Type",
        "application/json"
    )
    request.add_header(
        "Prefer",
        "resolution=merge-duplicates"
    )

    with urllib.request.urlopen(
        request,
        timeout=10
    ) as response:

        response.read()


# =========================================================
# CONNECT
# =========================================================

def connect(negocio_id, h):

    if not stripe_client_id():

        raise RuntimeError(
            "Falta STRIPE_CONNECT_CLIENT_ID "
            "o STRIPE_CLIENT_ID en Vercel."
        )

    if not stripe_secret_key():

        raise RuntimeError(
            "Falta STRIPE_SECRET_KEY en Vercel."
        )

    url = (
        "https://connect.stripe.com/oauth/authorize?"
        + urllib.parse.urlencode(
            {
                "response_type": "code",
                "client_id": stripe_client_id(),
                "scope": "read_write",
                "redirect_uri": redirect_uri(h),
                "state": state_make(negocio_id)
            }
        )
    )

    return {
        "ok": True,
        "url": url
    }


# =========================================================
# DISCONNECT
# =========================================================

def disconnect(negocio_id):

    data = get_data(negocio_id)

    account_id = (
        data.get("stripe_account_id")
        or data.get("stripeAccountId")
        or ""
    )

    if account_id:

        key = stripe_secret_key()
        client_id = stripe_client_id()

        if not key:

            raise RuntimeError(
                "Falta STRIPE_SECRET_KEY en Vercel."
            )

        if not client_id:

            raise RuntimeError(
                "Falta STRIPE_CONNECT_CLIENT_ID "
                "o STRIPE_CLIENT_ID en Vercel."
            )

        form = urllib.parse.urlencode(
            {
                "client_id": client_id,
                "stripe_user_id": account_id
            }
        ).encode()

        request = urllib.request.Request(
            "https://connect.stripe.com/oauth/deauthorize",
            data=form,
            method="POST"
        )

        request.add_header(
            "Authorization",
            "Basic " +
            base64.b64encode(
                (key + ":").encode()
            ).decode()
        )

        request.add_header(
            "Content-Type",
            "application/x-www-form-urlencoded"
        )

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            response.read()

    data.update(
        {
            "stripe_account_id": "",
            "stripe_connected": False
        }
    )

    save_data(
        negocio_id,
        data
    )

    return {
        "ok": True
    }


# =========================================================
# STATUS
# =========================================================

def status(negocio_id):

    data = get_data(negocio_id)

    account_id = (
        data.get("stripe_account_id")
        or data.get("stripeAccountId")
        or ""
    )

    connected = bool(
        account_id
        and data.get(
            "stripe_connected",
            True
        )
    )

    return {
        "ok": True,
        "connected": connected,
        "account_id": account_id if account_id else ""
    }


# =========================================================
# CALLBACK DE STRIPE
# =========================================================

def handle_callback(h):

    query = urllib.parse.parse_qs(
        urllib.parse.urlparse(
            h.path
        ).query
    )

    if query.get("error"):

        return redirect(
            h,
            FIXED_APP_URL + "/?stripe=cancelled"
        )

    code = (
        query.get("code", [""])[0]
        or ""
    ).strip()

    state = (
        query.get("state", [""])[0]
        or ""
    ).strip()

    negocio_id = state_read(state)

    if not code or not negocio_id:

        return redirect(
            h,
            FIXED_APP_URL + "/?stripe=invalid_state"
        )

    try:

        result = stripe_request(
            "/v1/oauth/token",
            "POST",
            {
                "client_secret":
                    stripe_secret_key(),
                "code":
                    code,
                "grant_type":
                    "authorization_code"
            }
        )

        account_id = (
            result.get("stripe_user_id")
            or result.get("stripe_account_id")
        )

        if not account_id:

            raise RuntimeError(
                "Stripe no devolvió la cuenta conectada."
            )

        data = get_data(negocio_id)

        data.update(
            {
                "stripe_account_id":
                    account_id,
                "stripe_connected":
                    True
            }
        )

        save_data(
            negocio_id,
            data
        )

        return redirect(
            h,
            FIXED_APP_URL + "/?stripe=connected"
        )

    except Exception:

        return redirect(
            h,
            FIXED_APP_URL + "/?stripe=error"
        )


# =========================================================
# REDIRECT
# =========================================================

def redirect(h, url):

    h.send_response(302)

    h.send_header(
        "Location",
        url
    )

    h.send_header(
        "Cache-Control",
        "no-store"
    )

    h.end_headers()


# =========================================================
# /api/stripe
# =========================================================

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):

        send_json(
            self,
            {}
        )

    def do_POST(self):

        try:

            data = read_json(self)

            negocio_id = str(
                data.get("negocio_id")
                or ""
            ).strip()

            if not negocio_id:

                return send_json(
                    self,
                    {
                        "ok": False,
                        "msg":
                            "Falta negocio_id."
                    },
                    400
                )

            action = str(
                data.get("action")
                or ""
            ).strip().lower()

            if action == "connect":

                return send_json(
                    self,
                    connect(
                        negocio_id,
                        self
                    )
                )

            if action == "disconnect":

                return send_json(
                    self,
                    disconnect(
                        negocio_id
                    )
                )

            if action == "status":

                return send_json(
                    self,
                    status(
                        negocio_id
                    )
                )

            return send_json(
                self,
                {
                    "ok": False,
                    "msg":
                        "Acción de Stripe no válida."
                },
                400
            )

        except Exception as error:

            return send_json(
                self,
                {
                    "ok": False,
                    "msg": str(error)
                },
                500
            )

    def do_GET(self):

        return handle_callback(self)
