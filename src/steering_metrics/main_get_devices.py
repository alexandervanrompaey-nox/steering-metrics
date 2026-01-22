from steering_metrics.factories import get_big_query_client
from arrow import Arrow

DEFAULT_DATE = Arrow(2025, 11,30, 23, tz="utc")
N_DAYS = 46

EXCLUDED_ENERGY_SUPPLIER = "Frank Energie"


MPC_DEVICE = "df9a5c3c-b733-4b30-a6de-f614cb662a08"


def get_query():
    since = DEFAULT_DATE
    until = DEFAULT_DATE.shift(days=N_DAYS + 1)
    start_date = since.datetime.strftime('%Y-%m-%d')
    end_date = until.datetime.strftime('%Y-%m-%d')
    until = until.to("utc").strftime("%Y-%m-%dT%H:%M:%S")
    since = since.to("utc").strftime("%Y-%m-%dT%H:%M:%S")
    return f"""
        SELECT 
          DISTINCT device_id, 
                   user_id,
                   brand,
                   system_id,
                   energy_supplier
        FROM `nox-energy-431214.asset_telemetry_raw.rbc_decisions`
        WHERE partition_date >= DATE('{start_date}')
            AND partition_date <= DATE('{end_date}')
            AND ingestion_time >= DATETIME('{since}')
            AND ingestion_time <= DATETIME('{until}')
            AND energy_supplier != '{EXCLUDED_ENERGY_SUPPLIER}'
        ORDER BY brand, device_id
    """

def main():
    query_job = get_big_query_client().query(get_query())
    response = query_job.result()
    data = []
    for row in response:
        data.append(dict(row))
        print(f'"{row["device_id"]}",')


if __name__=="__main__":
    main()