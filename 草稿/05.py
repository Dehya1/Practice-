import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 1000)
pd.set_option('display.width', 1000)

def sample(total, constraints):   # total-下单的全部持仓；constrains-各账户的持仓
    constraints_sum = sum(constraints)
    if total > constraints_sum:  # 如果各账户加起来的持仓都不够的话，让他执行全部仓位，肯定不会有0的情况
        return constraints
    else:  # 如果各账户加起来的持仓够了，那就执行随机的数。但如果输入的数量非常小，那么各个账户就有可能有0的情况，怎么处理呢
        probabilities = np.array(list(constraints)) / constraints_sum
        rng = np.random.default_rng()
        samples = rng.multinomial(total, probabilities, size=1)
        # print('samples\n', samples[0],type(samples[0]))
        return samples

# 构造数据字典
data = {
    'Account': ['FUTU MOOMOO ', 'WESTBULL', 'IWIN'],
    'symbol': ['OPK', 'OPK', 'OPK'],
    'side': ['SELL', 'SELL', 'SELL'],
    'price_type': ['Limit', 'Limit', 'Limit'],
    'price': [1.5, 1.5, 1.5],
    'quantity': [4, 4, 4],
    # 'quantity': [100, 100, 100],
    'tif': ['DAY', 'DAY', 'DAY'],
    'market_session': ['REGULAR', 'REGULAR', 'REGULAR'],
    'stop_price': [0, 0, 0],
    'GTD': [np.nan, np.nan, np.nan],
    'IOC': ['OFF', 'OFF', 'OFF'],
    # 'qty': [20, 10, 40]
    # 'qty': [20, 60, 40]
    'qty': [20, 60, 40]
}
# 创建DataFrame
df = pd.DataFrame(data)

exec_qty = sample(df.loc[0,'quantity'], df['qty'])  # 这是我待会儿要新添加的 要执行的数量的列，判断他的类型分别处理。
if isinstance(exec_qty,pd.Series):  # 持仓不够
    df['random_exec_qty'] = exec_qty
elif isinstance(exec_qty, np.ndarray):  # 持仓够了，随机出来的是numpy
    exec_qty = exec_qty[0]
    df['random_exec_qty__'] = exec_qty

print(df)