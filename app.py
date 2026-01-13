from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint, jsonify
import stripe
from model import db, User, VisitType, Booking, Payment, LoyaltyAccount, LoyaltyTransaction, ZooTicketType, HotelRoomType
from datetime import datetime, time
from flask_bcrypt import Bcrypt
import re 
from datetime import date
import pyotp # generates the secret key and time based otp
import qrcode as qr # creates qr image for the users to scan in their authenticator
import io
import base64
import random # for forgot password verification
import string # for forgot password verification
 # import time # for forgot password verification
from flask_mail import Mail, Message
from functools import wraps
import os
from dotenv import load_dotenv
import uuid
from utils.qr import generate_qr
load_dotenv()


app = Flask(__name__)
app.secret_key = "my_secrect_key"
admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

app.config["STRIPE_SECRET_KEY"] = os.getenv("STRIPE_SECRET_KEY")
app.config["STRIPE_PUBLISHABLE_KEY"] = os.getenv("STRIPE_PUBLISHABLE_KEY")

stripe.api_key = app.config["STRIPE_SECRET_KEY"]

# configuring the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Riget_Zoo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# flask mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
db.init_app(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

ROLE_ADMIN = "admin"
ROLE_USER = "user"
# -------------------------

# Helper decorators

# -------------------------

def login_required(f):

    @wraps(f)

    def decorated(*args, **kwargs):

        if not session.get('user_id'):

            flash("Please login to access this page.", "error")

            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated

def admin_required(f):

    @wraps(f)

    def decorated(*args, **kwargs):

        uid = session.get('user_id')

        if not uid:

            flash("Please login to access admin.", "error")

            return redirect(url_for('login'))

        user = User.query.get(uid)

        if not user or not user.role or user.role.strip().lower() != ROLE_ADMIN:
            flash("Admin access required.", "error")
            return redirect(url_for('user_dashboardd'))
        
        return f(*args, **kwargs)
    return decorated          

def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        sid = session.get('user_id')

        if not sid:
            flash("Please login to access user.", "error")
            return redirect(url_for('login'))
        uuser = User.query.get(sid)
        if not uuser or not uuser.role or uuser.role.strip().lower() != ROLE_USER:
            flash("User access required", "error")
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated





@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        
        full_name = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        dob_day = request.form.get('day')
        dob_month= request.form.get('month')
        dob_year = request.form.get('year')
        role = request.form.get('role')
        
        
        
        
        # formatting dob
        dob = f"{dob_day}-{dob_month.zfill(2)}-{dob_year.zfill(2)}"
        date_of_birth = datetime.strptime(dob, "%d-%B-%Y").date()
        
        
        # empty fields
        if not full_name or not email or not password or not confirm_password:  # password must not be less than 8 characters long
            flash("Please fill in all fields and try again", "error")
            return redirect(url_for("signup"))
        
        MIN_YEAR = 2012 # minimum age allowed to register

        
        
        if dob_year > str(MIN_YEAR):
            flash(f"Year of birth cannot be earlier than {MIN_YEAR}", "error")
            return redirect(url_for('signup'))
        
        
    
    
                
        # password validation
        if len(password) <8:
            flash("Password must be at least 8 characters long, try again!!", "error")
            return redirect(url_for('signup'))
        
        
        if not re.search(r'[A-Z]', password):
            flash("Password must contain at least one upper case letter", "error") #password must have at least one uppercase letter
            return redirect(url_for('signup'))
        
        
        
       
        
        # cuses regex to check only for letters, single spaces between words and no leading spaces.
        
        
        if not re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", full_name):
            flash("Full name should only contain letters and single spaces", "error")
            return redirect(url_for('signup'))
              
        
        if password != confirm_password:
            flash('Passwords do not match!!, try again', "error") # checks if passwords match
            return redirect(url_for('signup'))
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash("Password must contain at least one special symbol  like !, @, #, etc.", "error")
            return redirect(url_for('signup'))
        
    
        
        secret = pyotp.random_base32()
        session['secret'] = secret
        session['user_data'] = {
            'full_name': full_name,
            'date_of_birth' : date_of_birth,
            'email' : email,
            'password' : bcrypt.generate_password_hash(password).decode('utf-8'),
            'role' : role
        }
        
        # creating OTP and QR code
        otp = pyotp.TOTP(secret, digits=6, interval=30)
        uri = otp.provisioning_uri(name=email, issuer_name="Riget Zoo Adventures")
        qr_code = qr.QRCode(box_size=8, border=4)
        qr_code.add_data(uri)
        
        qr_code.make(fit=True)
        img = qr_code.make_image(fill_color="orange", back_color="white")
        # converting QR code to base64 so we can embed it into HTML
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return render_template("verify.html", qr_code=qr_base64)
    session.modified = True
    
    return render_template("signup.html")
    
@app.route('/verify', methods=['GET', 'POST'])

def verify():

    # if GET request → regenerate QR code

    if request.method == 'GET':
        secret = session.get('secret')
        if not secret:
            return redirect(url_for('signup'))

        otp = pyotp.TOTP(secret, digits=6, interval=30)
        uri = otp.provisioning_uri(name=session['user_data']['email'], issuer_name="Riget Zoo Adventures")
        qr = qr.QRCode(box_size=8, border=4)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="orange", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return render_template("verify.html", qr_code=qr_base64)

    # POST request → verify code

    otp_input = request.form['otp_code']
    secret = session.get('secret')

    if not secret:

        flash("Session expired. Please sign up again.", "error")
        return redirect(url_for("signup"))
    totp = pyotp.TOTP(secret, digits=6, interval=30)
    if totp.verify(otp_input):
        data = session['user_data']

        # check if email exists

        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            flash("This email is already registered. Please log in.", "error")
            return redirect(url_for('login'))

        # create new user

        new_user = User(

            full_name=data['full_name'],
            date_of_birth=data['date_of_birth'],
            email=data['email'],
            password=data['password'],
            role=data['role']
        )
        
        db.session.add(new_user)
        db.session.commit()
        session.pop('user_data', None)
        session.pop('secret', None)
        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    else:
        flash("Invalid OTP. Please try again.", "error")
        return redirect(url_for('verify'))
         
        
        

# route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # checks if the user exsists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # verifies password
            if bcrypt.check_password_hash(user.password, password):
                session['user_id'] = user.user_id
                session['fullname'] = user.full_name
                flash("Login sucessfully", "success")
                return redirect(url_for('login')) # would change later
            else:
                flash("Incorrect password. Please try again.", "error")
        else:
            flash("No account found with that email.", "error")
        return redirect(url_for('login'))
    
    return render_template('login.html')

# forgot password - entering email
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
     if request.method == 'POST':
         email = request.form.get('email', '').strip().lower()
         if not email:
             flash("Please enter your email", "error")
             return redirect(url_for('forgot_password'))
         
         # generate OTP and store in session 
         otp = ''.join(random.choices(string.digits, k=6))
         session['reset_email'] = email
         session['reset_otp'] = otp
         session['reset_otp_time'] = time.time()
         
         
         try:
             msg = Message('GibJohn password reset code', recipients=[email])
             msg.body = f'Your password reset code is: {otp}\nIt is valid for 90 seconds.'
             mail.send(msg)
             
         except Exception as e:
             app.logger.error("Mail send failed: %s", e)
             flash("Failed to send OTP. Try again later.", "error")
             return redirect(url_for('forgot_password'))
         
         flash('OTP sent to your email. Check your inbox.', 'info')
         return redirect(url_for('verify_otp'))
     
     return render_template('forgot_password.html')
 
# verify OTP
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered = request.form.get('otp', '').strip() # removes any unwanted spaces
        stored = session.get('reset_otp')
        ts = session.get('reset_otp_time')
        
        if not stored or not ts:
            flash("No OTP found. Please request a new code", "error")
            return redirect(url_for('forgot_password'))
        
        # expiry check - 90 seconds
        if time.time() - ts > 90:
            session.pop('reset_otp', None)
            session.pop('reset_otp_time',  None)
            flash("OTP expired. Please request a new code", "error")
            return redirect(url_for('forgot_password'))
        
        if entered == stored:
            session['otp_verified'] = True
            flash("OTP verified. You may reset your password.", "success")
            return redirect(url_for('reset_password'))
        else:
            flash("Incorrect OTP, try again", "error")
            return redirect(url_for('verify_otp'))
        
    return render_template('verify_otp.html')

# reset password

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    # requires verified OTP
    if not session.get('otp_verified'):
        flash("Please verify the OTP first", "error")
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_pw = request.form.get('new_password')
        confirm = request.form.get('confirm_password')
        if not new_pw or new_pw != confirm:
            flash("Password do not match or are empty", "error")
            return redirect(url_for('reset_password'))
        
        email = session.get('reset_email')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Account not found, please try again", "error")
            return redirect(url_for('reset_password'))
        
        user.password = bcrypt.generate_password_hash(new_pw).decode('utf-8')
        db.session.commit()
        
        # clears session entires for security and better ux
        session.pop('reset_otp', None)
        session.pop('reset_otp_time', None)
        session.pop('otp_verified', None)
        session.pop('reset_email', None)
        
        flash("Passowrd updated successfully, you can now log in", "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html')
 # home route  
@app.route('/')
def home ():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about_us.html')

@app.route('/privacy')
def privacy_page():
    return render_template('privacy_page.html')

@app.route('/contact')
def contact_us():
    return render_template('contact_us.html')

@app.route('/loyalty')
@login_required
def loyalty():
    return render_template('admin/loyalty.html')


# -------------------------

# Admin section (all as app routes)

# -------------------------

@app.route('/admin')

@login_required

@admin_required

def admin_dashboard():

    total_users = User.query.count()

    total_bookings = Booking.query.count()

    total_payments = db.session.query(db.func.sum(Payment.amount)).scalar() or 0

    pending_bookings = Booking.query.filter_by(status='Pending').count()

    recent_bookings = Booking.query.order_by(Booking.visit_date.desc()).limit(7).all()

    visit_types = VisitType.query.all()
    
    admin_info = {
        'id': session['user_id'],
        'full_name': session['fullname']
    }
    user = User.query.get(session['user_id'])
    return render_template('admin_dashboard.html',

                           total_users=total_users,

                           total_bookings=total_bookings,

                           total_payments=total_payments,

                           pending_bookings=pending_bookings,

                           recent_bookings=recent_bookings,

                           visit_types=visit_types,
                           user=user,
                           admin=admin_info
                           )


# VisitType CRUD



@app.route('/admin/visit_types/add', methods=['POST'])

@login_required

@admin_required

def add_visit_type():

    name = request.form.get('name', '').strip()

    price = request.form.get('price', '0').strip()

    description = request.form.get('description', '').strip()

    if not name or not price:

        flash("Name and price are required.", "error")

        return redirect(url_for('admin_visit_types'))

    try:

        price_val = float(price)

    except ValueError:

        flash("Price must be a number.", "error")

        return redirect(url_for('admin_visit_types'))

    vt = VisitType(name=name, description=description, price=price_val)

    db.session.add(vt)

    db.session.commit()

    flash("Visit type added.", "success")

    return redirect(url_for('admin_visit_types'))

@app.route('/admin/visit_types/<int:vt_id>/edit', methods=['POST'])

@login_required

@admin_required

def edit_visit_type(vt_id):

    vt = VisitType.query.get_or_404(vt_id)

    vt.name = request.form.get('name', vt.name).strip()

    vt.description = request.form.get('description', vt.description).strip()

    try:

        vt.price = float(request.form.get('price', vt.price))

    except ValueError:

        flash("Invalid price.", "error")

        return redirect(url_for('admin_visit_types'))

    db.session.commit()

    flash("Visit type updated.", "success")

    return redirect(url_for('admin_visit_types'))

@app.route('/admin/visit_types/<int:vt_id>/delete', methods=['POST'])

@login_required

@admin_required

def delete_visit_type(vt_id):

    vt = VisitType.query.get_or_404(vt_id)

    db.session.delete(vt)

    db.session.commit()

    flash("Visit type deleted.", "success")

    return redirect(url_for('admin_visit_types'))


# Bookings routes


@app.route('/admin/bookings/<int:booking_id>/update_status', methods=['POST'])

@login_required

@admin_required

def update_booking_status(booking_id):

    new_status = request.form.get('status')

    b = Booking.query.get_or_404(booking_id)

    if new_status:

        b.status = new_status

        db.session.commit()

        flash("Booking status updated.", "success")

    return redirect(url_for('admin_bookings'))

@app.route('/admin/bookings/<int:booking_id>/edit', methods=['POST'])

@login_required

@admin_required

def edit_booking(booking_id):

    b = Booking.query.get_or_404(booking_id)

    # example: update visit_date and guests

    date_str = request.form.get('visit_date', '').strip()

    guests = request.form.get('number_of_guests', '').strip()

    visit_type = request.form.get('visit_type_id', '').strip()

    try:

        if date_str:

            b.visit_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        if guests:

            b.number_of_guests = int(guests)

        if visit_type:

            b.visit_type_id = int(visit_type)

        db.session.commit()

        flash("Booking updated.", "success")

    except Exception as e:

        db.session.rollback()

        app.logger.exception("Failed to update booking: %s", e)

        flash("Failed to update booking.", "error")

    return redirect(url_for('admin_bookings'))


# Users management


@app.route('/admin/users/<int:user_id>/edit', methods=['POST'])

@login_required

@admin_required

def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    full_name = request.form.get('full_name', user.full_name).strip()

    email = request.form.get('email', user.email).strip().lower()

    role = request.form.get('role', user.role)

    user.full_name = full_name

    user.email = email

    user.role = role

    db.session.commit()

    flash("User updated.", "success")

    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['GET'])

@login_required

@admin_required

def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    db.session.delete(user)

    db.session.commit()

    flash("User deleted.", "success")

    return redirect(url_for('admin_users'))


# Loyalty management

@app.route('/admin/loyalty/<int:user_id>', methods=['GET'])
def view_loyalty(user_id):

    la = LoyaltyAccount.query.filter_by(user_id=user_id).first()

    if not la:

        flash("No loyalty account for user.", "info")

        return redirect(url_for('admin_users'))

    transactions = la.transactions

    return render_template('admin/loyalty.html', account=la, transactions=transactions)

@app.route('/admin/loyalty/<int:user_id>/adjust', methods=['POST'])

@login_required

@admin_required

def adjust_loyalty(user_id):

    la = LoyaltyAccount.query.filter_by(user_id=user_id).first()

    if not la:

        # create account if missing

        la = LoyaltyAccount(user_id=user_id, points=0)

        db.session.add(la)

        db.session.commit()

    try:

        delta = int(request.form.get('points_delta', '0'))

    except ValueError:

        flash("Invalid points value.", "error")

        return redirect(url_for('view_loyalty', user_id=user_id))

    la.points += delta

    # create transaction

    txn = LoyaltyTransaction(loyalty_id=la.loyalty_id, points_changed=delta,

                             description=request.form.get('description', 'Admin adjustment'))

    db.session.add(txn)

    db.session.commit()

    flash("Loyalty points adjusted.", "success")

    return redirect(url_for('view_loyalty', user_id=user_id))


# Payments


@app.route('/admin/payments/<int:payment_id>/update', methods=['POST'])

@login_required

@admin_required

def update_payment(payment_id):

    p = Payment.query.get_or_404(payment_id)

    try:

        p.amount = float(request.form.get('amount', p.amount))

        p.payment_method = request.form.get('payment_method', p.payment_method)

        db.session.commit()

        flash("Payment updated.", "success")

    except Exception as e:

        db.session.rollback()

        app.logger.exception("Unable to update payment: %s", e)

        flash("Unable to update payment.", "error")

    return redirect(url_for('admin_payments'))
# logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))


@app.route('/admin/visit-types')
@login_required
@admin_required
def admin_visit_types():
    visit_types = VisitType.query.all()
    return render_template('admin/visit_types.html', visit_types=visit_types)




@app.route('/admin/bookings')
@login_required
@admin_required
def admin_bookings():
    return render_template('admin/bookings.html')

@app.route('/admin/payments')
@login_required
@admin_required
def admin_payments():
    payments = Payment.query.join(Booking).order_by(Payment.payment_date.desc()).all()
    return render_template('admin/payments.html', payments=payments)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/loyalty')
@login_required
@admin_required
def admin_loyalty():
    flash("Select a user first.", "info")
    return render_template('admin/loyalty.html', account=None, transactions=None)

# app route to view all tickets
@app.route('/admin/tickets')
@login_required
@admin_required
def admin_tickets():
    tickets = ZooTicketType.query.all()
    return render_template("admin/admin_tickets.html", tickets=tickets)

# add ticket types as an admin
@app.route("/admin/tickets/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_ticket_type():
    if request.method == "POST":
        name = request.form["ticket_type_name"].strip()
        price = float(request.form["price"])
        total = int(request.form["total_available"])
    

        ticket = ZooTicketType(
            name=name, price=price, 
            total_available=total, 
            remaining_available=total
            )
        db.session.add(ticket)
        db.session.commit()
        flash(" Zoo Ticket type added.", "success")
        return redirect(url_for("admin_tickets"))
    
    return render_template("admin/admin_add_ticket.html")
# route for admin to edit ticket types
@app.route("/admin/tickets/edit/<int:ticket_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_tickets(ticket_id):
    ticket = ZooTicketType.query.get_or_404(ticket_id)

    if request.method == "POST":
        ticket.name = request.form["name"].strip()
        ticket.price = float(request.form["price"])
        new_total = int(request.form["total_available"])

        # adjust remaining based on new total
        diff = new_total - ticket.total_available
        ticket.remaining_available += diff
        ticket.total_available = new_total

        ticket.active = "active" in request.form
        db.session.commit()
        flash("Ticket updated successfully,", "success")
        return redirect(url_for("admin_tickets"))
    return render_template("admin/admin_edit_ticket.html", ticket=ticket)
# this preserves existing bookings
# if an admin increases stock, the remaining stock increases accordingly
# if an admin decreases stock, the remaining stock decreases but not below zero

# toggle active status of ticket types
@app.route("/admin/tickets/toggle/<int:ticket_id>")
@login_required
@admin_required
def admin_toggle_ticket(ticket_id):
    ticket = ZooTicketType.query.get_or_404(ticket_id)
    ticket.active = not ticket.active
    db.session.commit()
    flash("Ticket status toggled.", "success")
    return redirect(url_for("admin_tickets"))

@app.route("/admin/hotel")
@login_required
@admin_required
def admin_hotel_rooms():
    rooms = HotelRoomType.query.all()
    return render_template("admin/admin_hotel_rooms.html", rooms=rooms)


# route for admin to add  new hotel room types
@app.route("/admin/hotel/add", methods=["GET", "POST"])
@login_required
@admin_required
def admin_add_hotel_room():
    if request.method == "POST":
        room = HotelRoomType(
        name = request.form['name'].strip(),
        description = request.form['description'].strip(),
        price_per_night = request.form['price'],
        total_rooms = request.form['total_rooms'],
        remaining_rooms = request.form['total_rooms']
        )
        db.session.add(room)
        db.session.commit()
        
        return redirect(url_for("admin_hotel_rooms"))
    
    return render_template("admin/admin_add_hotel_room.html")   


# route for admin to edit hotel room types
@app.route("/admin/hotel/edit/<int:room_id>", methods=["GET", "POST"])  
@login_required
@admin_required
def admin_edit_hotel_room(room_id):
    room = HotelRoomType.query.get_or_404(room_id)
    
    if request.method == "POST":
        room.name = request.form['name']
        room.description = request.form['description']
        room.price_per_night = float(request.form['price'])
        room.total_rooms = int(request.form['total_rooms'])
        
        if room.remaining_rooms > room.total_rooms:
            room.remaining_rooms = room.total_rooms
            
        db.session.commit()
        return redirect(url_for("admin_hotel_rooms"))
    
    return render_template("admin/admin_edit_hotel_rooms.html", room=room)


# route for admin to enable and disbale room types
@app.route("/admin/hotel/toggle/<int:room_id>")
@login_required
@admin_required
def admin_toggle_hotel_room(room_id):
    room = HotelRoomType.query.get_or_404(room_id)
    room.active = not room.active
    db.session.commit()
    return redirect(url_for("admin_hotel_rooms"))

# route for users main dashboard
@app.route("/user/dashboard")
@login_required
@user_required


def user_dashboardd():
    # admin should never land here
    user = User.query.get(session["user_id"])
    
    # bookings 
    user_bookings = Booking.query.filter_by(
        user_id =user.user_id
    ).all()
    total_bookings = len(user_bookings)
    upcoming_visits = Booking.query.filter(
        Booking.user_id == user.user_id,
        Booking.visit_date >= date.today(),
        Booking.status != "Cancelled"
    ).count()

    # payments
    total_payments = Payment.query.join(Booking).filter(
        Booking.user_id == user.user_id
    ).count()
    
    

    #loyalty
    loyalty = LoyaltyAccount.query.filter_by(
        user_id=user.user_id
    ).first()
    
    membership_level = (
        "GOLD" if user.loyalty_points >= 500 else
        "SILVER" if user.loyalty_points >= 200 else
        "BRONZE"
    )
    loyalty_points = loyalty.points if loyalty else 0
    membership_level = loyalty.membership_level if loyalty else "None"
    
    uusser_info = {
        'full_name': session['fullname']
    }
    
    

    return render_template(
        "user/dashboard.html",
        total_bookings=total_bookings,
        upcoming_visits=upcoming_visits,
        total_payments=total_payments,
        loyalty_points=loyalty_points,
        membership_level=membership_level,
        user=user,
        uusser_info=uusser_info
    )

# route for user bookings
@app.route("/user/bookings")
@login_required
@user_required
def user_bookings():
    

    bookings = Booking.query \
    .filter_by(user_id=session["user_id"]) \
    .order_by(Booking.visit_date.desc()) \
    .all()
    
    today = date.today()
    
    upcoming = [b for b in bookings if b.visit_date >= today]
    past = [b for b in bookings if b.visit_date < today]
    
    return render_template(
        "user/booking.html",
        upcoming=upcoming,
        past=past
    )
    
# route for user zoo tickets
@app.route("/user/zoo-tickets")
@login_required
@user_required

def user_zoo_tickets():
    
    tickets = ZooTicketType.query.filter(
        ZooTicketType.active == True,
        ZooTicketType.remaining_available > 0
        ).all()
    
    return render_template(
        "user/zoo_tickets.html",
        tickets=tickets
    )

# opening Hours
def get_opening_hours_py(date):
    weekday = date.weekday()  # 0 = Monday
    
    if weekday <= 4:
        return time(9, 0), time(18, 0)  # Weekdays: 9 AM - 6 PM
    elif weekday == 5:
        return time(9, 0), time(19, 0) # Saturday: 9 AM - 7 PM
    else:
        return time(10, 0), time(17, 0) # Sunday: 10 AM - 5 PM

# route for zoo ticket booking
@app.route("/user/zoo-tickets/book/<int:ticket_id>", methods=["GET", "POST"])
@login_required
@user_required

def book_zoo_ticket(ticket_id):
    ticket = ZooTicketType.query.get_or_404(ticket_id)
    
    if not ticket.active or ticket.remaining_available <= 0:
        flash("This ticket is no longer available.", "error")
        return redirect(url_for("user_zoo_tickets"))
    
    if request.method == "POST":
        visit_date = datetime.strptime(
            request.form["visit_date"], "%Y-%m-%d"
            ).date()
        
        visit_time = datetime.strptime(
            request.form["visit_time"], "%H:%M"
            ).time()
        
        # date check
        if visit_date < date.today():
            flash("You cannot book a past date.", "error")
            return redirect(url_for("book_zoo_ticket", ticket_id=ticket_id))
        
        open_time, close_time = get_opening_hours_py(visit_date)
        
        if not (open_time <= visit_time <= close_time):
            flash(f"Visit time must be within opening hours: {open_time.strftime('%I:%M %p')} - {close_time.strftime('%I:%M %p')}", "error")
            return redirect(url_for("book_zoo_ticket", ticket_id=ticket_id))
        
        booking = Booking(
            user_id=session["user_id"],
            visit_type_id=ticket.ticket_type_id,   # zoo ticket, not visit type
            visit_date=visit_date,
            number_of_guests=1,  
            status="Pending",
        )

        ticket.remaining_available -= 1
        db.session.add(booking)
        db.session.commit()
        
        flash("Ticket reserved. Please proceed to payment.", "success")
        return redirect(url_for("payment_page", booking_id=booking.booking_id))
    
    return render_template(
        "user/book_zoo_ticket.html",
        ticket=ticket
    )

# payment route with stripe
@app.route("/user/payment/<int:booking_id>")
@login_required
@user_required
def payment_page(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != "Pending":
        flash("This booking has already been paid.", "info")
        return redirect(url_for("user_bookings"))
    
    # determine price (Zoo ticket)
    ticket = ZooTicketType.query.get(booking.visit_type_id)
    amount = ticket.price
    
    
    # reusing exisiting intent
    if booking.payment_intent_id:
        intent = stripe.PaymentIntent.retrieve(booking.payment_intent_id)
    else:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency="gbp",
            metadata={"booking_id": booking.booking_id}
        )
    
    return render_template(
        "user/payment.html",
        booking=booking,
        ticket=ticket,
        amount=amount,
        client_secret=intent.client_secret,
        stripe_public_key=app.config["STRIPE_PUBLISHABLE_KEY"]
    )

# route to confirm payment
@app.route("/user/payment/confirm", methods=["POST"])
@login_required
@user_required

def confirm_payment():
    data = request.get_json() or {}
    payment_intent_id = data.get("payment_intent_id")
    if not payment_intent_id:

        return jsonify({"status": "error", "message": "Missing payment_intent_id"}), 400
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    # Only proceed if Stripe says it succeeded
    if intent.status != "succeeded":
        return jsonify({"status": "not_paid"}), 400
    booking_id = intent.metadata.get("booking_id")
    if not booking_id:
        return jsonify({"status": "error", "message": "No booking_id in metadata"}), 400
    booking = Booking.query.get_or_404(int(booking_id))
    if booking.status == "Confirmed":
        return jsonify({"status": "already_paid", "booking_id": booking.booking_id})
    # Create payment row

    payment = Payment(
        booking_id=booking.booking_id,
        amount=intent.amount / 100,
        payment_method="Stripe",
        status="Completed"
    )

    # Confirm booking
    booking.status = "Confirmed"
    # QR token + QR image

    booking.qr_token = uuid.uuid4().hex
    booking.qr_image = generate_qr(booking.qr_token, booking.booking_id)
    # Loyalty points (fetch user safely)

    user = User.query.get_or_404(booking.user_id)
    if user.loyalty_points is None:
        user.loyalty_points = 0
    user.loyalty_points += int(payment.amount * 10)
    # Save everything

    db.session.add(payment)
    db.session.add(booking)
    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "success", "booking_id": booking.booking_id})
     
# success page route
@app.route("/user/payment/success/<int:booking_id>")
@login_required
@user_required
def payment_success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != "Confirmed":
        flash("Payment not completed.", "error")
        return redirect(url_for("user_bookings"))
    
    return render_template(
        "user/payment_success.html",
        booking=booking
    )
    














# Run app

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
    
    