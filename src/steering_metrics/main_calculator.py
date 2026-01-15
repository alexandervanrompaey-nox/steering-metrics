import pandas as pd
from arrow import Arrow

from steering_metrics.config import DEFAULT_DATE, N_DAYS, WANTED_DEVICE_IDS, DEVICE_ID, MPC_DEVICE, CALCULATOR_OPTIONS
from steering_metrics.day_prices.csv_price_getter import CSVPriceGetter
from steering_metrics.log import setup_logging, get_steering_metrics_logger
from steering_metrics.measurement_repo.csv_repo import CSVMeasurementRepo
from steering_metrics.metrics.calculator import DailyMetricCalculator
from steering_metrics.metrics.options import CalculatorOptions, ConsumptionRule


def calculate_metric(device_id: str, options: CalculatorOptions):
    calculator = DailyMetricCalculator(CSVPriceGetter(), CSVMeasurementRepo(), options)
    results = []
    for i in range(0, N_DAYS):
        results.append(calculator.calculate(device_id=device_id, date=DEFAULT_DATE.shift(days=i)))
    results = pd.DataFrame(results)
    results.to_csv(f"results/metric_{device_id}_{options.options_string()}.csv", index=False)
    get_steering_metrics_logger().info(f"calculated metrics for device id: {device_id}")


def calculate_metrics_for_all_devices(options: CalculatorOptions):
    for d in WANTED_DEVICE_IDS:
        calculate_metric(device_id=d, options=options)


def calculate_metric_and_plot_for_device(device_id: str, date: Arrow, options: CalculatorOptions):
    DailyMetricCalculator(CSVPriceGetter(), CSVMeasurementRepo(), options).calculate(device_id=device_id, date=date, plot=True)


if __name__ == "__main__":
    setup_logging()
    calculate_metrics_for_all_devices(options=CALCULATOR_OPTIONS)
    # device_id = "6bb416ea-f469-46c5-8b8e-5df6b3a3fed3" # better device no activating all the time
    # calculate_metric_and_plot_for_device(device_id, Arrow(2026, 1, 12, 23, tzinfo="utc"), options)
