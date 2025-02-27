# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()  # Initialize Flask-SQLAlchemy


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = {"implicit_returning": False}

    CategoryID = db.Column(db.Integer, primary_key=True)
    CategoryName = db.Column(db.String(255), unique=True, nullable=False)
    CreateDate = db.Column(db.Date)
    LastUpdated = db.Column(db.Date)


# Modify Expense model
class Expense(db.Model):
    __tablename__ = "expenses"

    ExpenseID = db.Column(db.Integer, primary_key=True)
    ScopeID = db.Column(db.Integer, db.ForeignKey("scopes.ScopeID"), nullable=False)  # Changed from AccountID
    PersonID = db.Column(db.Integer, db.ForeignKey("persons.PersonID"), nullable=True)
    Day = db.Column(db.Integer, nullable=False)
    Month = db.Column(db.String(50), nullable=False)
    Year = db.Column(db.Integer, nullable=False)
    ExpenseDate = db.Column(db.Date, nullable=False)
    ExpenseDayOfWeek = db.Column(db.String(50))
    Amount = db.Column(db.Float, nullable=False)
    AdjustedAmount = db.Column(db.Float)
    ExpenseCategory = db.Column(db.String(255), nullable=False)
    AdditionalNotes = db.Column(db.String(255))
    CreateDate = db.Column(db.Date)
    LastUpdated = db.Column(db.Date)
    Currency = db.Column(db.String(50))
    SuggestedCategory = db.Column(db.String(255))
    CategoryConfirmed = db.Column(db.Boolean)


class Account(UserMixin, db.Model):
    __tablename__ = "accounts"
    __table_args__ = {
        "implicit_returning": False
    }  # Avoid conflicts with database triggers for ID generation

    id = db.Column("AccountID", db.Integer, primary_key=True)
    account_name = db.Column("AccountName", db.String(255), unique=True, nullable=False)
    password = db.Column("Password", db.String(255))
    user_email = db.Column("UserEmail", db.String(255), unique=True)
    display_name = db.Column("AccountDisplayName", db.String(255))
    currency = db.Column("Currency", db.String(255))
    create_date = db.Column("CreateDate", db.Date)
    last_updated = db.Column("LastUpdated", db.Date)
    last_login_date = db.Column("LastLoginDate", db.Date)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Person(db.Model):
    __tablename__ = "persons"
    __table_args__ = {"implicit_returning": False}

    PersonID = db.Column(db.Integer, primary_key=True)
    AccountID = db.Column(
        db.Integer, db.ForeignKey("accounts.AccountID"), nullable=False
    )
    PersonName = db.Column(db.String(255), nullable=False)
    CreateDate = db.Column(db.Date)
    LastUpdated = db.Column(db.Date)

    def to_json(self):
        """
        This method returns the PersonID and PersonName as a dictionary,
        which can be easily converted to a JSON object.
        """
        return {"PersonID": self.PersonID, "PersonName": self.PersonName}

class Scope(db.Model):
    __tablename__ = "scopes"
    __table_args__ = {"implicit_returning": False}

    ScopeID = db.Column(db.Integer, primary_key=True)
    ScopeName = db.Column(db.String(255), nullable=False)
    ScopeType = db.Column(db.String(50), nullable=False)  # 'personal' or 'household'
    CreateDate = db.Column(db.Date)
    LastUpdated = db.Column(db.Date)

class ScopeAccess(db.Model):
    __tablename__ = "scope_access"
    __table_args__ = {"implicit_returning": False}

    AccessID = db.Column(db.Integer, primary_key=True)
    ScopeID = db.Column(db.Integer, db.ForeignKey("scopes.ScopeID"), nullable=False)
    AccountID = db.Column(db.Integer, db.ForeignKey("accounts.AccountID"), nullable=False)
    AccessType = db.Column(db.String(50), nullable=False)  # 'owner' or 'member'
    InviteStatus = db.Column(db.String(50), nullable=False)  # 'pending', 'accepted', 'rejected'
    CreateDate = db.Column(db.Date)
    LastUpdated = db.Column(db.Date)

class PlaidItem(db.Model):
    __tablename__ = "plaid_items"
    __table_args__ = {"implicit_returning": False}

    ItemID = db.Column(db.Integer, primary_key=True)
    ScopeID = db.Column(db.Integer, db.ForeignKey("scopes.ScopeID"), nullable=False)
    PlaidItemID = db.Column(db.String(255), nullable=False, unique=True)
    AccessToken = db.Column(db.String(255), nullable=False)
    SyncToken = db.Column(db.Text, nullable=True)  # Can be null initially
    InstitutionName = db.Column(db.String(255), nullable=True)
    InstitutionID = db.Column(db.String(255), nullable=True)
    LastSynced = db.Column(db.DateTime, nullable=True)
    CreateDate = db.Column(db.Date)
    LastUpdated = db.Column(db.Date)