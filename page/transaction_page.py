"""交易订单页面对象。"""

from typing import Any

from base.base_page import BasePage, todo_locator


class TransactionPage(BasePage):
    # ===== TODO：网页可访问后，在此区域填写真实定位器 =====
    ADD_ORDER_BUTTON = todo_locator("创建交易订单按钮")
    ASSET_SELECT = todo_locator("交易资产选择控件")
    DECLARATION_SELECT = todo_locator("交易关联申报选择控件")
    CONTRACT_SELECT = todo_locator("交易关联合同选择控件")
    QUANTITY_INPUT = todo_locator("交易数量输入框")
    SUBMIT_BUTTON = todo_locator("提交交易订单按钮")
    CONFIRM_BUTTON = todo_locator("确认提交订单按钮")
    SUCCESS_MESSAGE = todo_locator("订单创建成功提示")
    ORDER_ID = todo_locator("交易订单编号")
    ORDER_STATUS = todo_locator("交易订单状态")
    BLOCK_MESSAGE = todo_locator("交易前置条件阻断提示")
    SEARCH_INPUT = todo_locator("交易订单编号查询输入框")
    SEARCH_BUTTON = todo_locator("交易订单查询按钮")
    RESULT_ORDER_ID = todo_locator("交易查询结果订单编号")
    RESULT_ASSET_ID = todo_locator("交易结果资产编号")
    RESULT_DECLARATION_ID = todo_locator("交易结果申报编号")
    RESULT_CONTRACT_ID = todo_locator("交易结果合同编号")
    RESULT_AMOUNT = todo_locator("交易结果订单金额")
    RESULT_STATUS = todo_locator("交易结果订单状态")
    # ===== 定位器填写区域结束 =====

    def fill_order(self, data: dict[str, Any]) -> None:
        self.click(self.ADD_ORDER_BUTTON)
        self.select_by_text(self.ASSET_SELECT, data["asset_id"])
        self.select_by_text(self.DECLARATION_SELECT, data["declaration_id"])
        self.select_by_text(self.CONTRACT_SELECT, data["contract_id"])
        self.input(self.QUANTITY_INPUT, data["quantity"])

    def submit_order(self) -> None:
        self.click(self.SUBMIT_BUTTON)
        if self.is_visible(self.CONFIRM_BUTTON):
            self.click(self.CONFIRM_BUTTON)

    def create_order(self, data: dict[str, Any]) -> str:
        self.fill_order(data)
        self.submit_order()
        self.find_visible(self.SUCCESS_MESSAGE)
        return self.get_text(self.ORDER_ID)

    def current_status(self) -> str:
        return self.get_text(self.ORDER_STATUS)

    def get_block_message(self) -> str:
        return self.get_text(self.BLOCK_MESSAGE)

    def search(self, order_id: str) -> dict[str, str]:
        self.input(self.SEARCH_INPUT, order_id)
        self.click(self.SEARCH_BUTTON)
        return {
            "order_id": self.get_text(self.RESULT_ORDER_ID),
            "asset_id": self.get_text(self.RESULT_ASSET_ID),
            "declaration_id": self.get_text(self.RESULT_DECLARATION_ID),
            "contract_id": self.get_text(self.RESULT_CONTRACT_ID),
            "amount": self.get_text(self.RESULT_AMOUNT),
            "status": self.get_text(self.RESULT_STATUS),
        }
