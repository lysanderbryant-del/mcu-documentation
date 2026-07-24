# Design: Margin Reconciliation System

**Date**: 2026-07-23  
**Process**: Margin_Explain Automation  
**Type**: Web-based application with automated data ingestion

---

## Future-State Solution Summary

A lightweight, database-backed web application that:

1. **Automatically ingests** margin data from network drives (PDF, CSV, xlsx) on a configurable schedule
2. **Stores historical positions** in SQLite for flexible date-range analysis
3. **Provides a web UI** for querying movements, reconciling to bank accounts, and viewing exceptions
4. **Handles format changes gracefully** through parser versioning and fallback mechanisms
5. **Surfaces breaks immediately** with clear exception reporting

**Core principle**: Replace Excel as the single source of truth with a queryable database, while keeping the solution simple and self-contained.

### Key User Benefits

- **Compare any two dates** - not just consecutive days
- **Filter by dimension** - product, counterparty, clearer, margin type
- **Automated daily refresh** - no manual data entry
- **Exception visibility** - know immediately when reconciliation breaks
- **Audit trail** - track all data loads and changes
- **Weekend/holiday aware** - intelligent scheduling

---

## MVP Scope

### IN SCOPE (First Iteration)

#### Data Ingestion
- Parse **one representative file** from each type (PDF, CSV, xlsx)
- Store parsed data in SQLite database
- Manual trigger for data load (scheduled automation in future iteration)
- Basic error handling with logging

#### Database
- Core tables: `margin_positions`, `data_loads`, `reconciliation_breaks`
- SQLite file-based database (no server required)
- Schema versioning capability

#### Web UI
- **View daily positions** - single date snapshot
- **Compare two dates** - movement calculation
- **List data loads** - status and errors
- **View breaks** - reconciliation exceptions
- Simple HTML/CSS with minimal JavaScript (no framework)

#### Reconciliation Logic
- Calculate day-over-day movements for a single margin type (e.g., BNP clearer)
- Flag breaks when movements don't reconcile to expected bank movements

#### Analysis Dimensions (simplified)
- By **clearer** (BNP, SocGen)
- By **margin type** (initial margin, daily settlement, CSA, TSO)
- By **date**

### OUT OF SCOPE (Future Iterations)

- **Scheduled automation** - use Windows Task Scheduler initially, build in-app scheduler later
- **Multi-product drill-down** - commodity-level detail
- **Multi-counterparty CSA breakdown** - start with aggregated CSA
- **User authentication** - assume trusted network initially
- **Real-time data** - batch processing only
- **External system integration** - standalone application
- **Advanced visualizations** - charts, graphs
- **Mobile responsiveness** - desktop-first
- **Network drive auto-discovery** - hardcode paths initially
- **Format change auto-detection** - manual intervention required
- **LC risk exposure calculation** - defer complex calculations
- **Initial margin waiver capacity tracking** - defer to v2

---

## Architecture Components

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│                    (User Interface)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Python Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   FastAPI    │  │  Ingestion   │  │ Reconciliation│     │
│  │   Web API    │  │   Service    │  │    Engine     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            ▼                                 │
│                  ┌──────────────────┐                        │
│                  │  SQLite Database │                        │
│                  └──────────────────┘                        │
└────────────────────────┬────────────────────────────────────┘
                         │ File System Access
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Network Drives                           │
│         (PDF, CSV, xlsx source files)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema (SQLite)

### Design Principles
- **Normalized** - avoid redundancy
- **Auditable** - track who, what, when
- **Extensible** - easy to add dimensions later
- **Simple** - no over-engineering

### Core Tables

#### `data_loads`
Tracks each ingestion attempt.

```sql
CREATE TABLE data_loads (
    load_id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    business_date DATE NOT NULL,
    source_file_path TEXT NOT NULL,
    source_file_type TEXT NOT NULL,  -- 'PDF', 'CSV', 'XLSX'
    parser_version TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'SUCCESS', 'FAILURE', 'PARTIAL'
    records_loaded INTEGER,
    error_message TEXT,
    load_duration_seconds REAL
);

CREATE INDEX idx_data_loads_business_date ON data_loads(business_date);
CREATE INDEX idx_data_loads_status ON data_loads(status);
```

#### `margin_positions`
Daily margin positions by dimension.

```sql
CREATE TABLE margin_positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_id INTEGER NOT NULL,
    business_date DATE NOT NULL,
    clearer TEXT NOT NULL,  -- 'BNP', 'SOCGEN'
    margin_type TEXT NOT NULL,  -- 'INITIAL_MARGIN', 'DAILY_SETTLEMENT', 'CSA', 'TSO'
    entity TEXT,  -- 'CEL', etc.
    counterparty TEXT,  -- For CSA margins
    currency TEXT DEFAULT 'GBP',
    position_value REAL NOT NULL,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (load_id) REFERENCES data_loads(load_id)
);

CREATE INDEX idx_margin_positions_date ON margin_positions(business_date);
CREATE INDEX idx_margin_positions_clearer ON margin_positions(clearer);
CREATE INDEX idx_margin_positions_type ON margin_positions(margin_type);
CREATE UNIQUE INDEX idx_margin_positions_unique 
    ON margin_positions(business_date, clearer, margin_type, entity, counterparty);
```

#### `reconciliation_breaks`
Tracks exceptions and mismatches.

```sql
CREATE TABLE reconciliation_breaks (
    break_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_date DATE NOT NULL,
    break_type TEXT NOT NULL,  -- 'BANK_MISMATCH', 'MISSING_DATA', 'CALCULATION_ERROR'
    severity TEXT NOT NULL,  -- 'HIGH', 'MEDIUM', 'LOW'
    description TEXT NOT NULL,
    expected_value REAL,
    actual_value REAL,
    variance REAL,
    resolved BOOLEAN DEFAULT 0,
    resolved_by TEXT,
    resolved_timestamp DATETIME,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_breaks_date ON reconciliation_breaks(business_date);
CREATE INDEX idx_breaks_resolved ON reconciliation_breaks(resolved);
```

#### `bank_movements` (future, stub for MVP)
Reconciliation target for cash movements.

```sql
CREATE TABLE bank_movements (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_date DATE NOT NULL,
    bank_account TEXT NOT NULL,
    movement_type TEXT NOT NULL,  -- 'MARGIN_CALL', 'MARGIN_RETURN', 'SETTLEMENT'
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'GBP',
    reference TEXT,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bank_movements_date ON bank_movements(business_date);
```

#### `parser_config`
Track parser versions and file format expectations.

```sql
CREATE TABLE parser_config (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file_type TEXT NOT NULL,
    source_identifier TEXT NOT NULL,  -- e.g., 'BNP_MARGIN_PDF', 'SOCGEN_CSV'
    parser_version TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    config_json TEXT,  -- JSON blob with parsing rules
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_parser_config_active ON parser_config(source_identifier, active);
```

---

## Data Ingestion Layer

### Design Principles
- **Parser per file type** - separate PDF, CSV, xlsx parsers
- **Version-aware** - track parser version with each load
- **Fail gracefully** - log errors, don't crash
- **Idempotent** - re-running same file same date should not duplicate

### Component Structure

```
src/
└── ingestion/
    ├── __init__.py
    ├── base_parser.py           # Abstract base parser interface
    ├── pdf_parser.py             # PDF-specific parsing logic
    ├── csv_parser.py             # CSV parsing logic
    ├── xlsx_parser.py            # Excel parsing logic
    ├── file_scanner.py           # Scan network drives for new files
    ├── ingestion_service.py      # Orchestrates parsing and DB insert
    └── parser_registry.py        # Maps file types to parser versions
```

### Key Interfaces

#### `BaseParser` (abstract)

```python
class BaseParser(ABC):
    """Abstract base class for all file parsers."""
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the file."""
        pass
    
    @abstractmethod
    def parse(self, file_path: str, business_date: date) -> List[MarginPosition]:
        """Parse file and return list of margin positions."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return parser version identifier."""
        pass
```

#### `IngestionService`

```python
class IngestionService:
    """Orchestrates data ingestion from files to database."""
    
    def ingest_file(self, file_path: str, business_date: date) -> DataLoad:
        """
        Parse a file and load margin positions into database.
        
        Returns DataLoad object with status and metadata.
        """
        pass
    
    def ingest_all_for_date(self, business_date: date, source_dir: str) -> List[DataLoad]:
        """
        Scan directory, parse all files for a business date.
        """
        pass
```

### Error Handling Strategy

1. **File not found** - Log error, create failed DataLoad record
2. **Parse error** - Log error, save partial data if possible, flag as PARTIAL status
3. **Database constraint violation** - Roll back, log error
4. **Format change detected** - Flag in logs, create reconciliation_break record

---

## Web Application Structure

### Technology Stack
- **Backend**: FastAPI (Python web framework)
- **Frontend**: HTML + vanilla JavaScript + minimal CSS
- **Database**: SQLite
- **Deployment**: Standalone Python application (no Docker for MVP)

### Application Structure

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── positions.py          # Margin position endpoints
│   │   ├── loads.py              # Data load endpoints
│   │   ├── breaks.py             # Reconciliation break endpoints
│   │   └── admin.py              # Admin/config endpoints
│   └── models/
│       ├── __init__.py
│       └── schemas.py            # Pydantic models for API
│
├── database/
│   ├── __init__.py
│   ├── connection.py             # SQLite connection management
│   ├── schema.sql                # Database schema DDL
│   └── migrations/               # Future: schema migrations
│
├── reconciliation/
│   ├── __init__.py
│   ├── reconciliation_engine.py  # Core reconciliation logic
│   └── rules.py                  # Reconciliation rules
│
├── static/
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── app.js
│
├── templates/
│   ├── index.html                # Dashboard
│   ├── positions.html            # View positions
│   ├── compare.html              # Compare two dates
│   ├── loads.html                # Data load history
│   └── breaks.html               # Reconciliation breaks
│
└── config/
    ├── __init__.py
    └── settings.py               # Application configuration
```

### Key API Endpoints

#### Positions
- `GET /api/positions?date={YYYY-MM-DD}` - Get all positions for a date
- `GET /api/positions/compare?date1={}&date2={}` - Compare two dates
- `GET /api/positions/summary?date={}` - Aggregate summary by margin type

#### Data Loads
- `GET /api/loads` - List all data loads (paginated)
- `GET /api/loads/{load_id}` - Get specific load details
- `POST /api/loads/trigger` - Manually trigger ingestion for a date

#### Reconciliation Breaks
- `GET /api/breaks?resolved={true|false}` - List breaks
- `PUT /api/breaks/{break_id}/resolve` - Mark break as resolved

#### Admin
- `GET /api/admin/config` - Get current parser configurations
- `POST /api/admin/config` - Update parser configuration

---

## Key Interfaces Between Components

### 1. Ingestion → Database
- `IngestionService.ingest_file()` returns `DataLoad` object
- `DataLoad` object written to `data_loads` table
- `MarginPosition` objects written to `margin_positions` table
- Transaction-based: all or nothing per file

### 2. Database → API
- API routes query SQLite via `database.connection` module
- Read-only queries for positions, loads, breaks
- Write operations only through ingestion service (except break resolution)

### 3. API → Frontend
- JSON responses following standard REST conventions
- Pydantic schemas for validation
- Error responses with HTTP status codes and messages

### 4. Reconciliation Engine → Database
- Reads `margin_positions` and `bank_movements`
- Calculates expected vs actual movements
- Writes to `reconciliation_breaks` when mismatch detected

### 5. Frontend → API
- Fetch requests from vanilla JavaScript
- No framework dependencies for MVP
- Server-rendered HTML templates with progressive enhancement

---

## Build Plan (Small Increments)

### Increment 1: Database Foundation
**Goal**: Create SQLite database with core schema

1. Write SQL schema in `database/schema.sql`
2. Write `database/connection.py` with connection management
3. Write test to create database and verify tables exist
4. Write test to insert/query sample data

**Test Output**: Database file created, tables queryable

---

### Increment 2: Base Parser Interface
**Goal**: Define parsing abstraction

1. Write `ingestion/base_parser.py` with abstract base class
2. Write `MarginPosition` data class
3. Write test for interface contract (can instantiate, has required methods)

**Test Output**: Parser interface defined, ready for implementations

---

### Increment 3: CSV Parser Implementation
**Goal**: Parse simplest format first (CSV)

1. Write `ingestion/csv_parser.py` implementing BaseParser
2. Use pandas for CSV reading
3. Write tests with sample CSV file
4. Handle parse errors gracefully

**Test Output**: CSV file parsed into MarginPosition objects

---

### Increment 4: Ingestion Service
**Goal**: Orchestrate parsing and database insert

1. Write `ingestion/ingestion_service.py`
2. Implement `ingest_file()` method
3. Create `DataLoad` record on success/failure
4. Write tests with mock parser

**Test Output**: File parsed and stored in database with audit trail

---

### Increment 5: Excel Parser Implementation
**Goal**: Parse xlsx files

1. Write `ingestion/xlsx_parser.py`
2. Use openpyxl for Excel reading
3. Write tests with sample xlsx file
4. Handle multi-sheet workbooks

**Test Output**: Excel file parsed into MarginPosition objects

---

### Increment 6: PDF Parser Implementation
**Goal**: Parse PDF files (most complex)

1. Write `ingestion/pdf_parser.py`
2. Use PyPDF2 or pdfplumber for PDF text extraction
3. Write regex-based extraction logic
4. Write tests with sample PDF
5. Flag format change detection

**Test Output**: PDF file parsed into MarginPosition objects

---

### Increment 7: FastAPI Application Setup
**Goal**: Create web server foundation

1. Write `api/main.py` with FastAPI app
2. Add health check endpoint `GET /health`
3. Configure static file serving
4. Write test to verify server starts and responds

**Test Output**: Server starts, health check returns 200

---

### Increment 8: Positions API Endpoint
**Goal**: Query margin positions via API

1. Write `api/routes/positions.py`
2. Implement `GET /api/positions?date={}`
3. Write Pydantic schema for response
4. Write test with sample database data

**Test Output**: API returns margin positions for a date

---

### Increment 9: Simple Web UI - View Positions
**Goal**: Display positions in browser

1. Write `templates/positions.html`
2. Write `static/js/app.js` to fetch and display data
3. Add basic CSS styling
4. Manual test in browser

**Test Output**: Web page shows margin positions for a date

---

### Increment 10: Compare Two Dates Endpoint
**Goal**: Calculate movements between dates

1. Implement `GET /api/positions/compare?date1={}&date2={}`
2. Calculate differences by dimension
3. Write tests with sample data for two dates

**Test Output**: API returns movement calculation

---

### Increment 11: Compare UI
**Goal**: Web page to compare two dates

1. Write `templates/compare.html`
2. Add date pickers and comparison logic in JavaScript
3. Display movement table
4. Manual test in browser

**Test Output**: Web page shows movements between two dates

---

### Increment 12: Data Loads API and UI
**Goal**: View ingestion history

1. Implement `GET /api/loads`
2. Write `templates/loads.html`
3. Display load status, errors, timestamps
4. Manual test in browser

**Test Output**: Web page shows data load history

---

### Increment 13: Basic Reconciliation Engine
**Goal**: Detect simple breaks

1. Write `reconciliation/reconciliation_engine.py`
2. Implement single reconciliation rule (e.g., total movement equals sum of parts)
3. Write breaks to `reconciliation_breaks` table
4. Write tests with sample data that breaks

**Test Output**: Breaks detected and stored in database

---

### Increment 14: Breaks API and UI
**Goal**: View reconciliation exceptions

1. Implement `GET /api/breaks`
2. Implement `PUT /api/breaks/{break_id}/resolve`
3. Write `templates/breaks.html`
4. Manual test in browser

**Test Output**: Web page shows reconciliation breaks

---

### Increment 15: Manual Trigger for Ingestion
**Goal**: User-initiated data load

1. Implement `POST /api/loads/trigger`
2. Add UI button to trigger load for a date
3. Show progress/result to user
4. Manual test in browser

**Test Output**: User can trigger data load from UI

---

### Increment 16: Configuration Management
**Goal**: Store parser configuration in database

1. Populate `parser_config` table with initial configs
2. Write `api/routes/admin.py` to read/update configs
3. Add simple admin page
4. Manual test in browser

**Test Output**: User can view and update parser configurations

---

### Increment 17: Error Handling Polish
**Goal**: Improve error messages and logging

1. Add structured logging throughout application
2. Improve error messages in UI
3. Add validation for date inputs
4. Manual test error scenarios

**Test Output**: Errors clearly communicated to user

---

### Increment 18: Dashboard Page
**Goal**: Landing page with summary

1. Write `templates/index.html`
2. Show latest business date positions
3. Show recent breaks
4. Show recent loads
5. Manual test in browser

**Test Output**: Dashboard provides at-a-glance view

---

### Increment 19: Integration Testing
**Goal**: End-to-end workflow validation

1. Write integration test: ingest files → query API → verify UI
2. Test with realistic sample files
3. Test error scenarios (missing file, bad format)

**Test Output**: Full workflow works end-to-end

---

### Increment 20: Documentation and Deployment
**Goal**: Make it usable by others

1. Write README with setup instructions
2. Write user guide for web UI
3. Create requirements.txt
4. Document network drive configuration
5. Create simple startup script

**Test Output**: Another user can run the application

---

## Testing Strategy (TDD)

### Test Pyramid

```
        ┌───────────────┐
        │  Manual/E2E   │  (few)
        │   Browser     │
        └───────────────┘
       ┌─────────────────┐
       │   Integration   │  (some)
       │  API + Database │
       └─────────────────┘
      ┌───────────────────┐
      │   Unit Tests      │  (many)
      │  Parser, Logic    │
      └───────────────────┘
```

### Test Types per Increment

- **Database (Increment 1)**: Unit tests for connection, schema creation
- **Parsers (Increments 2-6)**: Unit tests with sample files, mock file system
- **API (Increments 7-16)**: Integration tests with test database, mock parsers
- **UI (Increments 9-18)**: Manual testing in browser (automated UI tests out of scope for MVP)
- **End-to-End (Increment 19)**: Integration tests with real files and database

### Test Data Strategy

- **Fixtures**: Sample PDF, CSV, xlsx files in `tests/fixtures/`
- **Test database**: Separate SQLite file for tests, torn down after each test
- **Mock network drives**: Use local filesystem paths for testing

---

## Configuration Management

### Configuration File: `config/settings.py`

```python
# Application settings
DATABASE_PATH = "./data/margin_reconciliation.db"
NETWORK_DRIVE_PATHS = {
    "bnp_clearer": "//network/share/bnp",
    "socgen": "//network/share/socgen",
    "csa": "//network/share/csa",
}
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/application.log"
API_HOST = "127.0.0.1"
API_PORT = 8000
```

### Environment-Specific Overrides

- Use environment variables to override defaults
- `MARGIN_DB_PATH` environment variable overrides `DATABASE_PATH`
- Allows testing without affecting production database

---

## Deployment Model (MVP)

### Single-User Desktop Application

- **Install Python 3.11+**
- **Install dependencies** from `requirements.txt`
- **Run database init script** to create schema
- **Start FastAPI server** with `uvicorn`
- **Open browser** to `http://localhost:8000`

### Future: Multi-User Server Deployment

- Deploy on internal server (Windows or Linux)
- Add authentication/authorization
- Use SQLite in WAL mode for concurrent access
- Consider migrating to PostgreSQL for true multi-user

---

## Risk Mitigation

### Risk: File Format Changes
**Mitigation**: 
- Parser versioning in database
- Log format mismatches
- Fallback to manual upload
- Config UI to adjust parsing rules

### Risk: Network Drive Access
**Mitigation**:
- Start with manual file upload option
- Add network drive support incrementally
- Document required permissions

### Risk: Data Quality
**Mitigation**:
- Validation rules in parsers
- Reconciliation engine detects breaks
- Manual review workflow for exceptions

### Risk: Performance with Large Datasets
**Mitigation**:
- SQLite sufficient for years of daily data
- Indexes on query columns
- Pagination for large result sets
- Future: archive old data

### Risk: User Adoption
**Mitigation**:
- Keep UI simple and familiar
- Preserve Excel export capability
- Training and documentation
- Iterative feedback

---

## Success Metrics for MVP

### Functional
- Successfully ingest 3+ file types (PDF, CSV, xlsx)
- Store 30+ days of historical data
- Compare any two dates in < 2 seconds
- Detect and display reconciliation breaks

### Non-Functional
- Application startup in < 5 seconds
- API response time < 500ms for typical queries
- Zero data loss on ingestion errors (transaction safety)
- Clear error messages for 90%+ of failure scenarios

### User Experience
- User can complete daily reconciliation in < 10 minutes (vs. 30+ minutes manual)
- User can answer ad-hoc date range questions in < 1 minute (vs. hours in Excel)
- User understands breaks without asking for help

---

## Out of Scope Items (Deferred)

These are valuable but not required for MVP:

1. **Advanced Analytics**
   - Trend charts and visualizations
   - Predictive analytics for margin movements
   - Statistical anomaly detection

2. **Integrations**
   - Direct bank feed integration
   - Trading system integration
   - Email alerting system

3. **Scheduling**
   - Built-in task scheduler
   - Holiday calendar integration
   - Retry logic for failed loads

4. **User Management**
   - Authentication and authorization
   - Role-based access control
   - User activity audit log

5. **Performance Optimization**
   - Database connection pooling
   - Result caching
   - Background job processing

6. **Advanced Reconciliation**
   - Multi-currency support
   - Complex calculation rules
   - Workflow for break resolution approval

7. **Mobile Access**
   - Responsive design
   - Mobile-optimized UI

---

## Technology Choices - Rationale

### SQLite (vs. PostgreSQL, SQL Server)
- **Pro**: Zero configuration, file-based, robust, sufficient for single-user
- **Pro**: Easy backup (copy file)
- **Pro**: No server dependencies
- **Con**: Limited concurrent writes (mitigated by read-heavy workload)
- **Future**: Can migrate to PostgreSQL if multi-user needed

### FastAPI (vs. Flask, Django)
- **Pro**: Modern, fast, built-in async support
- **Pro**: Automatic API documentation (Swagger)
- **Pro**: Pydantic integration for validation
- **Con**: Newer, smaller ecosystem (mitigated by good documentation)

### Vanilla JavaScript (vs. React, Vue)
- **Pro**: No build step, no dependencies
- **Pro**: Fast to develop for simple UI
- **Pro**: Easy to understand for non-frontend developers
- **Con**: Less structured for complex UIs (acceptable for MVP)

### Python Parsers (vs. External Tools)
- **Pro**: Single language stack
- **Pro**: Rich ecosystem for PDF/Excel parsing
- **Pro**: Easy to customize and maintain
- **Con**: Performance (mitigated by batch processing)

---

## Next Steps

1. **Review this design** with stakeholders
2. **Tester** defines acceptance criteria for Increment 1
3. **Builder** implements Increment 1 following TDD

---

*Design complete. Ready for test definition and implementation.*
