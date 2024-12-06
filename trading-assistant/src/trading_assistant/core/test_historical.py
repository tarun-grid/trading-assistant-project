# test_historical.py

from market_data import MarketData
import pandas as pd
from datetime import datetime

def test_max_historical():
    md = MarketData()
    symbol = 'AAPL'
    
    # Test maximum historical daily data
    print("\n=== Testing Maximum Historical Data ===")
    data = md.fetch_data(symbol, period='max', interval='1d')
    
    if data is not None:
        years = (data.index[-1] - data.index[0]).days / 365.25
        print(f"\nHistorical Data Range:")
        print(f"Start Date: {data.index[0].strftime('%Y-%m-%d')}")
        print(f"End Date: {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"Total Years: {years:.2f}")
        print(f"Total Trading Days: {len(data)}")
        
        # Sample some major historical events
        print("\nSample Historical Prices:")
        for year in [2008, 2020, 2022, 2024]:
            year_data = data[data.index.year == year]
            if not year_data.empty:
                print(f"\n{year}:")
                print(f"High: ${year_data['High'].max():.2f}")
                print(f"Low: ${year_data['Low'].min():.2f}")

if __name__ == "__main__":
    test_max_historical()