"""TransactionParser protocol — structural interface for pluggable parsers."""

from typing import Protocol, runtime_checkable

from credit_card_statement_extractor.pdf_reader._protocol import PageResult
from credit_card_statement_extractor.transaction_extractor._models import Transaction


@runtime_checkable
class TransactionParser(Protocol):
    """Structural interface for statement parsers.

    To support a new statement format, implement this protocol and pass the
    new parser to the CLI (or extend DefaultParser with additional headers).

    Note: The return type is ``tuple[list[Transaction], int]`` where the int
    represents the number of lines that could not be parsed (US3 / T024).
    This protocol reflects the final signature after T024 applies.
    """

    def parse(self, pages: list[PageResult]) -> tuple[list[Transaction], int]: ...
