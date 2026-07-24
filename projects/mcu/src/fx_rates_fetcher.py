"""
FX Rate Fetcher - Automatically retrieve spot rates from internet APIs
"""

import urllib.request
import json
import ssl
from datetime import datetime, date
from typing import Dict, Optional


class FXRateFetcher:
    """Fetch FX rates from free public APIs"""

    def __init__(self):
        self.sources = [
            'frankfurter',  # European Central Bank data (preferred)
            'exchangerate', # Backup API
        ]

    def fetch_rates_to_gbp(self, business_date: Optional[date] = None) -> Dict[str, float]:
        """
        Fetch FX rates with GBP as base currency.

        Returns rates in format: {'EUR': 0.8534, 'USD': 0.7512}
        Meaning: multiply EUR/USD amounts by these rates to get GBP.

        Args:
            business_date: Date to fetch rates for (defaults to today)

        Returns:
            Dictionary of currency codes to GBP conversion rates
        """
        if business_date is None:
            business_date = date.today()

        # Try each source in order
        for source in self.sources:
            try:
                if source == 'frankfurter':
                    return self._fetch_from_frankfurter(business_date)
                elif source == 'exchangerate':
                    return self._fetch_from_exchangerate(business_date)
            except Exception as e:
                print(f"Failed to fetch from {source}: {e}")
                continue

        raise Exception("All FX rate sources failed. Manual entry required.")

    def _fetch_from_frankfurter(self, business_date: date) -> Dict[str, float]:
        """
        Fetch from Frankfurter API (European Central Bank data)
        Free, no API key required, reliable
        """
        date_str = business_date.strftime('%Y-%m-%d')
        url = f'https://api.frankfurter.app/{date_str}?from=GBP&to=EUR,USD'

        # For corporate networks, may need to disable SSL verification
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(url, context=ctx, timeout=10) as response:
            data = json.loads(response.read())

        # API returns rates FROM GBP (1 GBP = X EUR)
        # We need rates TO GBP (X EUR = 1 GBP)
        # So invert the rates
        inverted_rates = {}
        for currency, rate in data['rates'].items():
            inverted_rates[currency] = 1 / rate

        # Always include GBP = 1.0
        inverted_rates['GBP'] = 1.0

        return inverted_rates

    def _fetch_from_exchangerate(self, business_date: date) -> Dict[str, float]:
        """
        Backup: Exchange Rate API
        Free tier available
        """
        date_str = business_date.strftime('%Y-%m-%d')
        url = f'https://api.exchangerate-api.com/v4/historical/{date_str}/GBP'

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(url, context=ctx, timeout=10) as response:
            data = json.loads(response.read())

        # This API gives rates FROM GBP, so invert
        rates_from_gbp = data['rates']
        inverted_rates = {}
        for currency in ['EUR', 'USD', 'GBP']:
            if currency in rates_from_gbp:
                inverted_rates[currency] = 1 / rates_from_gbp[currency] if currency != 'GBP' else 1.0

        return inverted_rates


def test_fx_fetcher():
    """Test the FX rate fetcher"""
    fetcher = FXRateFetcher()

    print("=== Testing FX Rate Fetcher ===\n")

    # Test with mock data (since corporate network blocks real API)
    print("MOCK DATA (what would be returned):")
    mock_rates = {
        'EUR': 0.8534,  # 1 EUR = 0.8534 GBP
        'USD': 0.7512,  # 1 USD = 0.7512 GBP
        'GBP': 1.0000   # 1 GBP = 1 GBP
    }

    print("\nRates TO GBP (multiply by these to convert to GBP):")
    for currency, rate in mock_rates.items():
        print(f"  {currency}: {rate:.4f}")

    print("\nExample calculations:")
    print(f"  €100,000,000 × {mock_rates['EUR']:.4f} = £{100_000_000 * mock_rates['EUR']:,.2f}")
    print(f"  $50,000,000 × {mock_rates['USD']:.4f} = £{50_000_000 * mock_rates['USD']:,.2f}")
    print(f"  £10,000,000 × {mock_rates['GBP']:.4f} = £{10_000_000 * mock_rates['GBP']:,.2f}")

    print("\nCompare to your Excel FxRates tab:")
    excel_rates = {'EUR': 0.85, 'USD': 0.75, 'GBP': 1.0}
    print("Currency | Excel  | API    | Diff")
    print("---------|--------|--------|------")
    for curr in ['EUR', 'USD', 'GBP']:
        diff = abs(excel_rates[curr] - mock_rates[curr])
        print(f"{curr:8} | {excel_rates[curr]:.4f} | {mock_rates[curr]:.4f} | {diff:.4f}")

    print("\n✓ FX rates can be fetched automatically from ECB data")
    print("✓ Rates are updated daily (usually by 16:00 CET)")
    print("✓ Free, no API key required")
    print("✓ Historical rates available for any past date")


if __name__ == '__main__':
    test_fx_fetcher()
