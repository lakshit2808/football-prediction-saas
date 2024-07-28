import stripe
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from DBConnection import increment_credits, usercheck_with_payment, register_user_with_payment, update_user_address

payment_plans = [
    {"credits": 10, "cost_cents": 3000},   # 10 credits for 30 dollars, which is 3000 cents
    {"credits": 50, "cost_cents": 5000},   # 50 credits for 50 dollars, which is 5000 cents
    {"credits": 100, "cost_cents": 10000}  # 100 credits for 100 dollars, which is 10000 cents
]
payment_data = {}

# Process the payment data and update credits
def process_payment(payment_data, payment_plans):
    """Function to process payment and update user credits."""
    email = payment_data['email']
    phone = payment_data['phone']
    amount_in_cents = payment_data['amount_in_cents']
    
    # Find the matching payment plan
    for plan in payment_plans:
        if plan['cost_cents'] == amount_in_cents:
            credits_to_add = plan['credits']
            increment_credits(email, credits_to_add)
            break
    else:
        print("No matching payment plan found.")


# Load environment variables
load_dotenv()

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_API_KEY")
endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")

# Initialize FastAPI app
app = FastAPI()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error("Invalid payload: %s", e)
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid signature: %s", e)
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    event_type = event['type']
    event_data = event['data']['object']

    # Add the event type to the event data for clarity
    event_data['event_type'] = event_type

    if event_type == 'checkout.session.completed':
        # Handle the checkout.session.completed event
        session_id = event_data.get('id')
        customer_id = event_data.get('customer')
        amount_total = event_data.get('amount_total')
        currency = event_data.get('currency')
        payment_status = event_data.get('payment_status')
        payment_intent = event_data.get('payment_intent')
        subscription = event_data.get('subscription')

        # Add details to event_data
        event_data.update({
            "session_id": session_id,
            "customer_id": customer_id,
            "amount_total": amount_total,
            "currency": currency,
            "payment_status": payment_status,
            "payment_intent": payment_intent,
            "subscription": subscription,

        })
        
        # Save event data
        customer_data = event_data['customer_details']
    
        payment_data = {
            'name': customer_data['name'],
            'email': customer_data['email'],
            'phone': customer_data['phone'],
            'amount_in_cents': event_data['amount_total'],
            'status': event_data['payment_status'],
        }

        address = {
            'city': customer_data['address']['city'],
            "state:": customer_data['address']['state'],
            "country": customer_data['address']['country']
        }
        if usercheck_with_payment(payment_data['email'], payment_data['phone']): # Check if address is none
            register_user_with_payment(payment_data['name'], payment_data['phone'], payment_data['email'])
            print("Registering User")

        update_user_address(payment_data['email'], address)
            
        process_payment(payment_data, payment_plans)
        print("Credits Added!")

        
    else:
        logger.info('Unhandled event type %s', event_type)

    return JSONResponse(content={"success": True})
