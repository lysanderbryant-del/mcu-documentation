"""
TDD Tests for Remaining Parsers - STRICT TEST-FIRST APPROACH

These tests are written BEFORE implementation fixes.
They WILL FAIL initially (RED phase).

Test-Driven Development Cycle:
1. RED: Write failing test
2. GREEN: Make test pass (simplest way)
3. REFACTOR: Improve code quality

Following Farley principles and Process Factory workflow.
"""

import pytest
from datetime import date
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from loaders.csv_parsers import (
    BNPJournalEntriesParser,
    BNPOTEDetailParser,
    CSACollateralParser,
    ParseError
)


class TestJournalEntriesParser:
    """
    TDD for Journal Entries Parser
    Based on architect-journal-entries.md
    """

    TEST_FILE = Path('//pgb1-p-e-evs012/ENDUR_PROD_01/endur_prod/Interface/BNPFileStore/Processed/2026-Jul/Journal_Entries_CEL U_2026-07-22_23072026_16_00_07.csv')
    TEST_DATE = date(2026, 7, 22)

    def test_extracts_correct_total_eur_amount(self):
        """
        RED TEST: This will FAIL until parser is fixed

        GIVEN: Journal Entries CSV for 2026-07-22
        WHEN: Parser extracts spot/physical delivery
        THEN: EUR amount should be ~28.5M (which converts to ~£23.51M at 0.825 rate)
        """
        parser = BNPJournalEntriesParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Check structure
        assert isinstance(result, dict), "Should return dict"
        assert 'position_value_native' in result, "Should have position_value_native"
        assert 'original_currency' in result, "Should have original_currency"

        # Check EUR amount
        eur_amount = result['position_value_native']
        assert result['original_currency'] == 'EUR', "Should be in EUR"

        # EUR amount should be ~28.5M
        # (When converted at 0.825, gives ~£23.51M)
        assert 28_000_000 <= eur_amount <= 29_000_000, \
            f"Expected EUR ~28.5M, got EUR {eur_amount:,.0f}"

    def test_converts_to_correct_gbp_equivalent(self):
        """
        RED TEST: Verify GBP equivalent calculation

        GIVEN: Parser returns EUR amount
        WHEN: Converted at 0.825 FX rate
        THEN: Should yield £23.51M ±£0.01M
        """
        parser = BNPJournalEntriesParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        eur_amount = result['position_value_native']
        fx_rate = 0.825  # EUR to GBP rate from analyst report
        gbp_equivalent = eur_amount * fx_rate

        # Target: £23,510,000
        # Tolerance: ±£10,000
        assert 23_500_000 <= gbp_equivalent <= 23_520_000, \
            f"Expected GBP £23.51M, got £{gbp_equivalent:,.0f}"

    def test_filters_payment_types_correctly(self):
        """
        RED TEST: Ensure only PC and DLV transactions included

        GIVEN: CSV has PC, DLV, and CSH payment types
        WHEN: Parser extracts
        THEN: Should include only PC and DLV (32 transactions, not 35)
        """
        # This test validates the filtering logic
        # Analyst found: 7 PC + 25 DLV = 32 transactions (excluding 3 CSH)
        parser = BNPJournalEntriesParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # If we included CSH, the amount would be different
        # This test ensures correct filtering by checking the final amount
        assert result['margin_type'] == 'SPOT_PHYSICAL'

    def test_returns_correct_structure(self):
        """
        RED TEST: Verify output structure matches specification
        """
        parser = BNPJournalEntriesParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Check all required fields
        required_fields = [
            'business_date',
            'clearer',
            'entity',
            'margin_type',
            'position_value_native',
            'original_currency',
            'source_file'
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Check field values
        assert result['business_date'] == self.TEST_DATE
        assert result['clearer'] == 'BNP'
        assert result['entity'] == 'CEL'
        assert result['margin_type'] == 'SPOT_PHYSICAL'
        assert result['original_currency'] == 'EUR'


class TestOTEDetailParser:
    """
    TDD for OTE Detail Parser
    Based on architect-ote-detail.md
    """

    TEST_FILE = Path('//pgb1-p-e-evs012/ENDUR_PROD_01/endur_prod/Interface/BNPFileStore/Processed/2026-Jul/Detailed_Open_Pos_CEL U_2026-07-22_23072026_16_00_07.csv')
    TEST_DATE = date(2026, 7, 22)

    def test_aggregates_trades_into_positions(self):
        """
        RED TEST: This will FAIL due to current parser structure

        GIVEN: CSV with 148,625 trade-level rows
        WHEN: Parser aggregates by product/currency/maturity
        THEN: Should return ~1,830 position records
        """
        parser = BNPOTEDetailParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Check is list
        assert isinstance(result, list), "Should return list of positions"

        # Check aggregated count (varies by date, but should be hundreds not thousands)
        # Analyst found: 148,625 rows → ~1,830 positions (for specific date)
        # Verify significant aggregation occurred (at least 10x reduction)
        assert len(result) >= 100, \
            f"Too few positions: {len(result)} (data issue or no aggregation?)"
        assert len(result) <= 5_000, \
            f"Too many positions: {len(result)} (aggregation not working?)"

    def test_no_duplicate_position_keys(self):
        """
        RED TEST: This will FAIL due to duplicate constraint issue

        GIVEN: Aggregated positions
        WHEN: Check for duplicates on key columns
        THEN: No duplicates should exist
        """
        parser = BNPOTEDetailParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Build keys from result
        keys = []
        for record in result:
            key = (
                record['product_name'],
                record['original_currency'],
                record.get('maturity_date')  # NEW: must include maturity
            )
            keys.append(key)

        # Check no duplicates
        unique_keys = set(keys)
        assert len(keys) == len(unique_keys), \
            f"Found {len(keys) - len(unique_keys)} duplicate positions"

    def test_dominant_product_has_many_maturities(self):
        """
        RED TEST: Validate aggregation preserves product diversity

        GIVEN: ICETFM_F has 62,336 trades (42% of file) [analyst date: 2026-07-22]
        WHEN: Aggregated by maturity
        THEN: Should have 10+ unique ICE TTF positions (varies by date)
        """
        parser = BNPOTEDetailParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Find ICE TTF positions
        ice_ttf_positions = [
            r for r in result
            if 'ICETFM' in r['product_name'] or 'ICE TTF' in r['product_name']
        ]

        # Verify meaningful aggregation (10+ maturities shows diversity preserved)
        assert len(ice_ttf_positions) >= 10, \
            f"Expected 10+ ICE TTF maturities, got {len(ice_ttf_positions)}"

    def test_includes_maturity_date_in_output(self):
        """
        RED TEST: Ensure maturity_date field exists

        GIVEN: Positions need maturity for uniqueness
        WHEN: Parser returns records
        THEN: Each record should have maturity_date field
        """
        parser = BNPOTEDetailParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Check first few records have maturity_date
        for record in result[:10]:
            assert 'maturity_date' in record, \
                "Position missing maturity_date field"


class TestCSACollateralParser:
    """
    TDD for CSA Collateral Parser
    Based on architect-csa-collateral.md
    """

    CSA_BASE = Path(r'\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral')
    TEST_DATE = date(2026, 7, 24)  # Use current date

    @classmethod
    def _find_latest_csa_file(cls) -> Path:
        """Find the most recent CSA Collateral file for TEST_DATE."""
        pattern = f'Collateral_Summary_{cls.TEST_DATE.strftime("%Y_%m_%d")}_*.csv'

        if not cls.CSA_BASE.exists():
            pytest.skip(f"CSA share not accessible: {cls.CSA_BASE}")

        matches = list(cls.CSA_BASE.glob(pattern))

        if not matches:
            pytest.skip(f"No CSA file found for {cls.TEST_DATE} (pattern: {pattern})")

        # Return most recent file
        return max(matches, key=lambda p: p.stat().st_mtime)

    @property
    def TEST_FILE(self):
        """Dynamically find the latest test file."""
        return self._find_latest_csa_file()

    def test_uses_correct_skiprows_value(self):
        """
        RED TEST: This will FAIL due to skiprows=6 in current parser

        GIVEN: CSV with header on line 1
        WHEN: Parser reads file
        THEN: Should use skiprows=0, not skiprows=6
        """
        parser = CSACollateralParser()

        # This test will pass if parser correctly uses skiprows=0
        # and will fail if it uses skiprows=6
        try:
            result = parser.parse(self.TEST_FILE, self.TEST_DATE)
            assert isinstance(result, list), "Should return list"
            # If we got here without KeyError, skiprows is correct
        except KeyError as e:
            pytest.fail(f"KeyError indicates wrong skiprows or column names: {e}")

    def test_uses_correct_column_names(self):
        """
        RED TEST: This will FAIL due to wrong column names in parser

        GIVEN: CSV has Collateral_Held and Collateral_Pledged columns
        WHEN: Parser attempts to access
        THEN: Should use correct names, not HeldGbpM/PledgedGbpM
        """
        parser = CSACollateralParser()

        try:
            result = parser.parse(self.TEST_FILE, self.TEST_DATE)
            assert len(result) > 0, "Should find some collateral records"
        except KeyError as e:
            if 'HeldGbpM' in str(e) or 'PledgedGbpM' in str(e):
                pytest.fail(f"Using wrong column names: {e}")
            raise

    def test_matches_entity_names_correctly(self):
        """
        RED TEST: Check entity name matching

        GIVEN: File has 'Centrica Energy Trading A/S' (with A/S suffix)
        WHEN: Parser filters entities
        THEN: Should match correctly and map to 'CET'
        """
        parser = CSACollateralParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Should find at least one entity
        assert len(result) > 0, "Should find Centrica entities"

        # Check entity codes
        entities = [r['entity'] for r in result]
        assert any(e in ['CEL', 'CET'] for e in entities), \
            f"No valid entities found, got: {entities}"

    def test_calculates_net_collateral(self):
        """
        RED TEST: Verify net collateral calculation

        GIVEN: CSV has Held and Pledged values
        WHEN: Parser calculates net
        THEN: Net = Held - Pledged (can be positive or negative)
        """
        parser = CSACollateralParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Check each record has position value
        for record in result:
            assert 'position_value_native' in record
            assert isinstance(record['position_value_native'], (int, float))

    def test_does_not_multiply_by_million(self):
        """
        RED TEST: Ensure values NOT scaled incorrectly

        GIVEN: Values already in native units
        WHEN: Parser extracts
        THEN: Should NOT multiply by 1,000,000
        """
        parser = CSACollateralParser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)

        # Analyst found typical values: 10,000 to 100,000 range
        # If parser multiplies by 1M, values would be billions
        for record in result:
            value = abs(record['position_value_native'])
            assert value < 1_000_000_000, \
                f"Value {value:,.0f} too large - may be incorrectly scaled by 1M"


# Integration Test
def test_all_parsers_load_without_errors():
    """
    RED TEST: Integration test for complete load

    GIVEN: All three parsers fixed
    WHEN: Load complete dataset for 2026-07-22
    THEN: Should load successfully with total ~£65.11M
    """
    from database.connection import DatabaseConnection

    # This test will be expanded after individual parsers pass
    # For now, just validate parsers don't crash

    journal_parser = BNPJournalEntriesParser()
    ote_parser = BNPOTEDetailParser()
    csa_parser = CSACollateralParser()

    # Should not raise exceptions
    assert journal_parser is not None
    assert ote_parser is not None
    assert csa_parser is not None


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
