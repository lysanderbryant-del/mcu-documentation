# Test Suite for Margin Reconciliation System

This directory contains all tests for the Margin Reconciliation System MVP, following Test-Driven Development (TDD) principles.

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests for a specific increment
```bash
pytest -m increment1  # Database foundation tests
pytest -m increment3  # CSV parser tests
```

### Run a specific test file
```bash
pytest tests/test_database_schema.py
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage report
```bash
pytest --cov=src --cov-report=html
```

## Test Organization

Tests are organized by component and increment, following the build plan from `outputs/2-design.md`:

- `test_database_schema.py` - Database schema creation (Increment 1)
- `test_database_operations.py` - Database operations (Increment 1)
- `test_base_parser.py` - Base parser interface (Increment 2)
- `test_csv_parser.py` - CSV parsing (Increment 3)
- `test_ingestion_service.py` - Ingestion orchestration (Increment 4)
- `test_xlsx_parser.py` - Excel parsing (Increment 5)
- `test_pdf_parser.py` - PDF parsing (Increment 6)
- `test_api_*.py` - API endpoint tests (Increments 7-14)
- `test_reconciliation_engine.py` - Reconciliation logic (Increment 13)

## Test Fixtures

The `fixtures/` directory contains sample data files for testing:

- `sample_margin.csv` - Sample CSV margin data
- `sample_margin.xlsx` - Sample Excel margin data (to be created)
- `sample_margin.pdf` - Sample PDF margin data (to be created)

## Shared Fixtures

`conftest.py` contains pytest fixtures available to all tests:

- `test_db_path` - Temporary database path
- `db_connection` - Database connection with schema initialized
- `fixtures_dir` - Path to test fixtures directory
- `sample_business_date` - Standard test date
- `sample_margin_positions` - Sample position data

## Current Status

**Increment 1: Database Foundation**
- Tests created: `test_database_schema.py`, `test_database_operations.py`
- Status: FAILING (implementation pending)
- Next step: Builder implements `src/database/schema.py` and `src/database/connection.py`

## Testing Principles

1. **Test behaviors, not implementation details**
   - Focus on what the code does, not how it does it
   - Tests should be resilient to refactoring

2. **Keep tests independent**
   - Each test sets up its own data
   - Tests can run in any order
   - Use fixtures for shared setup

3. **Use descriptive names**
   - Test names describe the scenario being tested
   - Follow Given/When/Then structure in docstrings

4. **Test edge cases**
   - Empty inputs
   - Invalid data
   - Boundary conditions
   - Error scenarios

5. **One assertion per concept**
   - Tests can have multiple assertions
   - But each test should verify one logical concept

## TDD Workflow

1. **Red**: Write a failing test that defines desired behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code while keeping tests passing
4. **Repeat**: Move to next test

## Test Markers

Use markers to organize test execution:

```python
@pytest.mark.increment1
def test_database_schema_creation():
    ...

@pytest.mark.slow
def test_large_file_parsing():
    ...
```

Run specific markers:
```bash
pytest -m increment1
pytest -m "not slow"
```
