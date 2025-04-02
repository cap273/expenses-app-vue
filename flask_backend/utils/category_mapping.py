"""
Maps Plaid Personal Finance Categories to app expense categories.
"""

# Map Plaid's Personal Finance Categories (primary) to our app categories
PLAID_TO_APP_CATEGORY_MAP = {
    # Food & Drink
    "FOOD_AND_DRINK": "Groceries",  # Default mapping
    "FOOD_AND_DRINK_RESTAURANTS": "Restaurant and Takeout (Non-Social)",
    "FOOD_AND_DRINK_COFFEE": "Restaurant and Takeout (Non-Social)",
    "FOOD_AND_DRINK_FAST_FOOD": "Restaurant and Takeout (Non-Social)",
    "FOOD_AND_DRINK_GROCERY": "Groceries",
    "FOOD_AND_DRINK_ALCOHOL": "Alcohol",
    
    # Transportation
    "TRANSPORTATION": "Other Transportation Expenses",
    "TRANSPORTATION_PUBLIC_TRANSIT": "Other Transportation Expenses",
    "TRANSPORTATION_TAXI": "Taxi and Ride-Sharing",
    "TRANSPORTATION_PARKING": "Car-Related Expenses (excluding gasoline)",
    "TRANSPORTATION_GAS": "Gasoline",
    "TRANSPORTATION_CAR_SERVICE": "Car-Related Expenses (excluding gasoline)",
    
    # Travel
    "TRAVEL": "Other Transportation Expenses",
    "TRAVEL_FLIGHTS": "Airplane Flights",
    "TRAVEL_LODGING": "Hotel and Lodging",
    "TRAVEL_RENTAL_CAR": "Car-Related Expenses (excluding gasoline)",
    
    # Shopping
    "SHOPPING": "Miscellaneous",
    "SHOPPING_CLOTHING": "Shoes and Clothing",
    "SHOPPING_ELECTRONICS": "Software and Electronics",
    "SHOPPING_SPORTING_GOODS": "Sports and Fitness",
    "SHOPPING_HOME_IMPROVEMENT": "Household Goods",
    
    # Home
    "HOME": "Household Goods",
    "HOME_RENT": "Rent",
    "HOME_MORTGAGE": "Mortgage Principal and Interest",
    "HOME_IMPROVEMENT": "Capital Improvements",
    "HOME_MAINTENANCE": "Home Services",
    "HOME_FURNITURE": "Household Goods",
    "HOME_INSURANCE": "Homeowners Insurance",
    "HOME_PROPERTY_TAXES": "Property Taxes",
    
    # Entertainment
    "ENTERTAINMENT": "Entertainment",
    
    # Personal Care
    "PERSONAL_CARE": "Haircuts and Cosmetics",
    
    # Health & Fitness
    "MEDICAL": "Healthcare and Medical",
    "HEALTH_FITNESS": "Sports and Fitness",
    
    # Professional Services
    "PROFESSIONAL_SERVICES": "Miscellaneous",
    "PROFESSIONAL_SERVICES_EDUCATION": "Education (including student loans)",
    
    # Utilities
    "UTILITIES": "Utilities",
    "UTILITIES_INTERNET": "Internet, Cell Phone, and TV",
    "UTILITIES_PHONE": "Internet, Cell Phone, and TV",
    "UTILITIES_TELEVISION": "Internet, Cell Phone, and TV",
    
    # Insurance
    "INSURANCE": "Car and Renters Insurance",
    
    # Financial
    "FEES_AND_CHARGES": "Interest and Banking Fees",
    "LOAN": "Education (including student loans)",
    
    # Income (will likely be ignored as expense categories)
    "INCOME": "Miscellaneous",
    "INCOME_DIVIDENDS": "Miscellaneous",
    
    # Catch-all
    "GENERAL_SERVICES": "Miscellaneous",
    "GENERAL_MERCHANDISE": "Miscellaneous",
    "UNCATEGORIZED": "Miscellaneous",
}

def get_app_category_from_plaid(plaid_category, merchant_name=None):
    """
    Maps a Plaid category to an application category.
    
    Args:
        plaid_category (str): The Plaid personal finance category primary or detailed value
        merchant_name (str, optional): The merchant name for additional context
        
    Returns:
        str: The mapped application category or None if no mapping exists
    """
    # Try to map using detailed category first (if provided)
    if plaid_category in PLAID_TO_APP_CATEGORY_MAP:
        return PLAID_TO_APP_CATEGORY_MAP[plaid_category]
    
    # If we can't find a mapping, try to extract the primary category
    if "_" in plaid_category:
        primary_category = plaid_category.split("_", 1)[0]
        if primary_category in PLAID_TO_APP_CATEGORY_MAP:
            return PLAID_TO_APP_CATEGORY_MAP[primary_category]
    
    # If no mapping is found, return a default category
    return "Miscellaneous"


# Certain merchants we can categorize directly regardless of Plaid category
MERCHANT_TO_CATEGORY_MAP = {
    "UBER": "Taxi and Ride-Sharing",
    "LYFT": "Taxi and Ride-Sharing",
    "NETFLIX": "Entertainment",
    "SPOTIFY": "Entertainment",
    "AMAZON PRIME": "Other Memberships and Fees",
    "AIRBNB": "Hotel and Lodging",
}

def get_category_for_transaction(transaction):
    """
    Determine the best category for a transaction based on Plaid data
    
    Args:
        transaction (dict): A dictionary containing Plaid transaction data
        
    Returns:
        str: The most appropriate category for the transaction
    """
    # Check if we have merchant-specific mapping
    merchant_name = transaction.get("merchant_name") or transaction.get("name", "")
    if merchant_name:
        merchant_upper = merchant_name.upper()
        for key, category in MERCHANT_TO_CATEGORY_MAP.items():
            if key in merchant_upper:
                return category
    
    # Try to use Plaid's personal finance categories (most reliable)
    plaid_pfc = transaction.get("personal_finance_category", {})
    if plaid_pfc:
        # Try detailed category first, then primary
        detailed = plaid_pfc.get("detailed")
        primary = plaid_pfc.get("primary")
        
        if detailed:
            app_category = get_app_category_from_plaid(detailed, merchant_name)
            if app_category:
                return app_category
                
        if primary:
            app_category = get_app_category_from_plaid(primary, merchant_name)
            if app_category:
                return app_category
    
    # Fallback to a default category
    return "Miscellaneous"