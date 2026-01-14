from arrow import Arrow

DEFAULT_DATE = Arrow(2025, 11,30, 23, tz="utc")
N_DAYS = 42
# DEVICE_ID = "df9a5c3c-b733-4b30-a6de-f614cb662a08"
# DEVICE_ID = "3c77a309-92da-5597-8a9c-e6668b3b51a9" # DEVICE adrian gave me, julien
DEVICE_ID = "e8e2a998-8847-47f4-b7e5-1b729e0f315a"

# WANTED_DEVICE_IDS = [ # Vailant
#     "1a6b47d4-a957-51ad-bb83-138e8e9f0ed8",
#     "2ddde996-4acd-5b0a-8419-bf721462f3c1",
#     "374ffb72-af5b-518a-91ea-e0ef1028d96b",
#     "374ffb72-af5b-518a-91ea-e0ef1028d96b",
#     "3c77a309-92da-5597-8a9c-e6668b3b51a9",
#     "4c126dff-b5a6-59c8-bca5-68d8a665f630",
#     "522dcb14-41ab-5762-9685-6929e1778f76",
#     "612e7767-0696-56e8-92b5-f44fca42a4b2",
#     "6a852169-c293-526e-991b-c93cf85f1987",
#     "aa3a21f9-1dcf-53a8-8754-3085f99990a8",
#     "b36e0feb-ca3d-537e-a6d6-469d15f9f28e",
#     "babd1b3e-cac0-54ea-8ad4-d58685f1f57e",
# ]
# WANTED_DEVICE_IDS = [ # Daikin
#     "01656764-cac2-45b1-b124-2dc5ea4c94e5",
#     "1f611bac-1e92-4771-95c1-b402e2316d57",
#     "1fcbcd9e-afb1-4870-9b17-de017dc02349",
#     "3bbe62f5-9cd6-41d2-b18b-b17a62df407b",
#     "3bbe62f5-9cd6-41d2-b18b-b17a62df407b",
#     "53812aa8-8b0b-48f9-a451-12007551e29e",
#     "53812aa8-8b0b-48f9-a451-12007551e29e",
#     "6bb416ea-f469-46c5-8b8e-5df6b3a3fed3",
#     "73eae5a0-34a2-42ad-9d3c-eb00489d5011",
#     "74d40dc8-f53c-4c66-9245-20ee8a6947f1",
#     "956be539-9544-44fb-8597-1c87e2978faa",
#     "a3ed01ad-2ec9-4d04-82b0-dc9badd35fa4",
#     "babb8353-cc3c-4c69-a58c-b13dffcd1e76",
#     "e8e2a998-8847-47f4-b7e5-1b729e0f315a",
# ]
WANTED_DEVICE_IDS = [  #DAIKIN NEW
    "01656764-cac2-45b1-b124-2dc5ea4c94e5",
    "1f611bac-1e92-4771-95c1-b402e2316d57",
    "1fcbcd9e-afb1-4870-9b17-de017dc02349",
    "238d79dd-740c-497e-8ec2-60929f06ff68",
    "3bbe62f5-9cd6-41d2-b18b-b17a62df407b",
    "3bbe62f5-9cd6-41d2-b18b-b17a62df407b",
    "53812aa8-8b0b-48f9-a451-12007551e29e",
    "53812aa8-8b0b-48f9-a451-12007551e29e",
    "6bb416ea-f469-46c5-8b8e-5df6b3a3fed3",
    "73eae5a0-34a2-42ad-9d3c-eb00489d5011",
    "74d40dc8-f53c-4c66-9245-20ee8a6947f1",
    "7b975678-5aaa-45cb-90c7-06549f334640",
    "956be539-9544-44fb-8597-1c87e2978faa",
    "a3ed01ad-2ec9-4d04-82b0-dc9badd35fa4",
    "b084a735-2429-4c44-b36d-bd5a65bce647",
    "babb8353-cc3c-4c69-a58c-b13dffcd1e76",
    "df9a5c3c-b733-4b30-a6de-f614cb662a08",
    "e8e2a998-8847-47f4-b7e5-1b729e0f315a",
]
EXCLUDED_ENERGY_SUPPLIER = "Frank Energie"
# WANTED_BRAND = "Vaillant"
WANTED_BRAND = "Daikin"