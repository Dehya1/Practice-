BASE = "https://api.tradestation.com/v3/"   # 主要
USER_PROFILE = "brokerage/accounts"  # 获取当前用户
BALANCE = "brokerage/accounts/{accounts}/balances"  # 余额
POSITION = "brokerage/accounts/{accounts}/positions"  # 持仓
ORDERS = "brokerage/accounts/{accounts}/orders"   #订单
AN_ORDERS = "brokerage/accounts/{accounts}/orders/{orderIds}"  #单个订单详情
PLACE_ORDER = "orderexecution/orders"   #下订单
MODIFY_ORDER = "orderexecution/orders/{order_id}"   #修改订单
CANCEL_ORDER = "orderexecution/orders/{order_id}"   #取消订单

# 待修改
STATUS_MAPPING = {
            'open': 'REPORTED',
            'partially_filled': 'PART_FILL',
            'filled': 'FILLED_ALL',
            'expired': 'REJECTED',
            'canceled': 'CANCELLED_ALL',
            'pending': 'REPORTING',
            'rejected': 'REJECTED',
            'error': 'REJECTED',
        }

# OrderType：Market，Limit，Stop Market，Stop Limit
"""
"Status": "OPN",
"StatusDescription": "Sent",

"Status": "FLL",
"StatusDescription": "Filled",

"Status": "ACK",
"StatusDescription": "Received",
"""


