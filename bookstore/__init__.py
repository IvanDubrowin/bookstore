from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from config import basedir
from flask_bootstrap import Bootstrap
from flask_login import LoginManager


app = Flask(__name__, static_url_path='/static')
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
app.config.from_object('config')
from bookstore import views, models
