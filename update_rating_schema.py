from app import app, db
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

def add_product_id_column():
    with app.app_context():
        try:
            # Check if column already exists
            with db.engine.connect() as connection:
                result = connection.execute(text("PRAGMA table_info(merchant);"))
                columns = [row[1] for row in result]
                if 'phone' in columns:
                    print("Column 'product_id' already exists in 'rating' table.")
                    return

                # Add the product_id column
                connection.execute(text("ALTER TABLE merchant ADD COLUMN phone INTEGER;"))
                print("Column 'phone' added to 'merchant' table.")

            # Optional: You may want to set foreign key constraints manually if needed
        except OperationalError as e:
            print(f"OperationalError: {e}")

if __name__ == "__main__":
    add_product_id_column()
