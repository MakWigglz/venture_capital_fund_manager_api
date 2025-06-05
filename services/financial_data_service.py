import requests
from .models import Company, FinancialData
from extensions import db
from datetime import date
import os

# Using a mock API for demonstration. In real world, this would be Alpha Vantage, Bloomberg, etc.
MOCK_FINANCIAL_API_BASE_URL = "https://api.mockfinancialdata.com/v1" # Replace with your actual API

# A more robust error handling and retry mechanism would be added for production
def fetch_and_store_financial_data(company_id, data_date=None):
    company = Company.query.get(company_id)
    if not company:
        raise ValueError(f"Company with ID {company_id} not found.")

    if data_date is None:
        data_date = date.today()

    # Check if data for this date already exists to avoid duplicates
    existing_data = FinancialData.query.filter_by(company_id=company.id, data_date=data_date).first()
    if existing_data:
        print(f"Financial data for {company.name} on {data_date} already exists. Updating...")
        # You might update existing data or skip, depending on your business logic

    try:
        if company.is_public and company.ticker_symbol:
            # Example for a public company using a hypothetical stock API
            # In a real scenario, you'd use Alpha Vantage or similar
            response = requests.get(f"{MOCK_FINANCIAL_API_BASE_URL}/stocks/{company.ticker_symbol}",
                                    params={'date': data_date.isoformat()})
            response.raise_for_status()
            data = response.json()
            # Assuming the mock API returns 'close_price' for stock_price
            stock_price = data.get('close_price')
            revenue = data.get('revenue')
            net_income = data.get('net_income')
            valuation = data.get('market_cap') # Market cap can be considered valuation for public companies
        else:
            # For private companies, mock or use internal valuation data
            # This would likely come from an internal valuation model or manual input
            # For demonstration, let's mock it
            response = requests.get(f"{MOCK_FINANCIAL_API_BASE_URL}/private_company_data/{company.id}",
                                    params={'date': data_date.isoformat()})
            response.raise_for_status()
            data = response.json()
            stock_price = None # Not applicable for private
            revenue = data.get('revenue')
            net_income = data.get('net_income')
            valuation = data.get('valuation') # For private companies

        if existing_data:
            existing_data.revenue = revenue
            existing_data.net_income = net_income
            existing_data.valuation = valuation
            existing_data.stock_price = stock_price
        else:
            financial_data_entry = FinancialData(
                company_id=company.id,
                data_date=data_date,
                revenue=revenue,
                net_income=net_income,
                valuation=valuation,
                stock_price=stock_price
            )
            db.session.add(financial_data_entry)

        db.session.commit()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {company.name}: {e}")
        db.session.rollback()
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        db.session.rollback()
        return False

# You would expose an endpoint to trigger this, or run it as a scheduled task
@api_bp.route('/companies/<int:company_id>/fetch_financial_data', methods=['POST'])
def trigger_financial_data_fetch(company_id):
    """
    Triggers fetching and storing financial data for a specific company.
    ---
    post:
      summary: Fetch and store financial data
      parameters:
        - in: path
          name: company_id
          schema:
            type: integer
          required: true
          description: ID of the company
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                date:
                  type: string
                  format: date
                  description: Optional date for which to fetch data (YYYY-MM-DD)
      responses:
        200:
          description: Data fetched successfully
        404:
          description: Company not found
        500:
          description: Error fetching data
    """
    data_date_str = request.json.get('date')
    data_date = None
    if data_date_str:
        try:
            data_date = datetime.strptime(data_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    try:
        success = fetch_and_store_financial_data(company_id, data_date)
        if success:
            return jsonify({"message": "Financial data fetched and stored successfully."}), 200
        else:
            return jsonify({"error": "Failed to fetch and store financial data."}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
