from flask import request, jsonify
from . import api_bp
from ..models import Fund
from ..schemas import FundSchema
from ..extensions import db
from sqlalchemy.exc import IntegrityError

fund_schema = FundSchema()
funds_schema = FundSchema(many=True)

@api_bp.route('/funds', methods=['POST'])
def create_fund():
    """
    Creates a new venture capital fund.
    ---
    post:
      summary: Create a new fund
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                target_size:
                  type: number
                vintage_year:
                  type: integer
      responses:
        201:
          description: Fund created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Fund'
        400:
          description: Invalid input or fund name already exists
    """
    try:
        fund = fund_schema.load(request.json)
        db.session.add(fund)
        db.session.commit()
        return jsonify(fund_schema.dump(fund)), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Fund with this name already exists or invalid data."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@api_bp.route('/funds', methods=['GET'])
def get_funds():
    """
    Retrieves a list of all venture capital funds.
    ---
    get:
      summary: Get all funds
      responses:
        200:
          description: A list of funds
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Fund'
    """
    funds = Fund.query.all()
    return jsonify(funds_schema.dump(funds)), 200

@api_bp.route('/funds/<int:fund_id>', methods=['GET'])
def get_fund(fund_id):
    """
    Retrieves a specific venture capital fund by ID.
    ---
    get:
      summary: Get a fund by ID
      parameters:
        - in: path
          name: fund_id
          schema:
            type: integer
          required: true
          description: ID of the fund to retrieve
      responses:
        200:
          description: Fund details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Fund'
        404:
          description: Fund not found
    """
    fund = Fund.query.get_or_404(fund_id)
    return jsonify(fund_schema.dump(fund)), 200