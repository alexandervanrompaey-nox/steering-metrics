from typing import Optional
from urllib.error import HTTPError
from pathlib import Path

import requests
import io
import pandas as pd
from dataclasses import dataclass
from arrow import Arrow
from pytz import timezone
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from lxml import etree

from steering_metrics.log import get_dam_fetcher_logger


@dataclass
class DAMDataSettings:
    token: str = "b43b4e0c-719e-4c37-9dda-2e4378eee666"
    base_url: str = "https://web-api.tp.entsoe.eu/api"
    bzn_eic: str = "10YBE----------2"
    doc_a44: str = "A44"
    proc_a01: str = "A01"
    contract_a01: str = "A01"
    timezone: str = "Europe/Brussels"

    day_shifts: int = 1
    output_csv: str = "dam_prices.csv"


class DAMDataFetcher:
    def __init__(self, settings: Optional[DAMDataSettings] = None):
        self._settings = settings or DAMDataSettings() # TODO make input

        self._latest_successful_date = Arrow(2000, 1, 1, tzinfo=timezone(self._settings.timezone))

    def _upsert_to_csv(self, new_df: pd.DataFrame) -> None:
        out_path = Path(self._settings.output_csv)

        if out_path.exists():
            existing = pd.read_csv(out_path, parse_dates=["ts_utc", "ts_local"])
            combined = pd.concat([existing, new_df.reset_index(drop=True)], ignore_index=True)
        else:
            combined = new_df.reset_index(drop=True)

        combined.drop_duplicates(subset=["ts_utc"], keep="last", inplace=True)
        combined.sort_values("ts_utc", inplace=True)
        combined.to_csv(out_path, index=False)
        get_dam_fetcher_logger().info(f"Upserted {len(new_df)} rows into {out_path}")

    def _process_dam(self, xml_response, start_period: Arrow):
        root = etree.parse(io.BytesIO(xml_response))
        ns = {"ns": root.getroot().nsmap.get(None)}
        series = []

        for ts_node in root.findall(".//ns:TimeSeries", namespaces=ns):
            periods = ts_node.findall(".//ns:Period", namespaces=ns)
            for period in periods:
                res = (period.findtext("ns:resolution", namespaces=ns) or "").upper()
                if res != "PT15M":
                    continue
                ti = period.find("ns:timeInterval", namespaces=ns)
                if ti is None:
                    continue
                start_text = ti.findtext("ns:start", namespaces=ns)
                if not start_text:
                    continue
                start = pd.Timestamp(start_text).tz_convert("UTC")

                points = period.findall(".//ns:Point", namespaces=ns)
                vals = []
                for p in points:
                    pos_txt = p.findtext("ns:position", namespaces=ns) or "0"
                    price_txt = p.findtext(
                        "ns:price.amount", namespaces=ns
                    ) or p.findtext("ns:quantity", namespaces=ns)
                    if not price_txt:
                        continue
                    vals.append((int(pos_txt), float(price_txt)))

                if not vals:
                    continue
                vals.sort(key=lambda x: x[0])
                idx = pd.date_range(
                    start=start, periods=len(vals), freq="15min", tz="UTC"
                )
                series.append(
                    pd.DataFrame({"price_EUR_MWh": [v for _, v in vals]}, index=idx)
                )

        if not series:
            get_dam_fetcher_logger().error(f"No PT15M TimeSeries found in ENTSO-E response for the requested period ({start_period}). Probably no data available yet")
        df = pd.concat(series).sort_index()
        if df.index.has_duplicates:
            df = df[~df.index.duplicated(keep="last")]
        df["ts_utc"] = df.index
        df["ts_local"] = df.index.tz_convert(self._settings.timezone)
        df["price_EUR_MWh"] = df["price_EUR_MWh"].astype(float)
        df["price_EUR_kWh"] = df["price_EUR_MWh"] / 1000.0

        df.sort_values("ts_local", inplace=True)
        self._upsert_to_csv(df[["ts_utc", "ts_local", "price_EUR_MWh", "price_EUR_kWh"]])
        get_dam_fetcher_logger().info(f"DAM prices saved for {start_period}")
        self._latest_successful_date = start_period

    def fetch_prices(self, start_period: Arrow, end_period: Arrow):
        params = {
            "securityToken": self._settings.token,
            "documentType": self._settings.doc_a44,
            "processType": self._settings.proc_a01,
            "contract_MarketAgreement.type": self._settings.contract_a01,
            "in_Domain": self._settings.bzn_eic,
            "out_Domain": self._settings.bzn_eic,
            "periodStart": start_period.to("utc").strftime("%Y%m%d%H%M"),
            "periodEnd": end_period.to("utc").strftime("%Y%m%d%H%M"),
        }
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        try:
            session.mount("https://", HTTPAdapter(max_retries=retry))
            response = session.get(self._settings.base_url, params=params)
            response.raise_for_status()
        except HTTPError as e:
            get_dam_fetcher_logger().warning(f"Error fetching DAM prices{e}")
        else:
            self._process_dam(response.content, start_period)

    def run(self, days_override: int = None) -> None:
        now = Arrow.now(tzinfo=timezone(self._settings.timezone))
        days_shift = days_override if days_override is not None else self._settings.day_shifts
        start_period = now.floor("day").shift(days=days_shift)
        end_period = start_period.shift(days=1)
        get_dam_fetcher_logger().info(f"Fetching DAM prices for {start_period} - {end_period}")
        if self._latest_successful_date == start_period:
            get_dam_fetcher_logger().info(f"DAM already available, skipping")
        else:
            self.fetch_prices(start_period, end_period)
