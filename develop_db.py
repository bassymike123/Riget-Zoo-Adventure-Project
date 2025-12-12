from flask import Flask
from model import db
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "my_secret_key"


# configuring the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Riget_Zoo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()
    print("database was created")