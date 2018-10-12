import os
from flask import Flask
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()

def create_app(test_config=None):
    #create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
    SERECT_KEY = 'dev',
    DATABASE = os.path.join(app.instance_path, 'ordery.sqlite')
    )

    app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
    ))

    if test_config is None:
        #load the instance config, if exits, then no testing.
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config if passed in
        app.config.from_maping(test_config)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    bootstrap.init_app(app)


    from . import db
    db.init_app(app)

    from . import orders
    app.register_blueprint(orders.bp)

    from . import products
    app.register_blueprint(products.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
