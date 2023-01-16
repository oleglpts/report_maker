#!/usr/bin/python3

import sys
import json
import importlib
from formats import ReportError

########################################################################################################################
#                                                 Main function                                                        #
########################################################################################################################


def main():
    sys.path.append('../')
    sys.path.append('/app')
    from reportmaker.utils.helpers import error_handler
    from reportmaker.config import translate as _, logger, cmd_args
    logger.info(_(f"loading report descriptor '{cmd_args.input}'"))
    try:
        with open(cmd_args.input) as descriptor_file:

            # Load descriptor
            descriptor = json.load(descriptor_file)
            if not descriptor.get('document', None):
                raise ReportError(f"{_('attribute')} descriptor['document'] {_('expected')}")

            # Get document format
            document_format = descriptor['document'].get('format', None)
            if not document_format:
                raise ReportError(f"{_('attribute')} descriptor['document']['format'] {_('expected')}")

            # Get module for selected format
            try:
                module = importlib.import_module(f'formats.{document_format}')
            except ModuleNotFoundError:
                error_handler(
                    logger, ReportError(
                        f"{_('module')} {_('for')} {document_format} {_('not implemented')}"
                    ), '', cmd_args, sys_exit=True, debug_info=True)

            # Get class for selected format
            try:
                format_class = f'{document_format[0].upper()}{document_format[1:]}Document'
                document = getattr(module, format_class)(descriptor)
            except AttributeError:
                error_handler(
                    logger, ReportError(
                        f"{_('class')} {format_class} {_('for')} {document_format} format {_('not implemented')}"
                    ), '', cmd_args, sys_exit=True, debug_info=True)

            # Generate and save document
            try:
                document.generate_document()
                logger.info(f"{_('document')} {_('with')} {_('descriptor')} {cmd_args.input} {_('created')} "
                            f"{_('and')} {_('saved to')} {_('file')} {_(cmd_args.output)}")
            except AttributeError as e:
                error_handler(
                    logger, ReportError(
                        f"{_('in')} {_('class')} {format_class} {_('for')} {document_format} "
                        f"format some method {_('not implemented')} ({str(e)})"
                    ), '', cmd_args, sys_exit=True, debug_info=True)
    except Exception as e:
        error_handler(logger, e, '', cmd_args, sys_exit=True, debug_info=True)

########################################################################################################################
#                                                  Entry point                                                         #
########################################################################################################################


if __name__ == '__main__':
    main()
    # from reportlab.graphics.charts.piecharts import Pie, Drawing
    # from reportlab.lib import colors
    # from reportlab.graphics import renderPDF, renderPM
    # from reportlab.platypus import Paragraph, Image, SimpleDocTemplate, Table
    #
    # d = Drawing(175, 175)
    # pc = Pie()
    # pc.x = 25
    # pc.y = 25
    # pc.width = 125
    # pc.height = 125
    # pc.data = [10, 20, 30, 40, 50, 60]
    # pc.labels = ['a', 'b', 'c', 'd', 'e', 'f']
    # pc.slices.strokeWidth = 0.5
    # pc.slices[3].popout = 10
    # pc.slices[3].strokeWidth = 2
    # pc.slices[3].strokeDashArray = [2, 2]
    # pc.slices[3].labelRadius = 1.75
    # pc.slices[3].fontColor = colors.red
    # d.add(pc)
    # x = renderPDF.GraphicsFlowable(d)
    # y = Paragraph('12345')
    # renderPM.drawToFile(d, '/tmp/example2.png', 'PNG')
    # z = Image('/tmp/example2.png', width=350, height=350)
    # a = Table([[x, x]])
    # layout = [y, y, a, y]
    # SimpleDocTemplate('/tmp/example1.pdf').build(layout)
    # # # renderPDF.drawToFile(d, '/tmp/example3.pdf', 'My First Drawing')
