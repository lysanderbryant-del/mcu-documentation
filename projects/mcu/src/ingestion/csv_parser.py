"""
CSV parser implementation for margin data files.
"""

import pandas as pd
from datetime import date
from typing import List
from pathlib import Path

from src.ingestion.base_parser import BaseParser, MarginPosition


class CSVParser(BaseParser):
    """
    Parser for CSV format margin data files.
    """

    def __init__(self):
        """Initialize CSV parser."""
        self.version = "1.0.0"

    def can_parse(self, file_path: str) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            bool: True if file has .csv extension, False otherwise
        """
        return file_path.lower().endswith('.csv')

    def parse(self, file_path: str, business_date: date) -> List[MarginPosition]:
        """
        Parse CSV file and return list of margin positions.

        Args:
            file_path: Path to the CSV file to parse
            business_date: Business date for the positions

        Returns:
            List[MarginPosition]: List of parsed margin positions

        Raises:
            Exception: If required columns are missing or data is invalid
        """
        # Read CSV file
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise Exception(f"Failed to read CSV file: {e}")

        # Check for required columns
        required_columns = ['clearer', 'margin_type', 'position_value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise Exception(f"Required columns missing: {', '.join(missing_columns)}")

        # Handle empty file
        if len(df) == 0:
            return []

        # Parse each row into MarginPosition
        positions = []
        for idx, row in df.iterrows():
            try:
                # Convert position_value to float
                position_value = float(row['position_value'])
            except (ValueError, TypeError) as e:
                raise Exception(f"Invalid numeric value in row {idx + 1}: position_value must be numeric")

            # Extract fields (use .get() for optional fields)
            position = MarginPosition(
                business_date=business_date,
                clearer=str(row['clearer']),
                margin_type=str(row['margin_type']),
                entity=str(row['entity']) if 'entity' in row and pd.notna(row['entity']) else None,
                counterparty=str(row['counterparty']) if 'counterparty' in row and pd.notna(row['counterparty']) else None,
                currency=str(row['currency']) if 'currency' in row and pd.notna(row['currency']) else 'GBP',
                position_value=position_value
            )
            positions.append(position)

        return positions

    def get_version(self) -> str:
        """
        Return parser version identifier.

        Returns:
            str: Version identifier for this parser
        """
        return self.version
