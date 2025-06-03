from flask import Flask, request, jsonify
from venture_capital_fund_manager_api.config import Config
from venture_capital_fund_manager_api.instance.config import DevelopmentConfig, ProductionConfig
import os
from flasgger import Swagger
from venture_capital_fund_manager_api.extensions import db, ma, migrate, jwt

def create_app():
    app = Flask(__name__)

    # Load configuration
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)
    app.config.from_object(Config)

    # Initialize extensions here
    from venture_capital_fund_manager_api.extensions import db, ma, migrate, jwt
    from venture_capital_fund_manager_api.api import api_bp

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  # Initialize JWT

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    # Basic route for health check
    @app.route('/')
    def health_check():
        return jsonify({"status": "API is running"}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
