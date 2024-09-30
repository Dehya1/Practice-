import pandas as pd
pos_list = []

# POS_COL列的定义
POS_COL = [
    "account",
    "code",
    "qty",
    "can_sell_qty",
    "nominal_price",
    "cost_price",
    "position_side",
    "today_pl_val",
    "pl_val",
    "today_buy_qty",
    "today_sell_qty",
    "today_total_qty",
]

# 创建一个包含数据的DataFrame
data_df1 = pd.DataFrame({
    "account": ["A123", "B456"],
    "qty": [100, 200],
    "today_pl_val": [1000, -500]
})

# 创建另一个包含不同数据的DataFrame
data_df2 = pd.DataFrame({
    "account": ["C789", "D012"],
    "qty": [50, 150],
    "today_pl_val": [750, 250]
})

# 创建一个空的DataFrame，只包含指定的列，但不包含任何行
empty_df = pd.DataFrame(columns=POS_COL)

# 显示DataFrames以验证
# print("第一个DataFrame:")
# print(data_df1)
# print("\n第二个DataFrame:")
# print(data_df2)
# print("\n空的DataFrame:")
# print(empty_df)

pos_list.append(data_df1)
pos_list.append(data_df2)
pos_list.append(empty_df)
print(pos_list)
position_df = pd.concat(pos_list, ignore_index=True)
print(position_df)

cash_dict = {'a':10,'b':20,'c':0}
df_dict = [{"Account": k, "cash": v} for k, v in cash_dict.items()]
print(df_dict)
df_dict = pd.DataFrame(df_dict)
print(df_dict)







