#!/usr/bin/env python3
"""
Migration script to create the category_targets table
"""

from flask_backend.create_app import create_app
from flask_backend.database.tables import category_targets_table, metadata
from sqlalchemy import text

def create_category_targets_table():
    """Create the category_targets table"""
    app = create_app()
    
    with app.app_context():
        try:
            with app.config["ENGINE"].connect() as connection:
                # Check if table already exists
                check_query = text("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'category_targets'
                """)
                result = connection.execute(check_query)
                table_exists = result.scalar() > 0
                
                if table_exists:
                    print("Table 'category_targets' already exists, skipping creation.")
                    return
                
                # Create the table
                category_targets_table.create(app.config["ENGINE"])
                connection.commit()
                print("Successfully created 'category_targets' table.")
                
        except Exception as e:
            print(f"Error creating table: {e}")
            raise

if __name__ == "__main__":
    create_category_targets_table()