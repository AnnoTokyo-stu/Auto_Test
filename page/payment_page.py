"""支付结算页面对象。"""

from typing import Any

from base.base_page import BasePage, todo_locator


class PaymentPage(BasePage):
    # ===== TODO：网页可访问后，在此区域填写真实定位器 =====
    START_PAYMENT_BUTTON = todo_locator("发起支付按钮")
    ORDER_ID_INPUT = todo_locator("支付订单编号输入框")
    AMOUNT_INPUT = todo_locator("支付金额输入框")
    PAYMENT_TIME_INPUT = todo_locator("支付时间输入框")
    VOUCHER_INPUT = todo_locator("支付凭证上传控件")
    SUBMIT_BUTTON = todo_locator("提交支付申请按钮")
    CONFIRM_BUTTON = todo_locator("确认提交支付申请按钮")
    SUCCESS_MESSAGE = todo_locator("支付申请提交成功提示")
    PAYMENT_STATUS = todo_locator("支付状态")
    BLOCK_MESSAGE = todo_locator("支付信息不一致阻断提示")
    SEARCH_INPUT = todo_locator("支付订单编号查询输入框")
    SEARCH_BUTTON = todo_locator("支付查询按钮")
    RESULT_ORDER_ID = todo_locator("支付结果订单编号")
    RESULT_AMOUNT = todo_locator("支付结果金额")
    RESULT_STATUS = todo_locator("支付结果状态")
    # ===== 定位器填写区域结束 =====

    def fill_payment(self, data: dict[str, Any]) -> None:
        self.click(self.START_PAYMENT_BUTTON)
        self.input(self.ORDER_ID_INPUT, data["order_id"])
        self.input(self.AMOUNT_INPUT, data["amount"])
        self.input(self.PAYMENT_TIME_INPUT, data["payment_time"])
        self.upload(self.VOUCHER_INPUT, data["voucher"])

    def submit(self) -> None:
        self.click(self.SUBMIT_BUTTON)
        if self.is_visible(self.CONFIRM_BUTTON):
            self.click(self.CONFIRM_BUTTON)

    def submit_payment(self, data: dict[str, Any]) -> None:
        self.fill_payment(data)
        self.submit()
        self.find_visible(self.SUCCESS_MESSAGE)

    def current_status(self) -> str:
        return self.get_text(self.PAYMENT_STATUS)

    def get_block_message(self) -> str:
        return self.get_text(self.BLOCK_MESSAGE)

    def search(self, order_id: str) -> dict[str, str]:
        self.input(self.SEARCH_INPUT, order_id)
        self.click(self.SEARCH_BUTTON)
        return {
            "order_id": self.get_text(self.RESULT_ORDER_ID),
            "amount": self.get_text(self.RESULT_AMOUNT),
            "status": self.get_text(self.RESULT_STATUS),
        }
