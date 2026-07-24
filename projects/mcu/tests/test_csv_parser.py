"""
Test Suite: CSV Parser Implementation
Increment 3: CSV Parser Implementation

Tests verify that:
- CSV files are parsed correctly into MarginPosition objects
- Invalid CSV formats are handled gracefully
- Missing required fields raise appropriate errors
- Extra columns are ignored
"""

import pytest
from datetime import date
from pathlib import Path


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    csv_content = """business_date,clearer,margin_type,entity,counterparty,currency,position_value
2026-07-23,BNP,INITIAL_MARGIN,CEL,,GBP,1000000.00
2026-07-23,BNP,DAILY_SETTLEMENT,CEL,,GBP,50000.00
2026-07-23,SOCGEN,INITIAL_MARGIN,CEL,,GBP,750000.00
"""
    csv_file = tmp_path / "sample_margin.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)


def test_parse_valid_csv_file(sample_csv_file):
    """
    GIVEN: A CSV file with well-formed margin data
    WHEN: The CSV parser processes the file
    THEN: All rows are converted to MarginPosition objects with correct values
    """
    from src.ingestion.csv_parser import CSVParser

    parser = CSVParser()
    positions = parser.parse(sample_csv_file, date(2026, 7, 23))

    assert len(positions) == 3
    assert positions[0].clearer == 'BNP'
    assert positions[0].margin_type == 'INITIAL_MARGIN'
    assert positions[0].position_value == 1000000.00
    assert positions[1].position_value == 50000.00
    assert positions[2].clearer == 'SOCGEN'


def test_csv_parser_can_parse_method(sample_csv_file):
    """
    GIVEN: A CSV file
    WHEN: Calling can_parse()
    THEN: Returns True for .csv files
    """
    from src.ingestion.csv_parser import CSVParser

    parser = CSVParser()
    assert parser.can_parse(sample_csv_file) is True
    assert parser.can_parse("file.xlsx") is False
    assert parser.can_parse("file.pdf") is False


def test_csv_parser_version(sample_csv_file):
    """
    GIVEN: A CSV parser instance
    WHEN: Calling get_version()
    THEN: Returns a version string
    """
    from src.ingestion.csv_parser import CSVParser

    parser = CSVParser()
    version = parser.get_version()

    assert isinstance(version, str)
    assert len(version) > 0


def test_csv_missing_required_field(tmp_path):
    """
    GIVEN: A CSV file missing a required column (position_value)
    WHEN: The CSV parser processes the file
    THEN: A parse error is raised with descriptive message
    """
    from src.ingestion.csv_parser import CSVParser

    csv_content = """business_date,clearer,margin_type,entity,currency
2026-07-23,BNP,INITIAL_MARGIN,CEL,GBP
"""
    csv_file = tmp_path / "missing_field.csv"
    csv_file.write_text(csv_content)

    parser = CSVParser()

    with pytest.raises(Exception) as exc_info:
        parser.parse(str(csv_file), date(2026, 7, 23))

    assert 'position_value' in str(exc_info.value).lower() or 'required' in str(exc_info.value).lower()


def test_csv_invalid_numeric_value(tmp_path):
    """
    GIVEN: A CSV file with non-numeric data in position_value column
    WHEN: The CSV parser processes the file
    THEN: A parse error is raised
    """
    from src.ingestion.csv_parser import CSVParser

    csv_content = """business_date,clearer,margin_type,entity,counterparty,currency,position_value
2026-07-23,BNP,INITIAL_MARGIN,CEL,,GBP,NOT_A_NUMBER
"""
    csv_file = tmp_path / "invalid_numeric.csv"
    csv_file.write_text(csv_content)

    parser = CSVParser()

    with pytest.raises(Exception) as exc_info:
        parser.parse(str(csv_file), date(2026, 7, 23))

    assert 'numeric' in str(exc_info.value).lower() or 'value' in str(exc_info.value).lower()


def test_csv_with_extra_columns(tmp_path):
    """
    GIVEN: A CSV file with columns not in the schema
    WHEN: The CSV parser processes the file
    THEN: The file is parsed successfully and extra columns are ignored
    """
    from src.ingestion.csv_parser import CSVParser

    csv_content = """business_date,clearer,margin_type,entity,counterparty,currency,position_value,extra_column1,extra_column2
2026-07-23,BNP,INITIAL_MARGIN,CEL,,GBP,1000000.00,ignored,also_ignored
"""
    csv_file = tmp_path / "extra_columns.csv"
    csv_file.write_text(csv_content)

    parser = CSVParser()
    positions = parser.parse(str(csv_file), date(2026, 7, 23))

    assert len(positions) == 1
    assert positions[0].position_value == 1000000.00


def test_csv_empty_file(tmp_path):
    """
    GIVEN: A CSV file with only headers, no data rows
    WHEN: The CSV parser processes the file
    THEN: An empty list is returned
    """
    from src.ingestion.csv_parser import CSVParser

    csv_content = """business_date,clearer,margin_type,entity,counterparty,currency,position_value
"""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text(csv_content)

    parser = CSVParser()
    positions = parser.parse(str(csv_file), date(2026, 7, 23))

    assert len(positions) == 0


def test_csv_with_negative_values(tmp_path):
    """
    GIVEN: A CSV file with negative position values
    WHEN: The CSV parser processes the file
    THEN: Negative values are preserved
    """
    from src.ingestion.csv_parser import CSVParser

    csv_content = """business_date,clearer,margin_type,entity,counterparty,currency,position_value
2026-07-23,BNP,DAILY_SETTLEMENT,CEL,,GBP,-50000.00
"""
    csv_file = tmp_path / "negative.csv"
    csv_file.write_text(csv_content)

    parser = CSVParser()
    positions = parser.parse(str(csv_file), date(2026, 7, 23))

    assert len(positions) == 1
    assert positions[0].position_value == -50000.00
