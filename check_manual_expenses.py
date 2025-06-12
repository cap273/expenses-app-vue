#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import text

load_dotenv()

def check_manual_expenses():
    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    
    connection_string = f"mssql+pyodbc://{db_username}:{db_password}@{db_server}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    
    engine = sa.create_engine(connection_string)
    
    with engine.connect() as conn:
        print("Manual expenses without MerchantName:")
        result = conn.execute(text("""
            SELECT ExpenseID, AdditionalNotes, MerchantName, Merchant
            FROM expenses 
            WHERE SourceType = 'manual' 
            ORDER BY ExpenseID
        """))
        
        for row in result:
            print(f"ID: {row[0]}, Notes: '{row[1]}', MerchantName: '{row[2]}', Merchant: '{row[3]}'")

if __name__ == "__main__":
    check_manual_expenses()