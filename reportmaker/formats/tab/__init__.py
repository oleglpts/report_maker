import json
from reportmaker.formats import Document
from reportmaker.config import cmd_args, logger
from reportmaker.utils.helpers import get_database_data


class TabDocument(Document):
    def __init__(self, descriptor: dict):
        """
        Constructor

        :param descriptor: document descriptor
        :type descriptor: dict
        """
        super().__init__(descriptor)
        self._data = None

    def create_table(self, table: dict):
        """
        Create table

        :param table: table descriptor
        :type table: dict
        """
        data = table.get('data', [])
        if isinstance(data, dict):
            data = get_database_data(cmd_args.database, ''.join(table.get('data').get('sql', '')), logger, cmd_args)
            table['data'] = data
        self._data = data[1:]

    def _create_document(self):
        """
        Create and save document
        """
        tab = {"data": []}
        for string in self._data:
            tab['data'].append([str(x) for x in string])
        with open(self._file_name, 'w') as output:
            json.dump(tab, output, ensure_ascii=False, indent=4)
