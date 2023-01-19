import json
from typing import Any
from abc import ABC, abstractmethod
from reportmaker.utils.helpers import error_handler
from reportmaker.config import translate as _, logger, cmd_args, config_args


class ReportError(Exception):
    """
    Custom exception
    """
    pass


class Document(ABC):
    """
    Abstract document
    """

    def __init__(self, descriptor: dict):
        """
        Constructor

        :param descriptor: document descriptor
        :type descriptor: dict
        """
        self._descriptor = descriptor
        self._styles = {}
        self._layout = []

    def generate_document(self):
        """
        This method generates and save document
        """
        logger.info(_('descriptor is loaded'))
        self._create_styles()
        self._create_layout()
        self._create_document()

    def _create_layout(self):
        """
        Create document layout
        """
        layout = self._descriptor['document'].get('layout', None)
        if not layout:
            raise ReportError(f"{_('omitted')} {_('attribute')} 'layout' {_('in')} report descriptor")
        for element in layout:
            logger.debug("%s '%s'" % (_('creating element '), json.dumps(element, ensure_ascii=False, indent=4)))
            self._layout.append(self._create_object(element))

    def _create_object(self, *args, method_postfix: str = '') -> Any:
        """
        Create object via descriptor

        :param args: method parameters, descriptor first
        :param method_postfix: method name postfix
        :type method_postfix: str
        :return: created object
        :rtype: Any
        """
        if len(args) < 1:
            raise ReportError(f"{_('object')} {_('must must have parameters')}")
        all_keys = args[0].keys() if isinstance(args[0], dict) else []
        for element in [key for key in all_keys if isinstance(args[0].get(key, None), list)] + ['']:
            data = args[0].get(element, None) if isinstance(args[0], dict) else args[0]
            if type(args[0]) not in (dict, list):
                return data
            if isinstance(data, list):
                data = [self._create_object(element) for i, element in enumerate(data)]
                if isinstance(args[0], dict):
                    args[0][element] = data
                else:
                    return data
        if not isinstance(args[0], dict):
            raise ReportError(f"{_('object')} {_('must be on some type')}: {_('check parameters')}")
        object_type = dict(args[0]).get('type', None)
        if not object_type:
            return dict(args[0])
        current_method = f'create_{object_type.lower()}{method_postfix}'
        if hasattr(self, current_method):
            return getattr(self, current_method)(*args)
        else:
            error_handler(
                logger, ReportError(f"{_('method')} '{current_method}' {_('not implemented')} {_('for class')} "
                                    f"{self.__class__.__name__}"), '', cmd_args, sys_exit=True, debug_info=True
            )

    def _create_styles(self):
        """
        This method create document's styles
        """
        styles = self._descriptor['document'].get('styles', None)
        if not styles:
            styles = config_args.get('default_styles', None)
            if not styles:
                raise ReportError(f"{_('omitted')} {_('attribute')} 'styles' {_('in')} "
                                  f"report descriptor and 'default_styles' in configuration file")
        for name, style in styles.items():
            self._styles[name] = self._create_object(style, name, method_postfix='_style')

    def set_attributes(self, attributes: dict, result: object, key_map: dict, value_map: dict) -> Any:
        """
        Set object attributes

        :param attributes: name -> value pairs from descriptor
        :type attributes: dict
        :param result: source object
        :type result: object
        :param key_map: mapping for attributes names
        :type key_map: dict
        :param value_map: mapping for attributes values
        :type value_map: dict
        :return: objects with set attributes
        :rtype: object
        """
        for key, value in attributes.items():
            if key not in key_map:
                if hasattr(result, key):
                    key_map[key] = key
                else:
                    continue
            if type(value).__name__ in ['list']:
                current_method = value_map.get(key, None)
                mapped_value = current_method.__func__(self, value) if current_method else value
            else:
                mapped_value = value_map.get(key, {}).get(value, None)
            attr = getattr(result, key_map[key])
            attr_type = type(attr)
            if mapped_value is not None:
                value = mapped_value
            elif attr is not None:
                value = attr_type(value)
            setattr(result, key_map[key], value)
        return result

    @abstractmethod
    def create_paragraph_style(self, style: dict, name: str) -> Any:
        """
        Create paragraph style

        :param style: style descriptor
        :type style: dict
        :param name: style name
        :type name: str
        :return: paragraph style object
        :rtype: Any
        """
        raise ReportError(f"Method 'create_paragraph_style' for class {self.__name__} not implemented")

    @abstractmethod
    def create_table(self, table: dict) -> Any:
        """
        Create table

        :param table: table descriptor
        :type table: dict
        :return: table object
        :rtype: Any
        """
        raise ReportError(f"Method 'create_table' for class {self.__name__} not implemented")

    def create_image(self, image: dict) -> Any:
        """
        Create image

        :param image: image attributes
        :type image: dict
        :return: image object
        :rtype: Any
        """
        raise ReportError(f"Method 'create_image' for class {self.__name__} not implemented")

    @abstractmethod
    def _create_document(self):
        """
        Create and save document
        """
        raise ReportError(f"Method 'create_document' for class {self.__name__} not implemented")
