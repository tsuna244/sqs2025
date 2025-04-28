import logging
import sys
from time import strftime

# singelton Logger Class
class LoggerClass(object):
    _logger = None
    _instance = None

    # ensure that there is only one instance of logger
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LoggerClass, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def get_logger(self):
        if LoggerClass._logger is None:
        
            # set logging format
            log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

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
def log_function(function_name: str, log_msg: str, log_type = "info"):
    log = LoggerClass().getLogger()
    msg = "(module_pokeapi | {:30s}) -> {}".format(function_name + "(...)", log_msg)
    if log_type == "error":
        log.error(msg)
    if log_type == "warn":
        log.warning(msg)
    else:
        log.info(msg)