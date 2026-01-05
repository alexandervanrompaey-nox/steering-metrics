import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np
from steering_metrics.config import DEVICE_ID


def create_metrics_evolution_plot(metrics: pd.DataFrame):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(
        4, 1, figsize=(30, 20), sharex=True, gridspec_kw={"height_ratios": [1, 1, 1, 1]}
    )
    ax1.set_title("Average prices")
    ax1.plot(
        metrics["timestamp"], metrics["avg_price_day"], label="avg_price_day", color="blue", marker=".", alpha=0.5,
    )
    ax1.plot(
        metrics["timestamp"], metrics["min_price_day"], label="min_price_day", color="green", marker=".", alpha=0.5
    )
    ax1.plot(
        metrics["timestamp"], metrics["max_price_day"], label="max_price_day", color="red", marker=".", alpha=0.5
    )
    ax1.plot(
        metrics["timestamp"], metrics["avg_price_cheapest"], label="avg_price_cheapest", color="green", linestyle="dashed", marker=".", alpha=0.5
    )
    ax1.plot(
        metrics["timestamp"], metrics["avg_price_most_expensive"], label="avg_price_most_expensive", color="red", linestyle="dashed", marker=".", alpha=0.5
    )
    ax1.plot(
        metrics["timestamp"], metrics["avg_price_actual"], label="avg_price_actual", color="black", linestyle="dashed", marker=".", alpha=0.5
    )
    ax1.plot(
        metrics["timestamp"], metrics["avg_price_actual_weighted"], label="avg_price_actual_weighted", color="black", marker=".", alpha=0.5
    )
    ax1.set_xlabel("Date")
    ax1.set_ylabel("EUR/kWh")
    ax1.legend()
    ax1.grid(True, linestyle=":", alpha=0.6)

    x = date2num(metrics["timestamp"])
    ax2.bar(x - 0.1, metrics["pct_better_than_avg_day_price"], width=0.2, alpha=0.9, label="pct_better_than_avg_day_price")
    ax2.bar(x + 0.1, metrics["pct_better_than_avg_day_price_weighted"], width=0.2, alpha=0.9, label="pct_better_than_avg_day_price_weighted")
    ax2.set_xlabel("Date")
    ax3.set_ylabel("%")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend()

    ax3.plot(metrics["timestamp"], np.maximum(np.minimum(metrics["avg_steering_efficiency"], np.ones(len(metrics))), np.zeros(len(metrics))), marker=".", label="avg_steering_efficiency")
    ax3.plot(metrics["timestamp"], np.maximum(np.minimum(metrics["avg_steering_efficiency_weighted"], np.ones(len(metrics))), np.zeros(len(metrics))), marker=".", label="avg_steering_efficiency_weighted")
    ax3.plot(metrics["timestamp"], np.maximum(np.minimum(metrics["cheapest_block_selection_relative_auc"], np.ones(len(metrics))), np.zeros(len(metrics))), marker=".", label="cheapest_block_selection_relative_auc")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("%")
    ax3.legend()
    ax3.grid(True, linestyle=":", alpha=0.6)

    x = date2num(metrics["timestamp"])
    ax4.bar(x - 0.1, metrics["n_active_power_blocks"], width=0.2, alpha=0.9, color="black", label="n_active_power_blocks")
    ax4.bar(x + 0.1, metrics["n_correct_cheap_blocks"], width=0.2, alpha=0.9, color="green", label="n_correct_cheap_blocks")
    ax4.set_xlabel("Date")
    ax4.grid(True, linestyle=":", alpha=0.6)
    ax4.legend()

    fig.tight_layout()
    plt.show()


def main():
    device_id = DEVICE_ID
    device_id = "aa3a21f9-1dcf-53a8-8754-3085f99990a8"
    df = pd.read_csv(f"results/metric_{device_id}.csv", parse_dates=["timestamp"])
    create_metrics_evolution_plot(df)



if __name__=="__main__":
    main()