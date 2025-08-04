import os
import logging
import logging.config
import configparser
from pathlib import Path

# Calculate project root - lg.py is at project root level
project_root = Path(__file__).parent
default_log_config = os.path.join(project_root, 'logging_config.ini')
def setup_logging_from_config(path: str = default_log_config) -> logging.Logger:
    # Always construct full path relative to project root
    if not os.path.isabs(path):
        config_path = project_root / path
    else:
        config_path = Path(path)

    # Check if file exists before trying to read it
    if not config_path.exists():
        # Fallback to basic logging if config file not found
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    config = configparser.ConfigParser()
    config.read(str(config_path))

    enabled: bool = config.getboolean('log_control', 'enabled', fallback=True)
    if enabled:
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
        logging.config.fileConfig(str(config_path))
    else:
        logging.disable(logging.CRITICAL)

    return logging.getLogger(__name__)

logger: logging.Logger = setup_logging_from_config()
