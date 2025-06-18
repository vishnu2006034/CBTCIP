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
    



if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)