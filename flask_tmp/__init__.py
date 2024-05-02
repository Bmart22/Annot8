import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask_tmp.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path,'uploads'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder and upload folder exist
    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass
        
    #Init database
    from . import db
    db.init_app(app)

#    Register auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import draw
    app.register_blueprint(draw.bp)
    app.add_url_rule('/', endpoint='index')


    return app
