import logging

from lab.business.common import Constants

logging_level = f"logging.{Constants.get_logging_level()}"

def start_logging():
    logging.basicConfig(
        level=logging.INFO,
        filename=Constants.log_file,
        filemode="a+",
        format="%(asctime)-15s — %(levelname)s\t— %(name)s\t— %(message)s"
        )
    logging.info("start logging")