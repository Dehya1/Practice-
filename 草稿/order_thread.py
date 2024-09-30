from PyQt5.QtCore import QThread, pyqtSignal, QMutex
import time
import logging
import pandas as pd
from utils.database import AuroraDB
from utils.error_counter import ErrorCounter
from datetime import datetime
from pytz import timezone
from tigeropen.common.exceptions import ApiException
from threading import Thread, Lock
import queue
import random
from concurrent.futures import ThreadPoolExecutor
logging.basicConfig(level=logging.DEBUG)


class OrderThread(QThread):
    failed = pyqtSignal()
    signal_acc_orders = pyqtSignal(dict)
    error_msg = pyqtSignal(str)

    def __init__(
            self,
            parent=None,
            aurora_account=None,
            broker_list=[],
            order=True,
            today=True,
            date=[],
            db_list=None
    ):
        super(OrderThread, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.broker_list = broker_list
        self.order = order
        self.today = today
        self.date = date
        self.db_list = db_list
        self.aurora_account = aurora_account

    def run(self):
        self.error_counter = ErrorCounter(interval_threshold=200, counter_threshold=20)
        while self.error_counter.emit is False:
            with ThreadPoolExecutor(max_workers=len(self.broker_list)) as pool:
                _ = pool.map(self.get_acc_order, self.broker_list)  # 使用线程池提升速度
        self.failed.emit()

    def get_acc_order(self, broker_obj):
            # for broker_obj in self.broker_list:
            random_time = random.uniform(2, 5)
            time.sleep(random_time)
            try:
                logging.info(f"Start {type(self).__name__}")
                logging.info(broker_obj.account_number)
                if self.order == True and self.today == True:
                    acc_orders = broker_obj.get_today_orders()
                elif self.order == True and self.today == False:
                    acc_orders = broker_obj.get_history_orders(
                        self.date[0], self.date[1]
                    )
                elif self.order == True and self.today == None:
                    acc_orders = broker_obj.get_active_orders()
                elif self.order == False and self.today == True:
                    acc_orders = broker_obj.get_today_deals()
                elif self.order == False and self.today == False:
                    acc_orders = broker_obj.get_history_deals(
                        self.date[0], self.date[1]
                    )
                acc_orders.insert(0, column="account", value=str(broker_obj))
            # except ApiException as e:
            #     logging.info(
            #         "Tiger Securities requires the interval between two dates to be less than 90 days."
            #     )

            except Exception as e:
                logging.error(e, exc_info=True)
                self.error_counter.error_occurred()
                # self.failed.emit()
                time.sleep(3)
            else:
                acc_orders_dict = {"index": str(broker_obj), "orders": acc_orders}
                self.signal_acc_orders.emit(acc_orders_dict)
                time.sleep(3)
            # self.failed.emit()
            time.sleep(2)
            try:
                acc_TO = broker_obj.get_today_orders()
                time.sleep(2)
                acc_TD = broker_obj.get_today_deals()
                self.sync_to_db(str(broker_obj), acc_TO, acc_TD)
            except Exception:
                pass
            time.sleep(2)

    def stop(self):
        self._running = False
        logging.info(f"Stop {type(self).__name__}")
        self.terminate()

    def sync_to_db(self, broker_str, acc_orders, acc_deals):
        self.db_obj = AuroraDB(self.db_list)
        if acc_orders.shape[0] == 0:
            pass
        else:
            order_db = acc_orders.loc[
                       :,
                       [
                           "code",
                           "trd_side",
                           "price",
                           "qty",
                           "order_type",
                           "order_status",
                           "create_time",
                           "order_id",
                       ],
                       ]

            order_db.rename(
                columns={
                    "trd_side": "side",
                    "order_type": "type",
                    "order_status": "status",
                },
                inplace=True,
            )
            order_db.reset_index(drop=True, inplace=True)
            order_db.loc[:, "username"] = self.aurora_account.username
            order_db.loc[:, "account"] = broker_str
            # 时区转换, 将上传时间统一为北京时间
            order_db.loc[:, "datetime"] = datetime.now(
                timezone("Asia/Shanghai")
            ).strftime("%Y-%m-%d %H:%M:%S")
            self.db_obj.insert_order(order_db)

        if acc_deals.shape[0] == 0:
            pass
        else:
            deal_db = acc_deals.loc[
                      :, ["code", "trd_side", "price", "qty", "create_time", "order_id"]
                      ]
            deal_db.rename(
                columns={"trd_side": "side", "order_type": "type"},
                inplace=True,
            )
            deal_db.reset_index(drop=True, inplace=True)
            deal_db.loc[:, "username"] = self.aurora_account.username
            deal_db.loc[:, "account"] = broker_str
            deal_db.loc[:, "datetime"] = datetime.now(
                timezone("Asia/Shanghai")
            ).strftime("%Y-%m-%d %H:%M:%S")
            self.db_obj.insert_deal(deal_db)


class CancelOrderThread(QThread):
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, parent=None, broker_obj=None, order_id=None):
        super(CancelOrderThread, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.broker_obj = broker_obj
        self.order_id = order_id

    def run(self):
        try:
            logging.info(f"Start {type(self).__name__}")
            data = self.broker_obj.cancel_order(self.order_id)
        except Exception as e:
            if str(e) == "此订单不支持此操作" or str(e) == "此订单号不存在":
                self.failed.emit(str(e))
            else:
                logging.error(e, exc_info=True)
                self.failed.emit(str(e))
        else:
            self.finished.emit()

    def stop(self):
        self._running = False
        logging.info(f"Stop {type(self).__name__}")
        self.terminate()


class CancelMultiOrderThread(QThread):
    failed = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, parent=None, broker_acc_list=[], order_list=[]):
        super(CancelMultiOrderThread, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.broker_acc_list = broker_acc_list
        self.order_list = order_list
        self.thread_list = []

    def cancel_broker_order(self, broker_obj, order_id):
        msg = ""
        try:
            broker_obj.cancel_order(order_id)
        except Exception as e:
            msg += f"{str(broker_obj)} {order_id} {str(e)} cancellation failed\n"
            self.finished.emit(msg)
        else:
            msg += f"{str(broker_obj)} {order_id} has been successfully canceled\n"
            self.finished.emit(msg)

    def run(self):
        logging.info(f"Start {type(self).__name__}")
        broker_acc_str_list = [str(broker) for broker in self.broker_acc_list]
        # msg = ""
        try:
            for broker, order_id in self.order_list:
                index = broker_acc_str_list.index(broker)
                t = Thread(
                    target=self.cancel_broker_order,
                    args=(self.broker_acc_list[index], order_id),
                )
                self.thread_list.append(t)

            if len(self.thread_list):
                for thread in self.thread_list:
                    thread.start()

        except Exception as e:
            logging.error(e, exc_info=True)
            self.failed.emit(str(e))

    def stop(self):
        self._running = False
        logging.info(f"Stop {type(self).__name__}")
        self.terminate()


class ModifyMultiOrderThread(QThread):
    failed = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, parent=None, broker_acc_list=[], modified_orders_list=[]):
        super(ModifyMultiOrderThread, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.broker_acc_list = broker_acc_list
        self.modified_orders_list = modified_orders_list
        self.thread_list = []

    def modify_broker_order(self, broker_obj, modified_order_dict):
        msg = ""
        try:
            broker_obj.modify_order(modified_order_dict)
        except Exception as e:
            msg += f"{modified_order_dict['account']} {modified_order_dict['order_id']} {str(e)} modification failed\n"
            self.finished.emit(msg)
        else:
            msg += f"{modified_order_dict['account']} {modified_order_dict['order_id']} has been successfully modified\n"
            self.finished.emit(msg)

    def run(self) -> None:
        logging.info(f"Start {type(self).__name__}")
        broker_acc_str_list = [str(broker) for broker in self.broker_acc_list]
        try:
            for modified_order_dict in self.modified_orders_list:
                index = broker_acc_str_list.index(modified_order_dict["account"])
                t = Thread(target=self.modify_broker_order,
                           args=(self.broker_acc_list[index], modified_order_dict))
                self.thread_list.append(t)

            if len(self.thread_list):
                for thread in self.thread_list:
                    thread.start()

        except Exception as e:
            logging.error(e, exc_info=True)
            self.failed.emit(str(e))

    def stop(self):
        self._running = False
        logging.info(f"Stop {type(self).__name__}")
        self.terminate()


class ModifyOrderThread(QThread):
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, parent=None, broker_obj=None, modified_order=None):
        super(ModifyOrderThread, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.broker_obj = broker_obj
        self.modified_order = modified_order

    def run(self):
        try:
            logging.info(f"Start {type(self).__name__}")
            data = self.broker_obj.modify_order(self.modified_order)
        except Exception as e:
            if str(e) == "此订单不支持此操作" or str(e) == "此订单号不存在":
                self.failed.emit(str(e))
            else:
                logging.error(e, exc_info=True)
                self.failed.emit(str(e))
        else:
            self.finished.emit()

    def stop(self):
        self._running = False
        logging.info(f"Stop {type(self).__name__}")
        self.terminate()


class TriggerMultiCancel(QThread):
    failed = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, parent=None, info_list=[]):
        super(TriggerMultiCancel, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.thread_list = []
        self.info_list = (
            info_list  # [(broker_obj1, order_df1), (broker_obj2, order_df2)]
        )
        self.execution_sign = 0

    def get_execution_sign(self, broker_obj, order_df):
        msg = ""
        time.sleep(0.2)
        error = 0
        while self.execution_sign == 0 and self._running:
            order_id = str(order_df.iloc[0, order_df.columns.get_loc("order_id")])
            try:
                ret, info = broker_obj.get_order_info(order_id)
                if ret == "OK":
                    info = info["order_df"]
                    error = 0
                    if info["executed_qty"][0] > 0:
                        self.execution_sign = 1
                    elif info["status"][0] not in [
                        "Filled",
                        "PartiallyFilled",
                        "Replaced",
                        "New",
                        "SUBMITTED",
                        "FILLED_PART",
                        "FILLED_ALL",
                    ]:
                        msg += f"{str(broker_obj)} {order_id} {str(info['status'][0])} Order status error\n"
                        self.execution_sign = 2
                    else:
                        time.sleep(0.2)
                        continue
                else:
                    msg += f"{str(broker_obj)} {order_id} {info} ret=Error, order query failed\n"
                    self.execution_sign = -1
            except Exception as e:
                msg += f"{str(broker_obj)} {order_id} {str(e)} order query failed\n"
                error = error + 1
                if error >= 5:
                    self.execution_sign = -2
        return msg

    def cancel_broker_order(self, broker_obj, order_df):
        order_id = str(order_df.iloc[0, order_df.columns.get_loc("order_id")])
        msg = ""
        try:
            broker_obj.cancel_order(order_id)
        except Exception as e:
            msg += f"{str(broker_obj)} {order_id} {str(e)} cancellation failed\n"
            self.finished.emit(msg)
        else:
            msg += f"{str(broker_obj)} {order_id} has been successfully canceled\n"
            self.finished.emit(msg)

    def run(self):
        logging.info(f"Start {type(self).__name__}")

        order_msg = self.get_execution_sign(
            self.info_list[0][0],
            self.info_list[0][1],
        )

        if self.execution_sign == 1:
            try:
                for broker_obj, order_df in self.info_list:
                    t = Thread(
                        target=self.cancel_broker_order, args=(broker_obj, order_df)
                    )
                    self.thread_list.append(t)

                if len(self.thread_list):
                    for thread in self.thread_list:
                        thread.start()

            except Exception as e:
                logging.error(e, exc_info=True)
                self.failed.emit(str(e))

        else:
            self.failed.emit(order_msg)

    def stop(self):
        self._running = False
        logging.info(f"Start {type(self).__name__}")
        self.terminate()


class OrderInfoThread(QThread):
    failed = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, parent=None, broker_obj=None, order_id=None):
        super(OrderInfoThread, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.broker_obj = broker_obj
        self.order_id = order_id

    def run(self):
        try:
            logging.info(f"Start {type(self).__name__}")
            ret, data = self.broker_obj.get_order_info(self.order_id)
        except Exception as e:
            if str(e) == "此订单不支持此操作" or str(e) == "此订单号不存在":
                self.failed.emit(str(e))
            else:
                logging.error(e, exc_info=True)
                self.failed.emit(str(e))
        else:
            if ret == "OK":
                info_dic = {"info": data["order_detail"]}
                self.finished.emit(info_dic)

            else:
                self.failed.emit(data)

    def stop(self):
        self._running = False
        logging.info(f"Stop {type(self).__name__}")
        self.terminate()


class ViewOrderThread(QThread):          # 333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
    failed = pyqtSignal()
    acc_orders_data = pyqtSignal(list)

    def __init__(
            self,
            parent=None,
            broker_obj=[],
            order=True,
            today=True,
    ):
        super(ViewOrderThread, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.broker_obj = broker_obj
        self.order = order
        self.today = today
        self.thread_list = []
        self._lock = Lock()
        self.result_queue = queue.Queue()

    def run(self):
        broker_str_list = [str(broker) for broker in self.broker_obj]
        try:
            for broker in self.broker_obj:
                broker_index = broker_str_list.index(str(broker))
                t = Thread(
                    target=self.get_broker_order,
                    args=(self.broker_obj[broker_index], self.result_queue),
                )
                self.thread_list.append(t)
                t.start()
            for thread in self.thread_list:
                thread.join()

        except ApiException as e:
            logging.info(
                "Tiger Securities requires the interval between two dates to be less than 90 days",
                e,
            )
            self.failed.emit()

        except Exception as e:
            logging.error(e, exc_info=True)
            # error_counter.error_occurred()
            self.failed.emit()
            time.sleep(1)
        else:
            all_data = []
            logging.info("ViewOrderThread execution succeeded")
            while not self.result_queue.empty():
                all_data.append(self.result_queue.get())
            last_df = pd.concat(all_data, ignore_index=True)
            list_of_dicts = last_df.to_dict(orient="records")
            self.acc_orders_data.emit(list_of_dicts)

    def get_broker_order(self, broker, result_queue):
        self._lock.acquire()
        try:
            if self.order == True and self.today == True:
                acc_orders = broker.get_today_orders()
            elif self.order == True and self.today == None:
                acc_orders = broker.get_active_orders()
            elif self.order == False and self.today == True:
                acc_orders = broker.get_today_deals()
            acc_orders.insert(0, column="account", value=str(broker))
        except Exception as e:
            logging.error(e, exc_info=True)
            self._lock.release()
        else:
            result_queue.put(acc_orders)
            self._lock.release()

    def stop(self):
        self._running = False
        logging.info(f"Stop {type(self).__name__}")
        self.terminate()


class Sync2DBThread(QThread):
    failed = pyqtSignal()

    def __init__(self, parent=None, aurora_account=None, broker_list=[], db_list=None):
        super(Sync2DBThread, self).__init__(parent)
        self._mutex = QMutex()
        self._running = True
        self.aurora_account = aurora_account
        self.broker_list = broker_list
        self.db_list = db_list

    def run(self):
        error_counter = ErrorCounter(interval_threshold=200, counter_threshold=20)
        while error_counter.emit is False:
            for broker_obj in self.broker_list:
                time.sleep(3)
                try:
                    logging.info(f"Start {type(self).__name__}")
                    logging.info(str(broker_obj))
                    # jimmy 降低 futu 请求频率, 否则 get_today_orders 与 get_today_deals 间隔太短报错
                    acc_orders = broker_obj.get_today_orders()
                    logging.info(acc_orders)
                    time.sleep(5)
                    acc_deals = broker_obj.get_today_deals()
                    logging.info(acc_deals)
                    time.sleep(5)
                    self.sync_to_db(str(broker_obj), acc_orders, acc_deals)
                except Exception as e:
                    logging.error(e, exc_info=True)
                    error_counter.error_occurred()
                    time.sleep(1)
                else:
                    error_counter.counter = 0
            time.sleep(10)
        self.failed.emit()

    def stop(self):
        self._running = False
        logging.info(f"Stop {type(self).__name__}")
        self.terminate()

    def sync_to_db(self, broker_str, acc_orders, acc_deals):
        self.db_obj = AuroraDB(self.db_list)
        if acc_orders.shape[0] == 0:
            pass
        else:
            order_db = acc_orders.loc[
                       :,
                       [
                           "code",
                           "trd_side",
                           "price",
                           "qty",
                           "order_type",
                           "order_status",
                           "create_time",
                           "order_id",
                       ],
                       ]

            order_db.rename(
                columns={
                    "trd_side": "side",
                    "order_type": "type",
                    "order_status": "status",
                },
                inplace=True,
            )
            order_db.reset_index(drop=True, inplace=True)
            order_db.loc[:, "username"] = self.aurora_account.username
            order_db.loc[:, "account"] = broker_str
            # 时区转换, 将上传时间统一为北京时间
            order_db.loc[:, "datetime"] = datetime.now(
                timezone("Asia/Shanghai")
            ).strftime("%Y-%m-%d %H:%M:%S")

            # order_db["date"] = datetime.today().date()
            # order_db["time"] = datetime.today().time()
            self.db_obj.insert_order(order_db)

        if acc_deals.shape[0] == 0:
            pass
        else:
            deal_db = acc_deals.loc[
                      :, ["code", "trd_side", "price", "qty", "create_time", "order_id"]
                      ]
            deal_db.rename(
                columns={"trd_side": "side", "order_type": "type"},
                inplace=True,
            )
            deal_db.reset_index(drop=True, inplace=True)
            deal_db.loc[:, "username"] = self.aurora_account.username
            deal_db.loc[:, "account"] = broker_str
            # deal_db["date"] = datetime.today().date()
            # deal_db["time"] = datetime.today().time()
            deal_db.loc[:, "datetime"] = datetime.now(
                timezone("Asia/Shanghai")
            ).strftime("%Y-%m-%d %H:%M:%S")

            self.db_obj.insert_deal(deal_db)
