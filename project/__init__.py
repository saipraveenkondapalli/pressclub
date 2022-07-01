import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Instance of the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('skey')


# flask bycrypt for password hashing
bcrypt = Bcrypt(app)


# Configure database
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"): # change to postgresql
    uri = uri.replace("postgres://", "postgresql://", 1)

# Note: We are using sqlite in production for development

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Configure mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.environ.get('FLASK_MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get("FLASK_MAIL_PASSWORD")
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)


# Configure login
login_manager = LoginManager(app = app)
login_manager.login_view = 'login'


# Upload config
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'raw', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



