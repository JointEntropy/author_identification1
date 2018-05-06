from gvars import app
from backend import be
import views


if __name__  ==  '__main__':
    # restore_after_flush()
    # app.config['DEBUG'] = True
    with app.app_context():
        be.on_start(
            generate_features=app.config['GENERATE_FEATURES_ON_START'],
            fit_extractor=app.config['FIT_EXTRACTOR'],
            fit_predict_model=app.config['FIT_PREDICT_MODEL']
        )
    app.run(host='0.0.0.0')










