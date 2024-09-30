import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 1000)
pd.set_option('display.width', 1000)

data = {
    'Account': ['IWIN', 'Westbull'],
    'symbol': ['Velox OMS-1889838', 'Velox OMS-W586843'],
    'side': ['US.F', 'US.F'],
    'price_type': ['BUY', 'BUY'],
    'price': [10.0, 10.0],
    'quantity': [3, 7],
    'tif': ['DAY', 'DAY'],
    'market_session': ['REGULAR', 'REGULAR'],
    'stop_price': [0, 0],
    'GTD': [pd.NA, pd.NA],  # 使用pd.NA来表示缺失值
    'IOC': ['OFF', 'OFF'],
    'cash': [301.54, 924.26],
    'can_use_cash': [301.54, 924.26],
    'max_buy_qty': [30.0, 92.0],
    'can_buy_qty': [3, 7]
}
df = pd.DataFrame(data)
list_samples = [8, 2]
for max_buy, can_buy in zip(df["max_buy_qty"], list_samples):
    print('max_buy:', max_buy)
    print('can_buy:', can_buy)
    # print(df)




