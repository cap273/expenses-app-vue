#!/usr/bin/env python3
"""
Script to add the new MerchantName, SourceType, and IsIncome columns to existing database.
"""

import os
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import text

# Load environment variables
load_dotenv()

def add_columns():
    """Add new columns to the expenses table."""
    
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
            print("Checking existing columns...")
            
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'expenses' 
                AND COLUMN_NAME IN ('MerchantName', 'SourceType', 'IsIncome')
            """))
            existing_columns = [row[0] for row in result]
            print(f"Existing new columns: {existing_columns}")
            
            # Add MerchantName if it doesn't exist
            if 'MerchantName' not in existing_columns:
                print("Adding MerchantName column...")
                conn.execute(text("ALTER TABLE expenses ADD MerchantName NVARCHAR(255)"))
                print("✓ MerchantName column added")
            else:
                print("✓ MerchantName column already exists")
            
            # Add SourceType if it doesn't exist
            if 'SourceType' not in existing_columns:
                print("Adding SourceType column...")
                conn.execute(text("ALTER TABLE expenses ADD SourceType NVARCHAR(10)"))
                print("✓ SourceType column added")
                
                # Add check constraint
                print("Adding SourceType check constraint...")
                conn.execute(text("""
                    ALTER TABLE expenses 
                    ADD CONSTRAINT CHK_SourceType 
                    CHECK (SourceType IN ('manual', 'plaid'))
                """))
                print("✓ SourceType constraint added")
            else:
                print("✓ SourceType column already exists")
            
            # Add IsIncome if it doesn't exist
            if 'IsIncome' not in existing_columns:
                print("Adding IsIncome column...")
                conn.execute(text("ALTER TABLE expenses ADD IsIncome BIT DEFAULT 0"))
                print("✓ IsIncome column added")
            else:
                print("✓ IsIncome column already exists")
            
            conn.commit()
            print("\nSchema update completed successfully!")
            
            # Show final schema
            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'expenses' 
                ORDER BY ORDINAL_POSITION
            """))
            
            print("\nCurrent expenses table schema:")
            for row in result:
                print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
    
    except Exception as e:
        print(f"Error during schema update: {e}")
        return

if __name__ == "__main__":
    add_columns()