from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

from app.models import updatePlaylists

scheduler = BackgroundScheduler()
scheduler.add_job(updatePlaylists, trigger='interval', seconds=30)
scheduler.start()

# from app import routes