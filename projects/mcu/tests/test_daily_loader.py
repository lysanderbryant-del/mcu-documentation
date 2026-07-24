"""
Tests for Daily Loader - File discovery, parsing, and database storage
"""

import pytest
from datetime import date
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from loaders.file_discovery import DailyFileDiscovery, FileDiscoveryError
from loaders.csv_parsers import ParserFactory


def test_file_discovery_formats_dates_correctly():
    """Test that date formatting produces correct patterns."""
    test_date = date(2026, 7, 22)
    discovery = DailyFileDiscovery(test_date)

    assert discovery.date_iso == '2026-07-22'
    assert discovery.date_compact == '20260722'
    assert discovery.date_underscore == '2026_07_22'
    assert discovery.month_folder == '2026-Jul'
    assert discovery.date_ddmmyyyy == '22072026'


def test_file_discovery_builds_correct_paths():
    """Test that directory paths are constructed correctly."""
    test_date = date(2026, 7, 22)
    discovery = DailyFileDiscovery(test_date)

    assert '2026-Jul' in str(discovery.bnp_processed)
    assert 'BNPFileStore' in str(discovery.bnp_processed)
    assert 'BNPCETFileStore' in str(discovery.bnpcet_processed)
    assert 'SocGenAAL' in str(discovery.socgen_dir)
    assert 'Collateral' in str(discovery.csa_dir)


def test_file_discovery_month_folder_changes_with_date():
    """Test that month folder updates correctly for different months."""
    jan_date = date(2026, 1, 15)
    jul_date = date(2026, 7, 22)
    dec_date = date(2025, 12, 31)

    jan_discovery = DailyFileDiscovery(jan_date)
    jul_discovery = DailyFileDiscovery(jul_date)
    dec_discovery = DailyFileDiscovery(dec_date)

    assert jan_discovery.month_folder == '2026-Jan'
    assert jul_discovery.month_folder == '2026-Jul'
    assert dec_discovery.month_folder == '2025-Dec'


def test_parser_factory_returns_correct_parsers():
    """Test that ParserFactory returns appropriate parser instances."""
    from loaders.csv_parsers import (
        BNPMCStatementParser,
        BNPOTEDetailParser,
        BNPJournalEntriesParser,
        BNPPnSParser,
        SocGenMarginParser,
        CSACollateralParser,
    )

    assert isinstance(ParserFactory.get_parser('bnp_cel_mc'), BNPMCStatementParser)
    assert isinstance(ParserFactory.get_parser('bnp_cet_mc'), BNPMCStatementParser)
    assert isinstance(ParserFactory.get_parser('bnp_cel_ote'), BNPOTEDetailParser)
    assert isinstance(ParserFactory.get_parser('bnp_cel_jnls'), BNPJournalEntriesParser)
    assert isinstance(ParserFactory.get_parser('bnp_cel_pns'), BNPPnSParser)
    assert isinstance(ParserFactory.get_parser('socgen'), SocGenMarginParser)
    assert isinstance(ParserFactory.get_parser('csa'), CSACollateralParser)


def test_parser_factory_raises_for_unknown_type():
    """Test that ParserFactory raises error for unknown file types."""
    with pytest.raises(ValueError, match="Unknown file type"):
        ParserFactory.get_parser('invalid_type')


def test_bnp_mc_statement_pattern_matches_expected():
    """Test that BNP MC Statement file pattern is correct."""
    test_date = date(2026, 7, 22)
    discovery = DailyFileDiscovery(test_date)

    # Expected pattern: MC_Statement_CEL U_2026-07-22_22072026_*.csv
    expected_base = 'MC_Statement_CEL U_2026-07-22_22072026_'

    # File discovery should look for this pattern
    source_file = discovery._find_bnp_mc_statement('CEL')

    assert expected_base in str(source_file.file_path)
    assert source_file.file_path.name.endswith('.csv')


def test_socgen_file_pattern_has_no_timestamp():
    """Test that SocGen file pattern uses compact date without timestamp."""
    test_date = date(2026, 7, 22)
    discovery = DailyFileDiscovery(test_date)

    # Expected: 20260722_GlobalMarginUnderlyingCurrencyReport.csv
    source_file = discovery._find_socgen_margin()

    assert '20260722_GlobalMarginUnderlyingCurrencyReport.csv' in str(source_file.file_path)
    assert '*' not in str(source_file.file_path)  # No wildcard for SocGen


def test_csa_file_uses_underscore_date_format():
    """Test that CSA file uses YYYY_MM_DD format."""
    test_date = date(2026, 7, 22)
    discovery = DailyFileDiscovery(test_date)

    # Expected: Collateral_Summary_2026_07_22_*.csv
    source_file = discovery._find_csa_collateral()

    assert 'Collateral_Summary_2026_07_22_' in str(source_file.file_path)


def test_file_discovery_returns_source_file_objects():
    """Test that file discovery returns SourceFile objects with correct attributes."""
    test_date = date(2026, 7, 22)
    discovery = DailyFileDiscovery(test_date)

    source_file = discovery._find_bnp_mc_statement('CEL')

    assert hasattr(source_file, 'file_type')
    assert hasattr(source_file, 'file_path')
    assert hasattr(source_file, 'exists')
    assert hasattr(source_file, 'size_bytes')
    assert hasattr(source_file, 'modified_time')


def test_date_formatting_works_for_edge_dates():
    """Test date formatting for edge cases (month/year boundaries)."""
    # First day of year
    jan_1 = date(2026, 1, 1)
    discovery_jan = DailyFileDiscovery(jan_1)

    assert discovery_jan.date_iso == '2026-01-01'
    assert discovery_jan.date_compact == '20260101'
    assert discovery_jan.month_folder == '2026-Jan'

    # Last day of year
    dec_31 = date(2025, 12, 31)
    discovery_dec = DailyFileDiscovery(dec_31)

    assert discovery_dec.date_iso == '2025-12-31'
    assert discovery_dec.date_compact == '20251231'
    assert discovery_dec.month_folder == '2025-Dec'


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
