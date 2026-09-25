import os, stripe
from flask import request, jsonify
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route('/api/crear-cobro', methods=['POST'])
def crear_cobro():
    data = request.get_json()
    monto = int(float(data.get('monto', 0)) * 100)  # $49 -> 4900 centavos
    # Crea el intento de cobro
    intent = stripe.PaymentIntent.create(
        amount=monto,
        currency='mxn',
        automatic_payment_methods={'enabled': True}
    )
    return jsonify({'clientSecret': intent.client_secret})

@app.route('/cobrar')
def cobrar_page():
    return """
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://js.stripe.com/v3/"></script>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-50 p-4 flex justify-center">
<div class="bg-white max-w-sm w-full p-6 rounded-2xl shadow mt-10">
<h1 class="text-xl font-bold">Cobrar con tarjeta 💳</h1>
<p class="text-sm text-gray-500">Botes Jacona - Jacona, Mich.</p>
<input id="monto" type="number" placeholder="Monto $ Ej: 150" class="w-full border p-3 rounded-xl mt-4 text-xl font-bold">
<div id="payment-element" class="mt-4"></div>
<button id="pagar" class="w-full mt-4 bg-black text-white py-3 rounded-xl font-bold">Cobrar ahora</button>
<p id="msg" class="text-center text-sm mt-3"></p>
</div>
<script>
const stripe = Stripe('pk_live_TU_PUBLIC_KEY_AQUI'); // Pon tu pk_live o pk_test
let elements, paymentElement, clientSecret;

document.getElementById('monto').addEventListener('change', async ()=>{
  let monto = document.getElementById('monto').value;
  if(!monto) return;
  const res = await fetch('/api/crear-cobro', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({monto: monto})
  });
  const data = await res.json();
  clientSecret = data.clientSecret;
  elements = stripe.elements({clientSecret});
  paymentElement = elements.create('payment');
  paymentElement.mount('#payment-element');
});

document.getElementById('pagar').onclick = async ()=>{
  document.getElementById('msg').innerText='Cobrando...';
  const {error} = await stripe.confirmPayment({elements, confirmParams:{return_url: window.location.href}});
  if(error){ document.getElementById('msg').innerText = error.message; }
};
</script>
</body>
</html>
"""
