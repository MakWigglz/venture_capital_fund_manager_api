from venture_capital_fund_manager_api.extensions import db
from datetime import datetime

class Fund(db.Model):
    __tablename__ = 'funds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    target_size = db.Column(db.Numeric(15, 2), nullable=False)
    commited_capital = db.Column(db.Numeric(15, 2), default=0.0)
    invested_capital = db.Column(db.Numeric(15, 2), default=0.0)
    vintage_year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    investments = db.relationship('Investment', backref='fund', lazy=True)

    def __repr__(self):
        return f"<Fund {self.name}>"

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    industry = db.Column(db.String(50))
    website = db.Column(db.String(200))
    is_public = db.Column(db.Boolean, default=False)
    ticker_symbol = db.Column(db.String(10))  # For public companies
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    investments = db.relationship('Investment', backref='company', lazy=True)
    financial_data = db.relationship('FinancialData', backref='company', lazy=True)

    def __repr__(self):
        return f"<Company {self.name}>"

class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('funds.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    investment_date = db.Column(db.Date, nullable=False)
    amount_invested = db.Column(db.Numeric(15, 2), nullable=False)
    equity_percentage = db.Column(db.Numeric(5, 2))  # e.g., 10.5 for 10.5%
    valuation_at_investment = db.Column(db.Numeric(15, 2))
    exit_date = db.Column(db.Date)
    exit_amount = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(20), default='Active', nullable=False)  # e.g., Active, Exited, Write-off
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Investment {self.fund_id} in {self.company_id} amount {self.amount_invested}>"

class FinancialData(db.Model):
    __tablename__ = 'financial_data'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    data_date = db.Column(db.Date, nullable=False)
    revenue = db.Column(db.Numeric(15, 2))
    net_income = db.Column(db.Numeric(15, 2))
    valuation = db.Column(db.Numeric(15, 2))  # Current valuation for private companies
    stock_price = db.Column(db.Numeric(10, 4))  # For public companies
    # Add more financial metrics as needed (e.g., EBITDA, cash flow, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('company_id', 'data_date', name='_company_data_date_uc'),)

    def __repr__(self):
        return f"<FinancialData {self.company_id} on {self.data_date}>"
