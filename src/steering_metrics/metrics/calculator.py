import matplotlib.pyplot as plt
import pandas as pd
from arrow import Arrow

from steering_metrics.day_prices.interfaces import IPriceProvider
from steering_metrics.measurement_repo.interfaces import IMeasurementRepo
from steering_metrics.metrics.domain import CheapestBlockSelection, DeviceMetric
from steering_metrics.metrics.options import CalculatorOptions, MissingDataFillType, ConsumptionRule


class DailyMetricCalculator:

    def __init__(self, price_provider: IPriceProvider, data_repo: IMeasurementRepo, options: CalculatorOptions):
        self._price_provider = price_provider
        self._data_repo = data_repo
        self._options = options

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
            percentiles.append(((i + 1) / length, (sorted_df.iloc[0:i+1]["is_consumption_block"].sum() / needed_blocks)))
        return CheapestBlockSelection(percentiles, required_blocks=needed_blocks, total_blocks=length)

    def calculate(self, device_id: str, date: Arrow, plot: bool = False) -> DeviceMetric:
        since = date
        until = date.shift(days=1)
        data = self._data_repo.get_measurements(device_id=device_id, since=date, until=until)
        prices = self._price_provider.get_prices(since=since, until=until)

        df = pd.merge(prices, data, left_index=True, right_index=True, how="outer")
        if len(df) == 0:
            print(device_id)
            print(date)
        data_accuracy = len(df[df["avg_power"].notna()]) / len(df)

        if self._options.missing_data_fill_type == MissingDataFillType.ZERO:
            df.fillna({"most_frequent_status": "UNKNOWN"}, inplace=True)
            df.fillna({"other_most_frequent_status": "UNKNOWN"}, inplace=True)
            df.fillna({"sh_mode": "UNKNOWN"}, inplace=True)
            df.fillna(0, inplace=True)
        else:
            df.ffill(inplace=True)
        df["total_power"] = df["avg_power"] + df["avg_aux_power"]
        df["consumption_power"] = df["total_power"] if self._options.auxiliary_power_included else df["avg_power"]

        if self._options.consumption_rule in [ConsumptionRule.SH_MANUAL_ONLY, ConsumptionRule.SH_DHW_MANUAL_ONLY]:
            _manual = df['sh_mode'] == "MANUAL"
            df["consumption_power"] = df["consumption_power"] * _manual

        if self._options.consumption_rule in [ConsumptionRule.SH, ConsumptionRule.SH_MANUAL_ONLY]:
            _sh = df['most_frequent_status'] == 'HEATING'.lower()
            df["consumption_power"] = df["consumption_power"] * _sh
        _power_greater_than_threshold = df["consumption_power"] >= self._options.power_threshold
        df["is_consumption_block"] = _power_greater_than_threshold

        # _manual = df['sh_mode'] == 'MANUAL' #TODO not using manual mode shizzle, ...
        _dhw = df['most_frequent_status'] == 'DHW'
        _sh = df['most_frequent_status'] == 'HEATING'
        # # TODO sometimes power when not in manual mode ... fucks it up again
        # # df["total_power_manual"] = df["total_power"] * _manual * _power_greater_than_threshold
        # # df["total_power_manual_sh"] = df["total_power"] * _manual * _power_greater_than_threshold * _sh
        # # df["total_power_manual_dhw"] = df["total_power"] * _manual * _power_greater_than_threshold * _dhw
        # # df["is_consumption_block"] = _manual * _power_greater_than_threshold
        df["total_power_manual"] = df["total_power"] * _power_greater_than_threshold
        df["total_power_manual_sh"] = df["total_power"] * _power_greater_than_threshold * _sh
        df["total_power_manual_dhw"] = df["total_power"] * _power_greater_than_threshold * _dhw

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

        cheapest_block_selection = self._calculate_percentile(df) if n_consumption_slots> 0 else None
        # cheapest_block_selection.plot()

        if plot:
            self._create_plot(df)
        if n_consumption_slots > 0:
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
                correct_selected_blocks_pct=df["is_correct_cheap_block"].sum() / n_consumption_slots,
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
        else:
            return DeviceMetric(
                timestamp=date,
                n_active_power_blocks=n_consumption_slots,
                active_power_blocks_pct=n_consumption_slots / len(df),
                avg_price_day=general_stats.loc["mean"]["price_EUR_kWh"],
                std_price_day=general_stats.loc["std"]["price_EUR_kWh"],
                min_price_day=general_stats.loc["min"]["price_EUR_kWh"],
                max_price_day=general_stats.loc["max"]["price_EUR_kWh"],
                avg_outdoor_temperature=general_stats.loc["mean"]["avg_outdoor_temperature"],
                avg_price_cheapest=None,
                avg_price_most_expensive=None,
                avg_price_actual=None,
                correct_selected_blocks_pct=None,
                n_correct_cheap_blocks=0,
                avg_price_actual_weighted=None,
                avg_steering_efficiency=None,
                avg_min_max_steering_efficiency=None,
                avg_min_max_steering_efficiency_weighted=None,
                avg_steering_efficiency_weighted=None,
                pct_better_than_avg_day_price=None,
                pct_better_than_avg_best_price=None,
                pct_better_than_avg_worst_price=None,
                pct_better_than_avg_day_price_weighted=None,
                pct_better_than_avg_best_price_weighted=None,
                pct_better_than_avg_worst_price_weighted=None,
                cheapest_block_selection=None,
                cheapest_block_selection_relative_auc=None,
                data_accuracy=data_accuracy,
            )