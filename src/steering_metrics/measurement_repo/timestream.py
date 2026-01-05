from enum import Enum
import pandas as pd
import boto3
from arrow import Arrow

from steering_metrics.measurement_repo.interfaces import IMeasurementRepo


class MeasurementType(Enum):
    VARCHAR = "varchar"
    DOUBLE = "double"

class TimestreamMeasurementRepo(IMeasurementRepo):

    def __init__(self):
        self._timestream_client = boto3.client('timestream-query', region_name="eu-central-1")
        self._database_name = "WebAppDB"
        self._table_name = "heat-pump-measurements"

    # def _query_single_measurement(self, device_id: str, measurement_name: str, since: Arrow, until: Optional[Arrow] = None, measurement_type: MeasurementType = MeasurementType.DOUBLE):
    #     since_str = since.to("utc").format("YYYY-MM-DD HH:mm:ss")
    #     until_str = until.to("utc").format("YYYY-MM-DD HH:mm:ss")
    #     return f"""
    #         SELECT
    #             time,
    #             measure_name,
    #             measure_value::{measurement_type.value}
    #         FROM "{self._database_name}"."{self._table_name}"
    #         WHERE
    #             device_id = '{device_id}'
    #             AND measure_name = '{measurement_name}'
    #             AND time > '{since_str}'
    #         ORDER BY time DESC
    #     """

    def _query_measurements(self, device_id: str, since: Arrow, until: Arrow) -> str:
        since_str = since.to("utc").format("YYYY-MM-DD HH:mm:ss")
        until_str = until.to("utc").format("YYYY-MM-DD HH:mm:ss")
        return f"""
            SELECT
                time,
                MAX(CASE WHEN measure_name = 'running_operational_statuses' THEN measure_value::varchar ELSE NULL END) as status,
                MAX(CASE WHEN measure_name = 'space1_temperature' THEN measure_value::double ELSE NULL END) as temperature,
                MAX(CASE WHEN measure_name = 'current_power' THEN measure_value::double ELSE NULL END) as power,
                MAX(CASE WHEN measure_name = 'space1_setpoint' THEN measure_value::double ELSE NULL END) as setpoint,
                MAX(CASE WHEN measure_name = 'auxiliary_heater_power' THEN measure_value::double ELSE NULL END) as auxiliary_power
            FROM "{self._database_name}"."{self._table_name}"
            WHERE
                device_id = '{device_id}'
                AND measure_name IN ('running_operational_statuses', 'space1_temperature', 'current_power', 'space1_setpoint', 'auxiliary_heater_power')
                    AND time >= '{since_str}' AND time <= '{until_str}'
            GROUP BY time, device_id
            ORDER BY time DESC
        """

    def get_measurements_df(self, device_id: str, since: Arrow, until: Arrow) -> pd.DataFrame:
        query_string = self._query_measurements(device_id, since, until)

        all_rows = []
        column_names = []
        next_token = None

        # Loop until all pages are fetched
        while True:
            query_kwargs = {"QueryString": query_string}
            if next_token:
                query_kwargs["NextToken"] = next_token

            response = self._timestream_client.query(**query_kwargs)

            # Set column names from the first page metadata
            if not column_names:
                column_names = [col["Name"] for col in response["ColumnInfo"]]

            # Parse the rows in the current page
            for row in response["Rows"]:
                row_values = [
                    cell.get("ScalarValue") for cell in row["Data"]
                ]
                all_rows.append(row_values)

            # Check if there is another page
            next_token = response.get("NextToken")
            if not next_token:
                break

        # Create DataFrame
        df = pd.DataFrame(all_rows, columns=column_names)

        if not df.empty:
            # Type Conversion
            df["time"] = pd.to_datetime(df["time"])

            # Automatic numeric conversion for everything except time and status
            cols_to_fix = [c for c in df.columns if c not in ["time", "status"]]
            for col in cols_to_fix:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def get_measurements(self, device_id: str, since: Arrow, until: Arrow) -> pd.DataFrame:
        df = self.get_measurements_df(device_id, since, until)
        df.to_csv(f"device_{device_id}.csv", index=False)
        return df

