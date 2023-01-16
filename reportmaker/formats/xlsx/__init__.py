import os
import pandas as pd
from typing import Any
from reportmaker.formats import Document
from reportmaker.config import translate as _, logger, cmd_args


class XlsxDocument(Document):
    def __init__(self, descriptor: dict):
        super().__init__(descriptor)
        file_name = os.path.join(cmd_args.output, os.path.basename(cmd_args.input).split('.')[0] + '.xlsx')
        self._writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

    def create_table_style(self, style: dict, name: str) -> Any:
        pass

    def create_paragraph(self, paragraph: dict) -> Any:
        pass

    def create_table(self, table: dict) -> Any:
        pd.DataFrame(self._data_to_frame(table.get('data', []))).to_excel(
            self._writer, sheet_name="Sheet1", index=False)

    def create_image(self, image: dict) -> Any:
        pass

    def create_pie(self, pie: dict) -> Any:
        pass

    def create_slice(self, sl: dict) -> dict:
        pass

    def create_line(self, line: dict) -> dict:
        pass

    def create_horizontal_line_chart(self, line_chart: dict) -> Any:
        pass

    def create_line_plot(self, line_plot: dict) -> Any:
        pass

    def create_vertical_bar_chart(self, bar_chart: dict) -> Any:
        pass

    def create_spacer(self, spacer: dict) -> Any:
        pass

    def _create_document(self):
        self._writer.close()

    def create_paragraph_style(self, style: dict, name: str) -> Any:
        pass

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
