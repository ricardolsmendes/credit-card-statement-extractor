from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from credit_card_extractor.models import ExtractionResult, Transaction

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PDF_FIXTURES_DIR = FIXTURES_DIR / "pdfs"


@pytest.fixture
def sample_transactions() -> list[Transaction]:
    return [
        Transaction(
            date=date(2024, 3, 15),
            description="SUPERMERCADO ABC",
            amount=Decimal("-125.40"),
            original_amount_str="-125,40",
            page_number=1,
        ),
        Transaction(
            date=date(2024, 3, 16),
            description="POSTO SHELL",
            amount=Decimal("-80.00"),
            original_amount_str="R$ 80,00",
            page_number=1,
        ),
        Transaction(
            date=date(2024, 3, 20),
            description="AMAZON.COM",
            amount=Decimal("1234.56"),
            original_amount_str="1,234.56",
            page_number=2,
        ),
    ]


@pytest.fixture
def sample_result(sample_transactions, tmp_path) -> ExtractionResult:
    return ExtractionResult(
        transactions=sample_transactions,
        warnings=[],
        source_file=str(tmp_path / "test.pdf"),
        pages_processed=2,
    )


@pytest.fixture
def result_with_warnings(sample_transactions, tmp_path) -> ExtractionResult:
    return ExtractionResult(
        transactions=sample_transactions,
        warnings=["Page 1: could not parse amount 'n/a'"],
        source_file=str(tmp_path / "test.pdf"),
        pages_processed=1,
    )
