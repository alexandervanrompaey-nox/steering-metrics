from dataclasses import dataclass, fields
from enum import Enum
from typing import Optional
from arrow import Arrow

from steering_metrics.metrics.domain import DeviceMetric


class MissingDataFillType(Enum):
    ZERO = "ZERO"
    FORWARD_FILL = "FFILL"


class ConsumptionRule(Enum):
    SH = "SH"
    SH_DHW = "SH-DHW"
    SH_MANUAL_ONLY = "SH-MANUAL-ONLY"
    SH_DHW_MANUAL_ONLY = "SH-MANUAL-ONLY"  #only for vaillant


@dataclass
class CalculatorOptions:
    missing_data_fill_type: Optional[MissingDataFillType] = MissingDataFillType.ZERO
    auxiliary_power_included: Optional[bool] = True
    consumption_rule: Optional[ConsumptionRule] = ConsumptionRule.SH_DHW
    power_threshold: Optional[float] = 0.2

    def options_string(self) -> str:
        threshold = f"{self.power_threshold:.2f}".replace(".", "")
        return f"df-{self.missing_data_fill_type.value}_aux-{self.auxiliary_power_included}_consumption-{self.consumption_rule.value}_threshold-{threshold}"





@dataclass
class PlotOptions:
    metric_name: str
    start_date: Arrow
    end_date: Arrow

    def __post_init__(self):
        if self.metric_name not in [f.name for f in fields(DeviceMetric)]:
            raise ValueError(f"Metric name {self.metric_name} must be in {fields(DeviceMetric)}")
