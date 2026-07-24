# Test Specification: Margin Reconciliation System MVP

**Date**: 2026-07-23  
**Phase**: TDD Test Definition  
**Approach**: Test behaviors, not implementation details

---

## MVP Acceptance Criteria

### Epic: Margin Data Ingestion and Reconciliation

#### AC1: Database Foundation
**Given** the application is initialized  
**When** the database schema is created  
**Then** all core tables exist (data_loads, margin_positions, reconciliation_breaks, bank_movements, parser_config)  
**And** appropriate indexes are created  
**And** foreign key constraints are enforced  

#### AC2: Data Load Tracking
**Given** a margin data file is processed  
**When** the ingestion completes  
**Then** a data_loads record is created with status, timestamp, and metadata  
**And** the load_id is associated with all margin positions from that load  
**And** any errors are captured in the error_message field  

#### AC3: Margin Position Storage
**Given** margin data is parsed from a file  
**When** positions are stored in the database  
**Then** each position includes business_date, clearer, margin_type, and position_value  
**And** duplicate positions for the same dimension combination are rejected  
**And** historical positions are preserved (no updates, only inserts)  

#### AC4: CSV File Parsing
**Given** a valid CSV file with margin data  
**When** the CSV parser processes the file  
**Then** all rows are converted to MarginPosition objects  
**And** numeric values are correctly parsed  
**And** date formats are standardized  
**And** missing required fields cause a parse error  

#### AC5: Excel File Parsing
**Given** a valid Excel file with margin data  
**When** the xlsx parser processes the file  
**Then** data is extracted from the correct worksheet  
**And** header rows are identified and skipped  
**And** formulas are evaluated to their values  
**And** multi-sheet workbooks only parse the target sheet  

#### AC6: PDF File Parsing
**Given** a valid PDF file with margin data  
**When** the PDF parser processes the file  
**Then** text is extracted and parsed using pattern matching  
**And** table structures are identified correctly  
**And** numeric values with formatting (commas, currency symbols) are handled  
**And** format changes are detected and logged  

#### AC7: Idempotent Data Loading
**Given** a file has been successfully loaded for a business date  
**When** the same file is loaded again  
**Then** duplicate positions are rejected by unique constraint  
**And** the second load is marked as failed with an appropriate error message  
**And** no duplicate data is created  

#### AC8: Date Comparison Query
**Given** margin positions exist for two different business dates  
**When** a user requests a comparison between date1 and date2  
**Then** the system calculates the movement (date2 - date1) for each dimension  
**And** results are grouped by clearer and margin_type  
**And** positions missing from either date are included with zero values  

#### AC9: Reconciliation Break Detection
**Given** margin movements for a business date  
**When** the reconciliation engine compares expected vs actual movements  
**Then** variances exceeding a threshold create a reconciliation_breaks record  
**And** the break includes description, expected_value, actual_value, and variance  
**And** severity is assigned based on variance magnitude  

#### AC10: API Query by Date
**Given** margin positions exist in the database  
**When** a user queries GET /api/positions?date=2026-07-23  
**Then** all positions for that business date are returned  
**And** the response includes clearer, margin_type, entity, and position_value  
**And** positions are sorted by clearer and margin_type  
**And** a date with no data returns an empty array (not an error)  

#### AC11: Web UI Display
**Given** the web application is running  
**When** a user navigates to the positions page  
**Then** a date picker allows selecting any business date  
**And** positions are displayed in a readable table format  
**And** totals are calculated by margin_type  
**And** loading states are shown during data fetch  

#### AC12: Error Handling and Logging
**Given** any operation fails (parse error, database error, missing file)  
**When** the error occurs  
**Then** a descriptive error message is logged with timestamp  
**And** the error is communicated to the user (API or UI)  
**And** partial success is handled gracefully (e.g., some files succeed, some fail)  
**And** the system remains in a consistent state  

---

## Key Test Scenarios

### 1. Database Schema and Operations

#### Scenario 1.1: Create Database Schema
**Given** no database exists  
**When** the schema initialization runs  
**Then** the database file is created  
**And** all tables are created with correct columns and types  
**And** indexes are created  
**And** constraints are enforced  

**Test**: `test_database_schema_creation`

#### Scenario 1.2: Insert Margin Position
**Given** the database schema exists  
**When** a margin position is inserted  
**Then** the record is stored with all fields  
**And** the position_id is auto-generated  
**And** created_timestamp is set to current time  

**Test**: `test_insert_margin_position`

#### Scenario 1.3: Enforce Unique Constraint
**Given** a margin position exists for a specific dimension combination  
**When** an identical position is inserted (same date, clearer, margin_type, entity, counterparty)  
**Then** the insert fails with a unique constraint violation  
**And** the original record remains unchanged  

**Test**: `test_unique_constraint_on_positions`

#### Scenario 1.4: Foreign Key Constraint
**Given** a margin position references a load_id  
**When** the position is inserted without a valid load_id  
**Then** the insert fails with a foreign key constraint violation  

**Test**: `test_foreign_key_constraint_enforced`

#### Scenario 1.5: Query Positions by Date
**Given** margin positions exist for multiple dates  
**When** querying for a specific business_date  
**Then** only positions for that date are returned  
**And** results are ordered consistently  

**Test**: `test_query_positions_by_date`

#### Scenario 1.6: Transaction Rollback on Error
**Given** multiple positions are being inserted in a transaction  
**When** one insert fails  
**Then** all inserts in the transaction are rolled back  
**And** no partial data is committed  

**Test**: `test_transaction_rollback_on_error`

---

### 2. File Parsing

#### Scenario 2.1: Parse Valid CSV File
**Given** a CSV file with well-formed margin data  
**When** the CSV parser processes the file  
**Then** all rows are converted to MarginPosition objects  
**And** data types are correctly converted (strings, floats, dates)  

**Test**: `test_parse_valid_csv_file`

#### Scenario 2.2: CSV with Missing Required Field
**Given** a CSV file missing a required column (e.g., position_value)  
**When** the CSV parser processes the file  
**Then** a parse error is raised  
**And** the error message identifies the missing field  

**Test**: `test_csv_missing_required_field`

#### Scenario 2.3: CSV with Invalid Numeric Value
**Given** a CSV file with non-numeric data in position_value column  
**When** the CSV parser processes the file  
**Then** a parse error is raised  
**And** the row number is identified in the error  

**Test**: `test_csv_invalid_numeric_value`

#### Scenario 2.4: CSV with Extra Columns
**Given** a CSV file with columns not in the schema  
**When** the CSV parser processes the file  
**Then** the file is parsed successfully  
**And** extra columns are ignored  

**Test**: `test_csv_with_extra_columns`

#### Scenario 2.5: Parse Valid Excel File
**Given** an Excel file with margin data on the first sheet  
**When** the xlsx parser processes the file  
**Then** data is extracted correctly  
**And** header rows are identified and skipped  

**Test**: `test_parse_valid_excel_file`

#### Scenario 2.6: Excel with Multiple Sheets
**Given** an Excel workbook with multiple sheets  
**When** the xlsx parser processes the file  
**Then** only the specified target sheet is parsed  
**And** other sheets are ignored  

**Test**: `test_excel_multi_sheet_parsing`

#### Scenario 2.7: Excel with Formula Cells
**Given** an Excel file with formula cells in the position_value column  
**When** the xlsx parser processes the file  
**Then** formulas are evaluated to their calculated values  
**And** values are stored, not formulas  

**Test**: `test_excel_formula_evaluation`

#### Scenario 2.8: Parse Valid PDF File
**Given** a PDF file with a table of margin data  
**When** the PDF parser processes the file  
**Then** text is extracted and parsed  
**And** table structure is identified  
**And** margin positions are created  

**Test**: `test_parse_valid_pdf_file`

#### Scenario 2.9: PDF with Currency Formatting
**Given** a PDF with values like "£1,234,567.89"  
**When** the PDF parser processes the file  
**Then** currency symbols and commas are removed  
**And** values are converted to float (1234567.89)  

**Test**: `test_pdf_currency_formatting`

#### Scenario 2.10: PDF Format Change Detection
**Given** a PDF file with an unexpected structure  
**When** the PDF parser attempts to parse the file  
**Then** a format change warning is logged  
**And** parsing fails gracefully with a descriptive error  

**Test**: `test_pdf_format_change_detection`

---

### 3. Data Storage and Retrieval

#### Scenario 3.1: Store Parsed Data with Load Record
**Given** a file has been successfully parsed  
**When** the ingestion service stores the data  
**Then** a data_loads record is created with SUCCESS status  
**And** all margin_positions are linked to that load_id  
**And** records_loaded count matches the number of positions  

**Test**: `test_store_parsed_data_with_load_record`

#### Scenario 3.2: Handle Partial Parse Success
**Given** a file with some valid and some invalid rows  
**When** the ingestion service processes the file  
**Then** valid rows are stored  
**And** the data_loads status is PARTIAL  
**And** the error_message field describes which rows failed  

**Test**: `test_handle_partial_parse_success`

#### Scenario 3.3: Store Load Failure
**Given** a file cannot be parsed at all  
**When** the ingestion service attempts to process the file  
**Then** a data_loads record is created with FAILURE status  
**And** no margin_positions are created  
**And** the error_message contains the failure reason  

**Test**: `test_store_load_failure`

#### Scenario 3.4: Query Load History
**Given** multiple data loads have been performed  
**When** querying the data_loads table  
**Then** loads are returned ordered by load_timestamp descending  
**And** status, business_date, and error information are included  

**Test**: `test_query_load_history`

#### Scenario 3.5: Track Load Duration
**Given** a file is being processed  
**When** the ingestion completes  
**Then** the load_duration_seconds field is populated  
**And** the duration is accurate to the actual processing time  

**Test**: `test_track_load_duration`

---

### 4. Date Comparison Logic

#### Scenario 4.1: Calculate Movements Between Two Dates
**Given** margin positions exist for date1 and date2  
**When** comparing the two dates  
**Then** movements are calculated as (date2_value - date1_value) for each dimension  
**And** dimensions present in only one date show the full value as movement  

**Test**: `test_calculate_movements_between_dates`

#### Scenario 4.2: Handle Missing Positions in Comparison
**Given** a position exists on date1 but not date2  
**When** comparing the dates  
**Then** the movement shows the date1 value as negative (outflow)  
**And** the position is included in results with date2_value = 0  

**Test**: `test_handle_missing_positions_in_comparison`

#### Scenario 4.3: Group Movements by Dimension
**Given** multiple positions for different entities on the same date  
**When** comparing dates with grouping by clearer and margin_type  
**Then** results are aggregated by the grouping dimensions  
**And** entity-level detail is summed appropriately  

**Test**: `test_group_movements_by_dimension`

#### Scenario 4.4: Compare Non-Sequential Dates
**Given** positions exist for 2026-07-01, 2026-07-15, and 2026-07-23  
**When** comparing 2026-07-01 and 2026-07-23 (skipping 2026-07-15)  
**Then** the comparison uses only the two specified dates  
**And** intermediate dates do not affect the calculation  

**Test**: `test_compare_non_sequential_dates`

---

### 5. Basic Reconciliation

#### Scenario 5.1: Detect Movement Variance
**Given** expected margin movement is 100,000  
**And** actual bank movement is 98,000  
**When** the reconciliation engine runs  
**Then** a reconciliation_break is created  
**And** variance is calculated as 2,000  
**And** break_type is BANK_MISMATCH  

**Test**: `test_detect_movement_variance`

#### Scenario 5.2: Calculate Severity Based on Variance
**Given** a variance of 50,000 (large)  
**When** the break is created  
**Then** severity is set to HIGH  

**Given** a variance of 500 (small)  
**When** the break is created  
**Then** severity is set to LOW  

**Test**: `test_calculate_severity_based_on_variance`

#### Scenario 5.3: No Break When Movements Match
**Given** expected and actual movements are identical  
**When** the reconciliation engine runs  
**Then** no reconciliation_break is created  

**Test**: `test_no_break_when_movements_match`

#### Scenario 5.4: Resolve Reconciliation Break
**Given** an open reconciliation_break exists  
**When** the break is marked as resolved  
**Then** resolved flag is set to 1  
**And** resolved_timestamp is set  
**And** resolved_by is populated  

**Test**: `test_resolve_reconciliation_break`

---

### 6. Exception Handling

#### Scenario 6.1: File Not Found
**Given** a file path that does not exist  
**When** the ingestion service attempts to process the file  
**Then** a FileNotFoundError is caught  
**And** a data_loads record is created with FAILURE status  
**And** the error message indicates file not found  

**Test**: `test_file_not_found_handling`

#### Scenario 6.2: Database Connection Failure
**Given** the database file cannot be accessed  
**When** any database operation is attempted  
**Then** a descriptive error is raised  
**And** the operation does not corrupt existing data  

**Test**: `test_database_connection_failure`

#### Scenario 6.3: Invalid Date Format
**Given** a query with an invalid date string (e.g., "2026-13-45")  
**When** the API endpoint is called  
**Then** a 400 Bad Request error is returned  
**And** the error message describes the invalid date format  

**Test**: `test_invalid_date_format_handling`

#### Scenario 6.4: Concurrent Load Attempts
**Given** two processes attempt to load data for the same business date simultaneously  
**When** both reach the database insert  
**Then** one succeeds and the other fails with unique constraint violation  
**And** no data corruption occurs  

**Test**: `test_concurrent_load_attempts`

---

## Edge Cases to Consider

### Data Quality Edge Cases

1. **Empty Files**
   - CSV with only headers, no data rows
   - Excel sheet with no data
   - PDF with no parseable tables
   - **Expected**: Load succeeds with 0 records, warning logged

2. **Negative Position Values**
   - Margin position_value is negative (e.g., collateral returned)
   - **Expected**: Value stored as-is, negative values are valid

3. **Very Large Numbers**
   - Position value exceeds typical margin amounts (e.g., 1 billion+)
   - **Expected**: Value stored correctly, possible warning for outliers

4. **Zero Values**
   - Position value is exactly 0.00
   - **Expected**: Stored as valid position, not filtered out

5. **Duplicate Rows in Source File**
   - CSV/Excel contains identical rows
   - **Expected**: First row succeeds, subsequent rows fail unique constraint

### Date and Time Edge Cases

6. **Weekend Business Dates**
   - Business date falls on Saturday or Sunday
   - **Expected**: Accepted as-is (system not holiday-aware in MVP)

7. **Future Dates**
   - Business date is in the future
   - **Expected**: Warning logged but accepted (user may be testing)

8. **Very Old Dates**
   - Business date is years in the past
   - **Expected**: Accepted, no time-based validation in MVP

9. **Date Comparison Edge Cases**
   - Comparing same date to itself (date1 == date2)
   - **Expected**: All movements are zero

10. **Missing Date Data**
    - Query for a date with no positions
    - **Expected**: Empty result set, not an error

### File Format Edge Cases

11. **CSV Encoding Issues**
    - File in UTF-16 instead of UTF-8
    - **Expected**: Encoding detection attempted, or clear error message

12. **Excel Password Protected**
    - xlsx file requires password
    - **Expected**: Parse fails with clear error message

13. **PDF Scanned Image**
    - PDF is scanned image, not text-based
    - **Expected**: Text extraction fails, clear error (OCR out of scope)

14. **Mixed Currency in Single File**
    - Some rows GBP, some rows USD
    - **Expected**: Currency field preserved, no automatic conversion

15. **Multi-page PDF**
    - Margin data spans multiple pages
    - **Expected**: All pages parsed and combined

### Database Edge Cases

16. **Database File Locked**
    - Another process has exclusive lock on SQLite file
    - **Expected**: Operation retries or fails with clear error

17. **Disk Space Exhausted**
    - Database write fails due to no disk space
    - **Expected**: Transaction rolled back, error logged

18. **Schema Version Mismatch**
    - Database schema is older version
    - **Expected**: Migration detected (future feature) or clear error

### Reconciliation Edge Cases

19. **Rounding Differences**
    - Variance of 0.01 due to rounding
    - **Expected**: Configurable tolerance threshold, not flagged if within tolerance

20. **Missing Bank Data**
    - No bank_movements record for comparison
    - **Expected**: Break created with break_type MISSING_DATA

### API Edge Cases

21. **Invalid Query Parameters**
    - date parameter missing or malformed
    - **Expected**: 400 Bad Request with validation error details

22. **Pagination Edge Cases**
    - Requesting page beyond available data
    - **Expected**: Empty results with pagination metadata

23. **Large Result Sets**
    - Query returns thousands of positions
    - **Expected**: Paginated response, performance acceptable

---

## The First Failing Test (Increment 1)

### Test: Database Schema Creation

**File**: `tests/test_database_schema.py`

**Purpose**: Verify that the database schema can be created and all tables exist with correct structure.

**Test Code**:
```python
import pytest
import sqlite3
from pathlib import Path
from src.database.connection import DatabaseConnection
from src.database.schema import create_schema


@pytest.fixture
def test_db_path(tmp_path):
    """Provide a temporary database path for testing."""
    return tmp_path / "test_margin_reconciliation.db"


@pytest.fixture
def db_connection(test_db_path):
    """Create a database connection for testing."""
    conn = DatabaseConnection(str(test_db_path))
    yield conn
    conn.close()


def test_create_database_schema(test_db_path):
    """
    GIVEN: No database exists
    WHEN: The schema creation function is called
    THEN: A database file is created with all required tables
    """
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
        assert columns[col_name] == col_type, f"Column {col_name} has wrong type"


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
        'currency': 'TEXT',
        'position_value': 'REAL',
        'created_timestamp': 'DATETIME'
    }
    
    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} not found in margin_positions"
        assert columns[col_name] == col_type, f"Column {col_name} has wrong type"


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
        'idx_data_loads_business_date',
        'idx_data_loads_status',
        'idx_margin_positions_date',
        'idx_margin_positions_clearer',
        'idx_margin_positions_type',
        'idx_margin_positions_unique',
        'idx_breaks_date',
        'idx_breaks_resolved',
        'idx_bank_movements_date',
        'idx_parser_config_active'
    ]
    
    for index in expected_indexes:
        assert index in indexes, f"Index {index} not found"


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
    THEN: Unique index exists on correct columns
    """
    cursor = db_connection.get_cursor()
    cursor.execute("PRAGMA index_info(idx_margin_positions_unique)")
    index_columns = [row[2] for row in cursor.fetchall()]
    
    expected_columns = [
        'business_date',
        'clearer',
        'margin_type',
        'entity',
        'counterparty'
    ]
    
    assert index_columns == expected_columns, \
        f"Unique constraint columns mismatch. Expected {expected_columns}, got {index_columns}"
```

**Expected Result**: All tests FAIL because the implementation does not exist yet.

**Success Criteria for Making Tests Pass**:
1. Create `src/database/schema.py` with SQL schema
2. Create `src/database/connection.py` with DatabaseConnection class
3. Implement `create_schema()` function that executes DDL statements
4. Enable foreign key constraints on connection
5. All tests pass

---

## Test Organization Structure

```
tests/
├── __init__.py
├── conftest.py                        # Shared fixtures
├── fixtures/                          # Sample data files
│   ├── sample_margin.csv
│   ├── sample_margin.xlsx
│   └── sample_margin.pdf
├── test_database_schema.py            # Increment 1 (FIRST)
├── test_database_operations.py        # Increment 1
├── test_base_parser.py                # Increment 2
├── test_csv_parser.py                 # Increment 3
├── test_ingestion_service.py          # Increment 4
├── test_xlsx_parser.py                # Increment 5
├── test_pdf_parser.py                 # Increment 6
├── test_api_health.py                 # Increment 7
├── test_api_positions.py              # Increment 8
├── test_api_compare.py                # Increment 10
├── test_api_loads.py                  # Increment 12
├── test_reconciliation_engine.py      # Increment 13
├── test_api_breaks.py                 # Increment 14
└── integration/                       # End-to-end tests
    ├── __init__.py
    └── test_full_workflow.py          # Increment 19
```

---

## Testing Principles

### Test Behaviors, Not Implementation

**Good** (tests behavior):
```python
def test_csv_parser_extracts_positions():
    """
    GIVEN: A CSV file with 3 margin positions
    WHEN: The parser processes the file
    THEN: 3 MarginPosition objects are returned with correct values
    """
    positions = parser.parse("sample.csv", date(2026, 7, 23))
    assert len(positions) == 3
    assert positions[0].clearer == "BNP"
    assert positions[0].position_value == 1000000.0
```

**Bad** (tests implementation):
```python
def test_csv_parser_uses_pandas():
    """Tests that pandas.read_csv is called (too coupled to implementation)"""
    with patch('pandas.read_csv') as mock_read:
        parser.parse("sample.csv", date(2026, 7, 23))
        mock_read.assert_called_once()
```

### Test Boundaries and Edge Cases

Focus tests on:
- Happy path (valid inputs produce expected outputs)
- Boundary values (empty, zero, maximum, minimum)
- Invalid inputs (wrong type, missing data, malformed)
- Error conditions (file not found, database locked)
- State transitions (unresolved break → resolved break)

### Keep Tests Independent

Each test should:
- Set up its own test data
- Clean up after itself
- Not depend on other tests running first
- Be runnable in any order

### Use Descriptive Test Names

Test names should read like specifications:
- `test_insert_margin_position_with_all_fields`
- `test_unique_constraint_prevents_duplicate_positions`
- `test_csv_parser_handles_missing_required_column`

---

## Test Data Fixtures

### Sample CSV File (`tests/fixtures/sample_margin.csv`)

```csv
business_date,clearer,margin_type,entity,counterparty,currency,position_value
2026-07-23,BNP,INITIAL_MARGIN,CEL,,GBP,1000000.00
2026-07-23,BNP,DAILY_SETTLEMENT,CEL,,GBP,50000.00
2026-07-23,SOCGEN,INITIAL_MARGIN,CEL,,GBP,750000.00
2026-07-23,BNP,CSA,CEL,COUNTERPARTY_A,GBP,200000.00
```

### Sample Excel File (`tests/fixtures/sample_margin.xlsx`)

Structure:
- Sheet1: "Margin Positions"
- Row 1: Headers (same as CSV)
- Rows 2-5: Data (same as CSV)

### Sample PDF File (`tests/fixtures/sample_margin.pdf`)

Text content:
```
Margin Report - 23/07/2026

Clearer: BNP Paribas
Initial Margin: £1,000,000.00
Daily Settlement: £50,000.00
CSA (Counterparty A): £200,000.00

Clearer: Societe Generale
Initial Margin: £750,000.00
```

---

## Next Steps

1. **Builder** will implement `src/database/schema.py` to make first test pass
2. **Builder** will implement `src/database/connection.py` to make first test pass
3. Once Increment 1 tests pass, move to Increment 2 (Base Parser)
4. Continue TDD cycle: Write test → Run test (fails) → Implement → Test passes → Refactor

---

*Test specification complete. Ready for TDD implementation.*
