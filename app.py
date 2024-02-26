from flask import Flask, request, jsonify
import requests
import base64
import datetime
import json

app = Flask(__name__)

# Replace these values with your actual Safaricom Daraja API credentials
CONSUMER_KEY = "Your consumer key"
CONSUMER_SECRET = "Your consumer secret"
LIPA_NA_MPESA_PASSKEY = "your passkey"
SHORTCODE = "174379"
LIPA_NA_MPESA_ONLINE_ENDPOINT = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

@app.route('/callback_url', methods=['POST'])
def callback_url():
    data = request.json

    # Process the callback data
    transaction_status = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    print(data)
    if transaction_status == 0:
        print("Payment successful")
    else:
        # Payment failed
        # Handle the failure scenario
        print("Payment failed")

    return jsonify({"ResultCode": 0, "ResultDesc": "Success"})  # Respond to Safaricom with a success message

@app.route('/lipa_na_mpesa', methods=['POST'])
def lipa_na_mpesa():
    try:
        token = generate_token()
        if token is None:
            return jsonify({"error": "Failed to generate token"}), 500
        phone_number = request.json.get('phone_number')
        amount = request.json.get('amount')
        
        if not phone_number or not amount:
            return jsonify({"error": "Phone number and amount are required"}), 400

        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((SHORTCODE + LIPA_NA_MPESA_PASSKEY + timestamp).encode()).decode('utf-8')

        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://8ead-41-80-111-14.ngrok-free.app/callback_url",
            "AccountReference": "Test123",
            "TransactionDesc": "Payment for testing"
        }

        headers = {
            "Authorization": "Bearer " + generate_token(),
            "Content-Type": "application/json"
        }

        response = requests.post(LIPA_NA_MPESA_ONLINE_ENDPOINT, json=payload, headers=headers)

        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_token():
    token_endpoint = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    credentials = base64.b64encode((CONSUMER_KEY + ':' + CONSUMER_SECRET).encode()).decode('utf-8')
    headers = {
        'Authorization': 'Basic ' + credentials
    }

    try:
        response = requests.get(token_endpoint, headers=headers)
        response.raise_for_status()  
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to generate token: {e}") from e


if __name__ == '__main__':
    app.run(debug=True)
