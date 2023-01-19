from typing import Any

from reportmaker.formats import Document

"""
{
    "data": [
        [
            "Capitan K / Domiseda / 1000-1063889856 / 1 / 1 / 3 / DECLINE",
            "Mastercard / IT",
            "529559******2952",
            "SALE / DECL / 538987",
            "45.00",
            "EUR",
            "2023-01-19 09:39:48"
        ],
        [
            "Capitan K / Domiseda / 1000-1063887342 / 1 / 1 / 3 / CHARGE",
            "Mastercard / FR",
            "539125******8555",
            "SALE / PERM / 538975",
            "43.00",
            "EUR",
            "2023-01-19 09:11:32"
        ]
    ]
}
"""


class TabDocument(Document):
    def create_table(self, table: dict):
        pass

    def _create_document(self):
        pass

    def create_paragraph_style(self, style: dict, name: str) -> Any:
        pass
