from arrow import Arrow

from steering_metrics.config import N_DAYS, DEFAULT_DATE
from steering_metrics.day_prices.dam_fetcher import DAMDataFetcher
from steering_metrics.log import setup_logging
from steering_metrics.utils import floor_to_15_minutes


def fetch_prices():
    DAMDataFetcher().fetch_prices(DEFAULT_DATE, DEFAULT_DATE.shift(days=N_DAYS))

if __name__ == "__main__":
    setup_logging()
    fetch_prices()