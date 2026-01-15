from arrow import Arrow
import pandas as pd
import matplotlib.pyplot as plt

from steering_metrics.config import MPC_DEVICE
from steering_metrics.day_prices.csv_price_getter import CSVPriceGetter
from steering_metrics.measurement_repo.csv_repo import CSVMeasurementRepo
from steering_metrics.metrics.calculator import DailyMetricCalculator
from steering_metrics.metrics.options import CalculatorOptions, MissingDataFillType, ConsumptionRule


def create_price_setpoint_plot(date: Arrow, device_id: str):
    data_repo = CSVMeasurementRepo()
    price_repo = CSVPriceGetter()

    since = date
    until = date.shift(days=4)
    data = data_repo.get_measurements(device_id=device_id, since=date, until=until)
    prices = price_repo.get_prices(since=since, until=until)

    df = pd.merge(prices, data, left_index=True, right_index=True, how="outer")
    data_accuracy = len(df[df["avg_power"].notna()]) / len(df)

    df.fillna({"most_frequent_status": "UNKNOWN"}, inplace=True)
    df.fillna({"other_most_frequent_status": "UNKNOWN"}, inplace=True)
    df.fillna({"sh_mode": "UNKNOWN"}, inplace=True)
    df.fillna(0, inplace=True)

    df["total_power"] = df["avg_power"] + df["avg_aux_power"]
    # df["consumption_power"] = df["total_power"] if self._options.auxiliary_power_included else df["avg_power"]
    df["consumption_power"] = df["avg_power"]
    _sh = df['most_frequent_status'] == 'HEATING'.lower()
    df["consumption_power"] = df["consumption_power"] * _sh
    _power_greater_than_threshold = df["consumption_power"] >= 0.2
    df["is_consumption_block"] = _power_greater_than_threshold

    fig, ax1 = plt.subplots(
        1, 1,
        figsize=(15, 6),
        gridspec_kw={"height_ratios": [1]},
        sharex=True
    )
    ax1.step(df.index, df["avg_setpoint"]>23, label="heat_control", where="post", alpha=0.2, color="tab:green")
    ax2 = ax1.twinx()
    ax2.step(df.index, df["price_EUR_kWh"], label="consumption", where="post", alpha=0.7, color="black")
    _controlling = df["avg_setpoint"] > 23
    ax2.fill_between(df.index, df["price_EUR_kWh"] * _controlling, step="post", alpha=0.2, color="tab:green")
    plt.show()



def main():
    date = Arrow(2026, 1, 13, 23)
    options = CalculatorOptions(missing_data_fill_type=MissingDataFillType.ZERO, auxiliary_power_included=False, consumption_rule=ConsumptionRule.SH)
    DailyMetricCalculator(CSVPriceGetter(), CSVMeasurementRepo(), options=options).calculate(device_id=MPC_DEVICE, date=date, plot=True)



if __name__ == '__main__':
    # main()
    create_price_setpoint_plot(Arrow(2026, 1, 11, 23), MPC_DEVICE)