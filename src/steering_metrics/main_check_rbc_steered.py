from arrow import Arrow
import matplotlib.pyplot as plt

from steering_metrics.factories import get_big_query_client
import pandas as pd


EXCLUDED_ENERGY_SUPPLIER = "Frank Energie"


def get_unique_steered_devices(date: Arrow) -> pd.DataFrame:
    partition_date = date.datetime.strftime('%Y-%m-%d')
    query =  f"""
        SELECT 
          DISTINCT device_id, 
                   user_id,
                   brand,
                   system_id,
                   energy_supplier
        FROM `nox-energy-431214.asset_telemetry_raw.rbc_decisions`
        WHERE partition_date = DATE('{partition_date}')
            AND energy_supplier != '{EXCLUDED_ENERGY_SUPPLIER}'
        ORDER BY brand, device_id
    """
    query_job = get_big_query_client().query(query)
    response = query_job.result()
    data = []
    for row in response:
        data.append(dict(row))
    return pd.DataFrame(data)

def main():
    start = Arrow(2026, 1, 1, 0, tzinfo="utc")
    dfs = []
    for i in range(0, 15):
        date = start.shift(days=i)
        _df = get_unique_steered_devices(date)
        _df["date"] = date.format("YYYY-MM-DD")
        dfs.append(_df)

    full_df = pd.concat(dfs)

    # Group by date and brand, then count
    stats = full_df.groupby(['date', 'brand']).size().unstack(fill_value=0)

    # Plot as a bar chart
    ax = stats.plot(kind='bar', figsize=(10, 6))
    ax.set_ylabel("Number of Devices")
    ax.set_title("Steered Devices per Brand by Day")
    plt.savefig("steered_devices_by_day.png")
    plt.show()


if __name__ == "__main__":
    main()