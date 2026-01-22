from steering_metrics.config import N_DAYS, DEFAULT_DATE
from steering_metrics.day_prices.dam_fetcher import DAMDataFetcher
from steering_metrics.log import setup_logging


def fetch_prices():
    DAMDataFetcher().fetch_prices(DEFAULT_DATE, DEFAULT_DATE.shift(days=N_DAYS+1))


if __name__ == "__main__":
    setup_logging()
    fetch_prices()
