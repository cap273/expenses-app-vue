from sqlalchemy import select, inspect
import pyodbc


def get_database_url(db_username, db_password, db_server, db_name):
    import platform
    drivers = [driver for driver in pyodbc.drivers()]
    driver = None

    # Check the operating system
    if platform.system() == 'Darwin':  # macOS
        driver_path = "/opt/homebrew/opt/msodbcsql17/lib/libmsodbcsql.17.dylib"
        driver = driver_path
    else:  # Windows or other systems
        if "ODBC Driver 18 for SQL Server" in drivers:
            driver = "ODBC+Driver+18+for+SQL+Server"
        elif "ODBC Driver 17 for SQL Server" in drivers:
            driver = "ODBC+Driver+17+for+SQL+Server"
        else:
            raise Exception("Suitable ODBC driver not found")

    # Database URL
    return f"mssql+pyodbc://{db_username}:{db_password}@{db_server}/{db_name}?driver={driver}"


def populate_categories_table(engine, categories_table, category_list):
    # Use inspection API to check for table existence
    inspector = inspect(engine)
    if inspector.has_table("categories"):
        with engine.connect() as connection:
            # Get existing categories in one query
            existing_categories_query = select(categories_table.c.CategoryName)
            existing_categories = connection.execute(
                existing_categories_query
            ).fetchall()
            existing_categories = {row.CategoryName for row in existing_categories}

            # Find which categories need to be added
            new_categories = [
                category
                for category in category_list
                if category not in existing_categories
            ]

            # Insert new categories in one query, if there are any
            if new_categories:
                insert_query = categories_table.insert().values(
                    [{"CategoryName": category} for category in new_categories]
                )
                connection.execute(insert_query)
                connection.commit()  # Commit the transaction after insertions


def get_categories(engine, categories_table):
    query = select(categories_table.c.CategoryName)
    with engine.connect() as connection:
        result = connection.execute(query)
        categories = [row.CategoryName for row in result]
        return categories  # Access the column as an attribute
