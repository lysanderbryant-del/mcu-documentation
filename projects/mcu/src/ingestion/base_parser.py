"""
Base parser interface and data models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class MarginPosition:
    """
    Data class representing a single margin position.
    """
    business_date: date
    clearer: str
    margin_type: str
    entity: Optional[str]
    counterparty: Optional[str]
    currency: str
    position_value: float


class BaseParser(ABC):
    """
    Abstract base class for all file parsers.
    """

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            bool: True if this parser can handle the file, False otherwise
        """
        pass

    @abstractmethod
    def parse(self, file_path: str, business_date: date) -> List[MarginPosition]:
        """
        Parse file and return list of margin positions.

        Args:
            file_path: Path to the file to parse
            business_date: Business date for the positions

        Returns:
            List[MarginPosition]: List of parsed margin positions
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        Return parser version identifier.

        Returns:
            str: Version identifier for this parser
        """
        pass
