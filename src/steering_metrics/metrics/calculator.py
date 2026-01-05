from dataclasses import dataclass
from typing import Tuple, List

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.metrics import auc
from arrow import Arrow

from steering_metrics.day_prices.interfaces import IPriceProvider
from steering_metrics.measurement_repo.interfaces import IMeasurementRepo

@dataclass
class CheapestBlockSelection:
    blocks: List[Tuple[float, float]]
    required_blocks: int
    total_blocks: int

    def plot(self) -> None:
        plt.step([p[0] for p in self.blocks], [p[1] for p in self.blocks], where='post')
        if self.required_blocks > 0:
            plt.step([l / self.total_blocks for l in range(self.total_blocks)], [min(l / self.required_blocks, 1) for l in range(self.total_blocks)],
                     where="post", linestyle="dashed", color="black")
        plt.show()

    def calculate_relative_auc(self) -> float:
        actual = auc([b[0] for b in self.blocks], [b[1] for b in self.blocks])
        if self.required_blocks > 0:
            best_possible = auc([l / self.total_blocks for l in range(self.total_blocks)], [min(l / self.required_blocks, 1) for l in range(self.total_blocks)])
        else:
            best_possible = actual
        return actual / best_possible


@dataclass
class DeviceMetric:
    timestamp: Arrow
    n_active_power_blocks: int
    n_correct_cheap_blocks:int
    active_power_blocks_pct: float
    avg_price_day: float
    std_price_day: float
    min_price_day: float
    max_price_day: float
    avg_price_cheapest: float
    avg_price_most_expensive: float
    avg_price_actual: float
    avg_price_actual_weighted: float
    avg_outdoor_temperature: float
    #actual metrics
    correct_selected_blocks_pct: float # not a good one in my opinion
    avg_steering_efficiency: float
    avg_steering_efficiency_weighted: float
    avg_min_max_steering_efficiency: float
    avg_min_max_steering_efficiency_weighted: float
    pct_better_than_avg_day_price: float
    pct_better_than_avg_best_price: float
    pct_better_than_avg_worst_price: float
    pct_better_than_avg_day_price_weighted: float
    pct_better_than_avg_best_price_weighted: float
    pct_better_than_avg_worst_price_weighted: float
    cheapest_block_selection: CheapestBlockSelection
    cheapest_block_selection_relative_auc: float

    data_accuracy: float # how many of the field have valid data



class DailyMetricCalculator:
    HEATING_POWER_MARGIN = 0.2 #KW

    def __init__(self, price_provider: IPriceProvider, data_repo: IMeasurementRepo):
        self._price_provider = price_provider
        self._data_repo = data_repo

    def _create_plot(self, df: pd.DataFrame) -> None:

        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(15, 8), sharex=True, gridspec_kw={"height_ratios": [1, 1]}
        )
        fig.suptitle(f"Consumption analysis, amount of consumption slots: {df["is_consumption_block"].sum()}")
        # --- Subplot 1: Temperature & Heating ---
        ax1.set_ylabel("Average Power (kW)")
        ax1.step(
            df.index,
            df["total_power"],
            color="tab:orange",
            where="post",
            label="total_power",
            linestyle="dashed"
        )
        ax1.step(
            df.index,
            df["total_power_manual_sh"],
            color="tab:red",
            where="post",
            label="total_power_manual_sh",
            alpha=0.6
        )
        ax1.step(
            df.index,
            df["total_power_manual_dhw"],
            color="tab:blue",
            where="post",
            label="total_power_manual_dhw",
            alpha=0.6
        )
        ax1.tick_params(axis="y")
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend()

        ax2.set_ylabel("Price (EUR/kWh)")
        ax2.step(df.index, df["price_EUR_kWh"], where="post", label="Price")
        ax2.fill_between(df.index, df["is_cheap_block"] * df["price_EUR_kWh"], step="post", alpha=0.2, color="tab:green", label=f"Cheapest {df["is_consumption_block"].sum()} periods")
        ax2.fill_between(df.index, df["is_consumption_block"] * df["price_EUR_kWh"], step="post", alpha=0.2, color="tab:orange", label=f"Actual {df["is_consumption_block"].sum()} periods")

        # ax2.fill_between(prices.index, prices["price_EUR_kWh"], where=prices["cheapest_slots"], step="post", alpha=0.2, color="tab:green", label=f"Cheapest {n_consumption_slots} periods")
        # ax2.fill_between(prices.index, prices["price_EUR_kWh"], where=prices["actual_selected_slots"], step="post", alpha=0.2, color="tab:orange", label=f"Actual {n_consumption_slots} periods")
        ax2.hlines(df["price_EUR_kWh"].sort_values().iloc[0:df["is_consumption_block"].sum()].max(), xmin=df.index[0], xmax=df.index[-1], linestyles="dashed", label="Cheapest ")
        ax2.tick_params(axis="y")
        ax2.grid(True, linestyle=":", alpha=0.6)
        ax2.set_ylim(0, 0.125)
        ax2.set_xlabel("Time")
        plt.show()

    def _calculate_pct_better(self, base: float, value: float) -> float:
        return (base - value) / base

    @staticmethod
    def _calculate_percentile(df_: pd.DataFrame) -> CheapestBlockSelection:
        percentiles = [(0., 0.)]
        sorted_df = df_.sort_values(by="price_EUR_kWh", ascending=True)
        length = len(df_)
        needed_blocks = sorted_df[sorted_df["is_consumption_block"] == True].shape[0]
        for i in range(len(df_)):
            percentiles.append(((i +1 ) / length, (sorted_df.iloc[0:i+1]["is_consumption_block"].sum() / needed_blocks)))
        return CheapestBlockSelection(percentiles, required_blocks=needed_blocks, total_blocks=length)

    def calculate(self, device_id: str, date: Arrow, plot: bool = False) -> DeviceMetric:
        since = date
        until = date.shift(days=1)
        data = self._data_repo.get_measurements(device_id=device_id, since=date, until=until)
        prices = self._price_provider.get_prices(since=since, until=until)

        df = pd.merge(prices, data, left_index=True, right_index=True, how="outer")
        data_accuracy = len(df[df["avg_power"].notna()]) / len(df)

        # Clean and calculate some field
        df.ffill(inplace=True)
        df["total_power"] = df["avg_power"] + df["avg_aux_power"]
        _manual = df['sh_mode'] == 'MANUAL'
        _power_greater_than_threshold = df["total_power"] > 0.2
        _dhw = df['most_frequent_status'] == 'DHW'
        _sh = df['most_frequent_status'] == 'HEATING'
        # TODO sometimes power when not in manual mode ... fucks it up again
        # df["total_power_manual"] = df["total_power"] * _manual * _power_greater_than_threshold
        # df["total_power_manual_sh"] = df["total_power"] * _manual * _power_greater_than_threshold * _sh
        # df["total_power_manual_dhw"] = df["total_power"] * _manual * _power_greater_than_threshold * _dhw
        # df["is_consumption_block"] = _manual * _power_greater_than_threshold
        df["total_power_manual"] = df["total_power"] * _power_greater_than_threshold
        df["total_power_manual_sh"] = df["total_power"] * _power_greater_than_threshold * _sh
        df["total_power_manual_dhw"] = df["total_power"] * _power_greater_than_threshold * _dhw
        df["is_consumption_block"] = _power_greater_than_threshold

        general_stats = df.describe()
        n_consumption_slots = len(df[df["is_consumption_block"]])
        _max_price_cheapest_slots = df["price_EUR_kWh"].sort_values().iloc[0:n_consumption_slots].max()
        df["is_cheap_block"] = df["price_EUR_kWh"] <= _max_price_cheapest_slots
        _min_price_most_expensive_slots = df["price_EUR_kWh"].sort_values(ascending=False).iloc[0:n_consumption_slots].min()
        df["is_expensive_block"] = df["price_EUR_kWh"] >= _min_price_most_expensive_slots
        df["is_correct_cheap_block"] = df["is_cheap_block"] * df["is_consumption_block"]
        df["is_incorrect_cheap_block"] = df["is_consumption_block"] * ~df["is_cheap_block"]

        avg_price_cheapest_blocks = df[df["is_cheap_block"]]["price_EUR_kWh"].mean()
        avg_price_most_expensive_blocks = df[df["is_expensive_block"]]["price_EUR_kWh"].mean()
        avg_price_selected_blocks = df[df["is_consumption_block"]]["price_EUR_kWh"].mean()
        df["consumption_pct"] = (df["total_power"] * df["is_consumption_block"]) / df[df["is_consumption_block"]]["total_power"].sum()
        avg_price_selected_blocks_energy_weighted = (df["consumption_pct"]*df["price_EUR_kWh"]).sum()

        # avg_price_incorrect_blocks = df[df["is_incorrect_cheap_block"]]["price_EUR_kWh"].mean() # TODO not needed
        # avg_price_correct_blocks = df[df["is_correct_cheap_block"]]["price_EUR_kWh"].mean() # TODO not needed

        avg_steering_efficiency = 0.0
        if avg_price_most_expensive_blocks != avg_price_cheapest_blocks:
            avg_steering_efficiency = (avg_price_most_expensive_blocks - avg_price_selected_blocks) / (
                avg_price_most_expensive_blocks - avg_price_cheapest_blocks
            )
        avg_steering_efficiency_weighted = 0.0
        if avg_price_most_expensive_blocks != avg_price_cheapest_blocks:
            avg_steering_efficiency_weighted = (avg_price_most_expensive_blocks - avg_price_selected_blocks_energy_weighted) / (
                avg_price_most_expensive_blocks - avg_price_cheapest_blocks
            )

        avg_min_max_steering_efficiency = 0.
        if df["price_EUR_kWh"].min() != df["price_EUR_kWh"].max():
            avg_min_max_steering_efficiency = (df["price_EUR_kWh"].max() - avg_price_selected_blocks) / (
                df["price_EUR_kWh"].max() - df["price_EUR_kWh"].min()
            )
        avg_min_max_steering_efficiency_weighted = 0.
        if df["price_EUR_kWh"].min() != df["price_EUR_kWh"].max():
            avg_min_max_steering_efficiency_weighted = (df["price_EUR_kWh"].max() - avg_price_selected_blocks_energy_weighted) / (
                df["price_EUR_kWh"].max() - df["price_EUR_kWh"].min()
            )

        cheapest_block_selection = self._calculate_percentile(df)
        # cheapest_block_selection.plot()

        if plot:
            self._create_plot(df)
        return DeviceMetric(
            timestamp=date,
            n_active_power_blocks=n_consumption_slots,
            active_power_blocks_pct=n_consumption_slots/len(df),
            avg_price_day=general_stats.loc["mean"]["price_EUR_kWh"],
            std_price_day=general_stats.loc["std"]["price_EUR_kWh"],
            min_price_day=general_stats.loc["min"]["price_EUR_kWh"],
            max_price_day=general_stats.loc["max"]["price_EUR_kWh"],
            avg_outdoor_temperature=general_stats.loc["mean"]["avg_outdoor_temperature"],
            avg_price_cheapest=avg_price_cheapest_blocks,
            avg_price_most_expensive=avg_price_most_expensive_blocks,
            avg_price_actual=avg_price_selected_blocks,
            correct_selected_blocks_pct=df["is_correct_cheap_block"].sum()/n_consumption_slots,
            n_correct_cheap_blocks=df["is_correct_cheap_block"].sum(),
            avg_price_actual_weighted=avg_price_selected_blocks_energy_weighted,
            avg_steering_efficiency=avg_steering_efficiency,
            avg_min_max_steering_efficiency=avg_min_max_steering_efficiency,
            avg_min_max_steering_efficiency_weighted=avg_min_max_steering_efficiency_weighted,
            avg_steering_efficiency_weighted=avg_steering_efficiency_weighted,
            pct_better_than_avg_day_price=self._calculate_pct_better(general_stats.loc["mean"]["price_EUR_kWh"], avg_price_selected_blocks),
            pct_better_than_avg_best_price=self._calculate_pct_better(avg_price_cheapest_blocks, avg_price_selected_blocks),
            pct_better_than_avg_worst_price=self._calculate_pct_better(avg_price_most_expensive_blocks, avg_price_selected_blocks),
            pct_better_than_avg_day_price_weighted=self._calculate_pct_better(general_stats.loc["mean"]["price_EUR_kWh"], avg_price_selected_blocks_energy_weighted),
            pct_better_than_avg_best_price_weighted=self._calculate_pct_better(avg_price_cheapest_blocks, avg_price_selected_blocks_energy_weighted),
            pct_better_than_avg_worst_price_weighted=self._calculate_pct_better(avg_price_most_expensive_blocks, avg_price_selected_blocks_energy_weighted),
            cheapest_block_selection=cheapest_block_selection,
            cheapest_block_selection_relative_auc=cheapest_block_selection.calculate_relative_auc(),
            data_accuracy=data_accuracy,
        )
