import logging
from logging import handlers
import sys


DAM_FETCHER_LOGGER = "DAM_FETCHER"
STEERING_METRICS_LOGGER = "STEERING_METRICS"

LOG_FORMAT = "%(asctime)s - %(name)s  - %(levelname)s - %(message)s"

def setup_logging(level=logging.INFO):

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Only WARNING+ for apscheduler logs
    aps_logger = logging.getLogger("apscheduler")
    aps_logger.setLevel(logging.WARNING)


def get_dam_fetcher_logger():
    return logging.getLogger(DAM_FETCHER_LOGGER)


def get_steering_metrics_logger():
    return logging.getLogger(STEERING_METRICS_LOGGER)