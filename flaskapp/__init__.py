from flask import Flask
from flask_bootstrap import Bootstrap
from flask_jwt_extended import JWTManager, get_current_user
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from worker import conn

import flask_cors

db = SQLAlchemy()
cors = flask_cors.CORS()
jwt = JWTManager()
q = Queue(connection=conn)


def create_app(config_path='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_path)
    Bootstrap(app)

    db.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    @app.context_processor
    def inject_current_user():
        return dict(current_user=get_current_user())

    with app.app_context():

        from flaskapp.api import s3_bp
        app.register_blueprint(s3_bp)

        from flaskapp.blueprints.user_files import files_bp
        app.register_blueprint(files_bp)

        from flaskapp.blueprints.auth import auth_bp
        app.register_blueprint(auth_bp)

        from flaskapp.utils import datetimeformat, strip_domain
        app.jinja_env.filters['datetimeformat'] = datetimeformat
        app.jinja_env.filters['strip_domain'] = strip_domain

        from flaskapp.models.Model import User
        db.create_all()
        db.session.commit()

    return app

