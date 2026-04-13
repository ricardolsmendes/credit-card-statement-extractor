"""Transaction frozen dataclass."""

import dataclasses
import datetime
import decimal


@dataclasses.dataclass(frozen=True)
class Transaction:
    """A single financial event parsed from a credit card statement.

    Attributes:
        date: Transaction date.
        description: Merchant name or transaction narrative (non-empty).
        amount: Positive for purchases/charges; negative for payments/credits.
    """

    date: datetime.date
    description: str
    amount: decimal.Decimal

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Transaction description must not be empty.")
