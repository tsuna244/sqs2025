import logging
import sys
import os
from time import strftime
import errno

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

logger = logging.getLogger()

logPath = "app/log/"

logFile = logPath + strftime("%Y-%m-%d %H:%M:%S") + "_system.log"

logger.addHandler(logging.StreamHandler(sys.stdout))

try:
    os.makedirs(logPath)
    logger.addHandler(logging.FileHandler(logFile))
except OSError as exception:
    print(str(exception))
    if exception.errno != errno.EEXIST:
        logger.warning(f"File {logPath} not Found. Will only log to stdout")

logger.info("Finished Logger setup")