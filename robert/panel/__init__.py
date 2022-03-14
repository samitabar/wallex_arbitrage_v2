from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from flask.json import JSONEncoder


db = SQLAlchemy()


class NiceJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NameError):
            return str(obj)
        elif isinstance(obj, TypeError):
            return str(obj)
        elif isinstance(obj, Exception):
            return str(obj)
        return JSONEncoder.default(self, obj)


def create_app():
    app = Flask(__name__)

    app.debug = True
    app.json_encoder = NiceJSONEncoder

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config['SECRET_KEY'] = 'WILLIAM'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)

    from .api_v1 import app as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix='/api/v1')

    from .website import website as website_blueprint
    app.register_blueprint(website_blueprint, url_prefix='/')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/')

    return app
