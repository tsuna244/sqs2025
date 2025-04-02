import logging
import sys
from time import strftime

# singelton Logger Class
class Logger(object):
    logger = None
    _instance = None

    # ensure that there is only one instance of logger
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def getLogger(self):
        if Logger.logger is None:
        
            # set logging format
            logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

            # create logger
            Logger.logger = logging.getLogger()
            Logger.logger.setLevel(logging.INFO)

            # console handler
            consoleHandler = logging.StreamHandler(sys.stdout)
            consoleHandler.setFormatter(logFormatter)
            Logger.logger.addHandler(consoleHandler)

            # file handler
            try:
                log_name = strftime("%Y-%m-%d %H:%M:%S") + "_system.log"
                fileHandler = logging.FileHandler(log_name, mode="a", encoding="utf-8")
                fileHandler.setFormatter(logFormatter)
                Logger.logger.addHandler(fileHandler)
            except:
                Logger.logger.warning("creating file logging did not work only")

            Logger.logger.info("Logger setup succesfully")
        return Logger.logger