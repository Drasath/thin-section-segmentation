import sys
import logging

from view import UI
from constants import *

def main() -> None:
    logging.info("Starting application...")
    exitcode = UI.main()    # FIXME - Rename the function. LH
    logging.info("Closing application...")
    sys.exit(exitcode)

if __name__ == "__main__":
    try:    # REVIEW - Check if this is the best way to handle exceptions with logging. LH
        main()
    except Exception as e:
        logging.exception(e)
        raise e
