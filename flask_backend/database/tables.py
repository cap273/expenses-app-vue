# tables.py
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Date,
    Float,
    Boolean,
    ForeignKey,   
    Text, 
    DateTime, 
)

metadata = MetaData()

# Define list of (default) categories
CATEGORY_LIST = [
    "Groceries",
    "Restaurants",
    "Restaurant and Takeout (Social)",
    "Shoes and Clothing",
    "Alcohol",
    "Loan",
    "Entertainment",
    "Utilities",
    "Sports and Fitness",
    "Haircuts and Cosmetics",
    "Airplane Flights",
    "Hotel and Lodging",
    "Car-Related Expenses (excluding gasoline)",
    "Car Rental",
    "Parking",
    "Taxi and Ride-Sharing",
    "Gasoline",
    "Household Goods",
    "Other Transportation Expenses",
    "Healthcare and Medical",
    "Gifts and Donations",
    "Software and Electronics",
    "Education (including student loans)",
    "Internet, Cell Phone, and TV",
    "Miscellaneous",
    "Rent",
    "Interest and Banking Fees",
    "Car and Renters Insurance",
    "Other Memberships and Fees",
    "Mortgage Insurance",
    "Homeowners Insurance",
    "Property Taxes",
    "Mortgage Principal and Interest",
    "Home Services",
    "Capital Improvements",
    "Landlord Expenses",
]

# Modify expenses_table definition
expenses_table = Table(
    "expenses",
    metadata,
    Column("ExpenseID", Integer, primary_key=True),
    Column("ScopeID", Integer, ForeignKey("scopes.ScopeID"), nullable=False),  # Required per SQL
    Column("PersonID", Integer, ForeignKey("persons.PersonID")),
    Column("Day", Integer),
    Column("Month", String(50)),
    Column("Year", Integer),
    Column("ExpenseDate", Date),
    Column("ExpenseDayOfWeek", String(50)),
    Column("Amount", Float, nullable=False),  # Required per SQL
    Column("AdjustedAmount", Float),
    Column("ExpenseCategory", String(255)),
    Column("AdditionalNotes", String(255)),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    Column("Currency", String(50)),
    Column("SuggestedCategory", String(255)),
    Column("CategoryConfirmed", Boolean),
    # Plaid-specific fields:
    Column("PlaidAccountID", String(255)),
    Column("PlaidTransactionID", String(255)),
    Column("PlaidTransactionType", String(255)),
    Column("PlaidCategoryID", String(255)),
    Column("PlaidAuthorizedDate", Date),
    Column("PlaidDate", Date),
    Column("PlaidAmount", Float),
    Column("PlaidCurrencyCode", String(10)),
    Column("PlaidMerchantLogoURL", String(255)),
    Column("PlaidMerchantEntityID", String(255)),
    Column("PlaidMerchantName", String(255)),
    Column("PlaidName", String(255)),
    Column("PlaidPending", Boolean),
    Column("PlaidPendingTransactionID", String(255)),
    Column("PlaidPersonalFinanceCategoryConfidence", String(255)),
    Column("PlaidPersonalFinanceCategoryDetailed", String(255)),
    Column("PlaidPersonalFinanceCategoryPrimary", String(255)),
    Column("PlaidPersonalFinanceCategoryIconURL", String(255)),
    Column("IsIncome", Boolean, default=False),
    extend_existing=False,
    implicit_returning=False,
)

# Define the categories table
categories_table = Table(
    "categories",
    metadata,
    Column("CategoryID", Integer, primary_key=True),
    Column("CategoryName", String(255), unique=True, nullable=False),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    extend_existing=False,
)

# Define the persons table
persons_table = Table(
    "persons",
    metadata,
    Column("PersonID", Integer, primary_key=True),
    Column("AccountID", Integer, ForeignKey("accounts.AccountID"), nullable=False),
    Column("PersonName", String(255), nullable=False),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    extend_existing=False,
    # Set implicit_returning to False so that
    # SQLAlchemy won't try to use the OUTPUT clause to fetch the inserted ID.
    # This should avoid conflicts with database triggers for ID generation
    implicit_returning=False,
)

scopes_table = Table(
    "scopes",
    metadata,
    Column("ScopeID", Integer, primary_key=True),
    Column("ScopeName", String(255), nullable=False),
    Column("ScopeType", String(50), nullable=False),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    extend_existing=False,
    implicit_returning=False,
)

scope_access_table = Table(
    "scope_access",
    metadata,
    Column("AccessID", Integer, primary_key=True),
    Column("ScopeID", Integer, ForeignKey("scopes.ScopeID"), nullable=False),
    Column("AccountID", Integer, ForeignKey("accounts.AccountID"), nullable=False),
    Column("AccessType", String(50), nullable=False),
    Column("InviteStatus", String(50), nullable=False),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    extend_existing=False,
    implicit_returning=False,
)

plaid_items_table = Table(
    "plaid_items",
    metadata,
    Column("ItemID", Integer, primary_key=True),
    Column("ScopeID", Integer, ForeignKey("scopes.ScopeID"), nullable=False),
    Column("PlaidItemID", String(255), nullable=False, unique=True),
    Column("AccessToken", String(255), nullable=False),
    Column("SyncToken", Text, nullable=True),
    Column("InstitutionName", String(255), nullable=True),
    Column("InstitutionID", String(255), nullable=True),
    Column("LastSynced", DateTime, nullable=True),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    extend_existing=False,
    implicit_returning=False,
)