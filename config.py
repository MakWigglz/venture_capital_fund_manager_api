import os
class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'a very secret and hard to guess string'  # Change in production
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	