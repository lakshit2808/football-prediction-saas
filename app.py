import json
import stripe
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

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

# File path to save event data
FILE_PATH = 'stripe_events.json'

def save_event_to_file(event_data: dict):
    # Read existing data from file
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)
    else:
        data = []

    # Append new event data
    data.append(event_data)

    # Write updated data to file
    with open(FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

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
        line_items = event_data.get('line_items', {}).get('data', [])

        # Add details to event_data
        event_data.update({
            "session_id": session_id,
            "customer_id": customer_id,
            "amount_total": amount_total,
            "currency": currency,
            "payment_status": payment_status,
            "payment_intent": payment_intent,
            "subscription": subscription,
            "line_items": []
        })

        # Fetch customer details if customer_id is present
        if customer_id:
            try:
                customer = stripe.Customer.retrieve(customer_id)
                customer_email = customer.get('email')
                event_data["customer_email"] = customer_email
            except stripe.error.StripeError as e:
                logger.error("Error retrieving customer details: %s", e)

        # Add line items details
        for item in line_items:
            price_id = item.get('price', {}).get('id')
            quantity = item.get('quantity')
            unit_amount = item.get('price', {}).get('unit_amount')
            event_data["line_items"].append({
                "price_id": price_id,
                "quantity": quantity,
                "unit_amount": unit_amount
            })
        
        # Save event data to file
        save_event_to_file(event_data)
        
    else:
        logger.info('Unhandled event type %s', event_type)

    return JSONResponse(content={"success": True})
