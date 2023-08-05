from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flaskext.markdown import Markdown
from sqlalchemy import create_engine
from flask_cors import CORS, cross_origin
from os import path
from socket import gethostname

db = SQLAlchemy()

def create_app(config_file = '../app.cfg'):
    # create and configure thenpm install markdown-it --save app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_file)

    #Flask_Session Variables
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    Markdown(app)
    #Init
    db.init_app(app)

    cors = CORS(app, resources={r"/pickup/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'Content-Type' 

    from .views import views
    app.register_blueprint(views, url_prefix = "/")
    from .forms import forms
    app.register_blueprint(forms, url_prefix = "/forms")
    from .external import external
    app.register_blueprint(external, url_prefix = "/ext")
    from .hackertracker import ht
    app.register_blueprint(ht, url_prefix = "/ht")
    from .dribble import dribble
    app.register_blueprint(dribble, url_prefix = '/demo')
    from .pickup import pickup
    app.register_blueprint(pickup, url_prefix = '/pickup')
    #Import all table models
    from .models import ytVideos
    from .models import ytClips
    from .models import ytChapters
    from .models import tfVersions
    from .models import mrtfHackerTracker
    from .models import mrtfVotes
    from .models import ptfServers
    
    from .models import htEvidence
    from .models import htUsers


    return app