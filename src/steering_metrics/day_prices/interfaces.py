from abc import ABC, abstractmethod

import pandas as pd
from arrow import Arrow


class IPriceProvider(ABC):
    @abstractmethod
    def get_prices(self, since: Arrow, until: Arrow) -> pd.DataFrame:
        raise NotImplementedError
