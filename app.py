from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app=Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = '123'

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String , nullable = False)
    phone = db.Column(db.Integer , nullable = False)
    address = db.Column(db.String , nullable = False)
    email = db.Column(db.String , nullable = False)
    password = db.Column(db.String , nullable = False)
    History = db.Column(db.String , nullable = True)
    # cart=db.relationship('Cart',backref='customer',uselist=False)

class Merchant(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String , nullable = False)
    email = db.Column(db.String , nullable = False)
    password = db.Column(db.String , nullable = False)
    products = db.Column(db.String , nullable = True)

class Product(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String , nullable = False)
    description = db.Column(db.String , nullable = False)
    quantity = db.Column(db.String , nullable = False)
    price = db.Column(db.Float ,nullable = False)
    image_url = db.Column(db.String , nullable = False)

from sqlalchemy.orm import backref

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', backref=backref('cart', uselist=False))
    items = db.relationship('CartItem', backref='cart', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    total_amount = db.Column(db.Float)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.relationship('Customer', backref='orders')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='ratings')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/custlogin', methods=['GET','POST'])
def custlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        customer = Customer.query.filter_by(email=email).first()
        if customer and customer.password == password:
            session['customer_id']=customer.id
            return redirect(url_for('main'))
    return render_template('custlogin.html')

@app.route('/custreg',methods=['GET','POST'])
def custreg():
    if request.method == "POST":  # to get information for employee
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        newdoc = Customer(name=name, email=email, address=address, phone=phone, password=password)
        db.session.add(newdoc)
        db.session.commit()
        # flash("account is successfully created", "success")
        return redirect(url_for('custlogin')) # after the registraion returns to login page
    # else:
        # flash("check for the account already exists")
    return render_template("custreg.html")  # it is the registration html
    
@app.route('/main', methods=['GET', 'POST'])
def main():
    search_query = request.args.get('search', '')
    sort_option = request.args.get('sort', '')

    products_query = Product.query

    if search_query:
        search_pattern = f"%{search_query}%"
        products_query = products_query.filter(
            (Product.name.ilike(search_pattern)) | (Product.description.ilike(search_pattern))
        )

    if sort_option == 'price_asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_option == 'price_desc':
        products_query = products_query.order_by(Product.price.desc())
    elif sort_option == 'name_asc':
        products_query = products_query.order_by(Product.name.asc())
    elif sort_option == 'name_desc':
        products_query = products_query.order_by(Product.name.desc())

    products = products_query.all()

    # Calculate average ratings per product
    product_ids = [product.id for product in products]
    ratings_data = db.session.query(
        Rating.product_id,
        db.func.avg(Rating.score).label('average_rating'),
        db.func.count(Rating.id).label('rating_count')
    ).filter(Rating.product_id.in_(product_ids)).group_by(Rating.product_id).all()

    ratings_dict = {str(r.product_id): {'average': round(r.average_rating, 2), 'count': r.rating_count} for r in ratings_data}

    return render_template('main.html', products=products, search_query=search_query, sort_option=sort_option, ratings=ratings_dict)

def get_current_customer():
    if 'customer_id' in session:
        return Customer.query.get(session['customer_id'])
    return None


@app.route('/add_to_cart/<int:product_id>', methods=['POST', 'GET'])
def add_to_cart(product_id):
    customer = get_current_customer()
    if not customer:
        return redirect(url_for('custlogin'))

    # Create cart if not exists
    if not customer.cart:
        cart = Cart(customer=customer)
        db.session.add(cart)
        db.session.commit()

    cart1=customer.cart
    cart_item = CartItem.query.filter_by(cart_id=cart1.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(cart=cart1, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    return redirect(url_for('main'))

@app.route('/cart')
def view_cart():
    customer = get_current_customer()
    if not customer:
        return redirect(url_for('custlogin'))

    cart = customer.cart
    total = sum(item.product.price * item.quantity for item in cart.items) if cart else 0
    return render_template('cart.html', cart=cart, total=total)

@app.route('/remove_cart_item/<int:item_id>', methods=['POST'])
def remove_cart_item(item_id):
    customer = get_current_customer()
    if not customer:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    cart = customer.cart
    if not cart:
        return jsonify({'success': False, 'message': 'Cart not found'}), 404

    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item removed'})


@app.context_processor
def inject_cart():
    customer = None
    cart = None
    total = 0
    if 'customer_id' in session:
        customer = Customer.query.get(session['customer_id'])
        if customer and customer.cart:
            cart = customer.cart
            total = sum(item.product.price * item.quantity for item in cart.items)
    return dict(cart=cart, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    customer = get_current_customer()
    if not customer or not customer.cart or not customer.cart.items:
        return redirect(url_for('main'))

    if request.method == 'POST':
        total_amount = sum(item.product.price * item.quantity for item in customer.cart.items)

        # Create order
        new_order = Order(customer=customer, total_amount=total_amount)
        db.session.add(new_order)

        # Empty the cart
        for item in customer.cart.items:
            product = item.product
            try:
                product_quantity = int(product.quantity)
            except (ValueError, TypeError):
                return f"Invalid quantity value for {product.name}"
            if product_quantity >= item.quantity:
                product.quantity = str(product_quantity - item.quantity)
            else:
                return f"Not enough quantity for {product.name}"
        for item in customer.cart.items:
            db.session.delete(item)
        db.session.commit()

        return render_template('payment_success.html', order=new_order)

    total = sum(item.product.price * item.quantity for item in customer.cart.items)
    return render_template('payment.html', total=total)


@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get(product_id)
    total_ratings = Rating.query.filter_by(product_id=product_id).count()
    if total_ratings == 0:
        average = 0
    else:
        sum_ratings = db.session.query(db.func.sum(Rating.score)).filter(Rating.product_id == product_id).scalar()
        average = sum_ratings / total_ratings
    return render_template('product.html', product=product, average=round(average, 2), total=total_ratings)

@app.route('/buy/<int:product_id>',methods=['GET','POST'])
def buy(product_id):
    customer = get_current_customer()
    product = Product.query.get(product_id)
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        if int(product.quantity) >= quantity:
            total = quantity * product.price
            new = Order(customer=customer,total_amount=total)
            db.session.add(new)
            product.quantity=int(product.quantity)-quantity
            db.session.commit()
            return render_template('payment_success.html',order=new)
        else :
            return f"Not enough quantity for {product.name}"
    return render_template('buy.html',product=product)

<<<<<<< HEAD
@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.get_json()
    score = data.get('rating')
    product_id = data.get('product_id')
    if score is None or not (1 <= score <= 5) or product_id is None:
        return jsonify({'message': 'Invalid rating or product ID'}), 400
    new_rating = Rating(score=score, product_id=product_id)
    db.session.add(new_rating)
    db.session.commit()
    return jsonify({'message': 'Rating submitted successfully'}), 200

@app.route('/get_average', methods=['GET'])
def get_average():
    product_id = request.args.get('product_id', type=int)
    if product_id is None:
        return jsonify({'average': 0, 'total': 0})
    total_ratings = Rating.query.filter_by(product_id=product_id).count()
    if total_ratings == 0:
        return jsonify({'average': 0, 'total': 0})
    sum_ratings = db.session.query(db.func.sum(Rating.score)).filter(Rating.product_id == product_id).scalar()
    average = sum_ratings / total_ratings
    return jsonify({'average': round(average, 2), 'total': total_ratings})

@app.route('/remove_cart', methods=['POST'])
def remove_cart():
    customer = get_current_customer()
    if not customer:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    cart = customer.cart
    if not cart:
        return jsonify({'success': False, 'message': 'Cart not found'}), 404

    data = request.get_json()
    item_id = data.get('item_id')
    if not item_id:
        return jsonify({'success': False, 'message': 'Item ID not provided'}), 400

    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item removed'})

@app.route('/update_cart_item_quantity', methods=['POST'])
def update_cart_item_quantity():
    customer = get_current_customer()
    if not customer:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    cart = customer.cart
    if not cart:
        return jsonify({'success': False, 'message': 'Cart not found'}), 404

    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity')

    if not item_id or quantity is None:
        return jsonify({'success': False, 'message': 'Item ID and quantity are required'}), 400

    try:
        quantity = int(quantity)
        if quantity < 1:
            return jsonify({'success': False, 'message': 'Quantity must be at least 1'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400

    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404

    cart_item.quantity = quantity
    db.session.commit()
    return jsonify({'success': True, 'message': 'Quantity updated'})
=======
@app.route('/add_rating', methods=['POST'])
def add_rating():
    product_id = request.form.get('product_id')
    reviewer_name = request.form.get('reviewer_name')
    rating_value = request.form.get('rating')
    review_text = request.form.get('review')

    if not product_id or not reviewer_name or not rating_value:
        return "Missing required fields", 400

    # Here you would add logic to save the rating to the database
    # For now, just simulate success

    # Redirect back to the product page
    return redirect(url_for('product', product_id=product_id))

>>>>>>> 9f6da84c8da2e6089ee80b30c07756d652f9d79a
@app.route('/logout')
def logout():
    session.pop('customer_id', None)
    return redirect(url_for('custlogin'))

@app.route('/order_history')
def order_history():
    customer = get_current_customer()
    if not customer:
        return redirect(url_for('custlogin'))
    orders = customer.orders
    return render_template('order.html', orders=orders)

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
