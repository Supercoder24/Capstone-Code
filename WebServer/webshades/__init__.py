import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True) # Config relative to external backend, not this webshades folder
    app.config.from_mapping(
        SECRET_KEY='dev', # TODO: Overwrite with random value before deployment
        DATABASE=os.path.join(app.instance_path, 'webshades.sqlite'), # Path to the SQLite database file
        VARIABLES='/home/shades/backend/variables/' # Path to folder to write variable files TODO: Edit this path when necessary
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True) # Can use to override the SECRET_KEY for actual deployment
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
        
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import control
    app.register_blueprint(control.bp)
    app.add_url_rule('/', endpoint='index') # Associates index with /, so both index and control.index generate /

    return app