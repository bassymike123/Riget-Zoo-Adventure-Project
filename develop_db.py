from flask import Flask
from model import db

app = Flask(__name__)

# configuring the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Riget_Zoo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print("database was created")