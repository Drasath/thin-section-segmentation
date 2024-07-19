from pathlib import Path
import logging.config

# Directory paths
PROJECT_DIRECTORY = Path(__file__).parent.parent
config_path = PROJECT_DIRECTORY / "logging_config.ini"
log_path = PROJECT_DIRECTORY / "logs" / "log.log"

# Make sure the logs directory exists and configure the logger
Path(log_path).parent.mkdir(parents=True, exist_ok=True)
logging.config.fileConfig(fname=config_path, disable_existing_loggers=False, defaults={"logfilename": 'logs/log.log'})

# Save file constants
SAVE_FILE_EXTENTION = ".save"
SUBJECT_NR = 1
