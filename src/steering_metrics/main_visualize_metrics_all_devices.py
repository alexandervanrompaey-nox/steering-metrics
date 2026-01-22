from typing import List

import pandas as pd
import numpy as np

from steering_metrics.config import DEFAULT_DATE, WANTED_DEVICE_IDS, CALCULATOR_OPTIONS
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
        # TODO check this before plotting
        df[d] = np.round(_df[options.metric_name],2)
        # df[d] = np.maximum(np.minimum(_df[options.metric_name], np.ones(len(_df[options.metric_name]))), np.zeros(len(_df[options.metric_name])))
        # df[d] = np.maximum(np.minimum(_df[options.metric_name], 0.3* np.ones(len(_df[options.metric_name]))), -0.3 * np.ones(len(_df[options.metric_name])))

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

    # fig, (ax1, ax2) = plt.subplots(
    #     2, 1,
    #     figsize=(15, 6),
    #     gridspec_kw={"height_ratios": [1, len(devices)]},
    #     sharex=True
    # )
    # plt.subplots_adjust(left=0.2)
    # ax1 = sns.heatmap(df_temp.T, annot=True, fmt=".2f", cmap="RdYlGn", ax=ax1, cbar=False, square=False, linecolor="black", linewidth=0.5, annot_kws={"size": 8})
    # ax1.tick_params(axis="y", rotation=0)  # 0 = horizontal
    #
    # sns.heatmap(df.T, annot=True, fmt=".2f", cmap="RdYlGn", mask=mask.T, ax=ax2, cbar=False, square=False, linecolor="black", linewidth=0.5, annot_kws={"size": 8})
    # ax2.tick_params(axis="x", rotation=90)  # 0 = horizontal
    # plt.show()
    # print("shit")

    fig, ax1 = plt.subplots(
        1, 1,
        figsize=(15, 6),
        gridspec_kw={"height_ratios": [len(devices)]},
        sharex=True
    )
    plt.subplots_adjust(left=0.2)
    sns.heatmap(df.T, annot=True, fmt=".2f", cmap="RdYlGn", mask=mask.T, ax=ax1, cbar=False, square=False, linecolor="black", linewidth=0.5, annot_kws={"size": 8})
    ax1.tick_params(axis="x", rotation=90)  # 0 = horizontal
    plt.show()
    print("shit")


if __name__ == "__main__":
    # TODO check the todo regarding plotting
    setup_logging()
    start_date = DEFAULT_DATE
    end_date = start_date.shift(days=41)
    # plot_options = PlotOptions("active_power_blocks_pct", start_date=start_date, end_date=end_date)
    # plot_options = PlotOptions("avg_steering_efficiency_weighted", start_date=start_date, end_date=end_date)
    # plot_options = PlotOptions("pct_better_than_avg_day_price_weighted", start_date=start_date, end_date=end_date)
    # plot_options = PlotOptions("n_active_power_blocks", start_date=start_date, end_date=end_date)
    plot_options = PlotOptions("data_accuracy", start_date=start_date, end_date=end_date)
    create_plot(WANTED_DEVICE_IDS, plot_options, CALCULATOR_OPTIONS)
