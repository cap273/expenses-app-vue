from flask import Blueprint, jsonify, request, current_app
from plaid.api import plaid_api
from plaid.model import *
from plaid import ApiClient
from plaid.configuration import Configuration
from plaid.exceptions import ApiException
import os

plaid_routes = Blueprint("plaid_routes", __name__)

# Initialize the Plaid API client with the environment variables
configuration = Configuration(
    host='sandbox',
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET')
    }
)

api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Route to create a link token
@plaid_routes.route('/api/create_link_token', methods=['GET'])
def create_link_token():
    try:
        response = api_client.LinkToken.create({
            'user': {
                'client_user_id': 'unique_user_id',  # This should be a unique ID for each user
            },
            'client_name': 'My Finance App',
            'products': ['transactions'],
            'country_codes': ['US'],
            'language': 'en',
        })
        return jsonify({'link_token': response['link_token']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to exchange public token for access token
@plaid_routes.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    public_token = request.json.get('public_token')
    try:
        response = api_client.Item.public_token.exchange(public_token)
        access_token = response['access_token']
        # Save the access token securely in your database associated with the user
        return jsonify({'access_token': access_token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to fetch transactions
@plaid_routes.route('/api/transactions', methods=['POST'])
def fetch_transactions():
    access_token = request.json.get('access_token')  # Retrieve user's access token from the request
    try:
        response = api_client.Transactions.get(access_token, start_date='2022-01-01', end_date='2022-12-31')
        transactions = response['transactions']
        return jsonify({'transactions': transactions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
