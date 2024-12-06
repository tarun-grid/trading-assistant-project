class ScanCommand:
    def __init__(self, market_data):
        self.market_data = market_data

    def execute(self, params):
        """Execute market scan with parameters"""
        print("🔍 Scanning markets...")
        
        # Get market overview data
        overview_data = self.market_data.get_market_overview(params.get('timeframe', '1d'))
        
        print("\n📊 Market Scan Results:")
        print("=" * 60)
        print("Filtering criteria:")
        if 'RSI' in params.get('conditions', {}):
            rsi_cond = params['conditions']['RSI']
            print(f"• RSI {rsi_cond['operator']} {rsi_cond['value']}")
        if 'volume' in params.get('conditions', {}):
            vol_cond = params['conditions']['volume']
            print(f"• Volume {vol_cond['operator']} {vol_cond['value']}")
        print(f"• Price range: ${params['filters']['price_min']} - ${params['filters']['price_max']}")
        print("-" * 60)

        print("\nCurrent Market Data:")
        print("-" * 60)
        matching_stocks = []
        
        for index, row in overview_data.iterrows():
            print(f"\n{index}: {row['Name']}")
            print(f"Price: ${row['Price']:.2f}")
            print(f"RSI: {row['RSI']:.2f}")
            print(f"Volume: {row['Volume']:,.0f}")
            
            matches = True
            # Check and report why it doesn't match
            if row['RSI'] >= params['conditions']['RSI']['value']:
                print("❌ RSI too high")
                matches = False
                
            volume_threshold = self._parse_volume(params['conditions']['volume']['value'])
            if row['Volume'] <= volume_threshold:
                print("❌ Volume too low")
                matches = False
                
            if row['Price'] < params['filters']['price_min'] or row['Price'] > params['filters']['price_max']:
                print("❌ Price out of range")
                matches = False
                
            if matches:
                print("✅ Matches all criteria!")
                matching_stocks.append(row)
        
        print("\nMatching Stocks Summary:")
        print("=" * 60)
        if not matching_stocks:
            print("❌ No stocks match all criteria")
        else:
            for stock in matching_stocks:
                print(f"\n{stock['Symbol']}: {stock['Name']}")
                print(f"Price: ${stock['Price']:.2f}")
                print(f"RSI: {stock['RSI']:.2f}")
                print(f"Volume: {stock['Volume']:,.0f}")

    def _parse_volume(self, volume_str: str) -> float:
        """Parse volume string like '1M' to actual number"""
        multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}
        unit = volume_str[-1].upper()
        value = float(volume_str[:-1])
        return value * multipliers.get(unit, 1)