import faulthandler      # type: ignore
from flask import Flask  # type: ignore

from config import CONFIG_DICT
from service import logging_config

# This causes the traceback to be written to the fault log file in case of serious faults
fault_log_file = open(CONFIG_DICT['FAULT_LOG_FILE_PATH'], 'a')
faulthandler.enable(file=fault_log_file)

app = Flask(__name__)
app.config.update(CONFIG_DICT)

logging_config.setup_logging()
