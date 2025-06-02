from flask import Flask, request, jsonify
from config import Config
from instance.config import DevelopmentConfig, ProductionConfig
import os

def create_app():
	app = Flask(__name__)
	# load configuration
	env = os.environ.get('FLASK_ENV', 'development')
	if env == 'development':
		app.config.from_object(DevelopmentConfig)
	else:
		app.config.from_object(ProductionConfig)
	app.config.from_object(Config)
	# Initialize extensions here
	from .extensions import db, ma, migrate
	db.init_app(app)
	ma.init_app(app)
	migrate.init_app(app, db)
	# register blueprints
	from .api import api_bp
	app.register_blueprint(api_bp, url_prefix='/api')

	# Basic route for health check
	@app.route('/')
	def health_check():
		return jsonify({"status": "API is running"}), 200
	return app
if __name__ == '__main__':
	app = create_app()
	app.run(debug=True)
