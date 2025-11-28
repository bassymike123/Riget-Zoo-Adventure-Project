from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
 # to initalsie the database
db = SQLAlchemy()

# users model
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    phone = db.Column(db.String(20))
    
# loylaty and booking relationship
loyalty_account = db.relationship("LoyaltyAccount", backref="user", uselist=False)
bookings = db.relationship("Booking", backref="user", lazy=True)

def __repr__(self):
    return f"<User {self.email}>"

# admin model
class Admin(db.Model):
    
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# visit type(hotel stay/standard visit/ VIP) model
class VisitType(db.Model):
    __tablename__ = "visit_types"
    visit_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    
    bookings = db.relationship("Booking", backref="VisitType", lazy=True)
    
# booking type model 
class Booking(db.Model):
    __tablename__ = "bookings"
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    visit_type_id = db.Column(db.Integer, db.ForeignKey("visit_types.visit_type_id"), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    
# linking payments to booking
payment = db.relationship("Payment", backref="booking", uselist=False)

#Payment Models
class Payment(db.Model):
    __tablename__ = "payments"
    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.booking_id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
#loyalty Acocunt Table
class LoyaltyAccount(db.Model):
    __tablename__ = "loyalty_accounts"
    
    loyalty_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    points = db.Column(db.Integer, default=0)
    membership_level = db.Column(db.String(50), default="Standard")
    transactions = db.relationship("LoyaltyTransaction", backref="loyalty_account", lazy=True)
    
# loyalty transaction model
class LoyaltyTransaction(db.Model):
    __tablename__ = "loyalty_transaction"
    transaction_id = db.Column(db.Integer, primary_key=True)
    loyalty_id = db.Column(db.Integer, db.ForeignKey("loyalty_accounts.loyalty_id"), nullable=False)
    points_changed = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
# accessibility model
class AccessibilitySettings(db.Model):
    __tablename__ = "accessibility_settings"
    setting_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    text_size = db.Column(db.String(20), default="medium")