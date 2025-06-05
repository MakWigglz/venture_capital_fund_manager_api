from flask import Flask, request, jsonify
from venture_capital_fund_manager_api.config import Config
from venture_capital_fund_manager_api.instance.config import DevelopmentConfig, ProductionConfig
import os
from flasgger import Swagger
from venture_capital_fund_manager_api.extensions import db, ma, migrate, jwt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

def create_app():
    app = Flask(__name__)

    # Load configuration
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)
        app.config.from_object(Config)

     # Access SQLALCHEMY_DATABASE_URI configuration value
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print("SQLALCHEMY_DATABASE_URI:", db_uri)
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  # Initialize JWT

    # Register blueprints
    from venture_capital_fund_manager_api.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Basic route for health check
    @app.route('/')
    def health_check():
        return jsonify({"status": "API is running"}), 200

    return app  # Correct placement of return

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

