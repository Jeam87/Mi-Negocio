import Stripe from 'stripe'
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY)

export async function POST(req) {
  const { monto, concepto, cuenta_conectada_id } = await req.json()
  
  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [{ price_data: { currency: 'mxn', product_data: { name: concepto }, unit_amount: monto * 100 }, quantity: 1 }],
    payment_intent_data: {
      application_fee_amount: Math.round(monto * 100 * 0.015), // tu 1.5%
      transfer_data: { destination: cuenta_conectada_id }
    },
    success_url: 'https://mi-negocio-mauve.vercel.app/exito',
  })
  return Response.json({ url: session.url })
}
