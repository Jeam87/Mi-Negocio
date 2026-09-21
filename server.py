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
        # Create the product on the connected account
        product = stripe.Product.create(
            name=product_name,
            description=product_description,
            stripe_account=account_id
        )

        # Create a price for the product on the connected account
        price = stripe.Price.create(
            product=product.id,
            unit_amount=product_price,
            currency='usd',
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
            # Set to "full" for the Stripe Dashboard or "express" for the Express Dashboard
            "dashboard": "full",
            "defaults": {
                "responsibilities": {
                    "fees_collector": "stripe",
                    "losses_collector": "stripe",
                }
            },
            "identity": {
                "country": "US",
                "entity_type": "company",
            },
            "configuration": {
                "merchant": {
                    "capabilities": {
                        "card_payments": {"requested": True},
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
                    "configurations": ["merchant"
],
                    "refresh_url": "https://example.com",
                    "return_url": f"https://example.com?accountId={account_id}",
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

    # Get the price's type from Stripe
    price = stripe.Price.retrieve(
        price_id,
        stripe_account=account_id
    )
    price_type = price.type
    mode = 'subscription' if price_type == 'recurring' else 'payment'

    checkout_session = stripe.checkout.Session.create(
      line_items=[
        {
          'price': price_id,
          'quantity': 1
        }
      ],
      mode=mode,
      payment_intent_data={
          'application_fee_amount': 150, # AQUI TU 1.5% - si el producto es de $100 pesos
      },
      success_url=f"{os.getenv('DOMAIN')}/done?session_id={{CHECKOUT_SESSION_ID}}",
      cancel_url=f"{os.getenv('DOMAIN')}",
      stripe_account=account_id
        )

    response = make_response(redirect(checkout_session.url, code=303))

    return response



@app.route('/api/webhook', methods=['POST'])
def webhook_received():
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
    endpoint_secret = ''
    request_data = json.loads(request.data)

    # Only verify the event if you have an endpoint secret defined.
    # Otherwise use the basic event deserialized with JSON.parse
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

    # Handle the event
    match event['type']:
        case 'checkout.session.completed':
            session = event['data']['object']
            status = session['status']
            app.logger.info(f'Checkout Session status is {status}.')
            # Then define and call a method to handle the checkout session completed.
            # handle_checkout_session_completed(session);
        case 'checkout.session.async_payment_failed':
            session = event['data']['object']
            status = session['status']
            app.logger.info(f'Checkout Session status is {status}.')
            # Then define and call a method to handle the checkout session failed.
            # handle_checkout_session_failed(session);
        case _:
            # Unexpected event type
            app.logger.info(f'Unhandled event type {event["type"]}')

    # Return a 200 response to acknowledge receipt of the event
    return jsonify({'status': 'success'})

@app.route('/api/thin-webhook', methods=['POST'])
def thin_webhook():
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
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
