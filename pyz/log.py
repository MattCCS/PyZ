"""
This is a very carefully-controlled file used to allow all other python modules
to log their activity in a sane manner.  Code which wishes to log its activity
will usually include lines such as the following at the top:

    ####################################
    # SETTING UP THE LOGGER
    import os
    ... from <project> import log ...
    ROOTPATH = os.path.splitext(__file__)[0]
    LOGPATH = "{0}.log".format(ROOTPATH)
    LOGGER = log.get(__name__, path=LOGPATH)
    LOGGER.info("----------BEGIN----------")

This will create a <filename>.log file adjacent to the source code file itself.
This is a boon to (human) debuggers.  The logger allows different levels of
criticality (debug, info, warning, error, critical). See
    https://docs.python.org/2/library/logging.html
for more details.

(c) 2015 Matthew Cotton
""" # TODO: confirm 'import log' vs something custom like 'from build import log'

import logging
from logging.handlers import RotatingFileHandler

from pyz import settings

import sys
import traceback
from functools import wraps

####################################
# meta helpers + logging
import os

####################################
# This code defines the ABSOLUTE path of where the __debug__.log file
# should be located, based on the root of where this log.py file is located.
#
#   Attempts to place __debug__.log at the base of each project.
#

THIS_FILE = os.path.realpath(__file__)
_DEBUG_LOG_PATH = os.path.join(os.path.dirname(THIS_FILE), "__debug__.log")
_FIRST = True

####################################

import inspect

class MattsCustomFormatter(logging.Formatter):
    """
    Class which acts as a Formatter object, but which automatically indents
    log messages based on how many function calls deep the messages originate.
    """
    # TODO: fine-tune indentation levels

    # SOURCE: http://stackoverflow.com/questions/9212228/using-custom-formatter-classes-with-pythons-logging-config-module
    # SOURCE: http://code.activestate.com/recipes/412603-stack-based-indentation-of-formatted-logging/

    def __init__( self, fmt=None, datefmt=None, allow_logpy_recursions=False ):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.baseline = len(inspect.stack()) + 1
        self.allow_logpy_recursions = allow_logpy_recursions

    def format( self, record ):

        ####################################
        # fetch the function call stack;
        # ignore logwraps as function calls,
        # and filter things like builtins

        stack = inspect.stack()
        stack = [e[1] for e in stack]
        stack = [e for e in stack if "Python.framework" not in e]
        stack = [e for e in stack if "logging/__init__.py" not in e]
        if not self.allow_logpy_recursions:
            stack = [e for e in stack if "log.py" not in e]
        # print stack
        MattsCustomFormatter.STACK = stack

        ####################################
        # establish the indent
        indent = bytearray(b'...') * (len(stack) - self.baseline)
        if indent:
            indent[0] = ' '
        record.indent = indent

        # record.function = stack[8][3]

        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)

        output_string = self._fmt.format(**record.__dict__)  # REVOLUTIONARY!  Not.

        ####################################
        # the rest of this is taken from
        # the actual logging module!

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it'output_string constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            if output_string[-1:] != "\n":
                output_string = output_string + "\n"
            try:
                output_string = output_string + record.exc_text
            except UnicodeError:
                # Sometimes filenames have non-ASCII chars, which can lead
                # to errors when output_string is Unicode and record.exc_text is str
                # See issue 8924.
                # We also use replace for when there are multiple
                # encodings, e.g. UTF-8 for the filesystem and latin-1
                # for a script. See issue 13232.
                output_string = output_string + record.exc_text.decode(sys.getfilesystemencoding(), 'replace')

        del record.indent
        # del record.function

        return output_string


def get(name, path='activity.log', allow_logpy_recursions=False):
    """
    Returns a logger object so that a given file can log its activity.
    If two loggers are created with the same name, they will output 2x to the same file.
    """
    # SOURCE: http://stackoverflow.com/questions/7621897/python-logging-module-globally

    # formatter = IndentFormatter("%(asctime)s [%(levelname)8s] %(module)30s:%(indent)s%(message)s")
    formatter = MattsCustomFormatter("{asctime} [{levelname:8}] {module} :{indent} {message}", allow_logpy_recursions=allow_logpy_recursions)
    handler = RotatingFileHandler(path, maxBytes=1024 * 100, backupCount=3)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name) # will return same logger if same name given

    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger

def get_old(name, path='activity.log'):
    """
    Returns a logger object so that a given file can log its activity.
    If two loggers are created with the same name, they will output 2x to the same file.

    OLD/UNUSED.  REPLACED WITH USING MattsCustomFormatter WHICH INDENTS LOGS.
    """
    # SOURCE: http://stackoverflow.com/questions/7621897/python-logging-module-globally

    formatter = logging.Formatter(fmt='%(asctime)s : %(levelname)s : %(module)s : %(message)s')
    # formatter = logging.Formatter(fmt='%(asctime)s : %(module)30s : [%(levelname)8s] : %(message)s')
    handler = RotatingFileHandler(path, maxBytes=1024 * 100, backupCount=10)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name) # will return same logger if same name given

    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger


_META_LOGGER = get("__debug__", _DEBUG_LOG_PATH, allow_logpy_recursions=True) # !!!


def logwrap(func):
    """
    This function is a decorator which allows all input/output/errors of any
    given function to be logged, timestamped, and output to a SINGLE __debug__.log FILE!

    Useful for more egregious errors (such as logical errors,
    or the abuse of function signatures).
    """
    
    if not settings.LOG_FUNCTIONS:
        return func

    global _FIRST, _META_LOGGER
    if _FIRST:
        _META_LOGGER.debug("----------BEGIN----------")
        _FIRST = False

    @wraps(func)
    def wrapped(*args, **kwargs):
        """
        Replacement function which wraps I/O and erroring.
        """

        _META_LOGGER.debug("<{}> called with:".format(func.__name__))
        _META_LOGGER.debug("args: {}".format(args))
        _META_LOGGER.debug("kwargs: {}".format(kwargs))

        try:
            out = func(*args, **kwargs)
            _META_LOGGER.debug("<{}> returned: {}\n".format(func.__name__, out))
            return out
        except:
            # SOURCE: http://stackoverflow.com/questions/9005941/python-exception-decorator-how-to-preserve-stacktrace
            _META_LOGGER.debug("<{}> threw error: {}\n".format(func.__name__, traceback.format_exc()))
            (errorobj, errortype, errtraceback) = sys.exc_info()  # error/type/traceback
            raise errorobj

    return wrapped


