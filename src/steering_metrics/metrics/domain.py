from dataclasses import dataclass
from typing import List, Tuple, Optional

from arrow import Arrow
from matplotlib import pyplot as plt
from sklearn.metrics import auc


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
    n_correct_cheap_blocks: int
    active_power_blocks_pct: float
    avg_price_day: float
    std_price_day: float
    min_price_day: float
    max_price_day: float
    data_accuracy: float  # how many of the field have valid data
    avg_price_cheapest: Optional[float] = None
    avg_price_most_expensive: Optional[float] = None
    avg_price_actual: Optional[float] = None
    avg_price_actual_weighted: Optional[float] = None
    avg_outdoor_temperature: Optional[float] = None
    #actual metrics
    correct_selected_blocks_pct: Optional[float] = None # not a good one in my opinion
    avg_steering_efficiency: Optional[float] = None
    avg_steering_efficiency_weighted: Optional[float] = None
    avg_min_max_steering_efficiency: Optional[float] = None
    avg_min_max_steering_efficiency_weighted: Optional[float] = None
    pct_better_than_avg_day_price: Optional[float] = None
    pct_better_than_avg_best_price: Optional[float] = None
    pct_better_than_avg_worst_price: Optional[float] = None
    pct_better_than_avg_day_price_weighted: Optional[float] = None
    pct_better_than_avg_best_price_weighted: Optional[float] = None
    pct_better_than_avg_worst_price_weighted: Optional[float] = None
    cheapest_block_selection: Optional[CheapestBlockSelection] = None
    cheapest_block_selection_relative_auc: Optional[float] = None
