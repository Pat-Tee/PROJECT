from flask_app import app
from flask import render_template, request, redirect, session, flash
from flask_app import app
from flask_bcrypt import Bcrypt
from flask_app.models.user import User

bcrypt = Bcrypt(app)

@app.route("/")
def index():
    if not session.get('user_id'):
        return redirect('/login')
    
    users = User.get_all_with_addresses()
    
    return render_template("index.html", users = users)

@app.route("/login")
def showlogin():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear();
    return redirect("/")

@app.route("/checklogin", methods=['POST'])
def login():
    data = {
        'email' :      request.form['email'],
        'password':    request.form['password']
        }
    valid = User.valid_login(data)
    if not valid:
        flash('This is not a valid login!', 'error')
        return redirect('/login')

    user = User.getby_email(data)
    if user:
        if (bcrypt.check_password_hash(user['password'], data['password'])):
            session['user_id'] = user['id']
            msg = 'Welcome, '+ user['first_name']+'!'
            print('User is valid, logged in.')
            flash(msg, 'welcome')
        else:
            flash("This is not a valid login!", 'error')
    else:
        flash("This is not a valid login!", 'error')
    return redirect("/")

@app.route("/register", methods = ["POST"])
def register():
    data = {
        'first_name' :  request.form['first_name'],
        'last_name' :   request.form['last_name'],
        'password':     request.form['password'],
        'pw_verify':    request.form['password_verify'],
        'email':        request.form['email'],
        'phone':        request.form['phone'],
        'phone_alt':    request.form['phone_alt'],
        'street1':      request.form['street1'],
        'street2':      request.form['street2'],
        'city':         request.form['city'],
        'state':        request.form['state'],
        'zipcode':      request.form['zipcode'],
        'country':      request.form['country'],
        'address_id':   0
        }
    
    validUser = User.valid_new_user(data)
    if not validUser:
        flash('These are not valid user details!', 'error')
        return redirect('/login')
    pw_hash = bcrypt.generate_password_hash(data['password'])
    data['password'] = pw_hash
    if not User.check_new(data):        #check if user already is in database
        data['address_id'] = User.add_address(data)
        user_id = User.add(data)       #if not, save user in database
        session['user_id'] = user_id
        msg = 'Welcome, '+ data['first_name']+'!'
        flash(msg, 'welcome')
    else:
        flash('This user already exists!','error')
    return redirect("/")

@app.errorhandler(404)
def unknown(err):
    return '404 : NOT FOUND!'
