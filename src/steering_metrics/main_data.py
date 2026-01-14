
from steering_metrics.config import DEVICE_ID, DEFAULT_DATE, N_DAYS, WANTED_DEVICE_IDS
from steering_metrics.factories import get_big_query_client
from steering_metrics.log import setup_logging, data_fetcher_logger
from steering_metrics.measurement_repo.bigquery import BigQueryMeasurementRepo


def fetch_data_single():
    BigQueryMeasurementRepo(get_big_query_client()).get_measurements(
        DEVICE_ID,
        DEFAULT_DATE.shift(days=-1),
        DEFAULT_DATE.shift(days=N_DAYS + 1)
    )

def fetch_data():
    repo = BigQueryMeasurementRepo(get_big_query_client())
    for device_id in WANTED_DEVICE_IDS:
        repo.get_measurements(
            device_id,
            DEFAULT_DATE.shift(days=-1),
            DEFAULT_DATE.shift(days=N_DAYS + 1)
        )
        data_fetcher_logger().info(f"Got aggregated measurements for device {device_id}")



if __name__ == "__main__":
    setup_logging()
    fetch_data()