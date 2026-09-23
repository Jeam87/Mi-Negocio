#! /usr/bin/env python3.6

import os
import json
from flask import Flask, jsonify, request, redirect, make_response
from dotenv import load_dotenv
from flask_cors import CORS
# Load environment variables
load_dotenv()

import stripe

from stripe import StripeClient
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

stripe_client = StripeClient(str(os.getenv("STRIPE_SECRET_KEY")))

app = Flask(__name__)

CORS(app)

# Helper method to parse request body (JSON or form data)
def parse_request_body():
    data = {}

    json_data = request.get_json(silent=True)
    if json_data and isinstance(json_data, dict):
        data.update(json_data)

    if request.form:
        data.update(request.form.to_dict())

    if request.args:
        data.update(request.args.to_dict())

    return data

@app.route('/api/create-product', methods=['POST'])
def create_product():
    data = parse_request_body()
    product_name = data['productName']
    product_description = data['productDescription']
    product_price = data['productPrice']
    account_id = data['accountId']

    try:
        product = stripe.Product.create(
            name=product_name,
            description=product_description,
            stripe_account=account_id
        )

        price = stripe.Price.create(
            product=product.id,
            unit_amount=product_price,
            currency='mxn', # Cambiado a MXN para México
            stripe_account=account_id
        )

        return jsonify({
            'productName': product_name,
            'productDescription': product_description,
            'productPrice': product_price,
            'priceId': price.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-connect-account', methods=['POST'])
def create_connect_account():
    data = parse_request_body()

    try:
        account = stripe_client.v2.core.accounts.create({
            "display_name": data.get("email"),
            "contact_email": data.get("email"),
            "dashboard": "express", # Express = tu modelo de 1.5%
            "defaults": {
                "responsibilities": {
                    "fees_collector": "stripe", # Ellas pagan la comisión de Stripe
                    "losses_collector": "stripe",
                }
            },
            "identity": {
                "country": "MX", # México
                "entity_type": "individual", # Autónomo
            },
            "configuration": {
                "merchant": {
                    "capabilities": {
                        "card_payments": {"requested": True},
                        "oxxo_payments": {"requested": True},
                    }
                },
            },
        })

        return jsonify({'accountId': account.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-account-link', methods=['POST'])
def create_account_link():
    data = parse_request_body()
    account_id = data['accountId']

    try:
        account_link = stripe_client.v2.core.account_links.create({
            "account": account_id,
            "use_case": {
                "type": "account_onboarding",
                "account_onboarding": {
                    "configurations": ["merchant"],
                    "refresh_url": f"{os.getenv('DOMAIN')}",
                    "return_url": f"{os.getenv('DOMAIN')}?accountId={account_id}",
                },
            },
        })

        return jsonify({'url': account_link.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/account-status/<account_id>', methods=['GET'])
def account_status(account_id):
    try:
        account = stripe_client.v2.core.accounts.retrieve(
            account_id, {
                "include": [
                    "requirements",
                    "configuration.merchant"
                ]
            }
        )
        payouts_enabled = (
            (account.get("configuration") or {}).get("merchant") or {}
        ).get("capabilities", {}).get("stripe_balance", {}).get("payouts", {}).get(
            "status"
        ) == "active"
        charges_enabled = (
            (account.get("configuration") or {}).get("merchant") or {}
        ).get("capabilities", {}).get("card_payments", {}).get("status") == "active"
        summary_status = (
            ((account.get("requirements") or {}).get("summary") or {})
            .get("minimum_deadline", {})
            .get("status")
        )
        details_submitted = (summary_status is None) or (
            summary_status == "eventually_due"
        )
        return jsonify(
            {
                "id": account["id"],
                "payoutsEnabled": payouts_enabled,
                "chargesEnabled": charges_enabled,
                "detailsSubmitted": details_submitted,
                "requirements": (account.get("requirements") or {}).get("entries"),
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<account_id>', methods=['GET'])
def get_products(account_id):
    try:
        if account_id != 'platform':
            prices = stripe.Price.list(
                expand=['data.product'],
                active=True,
                limit=100,
                stripe_account=account_id
            )
        else:
            prices = stripe.Price.list(
                expand=['data.product'],
                active=True,
                limit=100
            )

        products = []
        for price in prices.data:
            products.append({
                'id': price.product.id,
                'name': price.product.name,
                'description': price.product.description,
                'price': price.unit_amount,
                'priceId': price.id,
                'image': 'https://i.imgur.com/6Mvijcm.png'
            })

        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = parse_request_body()
    account_id = data['accountId']
    price_id = data['priceId']

    # Obtener el precio para calcular tu 1.5% automático
    price = stripe.Price.retrieve(
        price_id,
        stripe_account=account_id
    )
    
    # Calculo de tu comisión
    amount = price.unit_amount
    fee_amount = int(amount * 0.015) # 1.5%

    checkout_session = stripe.checkout.Session.create(
      line_items=[
        {
          'price': price_id,
          'quantity': 1
        }
      ],
      mode='payment',
      payment_intent_data={
          "application_fee_amount": fee_amount, # TU GANANCIA VA AQUÍ
      },
      success_url=f"{os.getenv('DOMAIN')}/done?session_id={{CHECKOUT_SESSION_ID}}",
      cancel_url=f"{os.getenv('DOMAIN')}",
      stripe_account=account_id
    )

    response = make_response(redirect(checkout_session.url, code=303))
    return response

@app.route('/api/webhook', methods=['POST'])
def webhook_received():
    endpoint_secret = ''
    request_data = json.loads(request.data)

    if endpoint_secret:
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                request.data, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            app.logger.info('⚠️  Webhook signature verification failed.')
            return jsonify({'error': str(e)}), 400
    else:
        event = request_data

    match event['type']:
        case 'checkout.session.completed':
            session = event['data']['object']
            status = session['status']
            app.logger.info(f'Checkout Session status is {status}.')
        case 'checkout.session.async_payment_failed':
            session = event['data']['object']
            status = session['status']
            app.logger.info(f'Checkout Session status is {status}.')
        case _:
            app.logger.info(f'Unhandled event type {event["type"]}')

    return jsonify({'status': 'success'})

@app.route('/api/thin-webhook', methods=['POST'])
def thin_webhook():
    thin_endpoint_secret = ''
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event_notif = stripe_client.parse_event_notification(
            payload, sig_header, thin_endpoint_secret
        )
    except Exception as e:
        app.logger.info(f"⚠️  Thin webhook signature verification failed: {e}")
        return jsonify({'error': 'bad signature'}), 400

    if event_notif.type == "v2.account.created":
        event_notif.fetch_related_object()
        event_notif.fetch_event()
    else:
        app.logger.info(f'Unhandled event type {event_notif.type}')

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(port=4242, host="::1", debug=True) 
