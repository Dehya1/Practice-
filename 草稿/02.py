from concurrent.futures import ThreadPoolExecutor

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 1000)
pd.set_option('display.width', 1000)

# position_list = []
# position_df = pd.concat(position_list, ignore_index=True)
# print(position_df)



import os
# print(os.cpu_count())  # 核
# print(os.cpu_count()*2)


def get_add(i):
    i += 1
    print(i)
broker_obj = list(range(1, 101))
# print(broker_obj)

with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
    _ = pool.map(get_add, broker_obj)




