from flask import Flask

db_path = 'sqlite:///data/test.db'
#modal_package_path = '/home/grigory/PycharmProjects/wikisource/predict_models/BWordCharLSTM'
modal_package_path = '/home/grigory/PycharmProjects/wikisource/predict_models/WordLSTM'


INIT_ON_START = False
FIT_EXTRACTOR = True
FIT_PREDICT_MODEL = True


def create_app():
    app = Flask(__name__.split('.')[0])
    app.secret_key = 'Master Kenobi!'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['GENERATE_FEATURES_ON_START'] = INIT_ON_START
    app.config['FIT_EXTRACTOR'] = FIT_EXTRACTOR
    app.config['FIT_PREDICT_MODEL'] = FIT_PREDICT_MODEL

    # app.config.from_object(config_object)
    register_extensions(app)
    return app


def register_extensions(app):
    from models import db
    db.init_app(app)


app = create_app()
pass
