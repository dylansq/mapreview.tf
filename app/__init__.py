from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from os import path
from socket import gethostname

db = SQLAlchemy()

def create_app(config_file = '../app.cfg'):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_file)

    db.init_app(app)

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
    #Import all table models
    from .models import ytVideos
    from .models import ytClips
    from .models import ytChapters
    from .models import tfVersions
    from .models import mrtfHackerTracker

    return app