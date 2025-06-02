import os
class DevelopmentConfig:
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
	            "sqlite:///vc_fund_dev.db"
	DEBUG = True

class ProductionConfig:
	SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL')
	DEBUG = False
