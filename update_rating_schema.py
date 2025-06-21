from app import app, db
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

def add_merchant_id_column():
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                # Check if column already exists
                result = connection.execute(text("PRAGMA table_info(product);"))
                columns = [row[1] for row in result]
                if 'merchant_id' in columns:
                    print("Column 'merchant_id' already exists in 'product' table.")
                    return

                # Add the merchant_id column
                connection.execute(text("ALTER TABLE product ADD COLUMN merchant_id INTEGER;"))
                print("Column 'merchant_id' added to 'product' table.")
                
                # Note: SQLite does not support adding foreign keys with ALTER TABLE
                # You can enforce foreign keys at application level or recreate the table with foreign key
                
                # Enable foreign keys (optional, if you haven't done already)
                connection.execute(text("PRAGMA foreign_keys = ON;"))

                # If you want to enforce foreign key constraint:
                print("NOTE: In SQLite, foreign keys cannot be added directly with ALTER TABLE.")
                print("If you need strict foreign key enforcement, consider recreating the table with the FK constraint.")

        except OperationalError as e:
            print(f"OperationalError: {e}")

if __name__ == "__main__":
    add_merchant_id_column()
