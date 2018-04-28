from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db_path = 'sqlite:///data/test.db'
# db_path = 'sqlite:///tools/agu.db'
#modal_package_path = '/home/grigory/PycharmProjects/wikisource/predict_models/BWordCharLSTM'
modal_package_path = '/home/grigory/PycharmProjects/wikisource/predict_models/WordLSTM'



db = SQLAlchemy()

def create_app():
    app = Flask(__name__.split('.')[0])
    app.secret_key = 'Master Kenobi!'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    # app.config.from_object(config_object)
    register_extensions(app)
    return app


def register_extensions(app):
    db.init_app(app)



app = create_app()
pass
