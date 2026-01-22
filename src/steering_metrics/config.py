from arrow import Arrow

from steering_metrics.metrics.options import CalculatorOptions, ConsumptionRule

DEFAULT_DATE = Arrow(2025, 11,30, 23, tz="utc")
N_DAYS = 46
# DEVICE_ID = "df9a5c3c-b733-4b30-a6de-f614cb662a08"
# DEVICE_ID = "3c77a309-92da-5597-8a9c-e6668b3b51a9" # DEVICE adrian gave me, julien
DEVICE_ID = "e8e2a998-8847-47f4-b7e5-1b729e0f315a"

CALCULATOR_OPTIONS = CalculatorOptions()


WANTED_DEVICE_IDS = [  #DAIKIN NEW
    # "01656764-cac2-45b1-b124-2dc5ea4c94e5", # bad device
    # "1f611bac-1e92-4771-95c1-b402e2316d57", # bad device
    # "1fcbcd9e-afb1-4870-9b17-de017dc02349", # bad device
    # "238d79dd-740c-497e-8ec2-60929f06ff68", # bad device
    "3bbe62f5-9cd6-41d2-b18b-b17a62df407b",
    # "53812aa8-8b0b-48f9-a451-12007551e29e", # bad device
    "6bb416ea-f469-46c5-8b8e-5df6b3a3fed3",  # GOOD this is steered a lot
    "73eae5a0-34a2-42ad-9d3c-eb00489d5011",  # GOOD this is steered
    "74d40dc8-f53c-4c66-9245-20ee8a6947f1",  # This one sucks to
    "7b975678-5aaa-45cb-90c7-06549f334640",  # only steered up until 01/12
    # "956be539-9544-44fb-8597-1c87e2978faa", # bad device
    "a3ed01ad-2ec9-4d04-82b0-dc9badd35fa4",  # only steered from 18/12 tem end 25/12
    # "b084a735-2429-4c44-b36d-bd5a65bce647", # no temperature data
    "babb8353-cc3c-4c69-a58c-b13dffcd1e76", # keep this but very power data is spiky, and does not really have rbc decisions last weeks, stopped being steered after 15/12 (but only steered a lot up until 11/12
    # "df9a5c3c-b733-4b30-a6de-f614cb662a08", # This is the mcp device
    # "e8e2a998-8847-47f4-b7e5-1b729e0f315a", # bad device
]
EXCLUDED_ENERGY_SUPPLIER = "Frank Energie"
# WANTED_BRAND = "Vaillant"
WANTED_BRAND = "Daikin"


MPC_DEVICE = "df9a5c3c-b733-4b30-a6de-f614cb662a08"
