from flask import Blueprint, jsonify, request, current_app
#category mapping added via utils
from flask_backend.utils.category_mapping import get_category_for_transaction, is_income_category


# Read env vars from .env file
import base64
import os
import datetime as dt
import json
import time
from datetime import date, timedelta, datetime
import uuid

# imports for scope assiociation
from flask_login import current_user
from flask_backend.utils.session import login_required_api
from flask_backend.database.models import db, Account, Person, Scope, ScopeAccess, PlaidItem
from flask_backend.database.tables import expenses_table
from sqlalchemy import and_, or_, select
from dateutil import parser

from dotenv import load_dotenv
from flask import Flask, request, jsonify
import plaid
from plaid.model.payment_amount import PaymentAmount
from plaid.model.payment_amount_currency import PaymentAmountCurrency
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.recipient_bacs_nullable import RecipientBACSNullable
from plaid.model.payment_initiation_address import PaymentInitiationAddress
from plaid.model.payment_initiation_recipient_create_request import PaymentInitiationRecipientCreateRequest
from plaid.model.payment_initiation_payment_create_request import PaymentInitiationPaymentCreateRequest
from plaid.model.payment_initiation_payment_get_request import PaymentInitiationPaymentGetRequest
from plaid.model.link_token_create_request_payment_initiation import LinkTokenCreateRequestPaymentInitiation
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.user_create_request import UserCreateRequest
from plaid.model.consumer_report_user_identity import ConsumerReportUserIdentity
from plaid.model.asset_report_create_request import AssetReportCreateRequest
from plaid.model.asset_report_create_request_options import AssetReportCreateRequestOptions
from plaid.model.asset_report_user import AssetReportUser
from plaid.model.asset_report_get_request import AssetReportGetRequest
from plaid.model.asset_report_pdf_get_request import AssetReportPDFGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.investments_transactions_get_request_options import InvestmentsTransactionsGetRequestOptions
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.transfer_authorization_create_request import TransferAuthorizationCreateRequest
from plaid.model.transfer_create_request import TransferCreateRequest
from plaid.model.transfer_get_request import TransferGetRequest
from plaid.model.transfer_network import TransferNetwork
from plaid.model.transfer_type import TransferType
from plaid.model.transfer_authorization_user_in_request import TransferAuthorizationUserInRequest
from plaid.model.ach_class import ACHClass
from plaid.model.transfer_create_idempotency_key import TransferCreateIdempotencyKey
from plaid.model.transfer_user_address_in_request import TransferUserAddressInRequest
from plaid.model.signal_evaluate_request import SignalEvaluateRequest
from plaid.model.statements_list_request import StatementsListRequest
from plaid.model.link_token_create_request_statements import LinkTokenCreateRequestStatements
from plaid.model.link_token_create_request_cra_options import LinkTokenCreateRequestCraOptions
from plaid.model.statements_download_request import StatementsDownloadRequest
from plaid.model.consumer_report_permissible_purpose import ConsumerReportPermissiblePurpose
from plaid.model.cra_check_report_base_report_get_request import CraCheckReportBaseReportGetRequest
from plaid.model.cra_check_report_pdf_get_request import CraCheckReportPDFGetRequest
from plaid.model.cra_check_report_income_insights_get_request import CraCheckReportIncomeInsightsGetRequest
from plaid.model.cra_check_report_partner_insights_get_request import CraCheckReportPartnerInsightsGetRequest
from plaid.model.cra_pdf_add_ons import CraPDFAddOns
from plaid.api import plaid_api

load_dotenv()


plaid_routes = Blueprint("plaid_routes", __name__)

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_REDIRECT_URI to 'http://localhost:3000/'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to configure
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))


# We store the access_token in memory - in production, store it in a secure
# persistent data store.
access_token = None
# The payment_id is only relevant for the UK Payment Initiation product.
# We store the payment_id in memory - in production, store it in a secure
# persistent data store.
payment_id = None
# The transfer_id is only relevant for Transfer ACH product.
# We store the transfer_id in memory - in production, store it in a secure
# persistent data store.
transfer_id = None
# We store the user_token in memory - in production, store it in a secure
# persistent data store.
user_token = None

item_id = None


@plaid_routes.route('/api/info', methods=['POST'])
def info():
    global access_token
    global item_id
    return jsonify({
        'item_id': item_id,
        'access_token': access_token,
        'products': PLAID_PRODUCTS
    })


@plaid_routes.route('/api/create_link_token_for_payment', methods=['POST'])
def create_link_token_for_payment():
    global payment_id
    try:
        request = PaymentInitiationRecipientCreateRequest(
            name='John Doe',
            bacs=RecipientBACSNullable(account='26207729', sort_code='560029'),
            address=PaymentInitiationAddress(
                street=['street name 999'],
                city='city',
                postal_code='99999',
                country='GB'
            )
        )
        response = client.payment_initiation_recipient_create(
            request)
        recipient_id = response['recipient_id']

        request = PaymentInitiationPaymentCreateRequest(
            recipient_id=recipient_id,
            reference='TestPayment',
            amount=PaymentAmount(
                PaymentAmountCurrency('GBP'),
                value=100.00
            )
        )
        response = client.payment_initiation_payment_create(
            request
        )
        pretty_print_response(response.to_dict())
        
        # We store the payment_id in memory for demo purposes - in production, store it in a secure
        # persistent data store along with the Payment metadata, such as userId.
        payment_id = response['payment_id']
        
        linkRequest = LinkTokenCreateRequest(
            # The 'payment_initiation' product has to be the only element in the 'products' list.
            products=[Products('payment_initiation')],
            client_name='Plaid Test',
            # Institutions from all listed countries will be shown.
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language='en',
            user=LinkTokenCreateRequestUser(
                # This should correspond to a unique id for the current user.
                # Typically, this will be a user ID number from your application.
                # Personally identifiable information, such as an email address or phone number, should not be used here.
                client_user_id=str(time.time())
            ),
            payment_initiation=LinkTokenCreateRequestPaymentInitiation(
                payment_id=payment_id
            )
        )

        if PLAID_REDIRECT_URI!=None:
            linkRequest['redirect_uri']=PLAID_REDIRECT_URI
        linkResponse = client.link_token_create(linkRequest)
        pretty_print_response(linkResponse.to_dict())
        return jsonify(linkResponse.to_dict())
    except plaid.ApiException as e:
        return json.loads(e.body)


@plaid_routes.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    global user_token
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Plaid Quickstart",
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            )
        )
        if PLAID_REDIRECT_URI!=None:
            request['redirect_uri']=PLAID_REDIRECT_URI
        if Products('statements') in products:
            statements=LinkTokenCreateRequestStatements(
                end_date=date.today(),
                start_date=date.today()-timedelta(days=30)
            )
            request['statements']=statements

        cra_products = ["cra_base_report", "cra_income_insights", "cra_partner_insights"]
        if any(product in cra_products for product in PLAID_PRODUCTS):
            request['user_token'] = user_token
            request['consumer_report_permissible_purpose'] = ConsumerReportPermissiblePurpose('ACCOUNT_REVIEW_CREDIT')
            request['cra_options'] = LinkTokenCreateRequestCraOptions(
                days_requested=60
            )
    # create link token
        response = client.link_token_create(request)
        print(response)
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        print(e)
        return json.loads(e.body)

# Create a user token which can be used for Plaid Check, Income, or Multi-Item link flows
# https://plaid.com/docs/api/users/#usercreate
@plaid_routes.route('/api/create_user_token', methods=['POST'])
def create_user_token():
    global user_token
    try:
        consumer_report_user_identity = None
        user_create_request = UserCreateRequest(
            # Typically this will be a user ID number from your application. 
            client_user_id="user_" + str(uuid.uuid4())
        )

        cra_products = ["cra_base_report", "cra_income_insights", "cra_partner_insights"]
        if any(product in cra_products for product in PLAID_PRODUCTS):
            print("Using CRA products")
            consumer_report_user_identity = ConsumerReportUserIdentity(
                first_name="Harry",
                last_name="Potter",
                phone_numbers= ['+16174567890'],
                emails= ['harrypotter@example.com'],
                primary_address= {
                    "city": 'New York',
                    "region": 'NY',
                    "street": '4 Privet Drive',
                    "postal_code": '11111',
                    "country": 'US'
                }
            )
            user_create_request["consumer_report_user_identity"] = consumer_report_user_identity

        user_response = client.user_create(user_create_request)
        print(user_response)
        user_token = user_response['user_token']
        return jsonify(user_response.to_dict())
    except plaid.ApiException as e:
        print(e)
        return jsonify(json.loads(e.body)), e.status


# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow


# Updated and new routes for plaid to support scope integration and properly target user
# Update the /api/set_access_token route
@plaid_routes.route('/api/set_access_token', methods=['POST'])
@login_required_api
def get_access_token():
    global access_token
    global item_id
    global transfer_id
    try:
        # Parse JSON data from request body
        data = request.get_json()
        public_token = data.get('public_token')
        scope_id = data.get('scope_id')
        
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400

        if not scope_id:
            return jsonify({"error": "scope_id is required"}), 400
            
        # Validate that user has access to this scope
        scope_access = ScopeAccess.query.filter_by(
            ScopeID=scope_id,
            AccountID=current_user.id,
            InviteStatus='accepted'
        ).first()
        
        if not scope_access:
            return jsonify({"error": "You don't have access to this scope"}), 403
        
        # Exchange the public token for an access token and item ID
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        
        # Store the access token and item ID globally (temporary storage for this example)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        
        # Get item details with institution information
        item_request = ItemGetRequest(access_token=access_token)
        item_response = client.item_get(item_request)
        
        institution_id = item_response['item']['institution_id']
        institution_name = "Unknown Institution"
        
        try:
            # Get institution name if available
            institution_request = InstitutionsGetByIdRequest(
                institution_id=institution_id,
                country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES))
            )
            institution_response = client.institutions_get_by_id(institution_request)
            institution_name = institution_response['institution'].get('name', institution_name)
        except plaid.ApiException:
            # Continue even if we can't get the institution name
            pass
        # Check if we already have this Plaid item in our database
        existing_item = PlaidItem.query.filter_by(PlaidItemID=item_id).first()
        
        if existing_item:
            # Update the existing item if needed
            existing_item.AccessToken = access_token
            existing_item.LastUpdated = datetime.now().date()
            db.session.commit()
        else:
            # Store the Plaid item in our database
            new_item = PlaidItem(
                ScopeID=scope_id,
                PlaidItemID=item_id,
                AccessToken=access_token,
                InstitutionName=institution_name,
                InstitutionID=institution_id,
                LastSynced=datetime.now(),
                CreateDate=datetime.now().date(),
                LastUpdated=datetime.now().date()
            )
            db.session.add(new_item)
            db.session.commit()
        
        # Return a success response with institution name for frontend display
        return jsonify({
            "success": True,
            "item_id": item_id,
            "access_token": access_token,  # Note: In production, you shouldn't return the actual token
            "institution_name": institution_name,
            "scope_id": scope_id
        })
        
    except KeyError:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Add a new route for syncing transactions
@plaid_routes.route('/api/sync_transactions', methods=['POST'])
@login_required_api
def sync_transactions():
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        
        if not item_id:
            return jsonify({"error": "item_id is required"}), 400
        
        # Get the plaid item from database
        plaid_item = PlaidItem.query.filter_by(PlaidItemID=item_id).first()
        if not plaid_item:
            return jsonify({"error": "Plaid item not found"}), 404
            
        # Verify user has access to the item's scope
        scope_access = ScopeAccess.query.filter_by(
            ScopeID=plaid_item.ScopeID,
            AccountID=current_user.id,
            InviteStatus='accepted'
        ).first()
        
        if not scope_access:
            return jsonify({"error": "You don't have access to this scope"}), 403
            
        # Set cursor to empty to receive initial updates, or use saved cursor for subsequent syncs
        cursor = plaid_item.SyncToken or ''
        
        # New transaction updates since "cursor"
        added = []
        modified = []
        removed = []  # Removed transaction ids
        has_more = True
        
        # Iterate through each page of new transaction updates for item
        while has_more:
            sync_request = TransactionsSyncRequest(
                access_token=plaid_item.AccessToken,
                cursor=cursor,
            )
            response = client.transactions_sync(sync_request).to_dict()
            
            # Update cursor with the new value
            cursor = response['next_cursor']
            
            # Add this page of results
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            has_more = response['has_more']
            
        # Save the cursor for future syncs
        plaid_item.SyncToken = cursor
        plaid_item.LastSynced = datetime.now()
        plaid_item.LastUpdated = datetime.now().date()
        db.session.commit()
        
        # Submit any new transactions to the database
        if added:
            # Submit the Plaid transactions to the backend
            result = submit_plaid_transactions_to_db(added, plaid_item.ScopeID)
            
        return jsonify({
            "success": True,
            "added": len(added),
            "modified": len(modified),
            "removed": len(removed),
            "cursor": cursor,
            "institution_name": plaid_item.InstitutionName
        })
        
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def submit_plaid_transactions_to_db(transactions, scope_id):
    """
    Helper function to submit Plaid transactions to the database
    """
    new_transactions = 0
    skipped = 0
    
    # Open a connection
    with current_app.config["ENGINE"].connect() as conn:
        # Build a list of unique (account_id, transaction_id) pairs from incoming transactions
        transaction_keys = [
            (txn.get("account_id"), txn.get("transaction_id"))
            for txn in transactions
            if txn.get("account_id") and txn.get("transaction_id")
        ]

        # Execute a single query to find any existing records matching these key pairs
        # Build a list of conditions for each (PlaidAccountID, PlaidTransactionID) pair.
        conditions = [
            and_(
                expenses_table.c.PlaidAccountID == account_id,
                expenses_table.c.PlaidTransactionID == transaction_id
            )
            for account_id, transaction_id in transaction_keys
        ]

        # Only add the WHERE clause if there is at least one condition
        if conditions:
            existing_rows = conn.execute(
                expenses_table.select().where(or_(*conditions))
            ).fetchall()
        else:
            existing_rows = []

        # Create a set of keys for quick lookup
        existing_keys = {
            (row.PlaidAccountID, row.PlaidTransactionID) for row in existing_rows
        }

        # Prepare a list of new transaction records to insert
        values_to_insert = []

        for txn in transactions:
            key = (txn.get("account_id"), txn.get("transaction_id"))
            if key in existing_keys:
                skipped += 1
                continue

            # Parse dates using dateutil.parser for flexibility
            try:
                authorized_date_str = txn.get("authorized_date")
                plaid_authorized_date = parser.parse(authorized_date_str).date() if authorized_date_str else None
            except Exception:
                plaid_authorized_date = None

            try:
                date_str = txn.get("date")
                plaid_date = parser.parse(date_str).date() if date_str else None
            except Exception:
                plaid_date = None

            # AFTER: Now we ensure every transaction has date information
            if plaid_date:
                day = plaid_date.day
                month = plaid_date.strftime("%B")  # e.g., "November"
                year = plaid_date.year
                expense_date = plaid_date
                expense_day_of_week = plaid_date.strftime("%A")
            else:
                # Default to today's date if no date is provided
                today = datetime.now().date()
                day = today.day
                month = today.strftime("%B")
                year = today.year
                expense_date = today
                expense_day_of_week = today.strftime("%A")

            
            # Get the appropriate category for this transaction
            category = get_category_for_transaction(txn)
            is_income = is_income_category(category)

            # Build a dictionary of values for insertion
            record = {
                "ScopeID": scope_id,
                "PersonID": None,  # Adjust if tying to a specific user
                "Day": day,
                "Month": month,
                "Year": year,
                "ExpenseDate": expense_date,
                "ExpenseDayOfWeek": expense_day_of_week,
                "Amount": txn.get("amount"),
                "AdjustedAmount": txn.get("amount"),  # Initially the same as Amount
                "ExpenseCategory": category,  # Can be updated later (04022025 - i updated it)
                "AdditionalNotes": None,
                "CreateDate": datetime.now().date(),
                "LastUpdated": datetime.now().date(),
                "Currency": txn.get("iso_currency_code"),
                "SuggestedCategory": None,
                "CategoryConfirmed": False,
                "IsIncome": is_income,

                # Plaid-specific fields
                "PlaidAccountID": txn.get("account_id"),
                "PlaidTransactionID": txn.get("transaction_id"),
                "PlaidTransactionType": txn.get("transaction_type"),
                "PlaidCategoryID": txn.get("category_id"),
                "PlaidAuthorizedDate": plaid_authorized_date,
                "PlaidDate": plaid_date,
                "PlaidAmount": txn.get("amount"),
                "PlaidCurrencyCode": txn.get("iso_currency_code"),
                "PlaidMerchantLogoURL": txn.get("logo_url"),
                "PlaidMerchantEntityID": txn.get("merchant_entity_id"),
                "PlaidMerchantName": txn.get("merchant_name"),
                "PlaidName": txn.get("name"),
                "PlaidPending": txn.get("pending"),
                "PlaidPendingTransactionID": txn.get("pending_transaction_id"),
                "PlaidPersonalFinanceCategoryConfidence": txn.get("personal_finance_category", {}).get("confidence_level"),
                "PlaidPersonalFinanceCategoryDetailed": txn.get("personal_finance_category", {}).get("detailed"),
                "PlaidPersonalFinanceCategoryPrimary": txn.get("personal_finance_category", {}).get("primary"),
                "PlaidPersonalFinanceCategoryIconURL": txn.get("personal_finance_category_icon_url"),
            }
            values_to_insert.append(record)
            new_transactions += 1

        # Execute a bulk insert for all new records
        if values_to_insert:
            conn.execute(expenses_table.insert(), values_to_insert)
        conn.commit()
        
    return {
        "new_transactions": new_transactions,
        "skipped": skipped
    }

# API route to get available scopes for the current user

@plaid_routes.route('/api/get_available_scopes', methods=['GET'])
@login_required_api
def get_available_scopes():
    try:
        # Join scope_access with scopes to get scope details
        scope_query = (
            db.session.query(Scope, ScopeAccess)
            .join(ScopeAccess, Scope.ScopeID == ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
            .all()
        )

        scopes = [{
            'id': scope.ScopeID,
            'name': scope.ScopeName,
            'type': scope.ScopeType,
            'access_type': access.AccessType
        } for scope, access in scope_query]

        return jsonify({"success": True, "scopes": scopes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Add a route to get the user's Plaid items
@plaid_routes.route('/api/get_plaid_items', methods=['GET'])
@login_required_api
def get_plaid_items():
    try:
        # Get all scopes that the user has access to
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        # Get all Plaid items associated with these scopes
        plaid_items = PlaidItem.query.filter(
            PlaidItem.ScopeID.in_(accessible_scope_ids)
        ).all()
        
        # Build response with item information
        items_data = []
        for item in plaid_items:
            # Get the scope name
            scope = Scope.query.get(item.ScopeID)
            scope_name = scope.ScopeName if scope else "Unknown Scope"
            
            items_data.append({
                "item_id": item.PlaidItemID,
                "institution_name": item.InstitutionName or "Unknown Institution",
                "scope_id": item.ScopeID,
                "scope_name": scope_name,
                "last_synced": item.LastSynced.isoformat() if item.LastSynced else None
            })
        
        return jsonify({
            "success": True,
            "items": items_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add this to your flask_backend/routes/plaid_routes.py file

@plaid_routes.route('/api/plaid_status', methods=['GET'])
@login_required_api
def get_plaid_status():
    """Get the status of the user's Plaid connections"""
    try:
        # Get all scopes that the user has access to
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        # Count plaid items
        plaid_items_count = PlaidItem.query.filter(
            PlaidItem.ScopeID.in_(accessible_scope_ids)
        ).count()
        
        # Count transactions from Plaid
        plaid_transactions_count = db.session.query(expenses_table).filter(
            expenses_table.c.ScopeID.in_(accessible_scope_ids),
            expenses_table.c.PlaidTransactionID.isnot(None)
        ).count()
        
        return jsonify({
            "success": True,
            "has_plaid_connections": plaid_items_count > 0,
            "plaid_items_count": plaid_items_count,
            "plaid_transactions_count": plaid_transactions_count
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Retrieve ACH or ETF account numbers for an Item
# https://plaid.com/docs/#auth


@plaid_routes.route('/api/auth', methods=['GET'])
def get_auth():
    try:
       request = AuthGetRequest(
            access_token=access_token
        )
       response = client.auth_get(request)
       pretty_print_response(response.to_dict())
       return jsonify(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# Retrieve Transactions for an Item
# https://plaid.com/docs/#transactions


@plaid_routes.route('/api/transactions', methods=['GET'])
def get_transactions():
    # Set cursor to empty to receive all historical updates
    cursor = ''

    # New transaction updates since "cursor"
    added = []
    modified = []
    removed = [] # Removed transaction ids
    has_more = True
    try:
        # Iterate through each page of new transaction updates for item
        while has_more:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor,
            )
            response = client.transactions_sync(request).to_dict()
            cursor = response['next_cursor']
            # If no transactions are available yet, wait and poll the endpoint.
            # Normally, we would listen for a webhook, but the Quickstart doesn't 
            # support webhooks. For a webhook example, see 
            # https://github.com/plaid/tutorial-resources or
            # https://github.com/plaid/pattern
            if cursor == '':
                time.sleep(2)
                continue  
            # If cursor is not an empty string, we got results, 
            # so add this page of results
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            has_more = response['has_more']
            pretty_print_response(response)

        # Return the 8 most recent transactions and all transactions
        latest_transactions = sorted(added, key=lambda t: t['date'])[-8:]
        all_transactions = sorted(added, key=lambda t: t['date'])

        return jsonify({
            'latest_transactions': latest_transactions,
            'all_transactions': all_transactions
        })

    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# Retrieve Identity data for an Item
# https://plaid.com/docs/#identity


@plaid_routes.route('/api/identity', methods=['GET'])
def get_identity():
    try:
        request = IdentityGetRequest(
            access_token=access_token
        )
        response = client.identity_get(request)
        pretty_print_response(response.to_dict())
        return jsonify(
            {'error': None, 'identity': response.to_dict()['accounts']})
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# Retrieve real-time balance data for each of an Item's accounts
# https://plaid.com/docs/#balance


@plaid_routes.route('/api/balance', methods=['GET'])
def get_balance():
    try:
        request = AccountsBalanceGetRequest(
            access_token=access_token
        )
        response = client.accounts_balance_get(request)
        pretty_print_response(response.to_dict())
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# Retrieve an Item's accounts
# https://plaid.com/docs/#accounts


@plaid_routes.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        request = AccountsGetRequest(
            access_token=access_token
        )
        response = client.accounts_get(request)
        pretty_print_response(response.to_dict())
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# Create and then retrieve an Asset Report for one or more Items. Note that an
# Asset Report can contain up to 100 items, but for simplicity we're only
# including one Item here.
# https://plaid.com/docs/#assets


@plaid_routes.route('/api/assets', methods=['GET'])
def get_assets():
    try:
        request = AssetReportCreateRequest(
            access_tokens=[access_token],
            days_requested=60,
            options=AssetReportCreateRequestOptions(
                webhook='https://www.example.com',
                client_report_id='123',
                user=AssetReportUser(
                    client_user_id='789',
                    first_name='Jane',
                    middle_name='Leah',
                    last_name='Doe',
                    ssn='123-45-6789',
                    phone_number='(555) 123-4567',
                    email='jane.doe@example.com',
                )
            )
        )

        response = client.asset_report_create(request)
        pretty_print_response(response.to_dict())
        asset_report_token = response['asset_report_token']

        # Poll for the completion of the Asset Report.
        request = AssetReportGetRequest(
            asset_report_token=asset_report_token,
        )
        response = poll_with_retries(lambda: client.asset_report_get(request))
        asset_report_json = response['report']

        request = AssetReportPDFGetRequest(
            asset_report_token=asset_report_token,
        )
        pdf = client.asset_report_pdf_get(request)
        return jsonify({
            'error': None,
            'json': asset_report_json.to_dict(),
            'pdf': base64.b64encode(pdf.read()).decode('utf-8'),
        })
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# Retrieve investment holdings data for an Item
# https://plaid.com/docs/#investments


@plaid_routes.route('/api/holdings', methods=['GET'])
def get_holdings():
    try:
        request = InvestmentsHoldingsGetRequest(access_token=access_token)
        response = client.investments_holdings_get(request)
        pretty_print_response(response.to_dict())
        return jsonify({'error': None, 'holdings': response.to_dict()})
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# Retrieve Investment Transactions for an Item
# https://plaid.com/docs/#investments


@plaid_routes.route('/api/investments_transactions', methods=['GET'])
def get_investments_transactions():
    # Pull transactions for the last 30 days

    start_date = (dt.datetime.now() - dt.timedelta(days=(30)))
    end_date = dt.datetime.now()
    try:
        options = InvestmentsTransactionsGetRequestOptions()
        request = InvestmentsTransactionsGetRequest(
            access_token=access_token,
            start_date=start_date.date(),
            end_date=end_date.date(),
            options=options
        )
        response = client.investments_transactions_get(
            request)
        pretty_print_response(response.to_dict())
        return jsonify(
            {'error': None, 'investments_transactions': response.to_dict()})

    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

# This functionality is only relevant for the ACH Transfer product.
# Authorize a transfer

@plaid_routes.route('/api/transfer_authorize', methods=['GET'])
def transfer_authorization():
    global authorization_id 
    global account_id
    request = AccountsGetRequest(access_token=access_token)
    response = client.accounts_get(request)
    account_id = response['accounts'][0]['account_id']
    try:
        request = TransferAuthorizationCreateRequest(
            access_token=access_token,
            account_id=account_id,
            type=TransferType('debit'),
            network=TransferNetwork('ach'),
            amount='1.00',
            ach_class=ACHClass('ppd'),
            user=TransferAuthorizationUserInRequest(
                legal_name='FirstName LastName',
                email_address='foobar@email.com',
                address=TransferUserAddressInRequest(
                    street='123 Main St.',
                    city='San Francisco',
                    region='CA',
                    postal_code='94053',
                    country='US'
                ),
            ),
        )
        response = client.transfer_authorization_create(request)
        pretty_print_response(response.to_dict())
        authorization_id = response['authorization']['id']
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

# Create Transfer for a specified Transfer ID

@plaid_routes.route('/api/transfer_create', methods=['GET'])
def transfer():
    try:
        request = TransferCreateRequest(
            access_token=access_token,
            account_id=account_id,
            authorization_id=authorization_id,
            description='Debit')
        response = client.transfer_create(request)
        pretty_print_response(response.to_dict())
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

@plaid_routes.route('/api/statements', methods=['GET'])
def statements():
    try:
        request = StatementsListRequest(access_token=access_token)
        response = client.statements_list(request)
        pretty_print_response(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)
    try:
        request = StatementsDownloadRequest(
            access_token=access_token,
            statement_id=response['accounts'][0]['statements'][0]['statement_id']
        )
        pdf = client.statements_download(request)
        return jsonify({
            'error': None,
            'json': response.to_dict(),
            'pdf': base64.b64encode(pdf.read()).decode('utf-8'),
        })
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)




@plaid_routes.route('/api/signal_evaluate', methods=['GET'])
def signal():
    global account_id
    request = AccountsGetRequest(access_token=access_token)
    response = client.accounts_get(request)
    account_id = response['accounts'][0]['account_id']
    try:
        request = SignalEvaluateRequest(
            access_token=access_token,
            account_id=account_id,
            client_transaction_id='txn1234',
            amount=100.00)
        response = client.signal_evaluate(request)
        pretty_print_response(response.to_dict())
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# This functionality is only relevant for the UK Payment Initiation product.
# Retrieve Payment for a specified Payment ID


@plaid_routes.route('/api/payment', methods=['GET'])
def payment():
    global payment_id
    try:
        request = PaymentInitiationPaymentGetRequest(payment_id=payment_id)
        response = client.payment_initiation_payment_get(request)
        pretty_print_response(response.to_dict())
        return jsonify({'error': None, 'payment': response.to_dict()})
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


# Retrieve high-level information about an Item
# https://plaid.com/docs/#retrieve-item


@plaid_routes.route('/api/item', methods=['GET'])
def item():
    try:
        request = ItemGetRequest(access_token=access_token)
        response = client.item_get(request)
        request = InstitutionsGetByIdRequest(
            institution_id=response['item']['institution_id'],
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES))
        )
        institution_response = client.institutions_get_by_id(request)
        pretty_print_response(response.to_dict())
        pretty_print_response(institution_response.to_dict())
        return jsonify({'error': None, 'item': response.to_dict()[
            'item'], 'institution': institution_response.to_dict()['institution']})
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

# Retrieve CRA Base Report and PDF
# Base report: https://plaid.com/docs/check/api/#cracheck_reportbase_reportget
# PDF: https://plaid.com/docs/check/api/#cracheck_reportpdfget
@plaid_routes.route('/api/cra/get_base_report', methods=['GET'])
def cra_check_report():
    try:
        get_response = poll_with_retries(lambda: client.cra_check_report_base_report_get(
            CraCheckReportBaseReportGetRequest(user_token=user_token, item_ids=[])
        ))
        pretty_print_response(get_response.to_dict())

        pdf_response = client.cra_check_report_pdf_get(
            CraCheckReportPDFGetRequest(user_token=user_token)
        )
        return jsonify({
            'report': get_response.to_dict()['report'],
            'pdf': base64.b64encode(pdf_response.read()).decode('utf-8')
        })
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

# Retrieve CRA Income Insights and PDF with Insights
# Income insights: https://plaid.com/docs/check/api/#cracheck_reportincome_insightsget
# PDF w/ income insights: https://plaid.com/docs/check/api/#cracheck_reportpdfget
@plaid_routes.route('/api/cra/get_income_insights', methods=['GET'])
def cra_income_insights():
    try:
        get_response = poll_with_retries(lambda: client.cra_check_report_income_insights_get(
            CraCheckReportIncomeInsightsGetRequest(user_token=user_token))
        )
        pretty_print_response(get_response.to_dict())

        pdf_response = client.cra_check_report_pdf_get(
            CraCheckReportPDFGetRequest(user_token=user_token, add_ons=[CraPDFAddOns('cra_income_insights')]),
        )

        return jsonify({
            'report': get_response.to_dict()['report'],
            'pdf': base64.b64encode(pdf_response.read()).decode('utf-8')
        })
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

# Retrieve CRA Partner Insights
# https://plaid.com/docs/check/api/#cracheck_reportpartner_insightsget
@plaid_routes.route('/api/cra/get_partner_insights', methods=['GET'])
def cra_partner_insights():
    try:
        response = poll_with_retries(lambda: client.cra_check_report_partner_insights_get(
            CraCheckReportPartnerInsightsGetRequest(user_token=user_token)
        ))
        pretty_print_response(response.to_dict())

        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

# Since this quickstart does not support webhooks, this function can be used to poll
# an API that would otherwise be triggered by a webhook.
# For a webhook example, see
# https://github.com/plaid/tutorial-resources or
# https://github.com/plaid/pattern
def poll_with_retries(request_callback, ms=1000, retries_left=20):
    while retries_left > 0:
        try:
            return request_callback()
        except plaid.ApiException as e:
            response = json.loads(e.body)
            if response['error_code'] != 'PRODUCT_NOT_READY':
                raise e
            elif retries_left == 0:
                raise Exception('Ran out of retries while polling') from e
            else:
                retries_left -= 1
                time.sleep(ms / 1000)

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True, default=str))

def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}

# Add these new endpoints to flask_backend/routes/plaid_routes.py

# Replace the existing get_item_accounts function in flask_backend/routes/plaid_routes.py with this improved version
# Replace the existing get_item_accounts function in flask_backend/routes/plaid_routes.py with this improved version

@plaid_routes.route('/api/get_item_accounts', methods=['GET'])
@login_required_api
def get_item_accounts():
    try:
        item_id = request.args.get('item_id')
        if not item_id:
            return jsonify({"success": False, "error": "item_id parameter is required"}), 400
        
        # Verify the plaid item exists and belongs to a scope the user has access to
        plaid_item = PlaidItem.query.filter_by(PlaidItemID=item_id).first()
        if not plaid_item:
            return jsonify({"success": False, "error": "Plaid item not found"}), 404
        
        # Verify user has access to the scope
        scope_access = ScopeAccess.query.filter_by(
            ScopeID=plaid_item.ScopeID,
            AccountID=current_user.id,
            InviteStatus='accepted'
        ).first()
        
        if not scope_access:
            return jsonify({"success": False, "error": "You don't have access to this item"}), 403
        
        try:
            # Use the stored access token for this specific item
            request_obj = AccountsBalanceGetRequest(
                access_token=plaid_item.AccessToken
            )
            response = client.accounts_balance_get(request_obj)
            
            # Update the last synced timestamp
            plaid_item.LastSynced = datetime.now()
            db.session.commit()
            
            # Convert the response to a dict first to handle serialization
            response_dict = response.to_dict()
            
            # Extract accounts data and manually build serializable objects
            accounts = []
            for account in response_dict.get('accounts', []):
                # Create a clean, serializable account object
                account_data = {
                    'account_id': account.get('account_id'),
                    'name': account.get('name', 'Unknown Account'),
                    'official_name': account.get('official_name'),
                    'balances': {
                        'available': account.get('balances', {}).get('available'),
                        'current': account.get('balances', {}).get('current'),
                        'iso_currency_code': account.get('balances', {}).get('iso_currency_code'),
                    },
                    'type': str(account.get('type')) if account.get('type') else None,
                    'subtype': str(account.get('subtype')) if account.get('subtype') else None,
                    'mask': account.get('mask')
                }
                accounts.append(account_data)
            
            return jsonify({
                "success": True,
                "accounts": accounts
            })
        except plaid.ApiException as e:
            error_response = format_error(e)
            print(f"Plaid API error for item {item_id}:", error_response)
            return jsonify({
                "success": False, 
                "error": error_response['error'].get('display_message', "Error fetching accounts")
            }), 400
        
    except Exception as e:
        print(f"Error in get_item_accounts: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
        

# Endpoint to delete a plaid item
@plaid_routes.route('/api/delete_plaid_item', methods=['POST'])
@login_required_api
def delete_plaid_item():
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        delete_transactions = data.get('delete_transactions', False)
        
        if not item_id:
            return jsonify({"success": False, "error": "item_id is required"}), 400
        
        # Find the plaid item
        plaid_item = PlaidItem.query.filter_by(PlaidItemID=item_id).first()
        if not plaid_item:
            return jsonify({"success": False, "error": "Plaid item not found"}), 404
        
        # Verify user has access to the scope
        scope_access = ScopeAccess.query.filter_by(
            ScopeID=plaid_item.ScopeID,
            AccountID=current_user.id,
            InviteStatus='accepted'
        ).first()
        
        if not scope_access:
            return jsonify({"success": False, "error": "You don't have access to this item"}), 403

        # Store info for response
        institution_name = plaid_item.InstitutionName
        scope_id = plaid_item.ScopeID
        
        # Begin transaction
        try:
            # If requested, delete all transactions associated with this item
            deleted_count = 0
            if delete_transactions:
                with current_app.config["ENGINE"].connect() as conn:
                    # Get accounts associated with this item
                    try:
                        # Use the stored access token to get account IDs
                        accounts_request = AccountsGetRequest(
                            access_token=plaid_item.AccessToken
                        )
                        accounts_response = client.accounts_get(accounts_request)
                        account_ids = [account['account_id'] for account in accounts_response['accounts']]
                        
                        # Delete expenses with matching PlaidAccountID
                        if account_ids:
                            delete_stmt = expenses_table.delete().where(
                                expenses_table.c.PlaidAccountID.in_(account_ids)
                            )
                            result = conn.execute(delete_stmt)
                            deleted_count = result.rowcount
                            conn.commit()
                    except plaid.ApiException:
                        # If we can't get accounts from Plaid, try deleting by scope
                        delete_stmt = expenses_table.delete().where(
                            and_(
                                expenses_table.c.ScopeID == scope_id,
                                expenses_table.c.PlaidTransactionID.isnot(None)
                            )
                        )
                        result = conn.execute(delete_stmt)
                        deleted_count = result.rowcount
                        conn.commit()
            
            # Delete the plaid item from database
            db.session.delete(plaid_item)
            db.session.commit()
            
            # Optionally, you could also call Plaid's API to remove the item
            # from Plaid's servers, but this isn't usually necessary
            
            return jsonify({
                "success": True,
                "message": f"Successfully removed connection to {institution_name}",
                "deleted_transactions": deleted_count if delete_transactions else 0
            })
            
        except Exception as db_err:
            db.session.rollback()
            raise db_err
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500