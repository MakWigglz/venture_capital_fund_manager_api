from .extensions import ma
from .models import Fund, Company, Investment, FinancialData
from marshmallow import fields

class FundSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Fund
        load_instance = True
        include_relationships = True # Include related investments (optional, can be controlled)

    investments = fields.List(fields.Nested(lambda: InvestmentSchema(exclude=("fund",)))) # Avoid circular reference

class CompanySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        load_instance = True
        include_relationships = True

    investments = fields.List(fields.Nested(lambda: InvestmentSchema(exclude=("company",))))
    financial_data = fields.List(fields.Nested(lambda: FinancialDataSchema(exclude=("company",))))

class InvestmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Investment
        load_instance = True
        include_relationships = True

    fund = fields.Nested(FundSchema(only=("id", "name"))) # Only show id and name of fund
    company = fields.Nested(CompanySchema(only=("id", "name", "ticker_symbol")))

class FinancialDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FinancialData
        load_instance = True
        include_relationships = True

    company = fields.Nested(CompanySchema(only=("id", "name", "ticker_symbol")))
