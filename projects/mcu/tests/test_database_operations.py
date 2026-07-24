"""
Test Suite: Database Operations
Increment 1: Database Foundation

Tests verify that:
- Data can be inserted into tables
- Queries return correct results
- Unique constraints prevent duplicates
- Foreign key constraints are enforced
- Transactions rollback on errors
"""

import pytest
import sqlite3
from datetime import date, datetime


@pytest.fixture
def test_db_path(tmp_path):
    """Provide a temporary database path for testing."""
    return tmp_path / "test_margin_reconciliation.db"


@pytest.fixture
def db_connection(test_db_path):
    """Create a database connection with schema initialized."""
    from src.database.schema import create_schema
    from src.database.connection import DatabaseConnection

    # Create schema
    create_schema(str(test_db_path))

    # Return connection
    conn = DatabaseConnection(str(test_db_path))
    yield conn
    conn.close()


def test_insert_data_load_record(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: A data_load record is inserted
    THEN: The record is stored with all fields and load_id is auto-generated
    """
    cursor = db_connection.get_cursor()

    # Insert a data load
    cursor.execute("""
        INSERT INTO data_loads (
            business_date, source_file_path, source_file_type,
            parser_version, status, records_loaded
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        '2026-07-23',
        '/path/to/file.csv',
        'CSV',
        'v1.0',
        'SUCCESS',
        5
    ))

    db_connection.commit()

    # Query the record
    cursor.execute("SELECT * FROM data_loads WHERE load_id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()

    assert row is not None
    assert row[0] > 0  # load_id is auto-generated
    assert row[2] == '2026-07-23'  # business_date
    assert row[3] == '/path/to/file.csv'  # source_file_path
    assert row[4] == 'CSV'  # source_file_type
    assert row[6] == 'SUCCESS'  # status
    assert row[7] == 5  # records_loaded


def test_insert_margin_position(db_connection):
    """
    GIVEN: Database schema exists with a valid data_load
    WHEN: A margin_position is inserted
    THEN: The record is stored with all fields and created_timestamp is set
    """
    cursor = db_connection.get_cursor()

    # First insert a data_load to satisfy foreign key
    cursor.execute("""
        INSERT INTO data_loads (
            business_date, source_file_path, source_file_type,
            parser_version, status, records_loaded
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('2026-07-23', '/path/to/file.csv', 'CSV', 'v1.0', 'SUCCESS', 1))

    load_id = cursor.lastrowid

    # Insert a margin position
    cursor.execute("""
        INSERT INTO margin_positions (
            load_id, business_date, clearer, margin_type,
            entity, counterparty, original_currency, position_value_native
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        load_id,
        '2026-07-23',
        'BNP',
        'INITIAL_MARGIN',
        'CEL',
        None,
        'GBP',
        1000000.00
    ))

    db_connection.commit()

    # Query the record
    cursor.execute("""
        SELECT position_id, load_id, business_date, clearer, margin_type, entity,
               original_currency, position_value_native, created_timestamp
        FROM margin_positions
        WHERE position_id = ?
    """, (cursor.lastrowid,))
    row = cursor.fetchone()

    assert row is not None
    assert row[0] > 0  # position_id
    assert row[1] == load_id  # load_id
    assert row[2] == '2026-07-23'  # business_date
    assert row[3] == 'BNP'  # clearer
    assert row[4] == 'INITIAL_MARGIN'  # margin_type
    assert row[5] == 'CEL'  # entity
    assert row[6] == 'GBP'  # original_currency
    assert row[7] == 1000000.00  # position_value_native
    assert row[8] is not None  # created_timestamp


def test_unique_constraint_prevents_duplicate_positions(db_connection):
    """
    GIVEN: A margin position exists for a specific dimension combination
    WHEN: An identical position is inserted (same date, clearer, margin_type, entity, counterparty)
    THEN: The insert fails with a unique constraint violation
    """
    cursor = db_connection.get_cursor()

    # First insert a data_load
    cursor.execute("""
        INSERT INTO data_loads (
            business_date, source_file_path, source_file_type,
            parser_version, status, records_loaded
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('2026-07-23', '/path/to/file.csv', 'CSV', 'v1.0', 'SUCCESS', 1))

    load_id = cursor.lastrowid

    # Insert first margin position
    cursor.execute("""
        INSERT INTO margin_positions (
            load_id, business_date, clearer, margin_type,
            entity, counterparty, original_currency, position_value_native
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (load_id, '2026-07-23', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 1000000.00))

    db_connection.commit()

    # Try to insert duplicate position
    with pytest.raises(sqlite3.IntegrityError) as exc_info:
        cursor.execute("""
            INSERT INTO margin_positions (
                load_id, business_date, clearer, margin_type,
                entity, counterparty, original_currency, position_value_native
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (load_id, '2026-07-23', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 2000000.00))
        db_connection.commit()

    assert 'UNIQUE constraint failed' in str(exc_info.value)


def test_foreign_key_constraint_enforced(db_connection):
    """
    GIVEN: Database schema exists with foreign key constraints enabled
    WHEN: A margin_position is inserted with an invalid load_id
    THEN: The insert fails with a foreign key constraint violation
    """
    cursor = db_connection.get_cursor()

    # Try to insert position with non-existent load_id
    with pytest.raises(sqlite3.IntegrityError) as exc_info:
        cursor.execute("""
            INSERT INTO margin_positions (
                load_id, business_date, clearer, margin_type,
                entity, counterparty, original_currency, position_value_native
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (999999, '2026-07-23', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 1000000.00))
        db_connection.commit()

    assert 'FOREIGN KEY constraint failed' in str(exc_info.value)


def test_query_positions_by_date(db_connection):
    """
    GIVEN: Margin positions exist for multiple dates
    WHEN: Querying for a specific business_date
    THEN: Only positions for that date are returned
    """
    cursor = db_connection.get_cursor()

    # Insert data_load
    cursor.execute("""
        INSERT INTO data_loads (
            business_date, source_file_path, source_file_type,
            parser_version, status, records_loaded
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('2026-07-23', '/path/to/file.csv', 'CSV', 'v1.0', 'SUCCESS', 3))

    load_id = cursor.lastrowid

    # Insert positions for different dates
    positions = [
        (load_id, '2026-07-22', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 1000000.00),
        (load_id, '2026-07-23', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 1100000.00),
        (load_id, '2026-07-23', 'SOCGEN', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 750000.00),
        (load_id, '2026-07-24', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 1200000.00),
    ]

    for pos in positions:
        cursor.execute("""
            INSERT INTO margin_positions (
                load_id, business_date, clearer, margin_type,
                entity, counterparty, original_currency, position_value_native
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, pos)

    db_connection.commit()

    # Query for specific date
    cursor.execute("""
        SELECT clearer, margin_type, original_currency, position_value_native
        FROM margin_positions
        WHERE business_date = ?
        ORDER BY clearer, margin_type
    """, ('2026-07-23',))

    results = cursor.fetchall()

    assert len(results) == 2
    assert results[0][0] == 'BNP'  # clearer
    assert results[0][3] == 1100000.00  # position_value_native
    assert results[1][0] == 'SOCGEN'  # clearer
    assert results[1][3] == 750000.00  # position_value_native


def test_transaction_rollback_on_error(db_connection):
    """
    GIVEN: Multiple positions are being inserted in a transaction
    WHEN: One insert fails due to a constraint violation
    THEN: All inserts in the transaction are rolled back
    """
    cursor = db_connection.get_cursor()

    # Insert data_load
    cursor.execute("""
        INSERT INTO data_loads (
            business_date, source_file_path, source_file_type,
            parser_version, status, records_loaded
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('2026-07-23', '/path/to/file.csv', 'CSV', 'v1.0', 'SUCCESS', 2))

    load_id = cursor.lastrowid
    db_connection.commit()

    # Start a new transaction
    try:
        # Insert first position (should succeed)
        cursor.execute("""
            INSERT INTO margin_positions (
                load_id, business_date, clearer, margin_type,
                entity, counterparty, original_currency, position_value_native
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (load_id, '2026-07-23', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 1000000.00))

        # Insert duplicate position (should fail)
        cursor.execute("""
            INSERT INTO margin_positions (
                load_id, business_date, clearer, margin_type,
                entity, counterparty, original_currency, position_value_native
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (load_id, '2026-07-23', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 1100000.00))

        db_connection.commit()
    except sqlite3.IntegrityError:
        db_connection.rollback()

    # Verify no positions were inserted
    cursor.execute("""
        SELECT COUNT(*) FROM margin_positions
        WHERE load_id = ?
    """, (load_id,))

    count = cursor.fetchone()[0]
    assert count == 0, "Transaction was not rolled back correctly"


def test_insert_reconciliation_break(db_connection):
    """
    GIVEN: Database schema exists
    WHEN: A reconciliation_break is inserted
    THEN: The record is stored with all fields and defaults are applied
    """
    cursor = db_connection.get_cursor()

    # Insert a reconciliation break
    cursor.execute("""
        INSERT INTO reconciliation_breaks (
            business_date, break_type, severity, description,
            expected_value, actual_value, variance
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        '2026-07-23',
        'BANK_MISMATCH',
        'HIGH',
        'Expected margin call of £100,000 but bank shows £98,000',
        100000.00,
        98000.00,
        2000.00
    ))

    db_connection.commit()

    # Query the record
    cursor.execute("SELECT * FROM reconciliation_breaks WHERE break_id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()

    assert row is not None
    assert row[0] > 0  # break_id
    assert row[1] == '2026-07-23'  # business_date
    assert row[2] == 'BANK_MISMATCH'  # break_type
    assert row[3] == 'HIGH'  # severity
    assert row[7] == 2000.00  # variance
    assert row[8] == 0  # resolved (default False)
    assert row[11] is not None  # created_timestamp


def test_resolve_reconciliation_break(db_connection):
    """
    GIVEN: An open reconciliation_break exists
    WHEN: The break is marked as resolved
    THEN: resolved flag is set and resolved_timestamp is populated
    """
    cursor = db_connection.get_cursor()

    # Insert a break
    cursor.execute("""
        INSERT INTO reconciliation_breaks (
            business_date, break_type, severity, description,
            expected_value, actual_value, variance
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('2026-07-23', 'BANK_MISMATCH', 'HIGH', 'Test break', 100000.00, 98000.00, 2000.00))

    break_id = cursor.lastrowid
    db_connection.commit()

    # Resolve the break
    cursor.execute("""
        UPDATE reconciliation_breaks
        SET resolved = 1,
            resolved_by = ?,
            resolved_timestamp = CURRENT_TIMESTAMP
        WHERE break_id = ?
    """, ('test_user', break_id))

    db_connection.commit()

    # Query the resolved break
    cursor.execute("SELECT resolved, resolved_by, resolved_timestamp FROM reconciliation_breaks WHERE break_id = ?", (break_id,))
    row = cursor.fetchone()

    assert row[0] == 1  # resolved
    assert row[1] == 'test_user'  # resolved_by
    assert row[2] is not None  # resolved_timestamp


def test_query_positions_by_clearer(db_connection):
    """
    GIVEN: Margin positions exist for multiple clearers
    WHEN: Querying for a specific clearer
    THEN: Only positions for that clearer are returned
    """
    cursor = db_connection.get_cursor()

    # Insert data_load
    cursor.execute("""
        INSERT INTO data_loads (
            business_date, source_file_path, source_file_type,
            parser_version, status, records_loaded
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('2026-07-23', '/path/to/file.csv', 'CSV', 'v1.0', 'SUCCESS', 3))

    load_id = cursor.lastrowid

    # Insert positions for different clearers
    positions = [
        (load_id, '2026-07-23', 'BNP', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 1000000.00),
        (load_id, '2026-07-23', 'BNP', 'DAILY_SETTLEMENT', 'CEL', None, 'GBP', 50000.00),
        (load_id, '2026-07-23', 'SOCGEN', 'INITIAL_MARGIN', 'CEL', None, 'GBP', 750000.00),
    ]

    for pos in positions:
        cursor.execute("""
            INSERT INTO margin_positions (
                load_id, business_date, clearer, margin_type,
                entity, counterparty, original_currency, position_value_native
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, pos)

    db_connection.commit()

    # Query for BNP only
    cursor.execute("""
        SELECT * FROM margin_positions
        WHERE clearer = ?
    """, ('BNP',))

    results = cursor.fetchall()

    assert len(results) == 2
    assert all(row[3] == 'BNP' for row in results)


def test_index_improves_query_performance(db_connection):
    """
    GIVEN: Database has index on business_date
    WHEN: Querying by business_date
    THEN: The query uses the index (verified via EXPLAIN QUERY PLAN)
    """
    cursor = db_connection.get_cursor()

    # Check query plan for date query
    cursor.execute("""
        EXPLAIN QUERY PLAN
        SELECT * FROM margin_positions
        WHERE business_date = '2026-07-23'
    """)

    query_plan = cursor.fetchall()
    plan_text = ' '.join([str(row) for row in query_plan])

    # Verify that the index is being used
    assert 'idx_margin_positions_date' in plan_text or 'USING INDEX' in plan_text.upper()
