#!/usr/bin/env python3
"""
Migration script to populate MerchantName and SourceType fields for existing expenses.
This script should be run once after the schema changes are deployed.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import text

# Load environment variables
load_dotenv()

def migrate_expense_data():
    """Migrate existing expense data to use new standardized fields."""
    
    # Get database connection details from environment
    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    
    if not all([db_server, db_name, db_username, db_password]):
        print("Error: Missing database connection details in .env file")
        return
    
    # Create connection string
    connection_string = f"mssql+pyodbc://{db_username}:{db_password}@{db_server}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    
    print(f"Connecting to database: {db_server}/{db_name}")
    
    try:
        engine = sa.create_engine(connection_string)
        
        with engine.connect() as conn:
            print("Starting data migration...")
            
            # First, let's see what we're working with
            result = conn.execute(text("SELECT COUNT(*) FROM expenses"))
            total_expenses = result.scalar()
            print(f"Total expenses to migrate: {total_expenses}")
            
            # Update SourceType for all expenses
            print("Setting SourceType...")
            
            # Set SourceType to 'plaid' for expenses with PlaidTransactionID
            plaid_update = conn.execute(text("""
                UPDATE expenses 
                SET SourceType = 'plaid' 
                WHERE PlaidTransactionID IS NOT NULL
            """))
            print(f"Set SourceType='plaid' for {plaid_update.rowcount} expenses")
            
            # Set SourceType to 'manual' for expenses without PlaidTransactionID
            manual_update = conn.execute(text("""
                UPDATE expenses 
                SET SourceType = 'manual' 
                WHERE PlaidTransactionID IS NULL
            """))
            print(f"Set SourceType='manual' for {manual_update.rowcount} expenses")
            
            # Update MerchantName for Plaid transactions
            print("Migrating MerchantName for Plaid transactions...")
            plaid_merchant_update = conn.execute(text("""
                UPDATE expenses 
                SET MerchantName = PlaidMerchantName 
                WHERE PlaidTransactionID IS NOT NULL 
                AND PlaidMerchantName IS NOT NULL
            """))
            print(f"Migrated MerchantName from PlaidMerchantName for {plaid_merchant_update.rowcount} Plaid expenses")
            
            # For Plaid transactions without PlaidMerchantName, use PlaidName
            plaid_name_update = conn.execute(text("""
                UPDATE expenses 
                SET MerchantName = PlaidName 
                WHERE PlaidTransactionID IS NOT NULL 
                AND MerchantName IS NULL 
                AND PlaidName IS NOT NULL
            """))
            print(f"Migrated MerchantName from PlaidName for {plaid_name_update.rowcount} Plaid expenses")
            
            # Update MerchantName for manual transactions
            print("Migrating MerchantName for manual transactions...")
            
            # Get manual transactions that have merchant info in AdditionalNotes
            manual_expenses = conn.execute(text("""
                SELECT ExpenseID, AdditionalNotes 
                FROM expenses 
                WHERE PlaidTransactionID IS NULL 
                AND AdditionalNotes IS NOT NULL 
                AND AdditionalNotes LIKE 'Merchant: %'
            """)).fetchall()
            
            manual_merchant_count = 0
            for expense in manual_expenses:
                expense_id, notes = expense
                if notes and notes.startswith('Merchant: '):
                    lines = notes.split('\n')
                    merchant_line = lines[0]
                    merchant_name = merchant_line.replace('Merchant: ', '')
                    
                    # Extract remaining notes (everything after first line)
                    remaining_notes = '\n'.join(lines[1:]) if len(lines) > 1 else None
                    remaining_notes = remaining_notes if remaining_notes and remaining_notes.strip() else None
                    
                    # Update the expense
                    conn.execute(text("""
                        UPDATE expenses 
                        SET MerchantName = :merchant_name, AdditionalNotes = :remaining_notes 
                        WHERE ExpenseID = :expense_id
                    """), {
                        'merchant_name': merchant_name,
                        'remaining_notes': remaining_notes,
                        'expense_id': expense_id
                    })
                    manual_merchant_count += 1
            
            print(f"Migrated MerchantName from AdditionalNotes for {manual_merchant_count} manual expenses")
            
            # Legacy: Handle old manual entries that might have used PlaidMerchantName incorrectly
            legacy_update = conn.execute(text("""
                UPDATE expenses 
                SET MerchantName = PlaidMerchantName 
                WHERE PlaidTransactionID IS NULL 
                AND MerchantName IS NULL 
                AND PlaidMerchantName IS NOT NULL
            """))
            print(f"Migrated MerchantName from legacy PlaidMerchantName for {legacy_update.rowcount} manual expenses")
            
            # Commit all changes
            conn.commit()
            print("Migration completed successfully!")
            
            # Verification
            print("\nVerification:")
            result = conn.execute(text("SELECT COUNT(*) FROM expenses WHERE SourceType = 'plaid'"))
            plaid_count = result.scalar()
            result = conn.execute(text("SELECT COUNT(*) FROM expenses WHERE SourceType = 'manual'"))
            manual_count = result.scalar()
            result = conn.execute(text("SELECT COUNT(*) FROM expenses WHERE MerchantName IS NOT NULL"))
            with_merchant = result.scalar()
            
            print(f"Plaid expenses: {plaid_count}")
            print(f"Manual expenses: {manual_count}")
            print(f"Expenses with MerchantName: {with_merchant}")
            print(f"Total: {plaid_count + manual_count} (should equal {total_expenses})")
    
    except Exception as e:
        print(f"Error during migration: {e}")
        return

if __name__ == "__main__":
    migrate_expense_data()