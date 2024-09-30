import pandas as pd

ORDER_DICT_KEY = [
    "account",
    "symbol",
    "side",
    "price_type",
    "price",
    "quantity",
    "tif",
    "market_session",
    "stop_price",
    "GTD",
    "IOC",
]
empty_pos_order_df = pd.DataFrame(columns=ORDER_DICT_KEY)

print(empty_pos_order_df.shape)

