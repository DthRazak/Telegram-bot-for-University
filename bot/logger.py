import logging
from logging.handlers import TimedRotatingFileHandler
import os


log_format = "%(asctime)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(log_format)
path = os.path.abspath(os.path.dirname(__file__))

msg_logger = logging.getLogger('msgLogs')
msg_logger.setLevel(logging.INFO)

db_logger = logging.getLogger('dbLogger')
db_logger.setLevel(logging.INFO)

msg_handler = TimedRotatingFileHandler(path + '/logs/msg', when='W6', interval=1, backupCount=5)
msg_handler.suffix = "%Y-%m-%d.log"
msg_handler.setFormatter(formatter)

db_handler = TimedRotatingFileHandler(path + '/logs/db', when='W6', interval=1, backupCount=5)
db_handler.suffix = "%Y-%m-%d.log"
db_handler.setFormatter(formatter)

msg_logger.addHandler(msg_handler)
db_logger.addHandler(db_handler)
