import sys
import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QTabBar,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
    QPushButton,
    QListWidgetItem,
    QListWidget, QLabel,
)
from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QMouseEvent
import pandas as pd
from UI.UI_refresh_selection_data import Ui_Form
from UI.window_language import View, ODT, CMT
from subwindow import ModifyOrderWindow, ModifyMultiOrderWindow
from utils.comboBox_control import comboBoxControl
from utils.table_model import pandasModel, OrderModel
from utils.worker.position_thread import ViewPositionThread
from utils.worker.order_thread import (
    ViewOrderThread,
    OrderInfoThread,
    CancelOrderThread,
    ModifyOrderThread, ModifyMultiOrderThread,
    CancelMultiOrderThread
)
from utils.constants import *
from UI.window_language import PST
import logging


class RefreshSelectionData(QWidget, Ui_Form):
    ICON = QIcon()
    aurora_account = None
    LANGUAGE = "EN"
    broker_account_list = []
    signal_window_failed = pyqtSignal()
    # broker_remark = None

    def __init__(self):
        super().__init__()
        # Your code will go here
        self.check_list = None
        self.setupUi(self)
        self.setWindowIcon(self.ICON)
        self.resize(1400, 400)
        self.move(800, 700)
        self.initialize()
        self.add_tab()
        self.add_combobox()
        self.acc_pos = dict()
        self.acc_orders = dict()
        self.acc_deals = dict()
        self.thread = {}
        self.populate_account_list()
        self.acc_listWidget.itemDoubleClicked.connect(self.doubleclick_acc_list)
        self.tableView_order.doubleClicked.connect(self.on_order_clicked)
        self.tab.setCurrentIndex(0)
        self.tab_changed()
        self.tab.currentChanged.connect(self.tab_changed)
        self.pushButton_refresh.clicked.connect(self.refresh_account_view)
        self.pushButton_clear.clicked.connect(self.clear_data)
        self.pushButton_modify.clicked.connect(self.modify_multi_check)
        self.pushButton_cancel.clicked.connect(self.cancel_multi_check)
        self.pushButton_Inquire.clicked.connect(self.single_stat)
        self.comboBox_choose_code.clicked.connect(self.comboBox_add_code)
        self.checkBox_all.stateChanged.connect(self.on_checked_all)
        self.pushButton_stock_sum.clicked.connect(self.sum_of_stock)
        self.pos_df = pd.DataFrame()
        self.comboBox_choose_code_2.clicked.connect(self.query_select_code_qty)
        self.show()

    def query_select_code_qty(self):
        self.comboBox_choose_code_2.clear()
        if len(self.pos_df) >= 1:
            self.pos_df['CODE'] = self.pos_df['CODE'].str.replace('US.', '')  # 下拉框显示的时候去掉US
            self.comboBox_choose_code_2.addItems(
                self.pos_df.iloc[:, 1].unique().tolist()
            )

    def sum_of_stock(self):
        code = self.comboBox_choose_code_2.currentText()
        df = self.pos_df
        if not df.empty:
            df['CODE'] = df['CODE'].str.replace('US.', '')  # 拿到持仓也去掉US
            df['QTY'] = df['QTY'].astype(int)  # 防止个别券商的qty不是int
            sum = df[df['CODE'] == code]['QTY'].sum()
            QMessageBox.about(
                self,
                str(code) + " position detail:",
                "Total position: " + str(sum),
            )
        else:
            QMessageBox.information(self, "Retrieval Failed", "Please select a stock")

    def on_checked_all(self):
        if self.checkBox_all.isChecked() is True:
            for i in range(len(self.acc_listWidget)):
                item = self.acc_listWidget.item(i)
                select_account = item.checkState()
                if select_account == 2:
                    pass
                elif select_account == 0:
                    item.setCheckState(Qt.Checked)
        else:
            for i in range(len(self.acc_listWidget)):
                item = self.acc_listWidget.item(i)
                select_account = item.checkState()
                if select_account == 2:
                    item.setCheckState(Qt.Unchecked)
                elif select_account == 0:
                    pass
    def add_tab(self):
        self.tab = QTabBar(self)
        self.tab.addTab(ODT.tab_OA[self.LANGUAGE])
        self.tab.addTab(ODT.tab_OT[self.LANGUAGE])
        self.tab.addTab(ODT.tab_DT[self.LANGUAGE])
        self.tab.setShape(QTabBar.TriangularNorth)
        self.horizontalLayout_tab = QHBoxLayout()
        self.horizontalLayout_tab.addWidget(self.tab)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_tab.addItem(spacerItem)
        self.verticalLayout_2.insertLayout(0, self.horizontalLayout_tab)

    def initialize(self):
        self.model = OrderModel(pd.DataFrame())
        today = datetime.today().date()
        year = today.year
        month = today.month
        day = today.day
        self.Qtoday = QDate(year, month, day)
        self.dateEdit_from.setDate(self.Qtoday)
        self.dateEdit_to.setDate(self.Qtoday)
        self.setWindowTitle(f"Selected Account Inquiry")
        self.acc_listWidget.addItem(f"Double-click following account")

    def add_combobox(self):  # 添加组合框
        self.select_code_label = QLabel(self)
        self.select_code_label.setText("Order Code")
        self.comboBox_choose_code = comboBoxControl(self)  # 组合框控制
        self.comboBox_choose_code.setObjectName("select_code")
        self.horizontalLayout_6.insertWidget(1, self.select_code_label)
        self.horizontalLayout_6.insertWidget(2, self.comboBox_choose_code)

        self.select_code_label_2 = QLabel(self)
        self.select_code_label_2.setText("Position Code")
        self.comboBox_choose_code_2 = comboBoxControl(self)  # 组合框控制
        self.comboBox_choose_code_2.setObjectName("select_code")
        self.horizontalLayout_2.insertWidget(15, self.select_code_label_2)
        self.horizontalLayout_2.insertWidget(16, self.comboBox_choose_code_2)

    def populate_account_list(self):
        if len(self.broker_account_list) > 0:
            for broker_obj in self.broker_account_list:
                item = QListWidgetItem(f'({broker_obj.remark})' + ' ' * 5 + str(broker_obj), self.acc_listWidget)
                item.setCheckState(Qt.Unchecked)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

    def doubleclick_acc_list(self):
        doubleclick_account = self.acc_listWidget.currentItem().text()  # 双击选中的账户
        print('doubleclick_account:\n', doubleclick_account)
        try:
            if doubleclick_account == "Double-click following account":
                pass
            else:
                select_account = self.acc_listWidget.currentItem().checkState()  # checkState() 方法返回的是一个整数，它表示复选框的当前状态
                print('select_account:\n', select_account)
                if select_account == 0:
                    self.acc_listWidget.currentItem().setCheckState(Qt.Checked)  # 选中
                else:
                    self.acc_listWidget.currentItem().setCheckState(Qt.Unchecked)  # 不选中
        except AttributeError as e:
            logging.error(e, exc_info=True)
            QMessageBox.information(self, " ", "Please try again")

    def tab_changed(self):
        if self.tab.currentIndex() == 0:
            logging.info("0")
            self.horizontalGroupBox.setVisible(False)
            self.groupBox.setVisible(False)  # 不显示查询栏
            try:
                self.tableView_order.doubleClicked.disconnect()
            except TypeError:
                pass
            self.tableView_order.doubleClicked.connect(self.on_order_clicked)

        elif self.tab.currentIndex() == 1:
            logging.info("1")
            self.horizontalGroupBox.setVisible(False)
            self.groupBox.setVisible(False)
            try:
                self.tableView_order.doubleClicked.disconnect()
            except TypeError:
                pass
            self.tableView_order.doubleClicked.connect(self.on_order_clicked)

        elif self.tab.currentIndex() == 2:
            logging.info("2")
            self.horizontalGroupBox.setVisible(True)
            self.groupBox.setVisible(True)
            self.comboBox_choose_code.setEnabled(False)
            self.pushButton_Inquire.setEnabled(False)

            try:
                self.tableView_order.doubleClicked.disconnect()
            except TypeError:
                pass
            self.tableView_order.doubleClicked.connect(self.on_order_clicked)

    def refresh_account_view(self):
        check_account_list = []
        if len(self.broker_account_list) > 0:
            for i in range(len(self.acc_listWidget)):
                item = self.acc_listWidget.item(i)
                if item.checkState():
                    add_account = item.text().split(")")[-1].strip()
                    for broker_obj in self.broker_account_list:
                        if str(broker_obj) == add_account:
                            check_account_list.append(broker_obj)
        else:
            QMessageBox.critical(self, "Refresh failed", "No broker account in list")

        if len(check_account_list) > 0:
            self.get_acc_pos(check_account_list)
            if self.tab.currentIndex() == 0:
                self.get_acc_OA(check_account_list)
            elif self.tab.currentIndex() == 1:
                self.get_acc_OT(check_account_list)
            elif self.tab.currentIndex() == 2:
                self.get_acc_DT(check_account_list)

            self.check_list = check_account_list
        else:
            QMessageBox.critical(self, "Refresh failed", "No account selected")

    def get_acc_OA(self, check_account_list):  # 获取账户活跃订单 000000000000000000000000000000000000000000000000000000000
        broker_list = check_account_list
        self.thread[1] = ViewOrderThread(broker_obj=broker_list, order=True, today=None)
        self.thread[1].start()
        self.thread[1].acc_orders_data.connect(self.get_orders_success)
        self.thread[1].failed.connect(self.on_get_orders_failed)

    def get_acc_OT(self, check_account_list):  # 获取账户今日订单 000000000000000000000000000000000000000000000000000000000
        broker_list = check_account_list
        self.thread[1] = ViewOrderThread(
            broker_obj=broker_list,
            order=True,
            today=True,
        )
        self.thread[1].start()
        self.thread[1].acc_orders_data.connect(self.get_orders_success)
        self.thread[1].failed.connect(self.on_get_orders_failed)

    def get_acc_DT(self, check_account_list):  # 获取今日成交 000000000000000000000000000000000000000000000000000000000000
        broker_list = check_account_list
        self.thread[1] = ViewOrderThread(
            broker_obj=broker_list, order=False, today=True
        )
        self.thread[1].start()
        self.thread[1].acc_orders_data.connect(self.get_orders_success)
        self.thread[1].failed.connect(self.on_get_orders_failed)

    def get_acc_pos(self, check_account_list):  # 获取账户持仓
        broker_list = check_account_list
        self.thread[0] = ViewPositionThread(
            broker_obj=broker_list,
        )
        self.thread[0].start()
        self.thread[0].signal_acc_pos.connect(self.on_acc_pos_emitted)
        self.thread[0].signal_acc_asset.connect(self.on_acc_asset_emitted)
        self.thread[0].failed.connect(self.on_acc_pos_failed)

    def get_orders_success(self, acc_orders_data):
        self.thread[1].stop()
        order_list = pd.DataFrame(acc_orders_data)
        logging.info(order_list)
        if self.tab.currentIndex() in [0, 1]:
            self.order_list = order_list.reindex(
                columns=View.order_columns[self.LANGUAGE]
            )
            self.order_list.columns = ODT.order_columns[self.LANGUAGE]
            self.model = OrderModel(self.order_list)
            self.tableView_order.setModel(self.model)
            self.tableView_order.resizeColumnsToContents()

        else:
            self.order_list = order_list.reindex(
                columns=View.deal_columns[self.LANGUAGE]
            )
            self.order_list.columns = ODT.deal_columns[self.LANGUAGE]
            self.tableView_order.setModel(pandasModel(self.order_list))
            self.tableView_order.resizeColumnsToContents()
            self.update_stat()  # 计算成交数据
            self.comboBox_choose_code.setEnabled(True)  # 开启查询选项
            self.pushButton_Inquire.setEnabled(True)

    def comboBox_add_code(self):  # 查询combobox中添加股票名称
        self.comboBox_choose_code.clear()
        if len(self.order_list) >= 1:
            self.comboBox_choose_code.addItems(
                self.order_list.iloc[:, 1].unique().tolist()
            )

    def update_stat(self):
        if len(self.order_list) >= 1:
            stat_df = self.order_list.iloc[:, [1, 2, 3, 4]].reset_index(drop=True)
            stat_df.columns = ["code", "side", "price", "qty"]

            buy_qty = stat_df.loc[stat_df["side"].isin(BUY_ORDER_STATUS)]["qty"].sum()
            sell_qty = stat_df.loc[stat_df["side"].isin(SELL_ORDER_STATUS)]["qty"].sum()

            stat_df["mult"] = stat_df["price"] * stat_df["qty"]
            cost = stat_df.loc[stat_df["side"].isin(BUY_ORDER_STATUS)]["mult"].sum()
            gain = stat_df.loc[stat_df["side"].isin(SELL_ORDER_STATUS)]["mult"].sum()
            total_qty = stat_df["qty"].sum()
        else:
            buy_qty = 0
            sell_qty = 0
            cost = 0
            gain = 0
            total_qty = 0
        self.lineEdit_total_B_qty.setText(str(buy_qty))
        self.lineEdit_Cost.setText(str(round(float(cost), 3)))
        self.lineEdit_total_S_qty.setText(str(sell_qty))
        self.lineEdit_Gain.setText(str(round(float(gain), 3)))
        self.lineEdit_total_Qty.setText(str(total_qty))

    def single_stat(self):  # 单个统计
        if len(self.order_list) >= 1 and self.comboBox_choose_code.currentText() != "":
            code = self.comboBox_choose_code.currentText()
            if code in self.order_list.iloc[:, 1].unique().tolist():
                stat_df = (
                    self.order_list.iloc[:, [1, 2, 3, 4]]
                    .loc[self.order_list.iloc[:, 1] == code]
                    .reset_index(drop=True)
                )
                stat_df.columns = ["code", "side", "price", "qty"]
                buy_qty = stat_df.loc[stat_df["side"].isin(BUY_ORDER_STATUS)][
                    "qty"
                ].sum()
                sell_qty = stat_df.loc[stat_df["side"].isin(SELL_ORDER_STATUS)][
                    "qty"
                ].sum()

                stat_df["mult"] = stat_df["price"] * stat_df["qty"]
                cost = stat_df.loc[stat_df["side"].isin(BUY_ORDER_STATUS)]["mult"].sum()
                gain = stat_df.loc[stat_df["side"].isin(SELL_ORDER_STATUS)][
                    "mult"
                ].sum()
                total_qty = stat_df["qty"].sum()
                QMessageBox.about(
                    self,
                    str(code) + " Volume Summary",
                    "Buy volume: " + str(buy_qty) + "\n"
                    "Expense: " + str(round(cost, 3)) + "\n"
                    "Sell volume: " + str(sell_qty) + "\n"
                    "Income: " + str(round(gain, 3)) + "\n"
                    "Total buy and sell volume: " + str(total_qty),
                )
            else:
                QMessageBox.information(
                    self, "Retrieval Failed", "Please reselect the stock"
                )
        else:
            QMessageBox.information(self, "Retrieval Failed", "Please select a stock")

    def on_get_orders_failed(self):
        self.thread[1].stop()
        self.signal_window_failed.emit()

    def on_acc_pos_emitted(self):
        temp_pos_df = pd.DataFrame(columns=PST.table_columns[self.LANGUAGE])
        if len(self.check_list) > 0:
            for broker_obj in self.check_list:
                pos_df = broker_obj.position
                pos_df.columns = PST.table_columns[self.LANGUAGE]
                temp_pos_df = pd.concat([temp_pos_df, pos_df])
        self.pos_df = temp_pos_df
        self.tableView_position.setModel(pandasModel(temp_pos_df))
        self.tableView_position.resizeColumnsToContents()

    def on_acc_asset_emitted(self):
        # temp_total_assets = 0
        # temp_cash = 0
        # temp_market_val = 0
        # temp_bp_cash = 0
        # temp_pending_cash = 0
        # total_account = len(self.account_list_widget)
        # print('123', total_account)
        # selected_account = len(self.broker_list)
        # print('321', selected_account)
        # if selected_account == 0 or total_account == 0:
        #     temp_total_assets = 0
        #     temp_cash = 0
        #     temp_market_val = 0
        #     temp_bp_cash = 0
        #     temp_pending_cash = 0
        # else:
        #     for broker_obj in self.check_list:
        #         temp_total_assets += broker_obj.total_assets
        #         temp_cash += broker_obj.cash
        #         temp_market_val += broker_obj.market_val
        #         temp_bp_cash += broker_obj.bp_cash
        #         temp_pending_cash += broker_obj.pending_cash
        # self.lineEdit_total_asset.setText(str(round(temp_total_assets, 3)))
        # self.lineEdit_cash.setText(str(round(temp_cash, 3)))
        # self.lineEdit_marketvalue.setText(str(round(temp_market_val, 3)))
        # self.lineEdit_buypower_cash.setText(str(round(temp_bp_cash, 3)))
        # self.lineEdit_pending_cash.setText(str(round(temp_pending_cash, 3)))
        # self.thread[0].stop()
        temp_total_assets = 0
        temp_cash = 0
        temp_market_val = 0
        temp_bp_cash = 0
        temp_pending_cash = 0
        for broker_obj in self.check_list:
            temp_total_assets += broker_obj.total_assets
            temp_cash += broker_obj.cash
            temp_market_val += broker_obj.market_val
            temp_bp_cash += broker_obj.bp_cash
            temp_pending_cash += broker_obj.pending_cash
        self.lineEdit_total_asset.setText(str(round(temp_total_assets, 3)))
        self.lineEdit_cash.setText(str(round(temp_cash, 3)))
        self.lineEdit_marketvalue.setText(str(round(temp_market_val, 3)))
        self.lineEdit_buypower_cash.setText(str(round(temp_bp_cash, 3)))
        self.lineEdit_pending_cash.setText(str(round(temp_pending_cash, 3)))
        self.thread[0].stop()

    def on_acc_pos_failed(self, e):
        self.thread[0].stop()
        self.signal_window_failed.emit(e)

    def on_order_clicked(self, click_index):
        self.clicked_row = click_index.row()
        selected_account = self.order_list.iloc[self.clicked_row, 0]
        for broker_obj in self.broker_account_list:
            if str(broker_obj) == selected_account:
                self.selected_broker_obj = broker_obj
        order_id = self.order_list.iloc[self.clicked_row, -1]
        code = self.order_list.iloc[self.clicked_row, 1]
        order_type = self.order_list.iloc[self.clicked_row, 3]
        trd_side = self.order_list.iloc[self.clicked_row, 2]
        qty = self.order_list.iloc[self.clicked_row, 5]
        price = self.order_list.iloc[self.clicked_row, 4]
        aux_price = self.order_list.iloc[self.clicked_row, -2]
        time_in_force = self.order_list.iloc[self.clicked_row, -5]
        market_session = self.order_list.iloc[self.clicked_row, -4]

        CM_box = QMessageBox()
        CM_box.setWindowTitle(CMT.window_title[self.LANGUAGE])
        CM_box.setText(CMT.text[self.LANGUAGE])
        CM_box.addButton(
            QPushButton(CMT.button_cancel[self.LANGUAGE]), QMessageBox.YesRole
        )
        CM_box.addButton(
            QPushButton(CMT.button_modify[self.LANGUAGE]), QMessageBox.NoRole
        )
        CM_box.addButton(
            QPushButton(CMT.button_discard[self.LANGUAGE]), QMessageBox.RejectRole
        )
        ret = CM_box.exec_()
        logging.info(ret)
        if ret == 0:
            ret_cancel = QMessageBox.critical(
                self,
                CMT.confirm[self.LANGUAGE][0],
                CMT.confirm[self.LANGUAGE][1],
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret_cancel == QMessageBox.Yes:
                self.cancel_order(order_id)
            else:
                return
        if ret == 1:
            self.modify_window = ModifyOrderWindow(
                order_id,
                code,
                order_type,
                trd_side,
                qty,
                price,
                aux_price,
                time_in_force,
                market_session,
                str(self.selected_broker_obj),
            )
            self.modify_window.pushButton_modify.clicked.connect(self.modify_confirmed)  # 右上角的两个控件：Modify Check 和 Cancel Check
            self.modify_window.pushButton_cancel.clicked.connect(self.modify_canceled)  # 关闭 self.modify_window.close() 窗口
            self.modify_window.show()

        if ret == 2:
            return

    def cancel_order(self, order_id):  # 双击单个订单取消的时候调用了
        self.thread[2] = CancelOrderThread(
            broker_obj=self.selected_broker_obj, order_id=order_id
        )
        self.thread[2].start()
        self.thread[2].failed.connect(self.cancel_order_failed)
        self.thread[2].finished.connect(self.cancel_order_successful)

    def cancel_order_failed(self, msg):
        self.thread[2].stop()
        QMessageBox.critical(self, "Order Cancellation failed", msg)

    def cancel_order_successful(self):
        self.thread[2].stop()
        QMessageBox.information(
            self, "Success", "The order has been successfully cancelled"
        )

    def modify_confirmed(self):
        self.modify_window.close()
        modified_order_dict = dict()
        modified_order_dict["qty"] = self.modify_window.spinBox_qty.value()
        modified_order_dict["order_id"] = self.modify_window.lineEdit_orderID.text()
        modified_order_dict["price"] = self.modify_window.doubleSpinBox_price.value()
        modified_order_dict["aux_price"] = (
            self.modify_window.doubleSpinBox_sprice.value()
        )

        # TD 修改订单，需要更多参数
        modified_order_dict["code"] = self.modify_window.lineEdit_sym.text()
        modified_order_dict["side"] = self.modify_window.lineEdit_side.text()
        modified_order_dict["order_type"] = self.modify_window.lineEdit_orderType.text()
        modified_order_dict["tif"] = self.modify_window.lineEdit_tif.text()
        modified_order_dict["market_session"] = (
            self.modify_window.lineEdit_session.text()
        )
        self.modify_order(modified_order_dict)

    def modify_canceled(self):
        self.modify_window.close()

    def modify_order(self, modified_order_dict):
        self.thread[3] = ModifyOrderThread(
            broker_obj=self.selected_broker_obj, modified_order=modified_order_dict
        )
        self.thread[3].start()
        self.thread[3].failed.connect(self.modify_failed)
        self.thread[3].finished.connect(self.modify_finished)

    def modify_failed(self, msg):
        self.thread[3].stop()
        QMessageBox.critical(self, "Order Modification Failed", msg)

    def modify_finished(self):
        self.thread[3].stop()
        QMessageBox.information(
            self, "Success", "The order has been successfully modified"
        )

    def clear_data(self):
        logging.info("Clear the account list's check state")
        if len(self.broker_account_list) > 0:
            for i in range(self.acc_listWidget.count()):
                item = self.acc_listWidget.item(i)
                if item.checkState():
                    item.setCheckState(Qt.Unchecked)
                    self.comboBox_choose_code.clear()
                else:
                    pass
        else:
            QMessageBox.critical(
                self, "Failed to uncheck the account", "No broker account in list"
            )

    def check_authorization(self):
        if self.aurora_account.quant_auth >= 1:
            return True
        else:
            return False

    def on_tab_changed(self):
        if self.check_authorization():
            if self.tab.currentIndex() in [0, 1]:
                check_order = self.model.checks
                return check_order
    def modify_multi_check(self):
        if self.check_authorization():
            if self.tab.currentIndex() in [0, 1]:
                check_order = self.model.checks  # 挑选出check的order
                print('check_order:\n', check_order)
                if len(check_order) > 0:
                    msg_str = "\n".join(
                        "index: " + str(index)
                        + "\n"
                        + "Account: " + str(order[0])
                        + "\n"
                        + "Order ID: " + str(order[1])
                        for index, order in enumerate(check_order)
                    )
                    ret_modify = QMessageBox.information(
                        self,
                        "Confirm",
                        f"Please confirm to modify the following order：\n{msg_str}",
                        QMessageBox.Yes | QMessageBox.No)
                    if ret_modify == QMessageBox.Yes:
                        temp_order_df = self.order_list.copy()
                        temp_order_df["broker_order"] = list(
                            zip(self.order_list.iloc[:, 0], self.order_list.iloc[:, -1]))
                        temp_order_df.query("broker_order in @check_order", inplace=True)
                        temp_order_df.drop(columns=["broker_order"], inplace=True)
                        order_select_list = temp_order_df.to_dict("records")
                        self.modify_multi_window = ModifyMultiOrderWindow(order_list=order_select_list)
                        self.modify_multi_window.signal_modify.connect(self.multi_modify_orders)
                        self.modify_multi_window.show()
                    else:
                        return

                else:
                    QMessageBox.information(self, "Unable to modify", "No order selected")
                    return
            else:
                QMessageBox.critical(self, "Unable to modify", "The current interface cannot modify orders")
                return
        else:
            QMessageBox.critical(self, "Permission error", "Please enable quantitative trading permissions！",
                                 QMessageBox.Ok)

    def multi_modify_orders(self, modify_orders_list):
        print('self.broker_account_list:\n', self.broker_account_list)
        self.thread[5] = ModifyMultiOrderThread(
            broker_acc_list=self.broker_account_list,
            modified_orders_list=modify_orders_list,
        )
        self.thread[5].failed.connect(self.on_multi_modify_failed)
        self.thread[5].finished.connect(self.on_multi_modify_finished)
        self.thread[5].start()

    def on_multi_modify_finished(self, msg):
        self.thread[5].stop()
        QMessageBox.information(self, "Modify multiple orders", f"{msg}")

    def on_multi_modify_failed(self, error_msg):
        self.thread[5].stop()
        QMessageBox.critical(self, "Modify order error", f"Please check the error message:{error_msg}")

    def cancel_multi_check(self):  # 取消选中的多个账号
        if self.check_authorization():
            if self.tab.currentIndex() in [0, 1]:
                check_order = self.model.checks  # 挑选出check的order  上述写成函数
                print('取消的check_order:\n', check_order)
                # broker_list = [tup[0] for tup in check_order]  # 订单列表
                # id_list = [tup[1] for tup in check_order]  # 订单号列表
                # self.thread[4] = CancelMultiOrderThread(
                #     broker_acc_list=broker_list,
                #     order_list=id_list
                # )
                # self.thread[4].start()
                # self.thread[4].failed.connect(self.on_multi_cancel_failed)
                # self.thread[4].finished.connect(self.on_multi_cancel_finished)
                self.model.checks = []
                if len(check_order) == 0:
                    QMessageBox.information(
                        self, "Cancel order", "Please select an order first"
                    )
                    return
                msg_str = "\n".join(
                    "index: "
                    + str(index)
                    + "\n"
                    + "Account: "
                    + str(order[0])
                    + "\n"
                    + "Order ID: "
                    + str(order[1])
                    for index, order in enumerate(check_order)
                )
                ret_cancel = QMessageBox.critical(
                    self,
                    "Confirm cancellation",
                    f"Please confirm the cancellation of the following orders: \n{msg_str}",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if ret_cancel == QMessageBox.Yes:
                    self.checkBox_all.setChecked(False)
                    self.thread[4] = CancelMultiOrderThread(
                        broker_acc_list=self.broker_account_list, order_list=check_order
                    )
                    self.thread[4].failed.connect(self.on_multi_cancel_failed)
                    self.thread[4].finished.connect(self.on_multi_cancel_finished)
                    self.thread[4].start()

            else:
                QMessageBox.critical(self, "Unable to modify", "The current interface cannot modify orders")
                return
        else:
            QMessageBox.critical(self, "Permission error", "Please enable quantitative trading permissions！",
                                 QMessageBox.Ok)

    def on_multi_cancel_finished(self, msg):
        self.thread[4].stop()
        QMessageBox.information(self, "Cancel multiple orders", f"{msg}")

    def on_multi_cancel_failed(self, error_msg):
        self.thread[4].stop()
        QMessageBox.critical(self, "Cancel order error", f"Please check the error message:{error_msg}")

    # def cancel_order(self, order_id):  # 双击单个订单取消的时候调用了
    #     self.thread[2] = CancelOrderThread(
    #         broker_obj=self.selected_broker_obj, order_id=order_id
    #     )
    #     self.thread[2].start()
    #     self.thread[2].failed.connect(self.cancel_order_failed)
    #     self.thread[2].finished.connect(self.cancel_order_successful)
    #
    # def cancel_order_failed(self, msg):
    #     self.thread[2].stop()
    #     QMessageBox.critical(self, "Order Cancellation failed", msg)
    #
    # def cancel_order_successful(self):
    #     self.thread[2].stop()
    #     QMessageBox.information(
    #         self, "Success", "The order has been successfully cancelled"
    #     )

#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     RefreshSelectionData.broker_account_list = [str("futu") + "-" + str("56161230"),
#                                                 str("dfg") + "-" + str("24324")]
#     w = RefreshSelectionData()
#     sys.exit(app.exec_())
