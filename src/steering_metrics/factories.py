from functools import lru_cache

from google.cloud import bigquery


@lru_cache(maxsize=1)
def get_big_query_client() -> bigquery.Client:
    return bigquery.Client()