import logging
from pathlib import Path
from datetime import datetime
from contextlib import redirect_stdout

def make_log_name(name):
    log_name = f"pred_age_{name}" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
    return log_name

def setup_logging(log_file, log_level=logging.INFO, handler=logging.StreamHandler()):
    """Setup logging configuration"""
    # setup log dir

    format = '%(asctime)s %(message)s'
    datefmt = '%m/%d/%Y %I:%M:%S %p'

    logger = logging.getLogger()
    logger.setLevel(log_level)
    formatter = logging.Formatter(format, datefmt=datefmt)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    return logger


class Logger():
    def __init__(self, name: str, result_dir: Path):
        log_name = make_log_name(name)
        log_dir = result_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / log_name

        self.logger = setup_logging(log_file)

        self._redirector = redirect_stdout(self)

    def write(self, message):
        if message.strip():
            self.logger.info(message.strip())

    def flush(self): pass

    def __enter__(self):
        self._redirector.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # let contextlib do any exception handling here
        self._redirector.__exit__(exc_type, exc_value, traceback)