"""
Shared test fixtures and configuration for pytest.

This file contains fixtures that are available to all test modules.
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def fixtures_dir():
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_business_date():
    """Provide a standard business date for testing."""
    return "2026-07-23"


@pytest.fixture
def sample_margin_positions():
    """Provide sample margin position data for testing."""
    return [
        {
            'business_date': '2026-07-23',
            'clearer': 'BNP',
            'margin_type': 'INITIAL_MARGIN',
            'entity': 'CEL',
            'counterparty': None,
            'currency': 'GBP',
            'position_value': 1000000.00
        },
        {
            'business_date': '2026-07-23',
            'clearer': 'BNP',
            'margin_type': 'DAILY_SETTLEMENT',
            'entity': 'CEL',
            'counterparty': None,
            'currency': 'GBP',
            'position_value': 50000.00
        },
        {
            'business_date': '2026-07-23',
            'clearer': 'SOCGEN',
            'margin_type': 'INITIAL_MARGIN',
            'entity': 'CEL',
            'counterparty': None,
            'currency': 'GBP',
            'position_value': 750000.00
        },
        {
            'business_date': '2026-07-23',
            'clearer': 'BNP',
            'margin_type': 'CSA',
            'entity': 'CEL',
            'counterparty': 'COUNTERPARTY_A',
            'currency': 'GBP',
            'position_value': 200000.00
        }
    ]
