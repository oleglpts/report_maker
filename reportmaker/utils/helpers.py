import os
import sys
import site
import gettext
import logging
import builtins
import traceback
from datetime import datetime
from argparse import Namespace

_ = builtins.__dict__.get('_', lambda x: x)

########################################################################################################################
#                                                    Some helpers                                                      #
########################################################################################################################


def set_config(config_name: str) -> dict:
    """

    Config parse

    :param config_name: config file name
    :type config_name: str
    :return: parsed config
    :rtype: dict

    """
    import json
    try:
        return json.load(open(config_name, 'r'))
    except FileNotFoundError:
        print('%s %s' % (config_name, 'not found'))
        exit(1)
    except json.JSONDecodeError as error:
        print('%s %s: %s' % (config_name, 'format error', str(error)))
        exit(1)


def activate_virtual_environment(**kwargs):
    """

    Activate virtual environment

    :param kwargs: key parameters

    Allowed following parameters:

    - environment (virtual environment directory, default: 'venv')
    - packages (path to packages in environment, default: 'lib/python{VERSION}/site-packages')

    """
    env = kwargs.get('environment', 'venv').replace('~', os.getenv('HOME'))
    env_path = env if env[0:1] == "/" else os.getcwd() + "/" + env
    env_activation = env_path + '/' + 'bin/activate_this.py'
    site.addsitedir(env_path + '/' + kwargs.get('packages', 'lib/python%s.%s/site-packages' % (
        sys.version_info.major, sys.version_info.minor)).replace(
        '{VERSION}', '%s.%s' % (sys.version_info.major, sys.version_info.minor)))
    sys.path.append('/'.join(env_path.split('/')[:-1]))
    try:
        exec(open(env_activation).read())
    except Exception as e:
        print('%s: (%s)' % ('virtual environment activation error', str(e)))
        exit(1)


def set_localization(**kwargs):
    """

    Install localization

    :param kwargs: key parameters

    Allowed following parameters:

    - locale_domain (default: sys.argv[0])
    - locale path (default: '/usr/share/locale')
    - language (default: 'en')
    - quiet (default: False)

    """
    locale_domain = kwargs.get('locale_domain', sys.argv[0])
    locale_dir = kwargs.get('locale_dir', '/usr/share/locale').replace('~', os.getenv('HOME'))
    language = kwargs.get('language', 'en')
    gettext.install(locale_domain, locale_dir)
    try:
        gettext.translation(locale_domain, localedir=locale_dir, languages=[language]).install()
    except FileNotFoundError:
        if not kwargs.get('quiet', False):
            print('%s %s \'%s\' %s, %s' % ('translation', 'for', language, 'not found', 'use default'))


def get_logger(logger_name: str, logging_format: str, file_name: str, level: int = logging.INFO) -> logging.Logger:
    """

    Get logger with path 'file name'. If permission error, create log in /tmp

    :param logger_name: logger name
    :type logger_name: str
    :param logging_format: log format
    :type logging_format: str
    :param file_name: log file name
    :type file_name: str
    :param level: logging level
    :type level: int
    :return: logger
    :rtype: logging.Logger

    """
    path, prepared = '', True
    for cat in file_name.split('/')[1:-1]:
        path += '/%s' % cat
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except PermissionError:
                prepared = False
                break
    if not prepared:
        file_name = '/tmp/%s' % file_name.split('/')[-1]
    logging.basicConfig(level=level, format=logging_format)
    log = logging.getLogger(logger_name)
    handler = logging.FileHandler(file_name, encoding='utf8')
    handler.setFormatter(logging.Formatter(logging_format))
    log.addHandler(handler)
    log.setLevel(level=level)
    return log


def get_parm_value(parameters: dict, name: str, env_name: str, default_value: str) -> str:
    """

    Get parameter value from config

    :param parameters: parameters
    :type parameters: dict
    :param name: parameter name
    :type name: str
    :param env_name: environment variable name
    :type env_name: str
    :param default_value: default parameter value
    :type default_value: str
    :return: actual parameter value
    :rtype: str

    """
    value = parameters.get(name, '')
    return os.environ.get(env_name, default=default_value) if not value else value


def database_connect(connection_string: str, logger: logging.Logger, cmd_args: Namespace):
    """

    ODBC connection to database

    :param connection_string: connection string
    :type connection_string: str
    :param logger: logger
    :type logger: logging.Logger
    :param cmd_args: command line parameters
    :type cmd_args: Namespace
    :return: ODBC connection
    :rtype: Connection

    """
    driver, parameters, error_count = None, None, 0
    while error_count < 2:
        try:
            parameters = {
                x.split('=')[0].strip().lower(): x.split('=')[1].strip() for x in connection_string.split(';')
            }
            driver = parameters.get('driver', '')
            break
        except IndexError as e:
            if error_count:
                error_handler(logger, e, _('connection string') + ' --> ', cmd_args, True)
            else:
                connection_string = connection_string[:-1]
                error_count += 1
    if driver == 'sqlite3':
        import sqlite3
        try:
            return sqlite3.connect(get_parm_value(parameters, 'database', 'POSTGRES_DB_NAME', 'postgres'))
        except Exception as e:
            error_handler(logger, e, 'sqlite3 ', cmd_args, True)
    if driver == 'psycopg2':
        import psycopg2
        try:
            return psycopg2.connect('host=%s port=%s dbname=%s user=%s password=%s' % (
                get_parm_value(parameters, 'host', 'POSTGRES_HOST', 'postgres'),
                get_parm_value(parameters, 'port', 'POSTGRES_PORT', '5432'),
                get_parm_value(parameters, 'dbname', 'POSTGRES_DB_NAME', 'postgres'),
                get_parm_value(parameters, 'user', 'POSTGRES_USER', 'postgres'),
                get_parm_value(parameters, 'password', 'POSTGRES_PASS', 'postgres')))
        except psycopg2.OperationalError as e:
            error_handler(logger, e, 'psycopg2 ', cmd_args, True)
        except Exception as e:
            error_handler(logger, e, 'psycopg2 ', cmd_args, True)
    else:
        import pyodbc
        try:
            return pyodbc.connect(connection_string)
        except pyodbc.Error as e:
            error_handler(logger, e, 'ODBC ', cmd_args, True)


def error_handler(logger: logging.Logger, error: Exception, message: str, cmd_args: Namespace = None,
                  sys_exit: bool = False, debug_info: bool = False):
    """

    Error handler

    :param logger: logger
    :type logger: logging.Logger
    :param error: current exception
    :type error: Exception or None
    :param message: custom message
    :type message: str
    :param cmd_args: commandline parameters
    :type cmd_args: Namespace
    :param sys_exit: if True, sys.exit(1)
    :type sys_exit: bool
    :param debug_info: if True, output traceback
    :type debug_info: bool

    """
    _ = builtins.__dict__.get('_', lambda x: x)
    if debug_info:
        et, ev, tb = sys.exc_info()
        logger.error(
            '%s %s: %s\n%s\n' % (message, _('error'), error,
                                 ''.join(traceback.format_exception(et, ev, tb))))
    else:
        logger.error('%s%s: %s' % (message, _('error'), error))
    if sys_exit:
        logger.error(_('error termination'))
        if cmd_args and hasattr(cmd_args, 'token') and cmd_args.token:
            print(cmd_args.callback_url)
            # TODO: Send request to callback url with token
        exit(1)


def get_database_data(connection_string: str, sql: str, logger: logging.Logger, cmd_args: Namespace) -> list:
    """
    Get data from database

    :param connection_string: database connection string
    :type connection_string: str
    :param sql: sql request
    :type sql: str
    :param logger: logger
    :type logger: logging.Logger
    :param cmd_args: commandline arguments
    :type cmd_args: Namespace
    :return: sql result
    :rtype: list
    """
    connection = database_connect(connection_string, logger, cmd_args)
    cursor = connection.cursor()
    cursor.execute(sql)
    columns_names = [desc[0] for desc in cursor.description]
    response = cursor.fetchall()
    data = list()
    data.append(columns_names)
    for row in response:
        formatted_row = []
        for col in row:
            if hasattr(col, 'real') and hasattr(col, 'imag'):
                formatted_row.append(float(col))
            elif isinstance(col, datetime):
                formatted_row.append(str(col))
            else:
                formatted_row.append(col)
        data.append(formatted_row)
    cursor.close()
    connection.close()
    return data
