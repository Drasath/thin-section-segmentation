import sys

from view import UI
import logging
import logging.config

from constants import *

def main() -> None:
    logging.info("Starting application...")
    exitcode = UI.main()    # FIXME - Rename the function. LH
    logging.info("Closing application...")
    sys.exit(exitcode)

if __name__ == "__main__":
    # TODO - Put the logging initialization in a separate module. LH
    config_path = PROJECT_DIRECTORY / "src" / "logging_config.ini"
    log_path = PROJECT_DIRECTORY / "logs" / "log.log"
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    logging.config.fileConfig(fname=config_path, disable_existing_loggers=False, defaults={"logfilename": 'logs/log.log', 'loglevel': 'INFO'})
    try:    # REVIEW - Check if this is the best way to handle exceptions with logging. LH
        main()
    except Exception as e:
        logging.exception(e)
        raise e
