from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(slots=True)
class Transaction:
    date: date
    description: str
    amount: Decimal
    original_amount_str: str = ""
    reference: str = ""
    category: str = ""
    page_number: int = 0


@dataclass(slots=True)
class ExtractionResult:
    transactions: list[Transaction]
    warnings: list[str]
    source_file: str
    pages_processed: int
