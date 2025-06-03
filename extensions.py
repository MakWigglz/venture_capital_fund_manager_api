# In venture_capital_fund_manager_api/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager # If used

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
jwt = JWTManager() # If used