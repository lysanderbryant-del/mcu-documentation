"""
Database connection management.
"""

import sqlite3


class DatabaseConnection:
    """
    Manages SQLite database connections with foreign key constraint support.
    """

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        # Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")

    def get_cursor(self):
        """
        Get a cursor for executing SQL commands.

        Returns:
            sqlite3.Cursor: Database cursor
        """
        return self.conn.cursor()

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def rollback(self):
        """Roll back the current transaction."""
        self.conn.rollback()

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def store_fx_rate(self, business_date, currency_from, currency_to, rate, source):
        """
        Store FX rate in database (upsert).

        Args:
            business_date: Date for the rate
            currency_from: Source currency (e.g., 'EUR')
            currency_to: Target currency (e.g., 'GBP')
            rate: Exchange rate
            source: Source of the rate (e.g., 'ECB_API', 'Manual')
        """
        cursor = self.get_cursor()
        cursor.execute("""
            INSERT INTO fx_rates (business_date, currency_from, currency_to, rate, source)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(business_date, currency_from, currency_to)
            DO UPDATE SET rate=excluded.rate, source=excluded.source
        """, (business_date, currency_from, currency_to, rate, source))
        self.commit()

    def get_fx_rate(self, business_date, currency_from, currency_to='GBP'):
        """
        Get FX rate for a specific date and currency pair.

        Args:
            business_date: Date to get rate for
            currency_from: Source currency
            currency_to: Target currency (default 'GBP')

        Returns:
            float: Exchange rate, or None if not found
        """
        cursor = self.get_cursor()
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE business_date = ? AND currency_from = ? AND currency_to = ?
        """, (business_date, currency_from, currency_to))

        result = cursor.fetchone()
        return result[0] if result else None

    def store_margin_position(self, business_date, clearer, margin_type, entity,
                             counterparty, original_currency, position_value_native,
                             position_value_gbp, product=None, commodity=None,
                             load_id=1, **kwargs):
        """
        Store margin position in database.

        Args:
            business_date: Business date for position
            clearer: Clearer name (BNP, SOCGEN, CSA)
            margin_type: Type of margin (MARGIN_CALL, COLLATERAL, etc.)
            entity: Entity (CEL, CET)
            counterparty: Counterparty name
            original_currency: Original currency of position
            position_value_native: Value in original currency
            position_value_gbp: Value converted to GBP
            product: Product name (optional)
            commodity: Commodity type (optional)
            load_id: Load ID from data_loads table (defaults to 1 for manual loads)
            **kwargs: Additional args (ignored for compatibility)
        """
        cursor = self.get_cursor()
        cursor.execute("""
            INSERT INTO margin_positions (
                business_date, clearer, margin_type, entity, counterparty,
                original_currency, position_value_native, position_value_gbp,
                product, commodity, load_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_date, clearer, margin_type, entity, counterparty,
            original_currency, position_value_native, position_value_gbp,
            product, commodity, load_id
        ))
        self.commit()
