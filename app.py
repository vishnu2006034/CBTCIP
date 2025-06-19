from flask import Flask,render_template,request,redirect,url_for,session
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
    return render_template('main.html', products=products, search_query=search_query, sort_option=sort_option)

def get_current_customer():
    if 'customer_id' in session:
        return Customer.query.get(session['customer_id'])
    return None


@app.route('/add_to_cart/<int:product_id>')
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
            product=item.product
            if int(product.quantity)>=item.quantity:
                product.quantity =int(product.quantity)-item.quantity
            else:
                return f"not enough quantity for{product.name}"
        for item in customer.cart.items:
            db.session.delete(item)
        db.session.commit()

        return render_template('payment_success.html', order=new_order)

    total = sum(item.product.price * item.quantity for item in customer.cart.items)
    return render_template('payment.html', total=total)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get(product_id)
    return render_template('product.html', product=product)

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

@app.route('/logout')
def logout():
    session.pop('customer_id', None)
    return redirect(url_for('custlogin'))

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)