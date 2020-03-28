import os
from flask import Flask
from flask_admin import Admin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

admin = Admin()
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    from main import main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/main')

    from auth import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    # login.init_app(app)

    return app