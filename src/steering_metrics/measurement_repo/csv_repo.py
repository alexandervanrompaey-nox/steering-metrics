from arrow import Arrow
import pandas as pd

from steering_metrics.measurement_repo.interfaces import IMeasurementRepo


class CSVMeasurementRepo(IMeasurementRepo):

    def get_measurements(self, device_id: str, since: Arrow, until: Arrow) -> pd.DataFrame:
        df = pd.read_csv(f"data/device_{device_id}.csv", parse_dates=["time_window"], index_col="time_window")
        return df.loc[since.datetime:until.shift(seconds=-1).datetime]
