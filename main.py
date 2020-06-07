"""
DiscoverDaily Web Application: Main File
Author: Luca Ostertag-Hill

Creates an instance of the application and configures it appropriately. 
Establishes a connection to the MySQL server on Google Cloud and makes sure
the database is correctly created. Also links Python logger to Google Cloud 
logging, so that any logging done through Python's logging module is also
logged in Google Cloud.
"""


from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
import sqlalchemy

# initial app configuration
app = Flask(__name__)
app.config.from_object(Config)

# connect to google cloud mysql
engine = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
        drivername='mysql+pymysql',
        username='root',
        password=app.config['DATABASE_PASSWORD'],
        database=app.config['DATABASE_NAME'],
        query={"unix_socket": '/cloudsql/discoverdaily:us-west2:discoverdailysql'},
    ),
)

# create session and base declarative
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# make sure user table is created
from models import User
Base.metadata.create_all(engine)

# schedule updates for the TopTracks playlists
from models import updatePlaylists
scheduler = BackgroundScheduler()
scheduler.add_job(updatePlaylists, trigger='interval', days=1)
scheduler.start()

import routes
bootstrap = Bootstrap(app)

# connect google cloud logging with python
import google.cloud.logging
client = google.cloud.logging.Client()
client.get_default_handler()
client.setup_logging()

