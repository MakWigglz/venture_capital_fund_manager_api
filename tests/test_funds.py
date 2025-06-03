import pytest
from app import create_app
from extensions import db
from models import Fund, Company, Investment, FinancialData
from datetime import date
from decimal import Decimal

@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:" # Use in-memory SQLite for tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_create_fund(test_client):
    response = test_client.post('/api/funds', json={
        "name": "Fund Alpha",
        "target_size": 100000000.00,
        "vintage_year": 2022
    })
    assert response.status_code == 201
    data = response.json
    assert data['name'] == "Fund Alpha"
    assert Fund.query.filter_by(name="Fund Alpha").first() is not None

def test_get_funds(test_client):
    test_client.post('/api/funds', json={
        "name": "Fund Beta",
        "target_size": 50000000.00,
        "vintage_year": 2023
    })
    response = test_client.get('/api/funds')
    assert response.status_code == 200
    data = response.json
    assert len(data) >= 2 # Assuming Fund Alpha was created in previous test

def test_calculate_tvpi_no_investments(test_client):
    response = test_client.post('/api/funds', json={
        "name": "Empty Fund",
        "target_size": 1000000.00,
        "vintage_year": 2024
    })
    fund_id = response.json['id']
    response = test_client.get(f'/api/funds/{fund_id}/metrics')
    assert response.status_code == 200
    assert response.json['tvpi'] == 0.0

def test_calculate_tvpi_with_investments(test_client):
    # Setup a fund, company, and investment
    fund_resp = test_client.post('/api/funds', json={"name": "Perf Fund", "target_size": 1000000, "vintage_year": 2020})
    fund_id = fund_resp.json['id']

    company_resp = test_client.post('/api/companies', json={"name": "Startup X", "industry": "Tech"})
    company_id = company_resp.json['id']

    test_client.post('/api/investments', json={
        "fund_id": fund_id,
        "company_id": company_id,
        "investment_date": "2021-01-01",
        "amount_invested": 100000.00,
        "equity_percentage": 10.0,
        "valuation_at_investment": 1000000.00
    })

    # Add financial data for valuation
    test_client.post(f'/api/companies/{company_id}/financial_data', json={
        "data_date": str(date.today()),
        "valuation": 2000000.00 # Company is now worth 2M
    })

    # Recalculate metrics
    metrics_resp = test_client.get(f'/api/funds/{fund_id}/metrics')
    assert metrics_resp.status_code == 200
    # Investment was 100k for 10% of 1M. Now company is 2M, so 10% is 200k.
    # TVPI = (0 (distributions) + 200000 (remaining value)) / 100000 (paid-in) = 2.0
    assert metrics_resp.json['tvpi'] == pytest.approx(2.0)
    assert metrics_resp.json['rvpi'] == pytest.approx(2.0)
    assert metrics_resp.json['dpi'] == pytest.approx(0.0)