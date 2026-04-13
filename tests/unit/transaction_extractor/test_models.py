"""Unit tests for Transaction frozen dataclass (T005)."""

import dataclasses
import datetime
import decimal

import pytest

from credit_card_statement_extractor.transaction_extractor._models import Transaction


class TestTransactionConstruction:
    def test_valid_construction(self) -> None:
        txn = Transaction(
            date=datetime.date(2026, 3, 1),
            description="Coffee Shop",
            amount=decimal.Decimal("-4.50"),
        )
        assert txn.date == datetime.date(2026, 3, 1)
        assert txn.description == "Coffee Shop"
        assert txn.amount == decimal.Decimal("-4.50")

    def test_amount_stored_as_decimal(self) -> None:
        txn = Transaction(
            date=datetime.date(2026, 3, 1),
            description="Coffee Shop",
            amount=decimal.Decimal("500.00"),
        )
        assert isinstance(txn.amount, decimal.Decimal)

    def test_negative_amount_accepted(self) -> None:
        txn = Transaction(
            date=datetime.date(2026, 3, 1),
            description="Gas Station",
            amount=decimal.Decimal("-89.50"),
        )
        assert txn.amount == decimal.Decimal("-89.50")

    def test_empty_description_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                date=datetime.date(2026, 3, 1),
                description="",
                amount=decimal.Decimal("-4.50"),
            )

    def test_whitespace_only_description_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                date=datetime.date(2026, 3, 1),
                description="   ",
                amount=decimal.Decimal("-4.50"),
            )

    def test_frozen_dataclass_mutation_raises(self) -> None:
        txn = Transaction(
            date=datetime.date(2026, 3, 1),
            description="Coffee Shop",
            amount=decimal.Decimal("-4.50"),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            txn.description = "Something else"  # type: ignore[misc]

    def test_is_frozen_dataclass(self) -> None:
        assert dataclasses.is_dataclass(Transaction)
        fields = dataclasses.fields(Transaction)
        assert any(f.name == "date" for f in fields)
        assert any(f.name == "description" for f in fields)
        assert any(f.name == "amount" for f in fields)
