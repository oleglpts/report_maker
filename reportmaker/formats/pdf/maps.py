from reportlab.lib.enums import *
from reportlab.lib.colors import *
from reportlab.platypus.tables import GRID_STYLE, BOX_STYLE, LABELED_GRID_STYLE, COLORED_GRID_STYLE,\
    LIST_STYLE, TableStyle

# Colors
colors = {x: globals()[x] for x in globals() if isinstance(globals()[x], Color)}


class ParagraphStyleMap:
    """
    Mapping the attributes of the report descriptor to the attributes of the Reportlab paragraph style object
    """

    # Mapping the attributes names (example: 'font_name': 'fontName')
    key_map = {}

    # Mapping the attributes values
    value_map = {
        'alignment': {
            'left': TA_LEFT,
            'right': TA_RIGHT,
            'center': TA_CENTER,
            'justify': TA_JUSTIFY
        },
        'bulletColor': colors,
        'textColor': colors,
        'backColor': colors,
        'borderColor': colors,
        'underlineColor': colors,
        'strikeColor': colors
    }


class TableStyleMap:
    """
    Mapping the attributes of the report descriptor to the attributes of the Reportlab table style object
    """

    @classmethod
    def map_table_style(cls, style: list) -> list:
        """
        TODO: Будет более сложной, зависящей от типа опции

        :param style:
        :return:
        """
        result = []
        for element in style:
            data = [element[0], tuple(element[1]), tuple(element[2])]
            if len(element) > 3:
                data.append(element[3])
            if len(element) > 4 and element[4] in colors:
                data.append(colors[element[4]])
            result.append(tuple(data))
        return result

    # Mapping the attributes names (example: 'font_name': 'fontName')
    key_map = {'data': '_cmds'}

    styles = {
        "grid_style": GRID_STYLE,
        "box_style": BOX_STYLE,
        "labeled_grid_style": LABELED_GRID_STYLE,
        "colored_grid_style": COLORED_GRID_STYLE,
        "list_style": LIST_STYLE,
        "win_style": TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#a7a5a5'),
            ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
            ('FONTSIZE', (0, 1), (-1, -1), 5),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, black),
            ('BOX', (0, 0), (-1, -1), 0.25, black),
        ])
    }

    # Mapping the attributes values
    value_map = {
        'data': map_table_style,
        'parent': styles,
        # TODO: _opts
    }


class TableMap:
    """
    Mapping the attributes of the table descriptor to the attributes of the Reportlab Table object
    """
    # Mapping the attributes names (example: 'font_name': 'fontName')
    key_map = {}

    # Mapping the attributes values
    value_map = {
        "style": TableStyleMap.map_table_style
    }


class SliceMap:
    """
    Mapping the attributes of the slice descriptor to the attributes of the Reportlab Pie slice object
    """
    # Mapping the attributes values
    value_map = {
        'fontColor': colors,
        'strokeColor': colors,
        'label_boxStrokeColor': colors,
        'label_boxFillColor': colors,
        'label_strokeColor': colors,
        'label_pointer_strokeColor': colors
    }


class LineMap:
    """
    Mapping the attributes of the slice descriptor to the attributes of the Reportlab Pie slice object
    """
    # Mapping the attributes values
    value_map = {
        'strokeColor': colors,
    }


class HorizontalLineChartMap:
    """
    Mapping the attributes of the slice descriptor to the attributes of the Reportlab Pie slice object
    """
    # Mapping the attributes values
    value_map = {
        'strokeColor': colors,
        'fillColor': colors
    }


class LabelMap:
    """
    Mapping the attributes of the slice descriptor to the attributes of the Reportlab Pie slice object
    """
    # Mapping the attributes values
    value_map = {
        'boxStrokeColor': colors,
        'boxFillColor': colors
    }


class CategoryAxisMap:
    value_map = {
        'strokeColor': colors,
    }


class ValueAxisMap:
    value_map = {
        'strokeColor': colors,
    }


class CircleMap:
    value_map = {
        'fillColor': colors,
    }
