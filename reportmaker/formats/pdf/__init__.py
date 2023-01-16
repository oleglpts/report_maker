import os
import uuid

from reportmaker.formats import Document
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF, renderPM
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.renderPDF import GraphicsFlowable
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.piecharts import Pie, Drawing
from reportmaker.config import translate as _, logger, cmd_args
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, TableStyle, Table, Image, Spacer
from reportmaker.formats.pdf.maps import ParagraphStyleMap, TableStyleMap, TableMap, SliceMap,\
    HorizontalLineChartMap, LineMap, LabelMap, CategoryAxisMap, ValueAxisMap, CircleMap

# Register fonts
pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))


class PdfDocument(Document):
    """
    PDF document
    """

    def _create_document(self):
        """
        Create and save document
        """
        filename = os.path.basename(cmd_args.input).split('.')[0] + '.pdf'
        SimpleDocTemplate(os.path.join(cmd_args.output, filename)).build(self._layout)

    # public

    def create_paragraph(self, paragraph: dict) -> Paragraph:
        """
        Create paragraph

        :param paragraph: paragraph descriptor
        :type paragraph: dict
        :return: paragraph object
        :rtype: Paragraph
        """
        return Paragraph(paragraph.get('text', 'There is not text'),
                         self._styles.get(paragraph.get('style', 'default')))

    def create_paragraph_style(self, style: dict, name: str) -> ParagraphStyle:
        """
        Create paragraph style

        :param style: style descriptor
        :type style: dict
        :param name: style name
        :type name: str
        :return: paragraph style object
        :rtype: ParagraphStyle
        """
        parent = None
        if style.get('parent_stylesheet', None) == 'sample':
            parent = getSampleStyleSheet()[style['parent_name'] if 'parent_name' in style else 'Normal']
        elif 'parent_name' in style:
            if style['parent_name'] in self._styles:
                parent = self._styles[style['parent_name']]
            else:
                logger.warning(f"{_('parent style')} '{style['parent_name']}' {_('for style')} "
                               f"'{name}' {_('not exists')}")
        return self.set_attributes(style, ParagraphStyle(name, parent=parent) if parent else ParagraphStyle(name),
                                   ParagraphStyleMap.key_map, ParagraphStyleMap.value_map)

    def create_table(self, table: dict) -> Table:
        """
        Create paragraph

        :param table: table descriptor
        :type table: dict
        :return: table object
        :rtype: Table
        """
        style = table.get('style', 'simple_table')
        row_heights = table.get('rowHeights', None)
        col_widths = table.get('colWidths', None)
        row_split_range = table.get('rowSplitRange', None)
        space_before = table.get('spaceBefore', None)
        space_after = table.get('spaceAfter', None)
        return self.set_attributes(
            table,
            Table(
                table.get('data', []),
                style=self._styles.get(style) if isinstance(style, str) else style,
                rowHeights=row_heights if row_heights else None,
                colWidths=col_widths if col_widths else None,
                rowSplitRange=row_split_range if row_split_range else None,
                spaceBefore=space_before if space_before else None,
                spaceAfter=space_after if space_after else None,
                repeatRows=table.get('repeatRows', 0),
                splitByRow=table.get('splitByRow', 1),
                repeatCols=table.get('repeatCols', 0)
            ),
            TableMap.key_map,
            TableMap.value_map
        )

    def create_table_style(self, style: dict, name: str) -> TableStyle:
        """
        Create table style

        :param style: style descriptor
        :type style: dict
        :param name: style name
        :type name: str
        :return: table style object
        :rtype: TableStyle
        """
        parent = None
        if 'parent' in style:
            parent = TableStyleMap.value_map.get('parent', {}).get(style['parent'], None)
            if not parent:
                logger.warning(f"{_('parent style')} '{style['parent_name']}' {_('for style')} "
                               f"'{name}' {_('not exists')}")
        if 'parent_name' in style:
            if style['parent_name'] in self._styles:
                parent = self._styles[style['parent_name']]
            else:
                logger.warning(f"{_('parent style')} '{style['parent_name']}' {_('for style')} "
                               f"'{name}' {_('not exists')}")
        return self.set_attributes(style, TableStyle(parent=parent) if parent else TableStyle(),
                                   TableStyleMap.key_map, TableStyleMap.value_map)

    def create_pie(self, pie: dict, render_to_file: bool = False) -> GraphicsFlowable or str:
        """
        Create pie chart

        :param pie: pie parameters
        :type pie: dict
        :param render_to_file: if True, render drawing to file
        :type render_to_file: bool
        :return: pie object ot PNG file name
        :rtype: GraphicsFlowable or str
        """
        pie_obj = Pie()
        attrs_dict = {'drawing': {}, 'slices': [], 'style': {}}
        attrs_list = ['drawing', 'slices', 'style']
        self._set_attrs(pie, pie_obj, attrs_dict, attrs_list)
        for attr in attrs_list:
            if attr == 'style':
                for part in self.create_slice(attrs_dict[attr]):
                    if hasattr(pie_obj.slices, part) and attrs_dict[attr][part] != 'None':
                        setattr(pie_obj.slices, part, attrs_dict[attr][part])
                    if hasattr(pie_obj, part) and attrs_dict[attr][part] != 'None':
                        setattr(pie_obj, part, attrs_dict[attr][part])
            if attr == 'slices':
                for i, part in enumerate(attrs_dict[attr]):
                    index = part['number'] if 'number' in part else i
                    for slice_attr, slice_attr_value in part.items():
                        if hasattr(pie_obj.slices[index], slice_attr):
                            setattr(pie_obj.slices[index], slice_attr, slice_attr_value)
        return self._get_result(attrs_dict['drawing'], pie_obj, pie, render_to_file)

    def create_image(self, image: dict) -> Image:
        """
        Create image

        :param image: image attributes
        :type image: dict
        :return: image object
        :rtype: Image
        """
        return self.set_attributes(image, Image(image.get('data', '')), {}, {})

    def create_spacer(self, spacer: dict) -> Spacer:
        """
        Create spacer

        :param spacer: spacer attributes
        :type spacer: dict
        :return: spacer object
        :rtype: Spacer
        """
        return Spacer(spacer.get('width', 0), spacer.get('height', 0))

    def create_slice(self, sl: dict) -> dict:
        """
        Create mapped slice attributes for pie chart

        :param sl: slice attributes
        :type sl: dict
        :return: mapped slice attributes
        :rtype: dict
        """
        for key, value in sl.items():
            if key in SliceMap.value_map and value in SliceMap.value_map[key]:
                sl[key] = SliceMap.value_map[key][value]
        return sl

    def create_line(self, line: dict) -> dict:
        """
        Create mapped line attributes for line chart

        :param line: line attributes
        :type line: dict
        :return: mapped line attributes
        :rtype: dict
        """
        for key, value in line.items():
            if key in LineMap.value_map and value in LineMap.value_map[key]:
                line[key] = LineMap.value_map[key][value]
        return line

    def create_horizontal_line_chart(self, line_chart: dict, render_to_file: bool = False) -> GraphicsFlowable or str:
        """
        Create horizontal line chart

        :param line_chart: horizontal_line_chart parameters
        :type line_chart: dict
        :param: render_to_file: if True, render drawing to file
        :type render_to_file: bool
        :return: rendered drawing
        :rtype: GraphicsFlowable or str
        """
        chart_obj = HorizontalLineChart()
        attrs_dict = {'drawing': {}, 'categoryAxis': {}, 'valueAxis': {}, 'lines': [], 'lineLabels': [],
                      'categoryAxisLabels': []}
        attrs_list = ['drawing', 'categoryAxis', 'valueAxis', 'strokeColor', 'lines', 'lineLabels',
                      'categoryAxisLabels']
        self._set_attrs(line_chart, chart_obj, attrs_dict, attrs_list)
        for attr in attrs_list:
            if attr == 'lines':
                for i, line in enumerate(chart_obj.lines):
                    if i >= len(attrs_dict[attr]):
                        break
                    for key, value in attrs_dict[attr][i].items():
                        if hasattr(chart_obj.lines[i], key):
                            setattr(chart_obj.lines[i], key, value)
            if attr == 'lineLabels':
                self._set_labels(attr, attrs_dict, chart_obj)
            self._set_axis(attr, attrs_dict, chart_obj)
        return self._get_result(attrs_dict['drawing'], chart_obj, line_chart, render_to_file)

    def create_line_plot(self, line_plot: dict, render_to_file: bool = False) -> GraphicsFlowable or str:
        """
        Create line plot

        :param line_plot: horizontal_line_chart parameters
        :type line_plot: dict
        :param: render_to_file: if True, render drawing to file
        :type render_to_file: bool
        :return: rendered drawing
        :rtype: GraphicsFlowable or str
        """
        plot_obj = LinePlot()
        attrs_dict = {'drawing': {}, 'xValueAxis': {}, 'yValueAxis': {}, 'lines': [], 'lineLabels': []}
        attrs_list = ['drawing', 'xValueAxis', 'yValueAxis', 'strokeColor', 'lines', 'lineLabels']
        self._set_attrs(line_plot, plot_obj, attrs_dict, attrs_list)
        for attr in attrs_list:
            if attr == 'lines':
                for i, line in enumerate(plot_obj.lines):
                    if i >= len(attrs_dict[attr]):
                        break
                    for key, value in attrs_dict[attr][i].items():
                        if key == 'symbol':
                            setattr(plot_obj.lines[i], key, makeMarker(value))
                            continue
                        if hasattr(plot_obj.lines[i], key):
                            setattr(plot_obj.lines[i], key, value)
            if attr == 'lineLabels':
                self._set_labels(attr, attrs_dict, plot_obj)
            self._set_axis(attr, attrs_dict, plot_obj)
        return self._get_result(attrs_dict['drawing'], plot_obj, line_plot, render_to_file)

    def create_vertical_bar_chart(self, bar_chart: dict, render_to_file: bool = False) -> GraphicsFlowable:
        """
        Create vertical bar chart

        :param bar_chart: vertical bar chart parameters
        :type bar_chart: dict
        :param: render_to_file: if True, render drawing to file
        :type render_to_file: bool
        :return: rendered drawing
        :rtype: GraphicsFlowable or str
        """
        chart_obj = VerticalBarChart()
        attrs_dict = {'drawing': {}, 'categoryAxis': {}, 'valueAxis': {}, 'barLabels': [], 'categoryAxisLabels': []}
        attrs_list = ['drawing', 'categoryAxis', 'valueAxis', 'strokeColor', 'barLabels', 'categoryAxisLabels']
        self._set_attrs(bar_chart, chart_obj, attrs_dict, attrs_list)
        for attr in attrs_list:
            if attr == 'barLabels':
                self._set_labels(attr, attrs_dict, chart_obj)
            self._set_axis(attr, attrs_dict, chart_obj)
        return self._get_result(attrs_dict['drawing'], chart_obj, bar_chart, render_to_file)

    # protected

    @staticmethod
    def _set_attrs(chart: dict, chart_obj, attrs_dict: dict, attr_list: list):
        """
        Set additional attributes for graphical object

        :param chart: all attributes
        :type chart: dict
        :param chart_obj: graphical object
        :type chart_obj: Any
        :param attrs_dict: additional attributes
        :type attrs_dict: dict
        :param attr_list: complex attributes
        :type attr_list: list
        """
        for attr in attrs_dict.keys():
            if attr in chart:
                attrs_dict[attr] = chart[attr]
                del chart[attr]
            if attr not in attr_list:
                setattr(chart_obj, attr, attrs_dict[attr])

    def _get_result(self, attrs: dict, chart_obj, chart: dict, render_to_file: bool = False) -> GraphicsFlowable or str:
        """
        Get rendered result

        :param attrs: drawing attributes
        :type attrs: dict
        :param chart_obj: graph object
        :type chart_obj: Any
        :param chart: graph object attributes
        :type chart: dict
        :param: render_to_file: if True, render drawing to file
        :type render_to_file: bool
        :return: rendered result
        :rtype: GraphicsFlowable or str
        """
        drawing = self.set_attributes(attrs, Drawing(), {}, {})
        drawing.add(self.set_attributes(chart, chart_obj, {}, HorizontalLineChartMap.value_map))
        if not render_to_file:
            return renderPDF.GraphicsFlowable(drawing)
        else:
            file_name = f'/tmp/{str(uuid.uuid4())}.png'
            renderPM.drawToFile(drawing, file_name, 'PNG')
            return file_name

    # static

    @staticmethod
    def _set_labels(attr: str, attrs: dict, chart_obj: HorizontalLineChart or VerticalBarChart or LinePlot):
        """
        Set labels parameters

        :param attr: current attribute
        :type attr: str
        :param attrs: attributes
        :type attrs: dict
        :param chart_obj: chart object
        :type chart_obj: HorizontalLineChart or VerticalBarChart or LinePlot
        """
        for i, line in enumerate(attrs[attr]):
            for j, label in enumerate(attrs[attr][i]):
                for key, value in label.items():
                    if key in LabelMap.value_map:
                        value = LabelMap.value_map[key][value]
                    setattr(getattr(chart_obj, attr)[(i, j)], key, value)

    @staticmethod
    def _set_axis(attr: str, attrs: dict, chart_obj: HorizontalLineChart or VerticalBarChart or LinePlot):
        """
        Set axis parameters

        :param attr: current attribute
        :type attr: str
        :param attrs: attributes
        :type attrs: dict
        :param chart_obj: chart object
        :type chart_obj: HorizontalLineChart or VerticalBarChart or LinePlot
        """
        if attr == 'categoryAxisLabels':
            for i, label in enumerate(attrs[attr]):
                for key, value in label.items():
                    if key in LabelMap.value_map:
                        value = LabelMap.value_map[key][value]
                    setattr(chart_obj.categoryAxis.labels[i], key, value)
        if attr == 'categoryAxis':
            for key, value in attrs.get(attr).items():
                if hasattr(chart_obj.categoryAxis, key):
                    if key in CategoryAxisMap.value_map:
                        value = CategoryAxisMap.value_map[key][value]
                    setattr(chart_obj.categoryAxis, key, value)
        if attr in ['valueAxis', 'xValueAxis', 'yValueAxis']:
            for key, value in attrs.get(attr).items():
                if hasattr(chart_obj, attr):
                    axis = getattr(chart_obj, attr)
                    if key == 'valueSteps':
                        setattr(axis, key, value)
                        continue
                    if hasattr(axis, key):
                        if key in ValueAxisMap.value_map:
                            value = ValueAxisMap.value_map[key][value]
                        setattr(axis, key, value)
