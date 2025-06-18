import csv
from app import db, Product, app

def import_products(csv_file):
    with app.app_context():
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip rows with missing price or stock
                if not row['price'].strip() or not row['quantity'].strip():
                    print(f"Skipping row with missing data: {row}")
                    continue

                try:
                    product = Product(
                        name=row['name'],
                        description=row['description'],
                        price=float(row['price']),
                        quantity=int(row['quantity']),
                        image_url=row['image_url']
                    )
                    db.session.add(product)
                except Exception as e:
                    print(f"Error processing row: {row}")
                    print(e)
            db.session.commit()
        print("Products imported successfully.")

if __name__ == '__main__':
    import_products('apparel.csv')
