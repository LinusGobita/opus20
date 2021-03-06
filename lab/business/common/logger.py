import logging

from lab.business.common import Constants

logging_level = f"logging.{Constants.get_logging_level()}"

def start_logging():
    logging.basicConfig(
        level=logging.INFO,
        filename=Constants.log_file,
        filemode="a+",
        format="%(asctime)-15s â %(levelname)s\tâ %(name)s\tâ %(message)s"
        )
    logging.info("start logging")