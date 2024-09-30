import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 1000)
pd.set_option('display.width', 1000)

def sample(total, constraints):   # total-下单的全部持仓；constrains-各账户的持仓
    constraints_sum = sum(constraints)
    if total > constraints_sum:  # 如果各账户加起来的持仓都不够的话，让他执行全部仓位
        return constraints
    else:  # 如果各账户加起来的持仓够了，那就执行随机的数
        probabilities = np.array(list(constraints)) / constraints_sum
        rng = np.random.default_rng()
        samples = rng.multinomial(total, probabilities, size=1)
        return samples

# 构造数据字典
data = {
    'Account': ['FUTU MOOMOO ', 'WESTBULL', 'IWIN'],
    'symbol': ['OPK', 'OPK', 'OPK'],
    'side': ['SELL', 'SELL', 'SELL'],
    'price_type': ['Limit', 'Limit', 'Limit'],
    'price': [1.5, 1.5, 1.5],
    'quantity': [3, 3, 3],  # 下单数量
    # 'quantity': [90000000, 90000000, 90000000],
    # 'quantity': [50, 50, 50],
    'tif': ['DAY', 'DAY', 'DAY'],
    'market_session': ['REGULAR', 'REGULAR', 'REGULAR'],
    'stop_price': [0, 0, 0],
    'GTD': [np.nan, np.nan, np.nan],
    'IOC': ['OFF', 'OFF', 'OFF'],
    # 'qty': [20, 10, 40]
    'qty': [1, 2, 1]  # 持仓 [2,1,0]
    # 'qty': [30000000, 30000000, 30000000]
}
# 创建DataFrame
df = pd.DataFrame(data)
# 显示DataFrame
print(df)
print('-'*150)

exec_qty = sample(df.loc[0,'quantity'], df['qty'])  # 这是我待会儿要新添加的 要执行的数量的列，判断他的类型分别处理。
if isinstance(exec_qty,pd.Series):
    df['random_exec_qty'] = exec_qty
elif isinstance(exec_qty, np.ndarray):  # 持仓够，能随，但是有可能发随机出来的数比我的持仓大，又或者随机出0来
    exec_qty = exec_qty[0]
    df['random_exec_qty'] = exec_qty
    condition = df['random_exec_qty'] > df['qty']
    has_zero = (df['random_exec_qty'] == 0).any()
    if not df[condition].empty or has_zero:  # 就证明condition成立，执行的数量比我的持仓大，要再随一次吗。如果执行数量大于持仓或者执行数量有任何一个是个0
        while True:
            exec_qty = sample(df.loc[0, 'quantity'], df['qty'])
            print('exec_qty\n', exec_qty)
            exec_qty = exec_qty[0]
            df['random_exec_qty'] = exec_qty
            are_equal = (df['qty'] >= df['random_exec_qty']).all()
            are_all_greater_than_zero = (df['random_exec_qty'] > 0).all()
            print('are_equal\n', are_equal)
            print('are_all_greater_than_zero\n', are_all_greater_than_zero)
            if are_equal and are_all_greater_than_zero:
                df['random_exec_qty'] = exec_qty
                break


print('-'*150)
print(df)
