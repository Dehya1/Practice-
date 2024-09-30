import requests

# 获取当前账户 —— 认证用
url = "https://api.tradestation.com/v3/brokerage/accounts"
headers = {"Authorization": "Bearer TOKEN"}
response = requests.request("GET", url, headers=headers)
print('获取账户：', response.text)

# 获取余额
url = "https://api.tradestation.com/v3/brokerage/accounts/61999124,68910124/balances"
headers = {"Authorization": "Bearer TOKEN"}
response = requests.request("GET", url, headers=headers)
print('获取余额：', response.text)

# 获取历史订单
url = "https://api.tradestation.com/v3/brokerage/accounts/61999124,68910124/historicalorders"
querystring = {"since":"2006-01-13"}
headers = {"Authorization": "Bearer TOKEN"}
response = requests.request("GET", url, headers=headers, params=querystring)
print(response.text)

# 获取订单
url = "https://api.tradestation.com/v3/brokerage/accounts/61999124,68910124/orders"
headers = {"Authorization": "Bearer TOKEN"}
response = requests.request("GET", url, headers=headers)
print(response.text)

# 按订单ID获取订单
url = "https://api.tradestation.com/v3/brokerage/accounts/61999124,68910124/orders/123456789,286179863"
headers = {"Authorization": "Bearer TOKEN"}
response = requests.request("GET", url, headers=headers)
print(response.text)

# 获取持仓
url = "https://api.tradestation.com/v3/brokerage/accounts/61999124,68910124/positions"
headers = {"Authorization": "Bearer TOKEN"}
response = requests.request("GET", url, headers=headers)
print(response.text)

# 下单
url = "https://api.tradestation.com/v3/orderexecution/orders"
payload = {
    "AccountID": "123456782",
    "Symbol": "MSFT",
    "Quantity": "10",
    "OrderType": "Market",
    "TradeAction": "BUY",
    "TimeInForce": {"Duration": "DAY"},
    "Route": "Intelligent"  # 路由
}
headers = {
    "content-type": "application/json",
    "Authorization": "Bearer TOKEN"
}
response = requests.request("POST", url, json=payload, headers=headers)
print(response.text)

# 替换订单
url = "https://api.tradestation.com/v3/orderexecution/orders/123456789"
payload = {
    "Quantity": "10",
    "LimitPrice": "132.52"
}
headers = {
    "content-type": "application/json",
    "Authorization": "Bearer TOKEN"
}
response = requests.request("PUT", url, json=payload, headers=headers)
print(response.text)

# 取消订单
url = "https://api.tradestation.com/v3/orderexecution/orders/123456789"
headers = {"Authorization": "Bearer TOKEN"}
response = requests.request("DELETE", url, headers=headers)
print(response.text)

