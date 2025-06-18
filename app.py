from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRETKEY'] = 'secret_key'

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String , nullable = False)
    phone = db.Column(db.Integer , nullable = False)
    address = db.Column(db.String , nullable = False)
    email = db.Column(db.String , nullable = False)
    password = db.Column(db.String , nullable = False)
    History = db.Column(db.String , nullable = True)

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


if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)