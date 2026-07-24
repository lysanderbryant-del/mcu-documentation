"""
Test Suite: Base Parser Interface
Increment 2: Base Parser Interface

Tests verify that:
- BaseParser abstract class defines required interface
- Parser implementations must implement all abstract methods
- MarginPosition data class has required fields
"""

import pytest
from abc import ABC


def test_base_parser_is_abstract():
    """
    GIVEN: The BaseParser class exists
    WHEN: Attempting to instantiate it directly
    THEN: TypeError is raised because it's abstract
    """
    from src.ingestion.base_parser import BaseParser

    with pytest.raises(TypeError):
        parser = BaseParser()


def test_base_parser_has_required_methods():
    """
    GIVEN: The BaseParser abstract class
    WHEN: Inspecting its methods
    THEN: It has can_parse, parse, and get_version abstract methods
    """
    from src.ingestion.base_parser import BaseParser

    assert hasattr(BaseParser, 'can_parse')
    assert hasattr(BaseParser, 'parse')
    assert hasattr(BaseParser, 'get_version')


def test_margin_position_dataclass_exists():
    """
    GIVEN: The MarginPosition data class exists
    WHEN: Creating an instance
    THEN: All required fields are present
    """
    from src.ingestion.base_parser import MarginPosition
    from datetime import date

    position = MarginPosition(
        business_date=date(2026, 7, 23),
        clearer='BNP',
        margin_type='INITIAL_MARGIN',
        entity='CEL',
        counterparty=None,
        currency='GBP',
        position_value=1000000.00
    )

    assert position.business_date == date(2026, 7, 23)
    assert position.clearer == 'BNP'
    assert position.margin_type == 'INITIAL_MARGIN'
    assert position.position_value == 1000000.00


def test_parser_implementation_must_implement_all_methods():
    """
    GIVEN: A class inheriting from BaseParser
    WHEN: It doesn't implement all abstract methods
    THEN: TypeError is raised on instantiation
    """
    from src.ingestion.base_parser import BaseParser

    class IncompleteParser(BaseParser):
        def can_parse(self, file_path: str) -> bool:
            return True
        # Missing parse() and get_version()

    with pytest.raises(TypeError):
        parser = IncompleteParser()
