"""
ciobrain/__init__.py

This module initialized the Flask application, sets up configuration settings,
creates necessary directories, and registers the main Blueprints for the admin
and customer sections.
"""

import os
from flask import Flask, render_template
from ciobrain.admin import admin_bp
from ciobrain.customer import create_customer_blueprint 
from ciobrain.mediator import Mediator

def create_app(test_config=None):
    """Initialize and configure the Flask app instance"""

    app = Flask(__name__, instance_relative_config=True)

    # Ensure the 'instance' directory is created
    os.makedirs(app.instance_path, exist_ok=True)

    # Default configuration settings
    app.config.from_mapping(
        SECRET_KEY='dev', # Set your own
        DATABASE=os.path.join(app.instance_path, 'ciobrain.sqlite'),
        UPLOADS=os.path.join(app.instance_path, 'obfuscation/01_uploads'),
        WORKING=os.path.join(app.instance_path,'obfuscation/02_working'),
        REVIEWED=os.path.join(app.instance_path,'obfuscation/03_reviewed'),
        ALLOWED_EXTENSIONS={'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'},
        KNOWLEDGE=os.path.join(app.instance_path, 'knowledge'),
        VECTOR_STORE=os.path.join(app.instance_path, 'knowledge/vector_store')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    directories = [
        app.config.get('UPLOADS'),
        app.config.get('WORKING'),
        app.config.get('REVIEWED'),
        app.config.get('KNOWLEDGE'),
        app.config.get('VECTOR_STORE')
    ]

    for directory in directories:
        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                app.logger.error("Error creating directory %s: %s", directory, e)

    # Define homepage route
    @app.route('/')
    def home():
        return render_template('index.html')
    
    mediator = Mediator()

    # Register Blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(create_customer_blueprint(mediator))
  
    with app.app_context():
        mediator.initialize_resources()

    from . import db
    db.init_app(app)
    return app
