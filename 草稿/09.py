import numpy as np
import pandas as pd
import csv
import json

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 1000)
pd.set_option('display.width', 1000)

# 公钥
PUBLIC_KEY_BASE64 = """
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC63Pn0sZZpaHJ1ha3CAW48IqHI62RlnG5zFiNGqbtb5EQtCRLsxjzkWSynMIJ6qR2eIBQ20Fpo
gpxpc9cRbTQw8cA+g/cHIsJPn3dn0tBTL4X/VoFP1cmSzLGaDuy+VI6FVt2JKlnkREWIeSYnouVHSoxH3Ujb6+c7Bu5/drmEqwIDAQAB
"""
# 私钥
PRIVATE_KEY_BASE64 = """
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAKu3HAA3+IoggBAaHn1onzG/v7AgEQUT2d+sTpdSKQ7qKwnVVcCnhPqvVbwnvRY
/d5y/vLr3l3FGZvIky+gDpSSAH5dnxipfY0G8u1DW/58s9ZckXtyblNpgsjIDir5IADmMZvDgNIXAn02nMMmCzCNa6kFgQb6jkQG0In/7fiwtAgMBAAEC
gYAPFIQpgsDZhJQqldiio9sDN/dCJPbJrt4d9hhq0qTXcfo4oVsoEa4sg9RwMz84YneDNRWCh/btVET7M/8ST6ujfac0Z58Q4pnJsnB3EpIFzwUA4NA8cf
YixLIkzCjNzHuW6UE40v2SetfytTvn9w0pHfDD/JbUY0UlWSXVtxDX0wJBANNdPx99jhdtUFXdnmhkRQshkOoQ8pSCfie6wvUq4DIe48o3F9kaKL8dVj
WnXTkaXGju636z/l7MfOuCQQOeoKcCQQDP+l0jaWQvd5vbtKRltO7YsMd0GZha45/ntPtw9UZmDxYpBFJEwXkTdU9ZOU6fRE5so2zzMqifnWqM1n
jidDMLAkA7I48C351/Po3IyK6G5O9Qkv66Dy3gkbZ8pUvhTzLVs0DnFo0sqJ4YAzxY3NA/pvmOPrNTi0cz/SFCv/oy6hJnAkB2vnFzCHdlCpt4Q5khYL6
GBdi7Fun/6rqfpptxEPlSyAZVANyf2P7x9yaIwMl88Zj9Ogm4iRHxoAT3yHRYhxOlAkAYI6Hq9BBi4zpOaarQTxNNE3Vdw6m43IWLHSGykh0oX6oWjQ
xYucGwxWVfEIx9C6L55zNNSbGASknYCQEtxfOJ
"""
import json

# 用户信息，包括用户名、公钥和私钥
# 注意：这里PrivateKey被转换为字符串，因为在JSON中，键的值应该是字符串、数字、布尔值、数组、对象或null
user_info = [
    {
        "username": "sdk240312",
        "PublicKey": """
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC63Pn0sZZpaHJ1ha3CAW48IqHI62RlnG5zFiNGqbtb5EQtCRLsxjzkWSynMIJ6qR2eIBQ20Fpo
gpxpc9cRbTQw8cA+g/cHIsJPn3dn0tBTL4X/VoFP1cmSzLGaDuy+VI6FVt2JKlnkREWIeSYnouVHSoxH3Ujb6+c7Bu5/drmEqwIDAQAB
""",  # 假设这是一个简化的公钥示例
        "PrivateKey": """
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAKu3HAA3+IoggBAaHn1onzG/v7AgEQUT2d+sTpdSKQ7qKwnVVcCnhPqvVbwnvRY
/d5y/vLr3l3FGZvIky+gDpSSAH5dnxipfY0G8u1DW/58s9ZckXtyblNpgsjIDir5IADmMZvDgNIXAn02nMMmCzCNa6kFgQb6jkQG0In/7fiwtAgMBAAEC
gYAPFIQpgsDZhJQqldiio9sDN/dCJPbJrt4d9hhq0qTXcfo4oVsoEa4sg9RwMz84YneDNRWCh/btVET7M/8ST6ujfac0Z58Q4pnJsnB3EpIFzwUA4NA8cf
YixLIkzCjNzHuW6UE40v2SetfytTvn9w0pHfDD/JbUY0UlWSXVtxDX0wJBANNdPx99jhdtUFXdnmhkRQshkOoQ8pSCfie6wvUq4DIe48o3F9kaKL8dVj
WnXTkaXGju636z/l7MfOuCQQOeoKcCQQDP+l0jaWQvd5vbtKRltO7YsMd0GZha45/ntPtw9UZmDxYpBFJEwXkTdU9ZOU6fRE5so2zzMqifnWqM1n
jidDMLAkA7I48C351/Po3IyK6G5O9Qkv66Dy3gkbZ8pUvhTzLVs0DnFo0sqJ4YAzxY3NA/pvmOPrNTi0cz/SFCv/oy6hJnAkB2vnFzCHdlCpt4Q5khYL6
GBdi7Fun/6rqfpptxEPlSyAZVANyf2P7x9yaIwMl88Zj9Ogm4iRHxoAT3yHRYhxOlAkAYI6Hq9BBi4zpOaarQTxNNE3Vdw6m43IWLHSGykh0oX6oWjQ
xYucGwxWVfEIx9C6L55zNNSbGASknYCQEtxfOJ
"""  # 私钥也被转换为字符串
    }
]

# # 将用户信息写入到JSON文件中
# with open('user_keys.json', 'w', encoding='utf-8') as file:
#     json.dump(user_info, file, ensure_ascii=False, indent=4)
#
# print("用户信息已保存到user_keys.json文件中。")

import json

# 打开JSON文件
with open('nested_dict.json', 'r', encoding='utf-8') as f:
    user_info = json.load(f)

print(user_info)  # {'sdkwer': {'PublicKey': '\nMIGfMA0GCSqG', 'PrivateKey': '\nMIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAg'}, 'sdk888': {'PublicKey': '\nMIGfMAdfghqGSIb3DQEBAQUAA4G', 'PrivateKey': '\nMIICdQIgfsdhdfghNBgkqhki'}}

target_username = 'sdkwer'
# 判断用户名是否在字典的键中
if target_username in user_info:
    print(f"用户名 '{target_username}' 在字典的键中。")
else:
    print(f"用户名 '{target_username}' 不在字典的键中。")
