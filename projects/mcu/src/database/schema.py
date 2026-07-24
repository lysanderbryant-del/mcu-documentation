"""
Database schema creation and management.
"""

import sqlite3


def create_schema(db_path: str) -> None:
    """
    Create the database schema with all required tables and indexes.

    Args:
        db_path: Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)

    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    # Create data_loads table
    cursor.execute("""
        CREATE TABLE data_loads (
            load_id INTEGER PRIMARY KEY AUTOINCREMENT,
            load_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            business_date DATE NOT NULL,
            source_file_path TEXT NOT NULL,
            source_file_type TEXT NOT NULL,
            parser_version TEXT NOT NULL,
            status TEXT NOT NULL,
            records_loaded INTEGER,
            error_message TEXT,
            load_duration_seconds REAL
        )
    """)

    # Create indexes for data_loads
    cursor.execute("""
        CREATE INDEX idx_data_loads_business_date ON data_loads(business_date)
    """)

    cursor.execute("""
        CREATE INDEX idx_data_loads_status ON data_loads(status)
    """)

    # Create margin_positions table
    cursor.execute("""
        CREATE TABLE margin_positions (
            position_id INTEGER PRIMARY KEY AUTOINCREMENT,
            load_id INTEGER NOT NULL,
            business_date DATE NOT NULL,
            clearer TEXT NOT NULL,
            margin_type TEXT NOT NULL,
            entity TEXT,
            counterparty TEXT,
            base_currency TEXT,
            original_currency TEXT NOT NULL,
            currency_flag INTEGER,
            position_value_native REAL NOT NULL,
            position_value_gbp REAL,
            product TEXT,
            commodity TEXT,
            created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (load_id) REFERENCES data_loads(load_id)
        )
    """)

    # Create indexes for margin_positions
    cursor.execute("""
        CREATE INDEX idx_margin_positions_date ON margin_positions(business_date)
    """)

    cursor.execute("""
        CREATE INDEX idx_margin_positions_clearer ON margin_positions(clearer)
    """)

    cursor.execute("""
        CREATE INDEX idx_margin_positions_type ON margin_positions(margin_type)
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX idx_margin_positions_unique
        ON margin_positions(
            business_date,
            clearer,
            margin_type,
            COALESCE(entity, ''),
            COALESCE(counterparty, ''),
            original_currency,
            COALESCE(product, '')
        )
    """)

    # Create reconciliation_breaks table
    cursor.execute("""
        CREATE TABLE reconciliation_breaks (
            break_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_date DATE NOT NULL,
            break_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            expected_value REAL,
            actual_value REAL,
            variance REAL,
            resolved BOOLEAN DEFAULT 0,
            resolved_by TEXT,
            resolved_timestamp DATETIME,
            created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for reconciliation_breaks
    cursor.execute("""
        CREATE INDEX idx_breaks_date ON reconciliation_breaks(business_date)
    """)

    cursor.execute("""
        CREATE INDEX idx_breaks_resolved ON reconciliation_breaks(resolved)
    """)

    # Create bank_movements table
    cursor.execute("""
        CREATE TABLE bank_movements (
            movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_date DATE NOT NULL,
            bank_account TEXT NOT NULL,
            movement_type TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'GBP',
            reference TEXT,
            created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create index for bank_movements
    cursor.execute("""
        CREATE INDEX idx_bank_movements_date ON bank_movements(business_date)
    """)

    # Create parser_config table
    cursor.execute("""
        CREATE TABLE parser_config (
            config_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file_type TEXT NOT NULL,
            source_identifier TEXT NOT NULL,
            parser_version TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            config_json TEXT,
            effective_from DATE NOT NULL,
            effective_to DATE,
            created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create index for parser_config
    cursor.execute("""
        CREATE INDEX idx_parser_config_active ON parser_config(source_identifier, active)
    """)

    # Create fx_rates table
    cursor.execute("""
        CREATE TABLE fx_rates (
            fx_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_date DATE NOT NULL,
            currency_from TEXT NOT NULL,
            currency_to TEXT DEFAULT 'GBP',
            rate REAL NOT NULL,
            source TEXT,
            created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create unique index for fx_rates
    cursor.execute("""
        CREATE UNIQUE INDEX idx_fx_rates_unique
        ON fx_rates(business_date, currency_from, currency_to)
    """)

    # Create index for fx_rates lookup
    cursor.execute("""
        CREATE INDEX idx_fx_rates_date ON fx_rates(business_date)
    """)

    conn.commit()
    conn.close()
