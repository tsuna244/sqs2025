import logging
import sys
from time import strftime

# singelton Logger Class
class LoggerClass(object):
    """
        Class that allows to log with a configured format

        Methods:
            get_logger: returns a logger object
    """
    _logger = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensures that the logger class is a singelton

        Returns:
            logging.Logger: Logger from the logging class as singelton object
        """
        if not cls._instance:
            cls._instance = super(LoggerClass, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def get_logger(self):
        """Function that returns a configured logger

        Returns:
            logging.Logger: Logger object from the logging module that is configured with stream and file output
                            File output only on linux systems
        """
        if LoggerClass._logger is None:
        
            # set logging format
            log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-7.7s]  %(message)s")

            # create logger
            LoggerClass._logger = logging.getLogger()
            LoggerClass._logger.setLevel(logging.INFO)

            # console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(log_formatter)
            LoggerClass._logger.addHandler(console_handler)

            # file handler
            try:
                log_name = strftime("%Y-%m-%d %H:%M:%S") + "_system.log"
                file_handler = logging.FileHandler(log_name, mode="a", encoding="utf-8")
                file_handler.setFormatter(log_formatter)
                LoggerClass._logger.addHandler(file_handler)
            except Exception:
                LoggerClass._logger.warning("creating file logging did not work only")

            LoggerClass._logger.info("Logger setup succesfully")
        return LoggerClass._logger


# utility function: log message for each function in specific format
def log_function(module_name: str, function_name: str, log_msg: str, log_type = "info"):
    """Utility function to help log functions with a better format

    Args:
        module_name (str): The name of the module that calls the log function
        function_name (str): The name of the function inside the module that calls the log function
        log_msg (str): the message that should be logged
        log_type (str, optional): Type of logging: "error", "warn" or "info". Defaults to "info".
    """
    log = LoggerClass().get_logger()
    msg = "({:15s} | {:30s}) -> {}".format(module_name, function_name + "(...)", log_msg)
    if log_type == "error":
        log.error(msg)
    elif log_type == "warn":
        log.warning(msg)
    else:
        log.info(msg)