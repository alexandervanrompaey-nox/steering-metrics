from typing import List

import pandas as pd

from steering_metrics.config import DEFAULT_DATE, WANTED_DEVICE_IDS
from steering_metrics.log import setup_logging
from steering_metrics.metrics.options import PlotOptions, CalculatorOptions

import seaborn as sns
import matplotlib.pyplot as plt


def create_plot(devices: List[str], options: PlotOptions, calculator_options: CalculatorOptions):
    # np.maximum(np.minimum(metrics["avg_steering_efficiency"], np.ones(len(metrics))), np.zeros(len(metrics)))

    df = pd.DataFrame()
    df_acc = pd.DataFrame()
    df_temp = pd.DataFrame()
    for d in devices:
        _df = pd.read_csv(f"results/metric_{d}_{calculator_options.options_string()}.csv", parse_dates=["timestamp"], index_col="timestamp")
        df[d] = _df[options.metric_name]
        df_acc[d] = _df["data_accuracy"]
        df_temp[d] = _df["avg_outdoor_temperature"]

    some_series = df_temp.T.mean()
    df_temp = pd.DataFrame(some_series, columns=["temperature"])
    df_temp.index = df_temp.index.tz_convert("Europe/Brussels")
    df_temp.index = df_temp.index.date
    mask = df_acc == 0
    mask.index = mask.index.tz_convert("Europe/Brussels")
    mask.index = mask.index.date
    df.index = df.index.tz_convert("Europe/Brussels")
    df.index = df.index.date

    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(15, 6),
        gridspec_kw={"height_ratios": [1, len(devices)]},
        sharex=True
    )
    plt.subplots_adjust(left=0.2)
    ax1 = sns.heatmap(df_temp.T, annot=True, fmt=".2f", cmap="RdYlGn", ax=ax1, cbar=False, square=False, linecolor="black", linewidth=0.5, annot_kws={"size": 8})
    ax1.tick_params(axis="y", rotation=0)  # 0 = horizontal

    sns.heatmap(df.T, annot=True, fmt=".2f", cmap="RdYlGn", mask=mask.T, ax=ax2, cbar=False, square=False, linecolor="black", linewidth=0.5, annot_kws={"size": 8})
    ax2.tick_params(axis="x", rotation=90)  # 0 = horizontal
    plt.show()
    print("shit")


if __name__ == "__main__":
    setup_logging()
    start_date = DEFAULT_DATE
    end_date = start_date.shift(days=41)
    # plot_options = PlotOptions("active_power_blocks_pct", start_date=start_date, end_date=end_date)
    plot_options = PlotOptions("avg_steering_efficiency", start_date=start_date, end_date=end_date)
    calc_options = CalculatorOptions()
    create_plot(WANTED_DEVICE_IDS, plot_options, calc_options)
