import os
import pandas as pd
from reportmaker.formats import Document
from reportmaker.utils.helpers import get_database_data
from reportmaker.config import translate as _, logger, cmd_args


class XlsxDocument(Document):
    """
    XLSX document

    See: https://xlsxwriter.readthedocs.io/
         https://xlsxwriter.readthedocs.io/chart.html

    """
    def __init__(self, descriptor: dict):
        """
        Constructor

        :param descriptor: document descriptor
        :type descriptor: dict
        """
        super().__init__(descriptor)
        file_name = os.path.join(cmd_args.output, os.path.basename(cmd_args.input).split('.')[0] + '.xlsx')
        self._writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        self._workbook = self._writer.book
        self._sheets = descriptor.get('document', {}).get('sheets', ['Sheet1'])
        self._max_row, self._max_col = 0, 0
        self._current_sheet = -1
        self._current_frame = None
        self._frame = {}
        self._start_row = 0
        self._start_column = 0
        self._delta_row = 1
        self._styles = {}
        self._table_last_row = 0
        self._table_last_column = 0

    def _create_document(self):
        """
        Create and save document
        """
        self._writer.close()

    def create_style(self, style: dict):
        """
        Create style

        :param style: style descriptor
        :type style: dict
        """
        self._styles[style.get('name', 'default')] = self._workbook.add_format(style.get('parameters', {}))

    def create_paragraph_style(self, style: dict, name: str):
        """
        Create paragraph style

        :param style: style descriptor
        :type style: dict
        :param name: style name
        :type name: str
        """
        pass

    def create_sheet(self, sheet: dict):
        """
        Create sheet

        :param sheet: sheet descriptor
        :type sheet: dict
        """
        self._current_sheet += 1
        if self._current_sheet >= len(self._sheets):
            self._sheets.append(f'Sheet{self._current_sheet + 1}')
        logger.debug(f"{_('new sheet')} '{str(sheet)}' {_('created')}")
        self._start_row = 0

    def create_table(self, table: dict):
        """
        Create table

        :param table: table descriptor
        :type table: dict
        """
        self._delta_row = table.get('delta_row', 0)
        self._start_row = table.get('start_row', self._start_row)
        self._start_column = table.get('start_column', self._start_column)

        # Get database data if sql

        if isinstance(table.get('data', []), dict):
            data = get_database_data(cmd_args.database, ''.join(table.get('data').get('sql', '')), logger, cmd_args)
            self._table_last_row = self._start_row + len(data) - 1
            self._table_last_column = self._start_column + len(data[0]) - 1
            table['data'] = data
        else:
            self._table_last_row = self._start_row + len(table.get('data', [])) - 1
            self._table_last_column = self._start_column + len(table.get('data', [])[0]) - 1

        # Frame to Excel

        frame = self._data_to_frame(table.get('data', []))
        self._current_frame = pd.DataFrame(frame)
        self._max_row, self._max_col = self._current_frame.shape
        self._current_frame.to_excel(self._writer, sheet_name=self._sheets[self._current_sheet], index=False,
                                     startrow=self._start_row + 1, startcol=self._start_column, header=False)

        # Current sheet object

        sheet_obj = self._workbook.sheetnames[self._sheets[self._current_sheet]]

        # Set headers

        for col_number, value in enumerate(table.get('data', [])[:1][0]):
            sheet_obj.write(self._start_row, col_number + self._start_column, value, self._styles.get(
                table.get('header_format', 'default'), 'default'))

        # Cells write to sheet

        for cell in table.get('cells', []):
            if len(cell) != 4 or not isinstance(cell[0], int) or not isinstance(cell[1], int) or \
                    not isinstance(cell[3], str):
                logger.warning(f"{_('cell')} '{str(cell)}' {_('is invalid')}")
                continue
            sheet_obj.write(cell[0], cell[1], cell[2], self._styles.get(cell[3], 'default'))

        # Columns formats

        for cf in table.get('columns_formats', []):
            if len(cf) != 4 or not isinstance(cf[2], int) or not isinstance(cf[3], str):
                logger.warning(f"{_('column format')} '{str(cf)}' {_('is invalid')}")
                continue
            cf[0], cf[1] = self._normalize_column(cf[0]), self._normalize_column(cf[1])
            sheet_obj.set_column(cf[0], cf[1], cf[2], self._styles.get(cf[3], 'default'))

        # Rows formats

        for rf in table.get('rows_formats', []):
            if len(rf) != 3 or not isinstance(rf[1], int) or not isinstance(rf[2], str):
                logger.warning(f"{_('row format')} '{str(rf)}' {_('is invalid')}")
                continue
            rf[0] = self._normalize_row(rf[0])
            if not rf[1]:
                rf[1] = None
            sheet_obj.set_row(rf[0], rf[1], self._styles.get(rf[2], 'default'))

        # Cells formats

        for cf in table.get('cells_formats', []):
            if len(cf) != 5 or not isinstance(cf[4], str):
                logger.warning(f"{_('cell format')} '{str(cf)}' {_('is invalid')}")
                continue
            cf[0], cf[1], cf[2], cf[3] = self._normalize_row(cf[0]), self._normalize_column(cf[1]), \
                self._normalize_row(cf[2]), self._normalize_column(cf[3])
            sheet_obj.conditional_format(cf[0], cf[1], cf[2], cf[3],
                                         {
                                             'type': 'no_errors',
                                             'format': self._styles.get(cf[4], 'default')
                                         })

        self._start_row += len(frame[list(frame.keys())[0]]) + self._delta_row + 1

    def create_image(self, image: dict):
        """
        Create image

        :param image: image attributes
        :type image: dict
        """
        pass

    def create_chart(self, common_chart: dict):
        """
        Create chart

        :param common_chart: chart descriptor
        :type common_chart: dict
        """
        chart = self._workbook.add_chart({'type': common_chart.get('graph', 'column'),
                                          'subtype': common_chart.get('subtype', 'stacked')})
        for seria in common_chart.get('series', []):
            chart.add_series(seria)
        self._writer.sheets[self._sheets[self._current_sheet]].insert_chart(
            common_chart.get('row', 1), common_chart.get('column', 10), chart, common_chart.get('options', None))

    @staticmethod
    def _data_to_frame(data: list) -> dict:
        """
        Convert data to frame

        :param data: data (list of rows)
        :type data: list
        :return: data frame
        :rtype: dict
        """
        frame = {}
        for i in range(len(data)):
            for j in range(len(data[i])):
                if not i:
                    frame[data[i][j]] = []
                else:
                    frame[data[0][j]].append(data[i][j])
        return frame

    def _normalize_column(self, column: int) -> int:
        """
        Column normalization

        :param column: column
        :return: normalized column
        """
        if column == 'last':
            column = self._table_last_column
        if column == 'first':
            column = self._start_column
        if not isinstance(column, int):
            logger.warning(f"{_('column')} '{str(column)}' {_('is not integer')}, {_('set to 0')}")
            column = 0
        return column

    def _normalize_row(self, row: int) -> int:
        """
        Row normalization

        :param row: row
        :return: normalized row
        """
        if row == 'last':
            row = self._table_last_row
        if row == 'first':
            row = self._start_row
        if not isinstance(row, int):
            logger.warning(f"{_('row')} '{str(row)}' {_('is not integer')}, {_('set to 0')}")
            row = 0
        return row
