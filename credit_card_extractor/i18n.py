from enum import StrEnum


class Language(StrEnum):
    EN = "en"
    PT = "pt"


HEADERS: dict[str, dict[str, str]] = {
    Language.EN: {
        "date": "Date",
        "description": "Description",
        "amount": "Amount",
        "reference": "Reference",
        "category": "Category",
    },
    Language.PT: {
        "date": "Data",
        "description": "Descrição",
        "amount": "Valor",
        "reference": "Referência",
        "category": "Categoria",
    },
}

DEFAULT_COLUMNS: list[str] = ["date", "description", "amount"]
EXTENDED_COLUMNS: list[str] = ["date", "description", "amount", "reference", "category"]


def get_headers(language: Language, columns: list[str] = DEFAULT_COLUMNS) -> list[str]:
    return [HEADERS[language][col] for col in columns]
