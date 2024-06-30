from pathlib import Path
import logging.config

PROJECT_DIRECTORY = Path(__file__).parent.parent
SAVE_FILE_EXTENTION = ".save"

config_path = PROJECT_DIRECTORY / "logging_config.ini"
log_path = PROJECT_DIRECTORY / "logs" / "log.log"
Path(log_path).parent.mkdir(parents=True, exist_ok=True)
logging.config.fileConfig(fname=config_path, disable_existing_loggers=False, defaults={"logfilename": 'logs/log.log'})
SUBJECT_NR = 100