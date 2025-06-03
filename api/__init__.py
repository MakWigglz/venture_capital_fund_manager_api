# venture_capital_fund_manager_api/api/__init__.py

from flask import Blueprint

api_bp = Blueprint('api', __name__)

# You would typically define your routes here or import them from other files
# For example:
# @api_bp.route('/test')
# def test_api():
#     return "Hello from API Blueprint!"

# If you have separate files like api/funds.py for routes, you'd import them here:
# from . import funds # if funds.py is directly in the 'api' folder