import inspect
import logging
import logging.handlers
import os
import sys
import traceback


try:
    d = os.path.dirname(os.path.expanduser("~/.qgis2/log/"))
    if not os.path.exists(d):
        os.mkdir(d)
finally:
    pluginName = "Equirectangular Viewer"
    logFilePath = os.path.expanduser("~/.qgis2/log/%s.log" % pluginName)


class log(object):

    handler = None
    pluginId = 'EquirectangularViewer'

    @staticmethod
    def error(text):
        logger = logging.getLogger(log.pluginId)
        logger.error(text)

    @staticmethod
    def info(text):
        logger = logging.getLogger(log.pluginId)
        logger.info(text)

    @staticmethod
    def warning(text):
        logger = logging.getLogger(log.pluginId)
        logger.warning(text)

    @staticmethod
    def debug(text):
        logger = logging.getLogger(log.pluginId)
        logger.debug(text)

    @staticmethod
    def last_exception(msg):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log.error(
            msg + '\n  '.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    @staticmethod
    def initLogging():
        try:
            """ set up rotating log file handler with custom formatting """
            log.handler = logging.handlers.RotatingFileHandler(
                logFilePath, maxBytes=1024 * 1024 * 10, backupCount=5)
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)-8s %(message)s")
            log.handler.setFormatter(formatter)
            logger = logging.getLogger(log.pluginId)  # root logger
            logger.setLevel(logging.DEBUG)
            logger.addHandler(log.handler)
        except Exception as e:
            pass

    @staticmethod
    def removeLogging():
        logger = logging.getLogger(log.pluginId)
        logger.removeHandler(log.handler)
        del log.handler

    @staticmethod
    def logStackTrace():
        logger = logging.getLogger(log.pluginId)
        logger.debug("logStackTrace")
        for x in inspect.stack():
            logger.debug(x)
