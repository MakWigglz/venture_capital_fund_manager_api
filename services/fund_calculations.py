from ..models import Fund, Investment, FinancialData
from ..extensions import db
from datetime import datetime, date
from decimal import Decimal

# Helper to get current valuation of an investment
def get_current_investment_valuation(investment: Investment) -> Decimal:
    """Calculates the current valuation of a specific investment."""
    latest_financial_data = FinancialData.query.filter_by(company_id=investment.company_id)\
                                                .order_by(FinancialData.data_date.desc())\
                                                .first()
    if latest_financial_data and latest_financial_data.valuation:
        # Assuming equity_percentage is stored as a decimal (e.g., 0.1 for 10%)
        # Or if it's 10.5 for 10.5%, divide by 100 first
        equity_decimal = investment.equity_percentage / 100 if investment.equity_percentage else Decimal('0')
        return latest_financial_data.valuation * equity_decimal
    elif investment.exit_amount:
        return investment.exit_amount # If exited, the exit amount is the final valuation
    return Decimal('0') # Default to 0 if no current data or exited without amount

# Example: Total Value to Paid-in (TVPI)
def calculate_tvpi(fund_id: int) -> Decimal:
    """
    Calculates the Total Value to Paid-in (TVPI) for a given fund.
    TVPI = (Distributions + Remaining Value) / Paid-in Capital
    """
    fund = Fund.query.get_or_404(fund_id)
    total_paid_in = sum(inv.amount_invested for inv in fund.investments)
    if total_paid_in == Decimal('0'):
        return Decimal('0')

    total_distributions = sum(inv.exit_amount for inv in fund.investments if inv.exit_amount)
    total_remaining_value = sum(get_current_investment_valuation(inv) for inv in fund.investments if inv.status == 'Active')

    tvpi = (total_distributions + total_remaining_value) / total_paid_in
    return round(tvpi, 4)

# Example: Distributions to Paid-in (DPI)
def calculate_dpi(fund_id: int) -> Decimal:
    """
    Calculates the Distributions to Paid-in (DPI) for a given fund.
    DPI = Distributions / Paid-in Capital
    """
    fund = Fund.query.get_or_404(fund_id)
    total_paid_in = sum(inv.amount_invested for inv in fund.investments)
    if total_paid_in == Decimal('0'):
        return Decimal('0')

    total_distributions = sum(inv.exit_amount for inv in fund.investments if inv.exit_amount)
    dpi = total_distributions / total_paid_in
    return round(dpi, 4)

# Example: Remaining Value to Paid-in (RVPI)
def calculate_rvpi(fund_id: int) -> Decimal:
    """
    Calculates the Remaining Value to Paid-in (RVPI) for a given fund.
    RVPI = Remaining Value / Paid-in Capital
    """
    fund = Fund.query.get_or_404(fund_id)
    total_paid_in = sum(inv.amount_invested for inv in fund.investments)
    if total_paid_in == Decimal('0'):
        return Decimal('0')

    total_remaining_value = sum(get_current_investment_valuation(inv) for inv in fund.investments if inv.status == 'Active')
    rvpi = total_remaining_value / total_paid_in
    return round(rvpi, 4)

# TODO: Implement more complex calculations like IRR (requires a more sophisticated library or custom algo)
# You'd need to use a financial library like numpy_financial for XIRR/IRR.
# pip install numpy-financial

# Example API endpoint for fund metrics
@api_bp.route('/funds/<int:fund_id>/metrics', methods=['GET'])
def get_fund_metrics(fund_id):
    """
    Retrieves key performance metrics for a specific fund.
    ---
    get:
      summary: Get fund performance metrics
      parameters:
        - in: path
          name: fund_id
          schema:
            type: integer
          required: true
          description: ID of the fund
      responses:
        200:
          description: Fund metrics
          content:
            application/json:
              schema:
                type: object
                properties:
                  tvpi:
                    type: number
                  dpi:
                    type: number
                  rvpi:
                    type: number
                  # ... other metrics
        404:
          description: Fund not found
    """
    fund = Fund.query.get_or_404(fund_id)
    metrics = {
        "tvpi": calculate_tvpi(fund.id),
        "dpi": calculate_dpi(fund.id),
        "rvpi": calculate_rvpi(fund.id),
        # Add more metrics here
    }
    return jsonify(metrics), 200