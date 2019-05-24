from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
bootstrap = Bootstrap(app)

from app import routes