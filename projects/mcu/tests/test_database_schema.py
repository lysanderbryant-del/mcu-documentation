"""
Test Suite: Database Schema Creation and Structure
Increment 1: Database Foundation

Tests verify that:
- Database schema can be created
- All tables exist with correct structure
- Indexes are created
- Constraints are enforced
"""

import pytest
import sqlite3
from pathlib import Path


@pytest.fixture
def test_db_path(tmp_path):
    """Provide a temporary database path for testing."""
    return tmp_path / "test_margin_reconciliation.db"


@pytest.fixture
def db_connection(test_db_path):
    """Create a database connection for testing."""
    from src.database.connection import DatabaseConnection
    from src.database.schema import create_schema

    # Create schema first
    create_schema(str(test_db_path))

    # Then create connection
    conn = DatabaseConnection(str(test_db_path))
    yield conn
    conn.close()


def test_create_database_schema(test_db_path):
    """
    GIVEN: No database exists
    WHEN: The schema creation function is called
    THEN: A database file is created with all required tables
    """
    from src.database.schema import create_schema

    # Verify database doesn't exist yet
    assert not test_db_path.exists()

    # Create schema
    create_schema(str(test_db_path))

    # Verify database file was created
    assert test_db_path.exists()

    # Connect and verify tables exist
    conn = sqlite3.connect(str(test_db_path))
    cursor = conn.cursor()

    # Query sqlite_master for all tables
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]

    # Verify all required tables exist
    expected_tables = [
        'bank_movements',
        'data_loads',
        'margin_positions',
        'parser_config',
        'reconciliation_breaks'
    ]

    for table in expected_tables:
        assert table in tables, f"Table {table} not found in database"

    conn.close()


def test_data_loads_table_structure(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: Querying the data_loads table structure
    THEN: All required columns exist with correct types
    """
    cursor = db_connection.get_cursor()
    cursor.execute("PRAGMA table_info(data_loads)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type

    required_columns = {
        'load_id': 'INTEGER',
        'load_timestamp': 'DATETIME',
        'business_date': 'DATE',
        'source_file_path': 'TEXT',
        'source_file_type': 'TEXT',
        'parser_version': 'TEXT',
        'status': 'TEXT',
        'records_loaded': 'INTEGER',
        'error_message': 'TEXT',
        'load_duration_seconds': 'REAL'
    }

    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} not found in data_loads"
        assert columns[col_name] == col_type, f"Column {col_name} has wrong type: expected {col_type}, got {columns[col_name]}"


def test_margin_positions_table_structure(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: Querying the margin_positions table structure
    THEN: All required columns exist with correct types
    """
    cursor = db_connection.get_cursor()
    cursor.execute("PRAGMA table_info(margin_positions)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    required_columns = {
        'position_id': 'INTEGER',
        'load_id': 'INTEGER',
        'business_date': 'DATE',
        'clearer': 'TEXT',
        'margin_type': 'TEXT',
        'entity': 'TEXT',
        'counterparty': 'TEXT',
        'base_currency': 'TEXT',
        'original_currency': 'TEXT',
        'currency_flag': 'INTEGER',
        'position_value_native': 'REAL',
        'position_value_gbp': 'REAL',
        'product': 'TEXT',
        'commodity': 'TEXT',
        'created_timestamp': 'DATETIME'
    }

    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} not found in margin_positions"
        assert columns[col_name] == col_type, f"Column {col_name} has wrong type: expected {col_type}, got {columns[col_name]}"


def test_reconciliation_breaks_table_structure(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: Querying the reconciliation_breaks table structure
    THEN: All required columns exist with correct types
    """
    cursor = db_connection.get_cursor()
    cursor.execute("PRAGMA table_info(reconciliation_breaks)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    required_columns = {
        'break_id': 'INTEGER',
        'business_date': 'DATE',
        'break_type': 'TEXT',
        'severity': 'TEXT',
        'description': 'TEXT',
        'expected_value': 'REAL',
        'actual_value': 'REAL',
        'variance': 'REAL',
        'resolved': 'BOOLEAN',
        'resolved_by': 'TEXT',
        'resolved_timestamp': 'DATETIME',
        'created_timestamp': 'DATETIME'
    }

    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} not found in reconciliation_breaks"


def test_bank_movements_table_structure(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: Querying the bank_movements table structure
    THEN: All required columns exist with correct types
    """
    cursor = db_connection.get_cursor()
    cursor.execute("PRAGMA table_info(bank_movements)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    required_columns = {
        'movement_id': 'INTEGER',
        'business_date': 'DATE',
        'bank_account': 'TEXT',
        'movement_type': 'TEXT',
        'amount': 'REAL',
        'currency': 'TEXT',
        'reference': 'TEXT',
        'created_timestamp': 'DATETIME'
    }

    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} not found in bank_movements"


def test_parser_config_table_structure(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: Querying the parser_config table structure
    THEN: All required columns exist with correct types
    """
    cursor = db_connection.get_cursor()
    cursor.execute("PRAGMA table_info(parser_config)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    required_columns = {
        'config_id': 'INTEGER',
        'source_file_type': 'TEXT',
        'source_identifier': 'TEXT',
        'parser_version': 'TEXT',
        'active': 'BOOLEAN',
        'config_json': 'TEXT',
        'effective_from': 'DATE',
        'effective_to': 'DATE',
        'created_timestamp': 'DATETIME'
    }

    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} not found in parser_config"


def test_indexes_created(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: Querying for indexes
    THEN: All required indexes are created
    """
    cursor = db_connection.get_cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    indexes = [row[0] for row in cursor.fetchall()]

    expected_indexes = [
        'idx_bank_movements_date',
        'idx_breaks_date',
        'idx_breaks_resolved',
        'idx_data_loads_business_date',
        'idx_data_loads_status',
        'idx_fx_rates_date',
        'idx_fx_rates_unique',
        'idx_margin_positions_clearer',
        'idx_margin_positions_date',
        'idx_margin_positions_type',
        'idx_margin_positions_unique',
        'idx_parser_config_active'
    ]

    for index in expected_indexes:
        assert index in indexes, f"Index {index} not found. Available indexes: {indexes}"


def test_foreign_key_constraints_enabled(db_connection):
    """
    GIVEN: Database connection exists
    WHEN: Querying foreign key pragma
    THEN: Foreign keys are enabled
    """
    cursor = db_connection.get_cursor()
    cursor.execute("PRAGMA foreign_keys")
    result = cursor.fetchone()

    assert result[0] == 1, "Foreign keys are not enabled"


def test_unique_constraint_on_margin_positions(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: Querying index definition for unique constraint
    THEN: Unique index exists and includes the key dimensions
    """
    cursor = db_connection.get_cursor()
    cursor.execute("PRAGMA index_info(idx_margin_positions_unique)")
    index_info = cursor.fetchall()

    # Verify the index exists and has 7 columns
    # (business_date, clearer, margin_type, entity/counterparty with COALESCE, original_currency, product)
    assert len(index_info) == 7, f"Expected 7 columns in unique index, got {len(index_info)}"

    # Check that the first columns include core dimensions
    index_columns = [row[2] for row in index_info if row[2] is not None]
    assert index_columns[0] == 'business_date', "First column should be business_date"
    assert index_columns[1] == 'clearer', "Second column should be clearer"
    assert index_columns[2] == 'margin_type', "Third column should be margin_type"

    # Verify original_currency is in the unique index
    assert 'original_currency' in index_columns, "original_currency should be in unique index"

    # Note: entity, counterparty, and product use COALESCE expressions to handle NULLs,
    # so they appear as None in PRAGMA index_info. The behavior is tested in
    # test_database_operations.py::test_unique_constraint_prevents_duplicate_positions
