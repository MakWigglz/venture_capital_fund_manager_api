import timeit
from .app import create_app
from .extensions import db
from .models import Fund, Company, Investment, FinancialData
from datetime import date
from decimal import Decimal

def setup_data_for_benchmarking(app):
    with app.app_context():
        db.create_all()
        # Create a large number of funds, companies, investments, and financial data
        print("Setting up large dataset for benchmarking...")
        for i in range(1, 101): # 100 funds
            fund = Fund(name=f"Benchmark Fund {i}", target_size=Decimal('10000000.00'), vintage_year=2020 + (i % 5))
            db.session.add(fund)
            db.session.commit() # Commit individually for IDs

            for j in range(1, 21): # 20 investments per fund
                company = Company(name=f"Company {i}-{j}", industry="Tech", is_public=False)
                db.session.add(company)
                db.session.commit() # Commit individually for IDs

                investment = Investment(
                    fund_id=fund.id,
                    company_id=company.id,
                    investment_date=date(2021, 1, 1),
                    amount_invested=Decimal('50000.00'),
                    equity_percentage=Decimal('5.0'),
                    valuation_at_investment=Decimal('1000000.00')
                )
                db.session.add(investment)
                db.session.commit() # Commit individually for IDs

                financial_data = FinancialData(
                    company_id=company.id,
                    data_date=date.today(),
                    revenue=Decimal('1000000.00'),
                    net_income=Decimal('100000.00'),
                    valuation=Decimal('2000000.00')
                )
                db.session.add(financial_data)
        db.session.commit()
        print("Dataset setup complete.")


def benchmark_fund_metrics_calculation():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///vc_fund_benchmark.db" # Use a separate DB for benchmark
    setup_data_for_benchmarking(app) # Setup data before benchmarking

    with app.app_context():
        funds = Fund.query.all()
        times = []
        for fund in funds:
            stmt = f"from services.fund_calculations import calculate_tvpi; calculate_tvpi({fund.id})"
            # Use `timeit` to measure execution time
            # For more detailed profiling, use cProfile
            t = timeit.timeit(stmt, globals=locals(), number=1)
            times.append(t)
            print(f"Fund {fund.id} TVPI calculation took {t:.4f} seconds")

        avg_time = sum(times) / len(times)
        print(f"\nAverage TVPI calculation time: {avg_time:.4f} seconds")

if __name__ == '__main__':
    benchmark_fund_metrics_calculation()
