#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import text

load_dotenv()

def fix_manual_merchants():
    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    
    connection_string = f"mssql+pyodbc://{db_username}:{db_password}@{db_server}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    
    engine = sa.create_engine(connection_string)
    
    with engine.connect() as conn:
        print("Fixing manual expense merchants...")
        
        # Fix cases where MerchantName is 'None' (string) but AdditionalNotes has merchant info
        result = conn.execute(text("""
            SELECT ExpenseID, AdditionalNotes
            FROM expenses 
            WHERE SourceType = 'manual' 
            AND (MerchantName IS NULL OR MerchantName = 'None')
            AND AdditionalNotes IS NOT NULL 
            AND AdditionalNotes != ''
        """))
        
        # Fetch all rows first to avoid connection busy error
        rows_to_update = result.fetchall()
        
        updated_count = 0
        for row in rows_to_update:
            expense_id, notes = row
            # Use the notes as merchant name if no proper merchant exists
            if notes and notes.strip():
                conn.execute(text("""
                    UPDATE expenses 
                    SET MerchantName = :merchant_name, AdditionalNotes = NULL
                    WHERE ExpenseID = :expense_id
                """), {
                    'merchant_name': notes.strip(),
                    'expense_id': expense_id
                })
                updated_count += 1
                print(f"Updated expense {expense_id}: '{notes}' -> MerchantName")
        
        # Clean up MerchantName values that are 'None' string to actual NULL
        result = conn.execute(text("""
            UPDATE expenses 
            SET MerchantName = NULL 
            WHERE MerchantName = 'None'
        """))
        print(f"Cleaned up {result.rowcount} 'None' string values")
        
        conn.commit()
        print(f"Fixed {updated_count} manual expenses")
        
        # Final verification
        print("\nFinal manual expenses status:")
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(MerchantName) as with_merchant
            FROM expenses 
            WHERE SourceType = 'manual'
        """))
        row = result.fetchone()
        print(f"Total manual expenses: {row[0]}")
        print(f"With MerchantName: {row[1]}")

if __name__ == "__main__":
    fix_manual_merchants()