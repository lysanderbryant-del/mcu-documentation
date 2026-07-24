"""
CSV Parsers - Extract data from each of the 7 source file types
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import date


class ParseError(Exception):
    """Raised when CSV parsing fails."""
    pass


class BNPMCStatementParser:
    """Parse BNP MC_Statement files (CEL or CET)."""

    def parse(self, file_path: Path, business_date: date, entity: str) -> List[Dict[str, Any]]:
        """
        Parse MC_Statement CSV and extract NLV by currency.

        Expected columns:
        - BA: NLV (Net Liquidation Value)
        - AB: ORIGINAL_CURRENCY (EUR/GBP/USD)
        - AA: BASE_CURRENCY (EUR)
        - Z: CURRENCY_1 (filter = 0)

        Args:
            file_path: Path to MC_Statement CSV
            business_date: Business date for this data
            entity: 'CEL' or 'CET'

        Returns:
            List of dicts with margin positions by currency
        """
        try:
            # Read CSV
            df = pd.read_csv(file_path, encoding='utf-8-sig')

            # Map column letters to names (assuming column order)
            # Z=25, AA=26, AB=27, BA=52
            col_map = {
                'CURRENCY_1': df.columns[25] if len(df.columns) > 25 else None,
                'BASE_CURRENCY': df.columns[26] if len(df.columns) > 26 else None,
                'ORIGINAL_CURRENCY': df.columns[27] if len(df.columns) > 27 else None,
                'NLV': df.columns[52] if len(df.columns) > 52 else None,
            }

            # Validate required columns exist
            if None in col_map.values():
                raise ParseError(f"Missing required columns in {file_path.name}")

            # Filter: BASE_CURRENCY = 'EUR' AND CURRENCY_1 = 0
            filtered = df[
                (df[col_map['BASE_CURRENCY']] == 'EUR') &
                (df[col_map['CURRENCY_1']] == 0)
            ]

            # Aggregate by ORIGINAL_CURRENCY
            result = []
            for currency in filtered[col_map['ORIGINAL_CURRENCY']].unique():
                currency_rows = filtered[filtered[col_map['ORIGINAL_CURRENCY']] == currency]
                nlv_sum = currency_rows[col_map['NLV']].sum()

                result.append({
                    'business_date': business_date,
                    'clearer': 'BNP',
                    'entity': entity,
                    'counterparty': 'BNP',
                    'margin_type': 'MARGIN_CALL',
                    'original_currency': currency,
                    'position_value_native': nlv_sum,
                    'source_file': str(file_path),
                })

            return result

        except Exception as e:
            raise ParseError(f"Failed to parse {file_path.name}: {e}")


class BNPOTEDetailParser:
    """Parse BNP Detailed_Open_Pos files."""

    def parse(self, file_path: Path, business_date: date) -> List[Dict[str, Any]]:
        """
        Parse Detailed_Open_Pos CSV for product-level OTE breakdown.

        Aggregates trade-level data to position-level by:
        [PRODUCT, CURRENCY, MATURITY_DATE]

        Args:
            file_path: Path to Detailed_Open_Pos CSV
            business_date: Business date for this data

        Returns:
            List of dicts with OTE positions by product (aggregated)
        """
        try:
            # Read large file with low_memory=False to handle mixed types
            df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
            df.columns = df.columns.str.strip()

            # Map actual column names to expected names
            column_mapping = {
                'ORIGINAL_CURRENCY': 'CURRENCY',
                'MAT_DATE': 'MATURITY_DATE'
            }

            # Check required columns exist (before renaming)
            required = ['PRODUCT', 'ORIGINAL_CURRENCY', 'MAT_DATE', 'OTE']
            missing = [col for col in required if col not in df.columns]
            if missing:
                raise ParseError(f"Missing columns: {missing}. Found: {list(df.columns[:20])}")

            # Rename for consistency
            df = df.rename(columns=column_mapping)

            # Aggregate by key columns to avoid duplicates
            group_cols = ['PRODUCT', 'CURRENCY', 'MATURITY_DATE']

            # Aggregate trades to positions
            aggregated = df.groupby(group_cols, dropna=False).agg({
                'OTE': 'sum'
            }).reset_index()

            # Transform to output format
            result = []
            for _, row in aggregated.iterrows():
                result.append({
                    'business_date': business_date,
                    'clearer': 'BNP',
                    'entity': 'CEL',
                    'margin_type': 'OTE',
                    'counterparty': 'BNP',
                    'product_name': row['PRODUCT'],
                    'original_currency': row['CURRENCY'],
                    'position_value_native': row['OTE'],
                    'maturity_date': str(row['MATURITY_DATE']) if pd.notna(row['MATURITY_DATE']) else None,
                    'source_file': str(file_path),
                })

            return result

        except Exception as e:
            raise ParseError(f"Failed to parse {file_path.name}: {e}")


class BNPJournalEntriesParser:
    """Parse BNP Journal_Entries files."""

    def parse(self, file_path: Path, business_date: date) -> Dict[str, Any]:
        """
        Parse Journal_Entries CSV for spot/physical delivery total.

        Based on analyst findings:
        - Column 7: DEBIT_AMOUNT
        - Column 8: CREDIT_AMOUNT
        - Column 11: PAYMENT_TYPE
        - Filter: PAYMENT_TYPE IN ('PC', 'DLV')
        - Formula: ABS(SUM(DEBIT) - SUM(CREDIT))

        Args:
            file_path: Path to Journal_Entries CSV
            business_date: Business date for this data

        Returns:
            Dict with spot/physical delivery total in EUR
        """
        try:
            # Read CSV, header at row 1
            df = pd.read_csv(file_path, encoding='utf-8-sig', skiprows=0)

            # Validate structure
            if len(df.columns) < 12:
                raise ParseError(f"Insufficient columns: expected 12+, got {len(df.columns)}")

            # Get column references (0-indexed)
            debit_col = df.columns[7]      # Column 7: DEBIT_AMOUNT
            credit_col = df.columns[8]     # Column 8: CREDIT_AMOUNT
            payment_type_col = df.columns[11]  # Column 11: PAYMENT_TYPE

            # Filter for spot/physical transactions (PC = Payment Commodity, DLV = Physical Delivery)
            mask = df[payment_type_col].isin(['PC', 'DLV'])
            filtered = df[mask]

            # Calculate net EUR amount (debit - credit, take absolute)
            debit_sum = pd.to_numeric(filtered[debit_col], errors='coerce').fillna(0).sum()
            credit_sum = pd.to_numeric(filtered[credit_col], errors='coerce').fillna(0).sum()
            net_eur = abs(debit_sum - credit_sum)

            return {
                'business_date': business_date,
                'clearer': 'BNP',
                'entity': 'CEL',
                'margin_type': 'SPOT_PHYSICAL',
                'position_value_native': float(net_eur),
                'original_currency': 'EUR',
                'source_file': str(file_path),
            }

        except Exception as e:
            raise ParseError(f"Failed to parse {file_path.name}: {e}")


class BNPPnSParser:
    """Parse BNP PnS (P&L cascade) files."""

    def parse(self, file_path: Path, business_date: date) -> Dict[str, Any]:
        """
        Parse PnS CSV for cascading P&L total.

        Expected columns (from header row 10):
        - COB Date (Column C)
        - Clearer (Column H)
        - Party (Column J)
        - Product Type (Column M)
        - Product (Column N)
        - P&L Amount (needs identification)

        Args:
            file_path: Path to PnS CSV
            business_date: Business date for this data

        Returns:
            Dict with cascade P&L total
        """
        try:
            # Read CSV, header at row 10
            df = pd.read_csv(file_path, encoding='utf-8-sig', skiprows=9)

            # Find P&L column (look for column with "PNL" or "P&L" in name)
            pnl_col = None
            for col in df.columns:
                if 'PNL' in col.upper() or 'P&L' in col.upper():
                    pnl_col = col
                    break

            if pnl_col is None:
                # Fallback: assume last numeric column
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                pnl_col = numeric_cols[-1] if len(numeric_cols) > 0 else None

            total = df[pnl_col].sum() if pnl_col else 0

            return {
                'business_date': business_date,
                'clearer': 'BNP',
                'entity': 'CEL',
                'margin_type': 'CASCADE_PNL',
                'position_value_native': total,
                'original_currency': 'EUR',  # Assumed
                'source_file': str(file_path),
            }

        except Exception as e:
            raise ParseError(f"Failed to parse {file_path.name}: {e}")


class SocGenMarginParser:
    """Parse SocGen Global Margin Report."""

    def parse(self, file_path: Path, business_date: date) -> Dict[str, Any]:
        """
        Parse SocGen GlobalMarginUnderlyingCurrencyReport CSV.

        Note: File structure unknown - needs investigation.
        Assuming single margin value somewhere in the file.

        Args:
            file_path: Path to SocGen CSV
            business_date: Business date for this data

        Returns:
            Dict with SocGen margin value
        """
        try:
            # Check if file is empty
            if file_path.stat().st_size == 0:
                margin_value = 0.0
            else:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                # Placeholder: extract single margin value
                # TODO: Determine actual column/row structure
                margin_value = 0.0  # Default to zero until structure known

            return {
                'business_date': business_date,
                'clearer': 'SOCGEN',
                'entity': 'CEL',
                'margin_type': 'MARGIN_CALL',
                'position_value_native': margin_value,
                'original_currency': 'EUR',  # Assumed
                'source_file': str(file_path),
            }

        except Exception as e:
            raise ParseError(f"Failed to parse {file_path.name}: {e}")


class CSACollateralParser:
    """Parse CSA Collateral Summary files."""

    def parse(self, file_path: Path, business_date: date) -> List[Dict[str, Any]]:
        """
        Parse Collateral_Summary CSV.

        Based on analyst findings:
        - Header on line 1 (skiprows=0, NOT 6)
        - Columns: Collateral_Held, Collateral_Pledged (NOT HeldGbpM/PledgedGbpM)
        - Entity: 'Centrica Energy Trading A/S' (includes A/S suffix)
        - Values: Already in native units (NO scaling by 1M)

        Args:
            file_path: Path to CSA CSV
            business_date: Business date for this data

        Returns:
            List of dicts with CSA collateral by entity and currency
        """
        try:
            # Check if file is empty
            if file_path.stat().st_size == 0:
                return []  # Return empty list for empty file

            # Read CSV - CORRECTED: header on line 1, not line 7
            df = pd.read_csv(file_path, encoding='utf-8-sig', skiprows=0)

            # Validate required columns exist
            required_columns = ['Our_Entity', 'Collateral_Held', 'Collateral_Pledged', 'Reporting_Currency']
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                raise ParseError(f"Missing columns: {missing}. Found: {list(df.columns)}")

            # Map entity names - CORRECTED: include A/S suffix
            entity_map = {
                'Centrica Energy Limited': 'CEL',
                'Centrica Energy Trading A/S': 'CET',
            }

            # Filter for Centrica entities
            df_centrica = df[df['Our_Entity'].isin(entity_map.keys())]

            if len(df_centrica) == 0:
                return []  # No Centrica data found

            # Calculate net collateral (held - pledged) - NO SCALING
            df_centrica = df_centrica.copy()
            df_centrica['net_collateral'] = (
                df_centrica['Collateral_Held'] - df_centrica['Collateral_Pledged']
            )

            # Aggregate by entity and currency
            aggregated = df_centrica.groupby([
                'Our_Entity',
                'Reporting_Currency'
            ]).agg({
                'net_collateral': 'sum',
                'Trading_Counterparty': lambda x: ', '.join(x.unique())
            }).reset_index()

            # Transform to output format
            result = []
            for _, row in aggregated.iterrows():
                result.append({
                    'business_date': business_date,
                    'clearer': 'CSA',
                    'entity': entity_map[row['Our_Entity']],
                    'margin_type': 'COLLATERAL',
                    'counterparty': row['Trading_Counterparty'],
                    'original_currency': row['Reporting_Currency'],
                    'position_value_native': row['net_collateral'],  # Already in native units
                    'source_file': str(file_path),
                })

            return result

        except Exception as e:
            raise ParseError(f"Failed to parse {file_path.name}: {e}")


class ParserFactory:
    """Factory to get appropriate parser for each file type."""

    @staticmethod
    def get_parser(file_type: str):
        """
        Get parser instance for a file type.

        Args:
            file_type: One of 'bnp_cel_mc', 'bnp_cet_mc', 'bnp_cel_ote',
                      'bnp_cel_jnls', 'bnp_cel_pns', 'socgen', 'csa'

        Returns:
            Parser instance

        Raises:
            ValueError: If file type is unknown
        """
        parsers = {
            'bnp_cel_mc': BNPMCStatementParser(),
            'bnp_cet_mc': BNPMCStatementParser(),
            'bnp_cel_ote': BNPOTEDetailParser(),
            'bnp_cel_jnls': BNPJournalEntriesParser(),
            'bnp_cel_pns': BNPPnSParser(),
            'socgen': SocGenMarginParser(),
            'csa': CSACollateralParser(),
        }

        if file_type not in parsers:
            raise ValueError(f"Unknown file type: {file_type}")

        return parsers[file_type]
