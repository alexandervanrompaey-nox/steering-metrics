import pandas as pd

from arrow import Arrow
from google.cloud.bigquery import Client
from steering_metrics.measurement_repo.interfaces import IMeasurementRepo


class BigQueryMeasurementRepo(IMeasurementRepo):
    def __init__(self, client: Client):
        self._client = client

    def _build_query(self, device_id: str, since: Arrow, until: Arrow) -> str:
        start_date = since.datetime.strftime('%Y-%m-%d')
        end_date = until.datetime.strftime('%Y-%m-%d')
        until = until.to("utc").strftime("%Y-%m-%dT%H:%M:%S")
        since = since.to("utc").strftime("%Y-%m-%dT%H:%M:%S")
        query = f"""
        SELECT 
            device_id,
            timestamp,
            current_power,
            auxiliary_heater_power,
            space1_temperature,
            space1_setpoint
        FROM `nox-energy-431214.asset_telemetry_raw.heat-pump-measurements` 
        WHERE partition_date >= DATE('{start_date}')
        AND partition_date <= DATE('{end_date}')
        AND timestamp >= DATETIME('{since}')
        AND timestamp <= DATETIME('{until}')
        AND device_id = '{device_id}'
        """
        return query

    def _build_query_15_minute_window(self, device_id: str, since: Arrow, until: Arrow) -> str:
        start_date = since.datetime.strftime('%Y-%m-%d')
        end_date = until.datetime.strftime('%Y-%m-%d')
        until = until.to("utc").strftime("%Y-%m-%dT%H:%M:%S")
        since = since.to("utc").strftime("%Y-%m-%dT%H:%M:%S")
        return f"""
            WITH aggregated_15_min AS (
            SELECT
                device_id,
                TIMESTAMP_BUCKET(timestamp, INTERVAL 15 MINUTE) AS time_window,
                AVG(current_power) AS avg_power,
                MAX(current_power) AS max_power,
                AVG(auxiliary_heater_power) AS avg_aux_power,
                MAX(auxiliary_heater_power) AS max_aux_power,
                AVG(space1_temperature) AS avg_temperature,
                MIN(space1_temperature) AS min_temperature,
                MAX(space1_temperature) AS max_temperature,
                AVG(outdoor_temperature) AS avg_outdoor_temperature,
                AVG(space1_setpoint) AS avg_setpoint,
                ARRAY_AGG(running_operational_statuses ORDER BY running_operational_statuses DESC LIMIT 1)[OFFSET(0)] as most_frequent_status,
                APPROX_TOP_COUNT(running_operational_statuses, 1)[OFFSET(0)].value AS other_most_frequent_status,
                APPROX_TOP_COUNT(current_space_heating_mode, 1)[OFFSET(0)].value AS sh_mode
            FROM `nox-energy-431214.asset_telemetry_raw.heat-pump-measurements` 
            WHERE partition_date >= DATE('{start_date}')
            AND partition_date <= DATE('{end_date}')
            AND timestamp >= DATETIME('{since}')
            AND timestamp <= DATETIME('{until}')
            AND device_id = '{device_id}'
            GROUP BY time_window, device_id)
        SELECT *
        FROM GAP_FILL(
            TABLE aggregated_15_min,
            ts_column => 'time_window',
            bucket_width => INTERVAL 15 MINUTE,
            partitioning_columns => ['device_id'],
            value_columns => [
                ('avg_power', 'null'),
                ('max_power', 'null'),
                ('avg_aux_power', 'null'),
                ('max_aux_power', 'null'),
                ('avg_temperature', 'null'),
                ('min_temperature', 'null'),
                ('max_temperature', 'null'),
                ('avg_setpoint', 'null'),
                ('most_frequent_status', 'null'),
                ('other_most_frequent_status', 'null'),
                ('sh_mode', 'null'),
                ('avg_outdoor_temperature', 'null')
            ]
        )
        ORDER BY time_window asc
        """

    def get_measurements_df(self, device_id: str, since: Arrow, until: Arrow) -> pd.DataFrame:
        query_job = self._client.query(self._build_query_15_minute_window(device_id, since, until))
        response = query_job.result()
        data = []
        for row in response:
            data.append(dict(row))

        df = pd.DataFrame(data)
        df['time_window'] = pd.to_datetime(df['time_window'], utc=True)
        df.set_index("time_window", inplace=True)
        df.drop(columns=["device_id"], inplace=True)
        return df

    def get_measurements(self, device_id: str, since: Arrow, until: Arrow) -> pd.DataFrame:
        df = self.get_measurements_df(device_id, since, until)
        df.to_csv(f"data/device_{device_id}.csv", index=True)
        return df