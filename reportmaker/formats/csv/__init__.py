import os
import pandas as pd
from typing import Any
from reportmaker.formats import Document
from reportmaker.config import cmd_args, logger
from reportmaker.formats.xlsx import XlsxDocument
from reportmaker.utils.helpers import get_database_data


class CsvDocument(Document):
    def __init__(self, descriptor: dict):
        """
        Constructor

        :param descriptor: document descriptor
        :type descriptor: dict
        """
        super().__init__(descriptor)
        self._file_name = os.path.join(cmd_args.output, os.path.basename(cmd_args.input).split('.')[0] + '.csv')
        self._data = []

    def create_table(self, table: dict) -> Any:
        """
        Create table

        :param table: table descriptor
        :type table: dict
        """
        data = table.get('data', [])
        if isinstance(data, dict):
            data = get_database_data(cmd_args.database, ''.join(table.get('data').get('sql', '')), logger, cmd_args)
            table['data'] = data
        for string in data:
            self._data.append(string)

    def _create_document(self):
        """
        Create and save document
        """
        max_str_len = 0
        for string in self._data:
            if len(string) > max_str_len:
                max_str_len = len(string)
        for i, string in enumerate(self._data):
            while len(string) < max_str_len:
                string.append('')
            self._data[i] = string
        pd.DataFrame(XlsxDocument.data_to_frame(self._data)).to_csv(self._file_name, index=False)

    def create_paragraph_style(self, style: dict, name: str) -> Any:
        pass
