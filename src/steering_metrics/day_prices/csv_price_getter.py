import os
import pandas as pd
from arrow import Arrow

from steering_metrics.day_prices.interfaces import IPriceProvider


class CSVPriceGetter(IPriceProvider):
    def __init__(self):
        self._path = f"{os.getcwd()}/dam_prices.csv"

    def get_prices(self, since: Arrow, until: Arrow) -> pd.DataFrame:
        df_prices = pd.read_csv(self._path, parse_dates=["ts_utc", "ts_local"], index_col="ts_utc")
        return df_prices.loc[since.datetime:until.shift(seconds=-1).datetime]


