"""数据传输订单页面对象。"""

from typing import Any

from base.base_page import BasePage, todo_locator


class TransferPage(BasePage):
    # ===== TODO：网页可访问后，在此区域填写真实定位器 =====
    ADD_ORDER_BUTTON = todo_locator("新建传输订单按钮")
    ASSET_SELECT = todo_locator("传输资产选择控件")
    CERTIFICATE_SELECT = todo_locator("证书选择控件")
    ROUTE_SELECT = todo_locator("路由选择控件")
    TRANSFER_METHOD_SELECT = todo_locator("传输方式选择控件")
    SAVE_BUTTON = todo_locator("保存传输订单按钮")
    START_BUTTON = todo_locator("启动传输按钮")
    CONFIRM_START_BUTTON = todo_locator("确认启动传输按钮")
    SUCCESS_MESSAGE = todo_locator("传输操作成功提示")
    BLOCK_MESSAGE = todo_locator("传输前置校验阻断提示")
    ORDER_ID = todo_locator("传输订单编号")
    ORDER_STATUS = todo_locator("传输订单状态")
    SEARCH_INPUT = todo_locator("传输订单编号查询输入框")
    SEARCH_BUTTON = todo_locator("传输订单查询按钮")
    RESULT_ORDER_ID = todo_locator("传输查询结果订单编号")
    RESULT_ASSET_ID = todo_locator("传输结果资产编号")
    RESULT_STATUS = todo_locator("传输结果状态")
    ASSET_OPTIONS = todo_locator("传输订单可选资产列表")
    # ===== 定位器填写区域结束 =====

    def fill_order(self, data: dict[str, Any]) -> None:
        self.start_new_order()
        self.select_by_text(self.ASSET_SELECT, data["asset_id"])
        self.select_by_text(self.CERTIFICATE_SELECT, data["certificate"])
        self.select_by_text(self.ROUTE_SELECT, data["route"])
        self.select_by_text(self.TRANSFER_METHOD_SELECT, data["transfer_method"])

    def start_new_order(self) -> None:
        self.click(self.ADD_ORDER_BUTTON)

    def available_asset_ids(self) -> list[str]:
        self.click(self.ASSET_SELECT)
        return [item.text.strip() for item in self.find_all(self.ASSET_OPTIONS)]

    def save_order(self) -> None:
        self.click(self.SAVE_BUTTON)

    def create_order(self, data: dict[str, Any]) -> str:
        self.fill_order(data)
        self.save_order()
        self.find_visible(self.SUCCESS_MESSAGE)
        return self.get_text(self.ORDER_ID)

    def start(self) -> None:
        self.start_without_wait()
        self.find_visible(self.SUCCESS_MESSAGE)

    def start_without_wait(self) -> None:
        self.click(self.START_BUTTON)
        self.click(self.CONFIRM_START_BUTTON)

    def status(self) -> str:
        return self.get_text(self.ORDER_STATUS)

    def get_block_message(self) -> str:
        return self.get_text(self.BLOCK_MESSAGE)

    def search(self, order_id: str) -> dict[str, str]:
        self.input(self.SEARCH_INPUT, order_id)
        self.click(self.SEARCH_BUTTON)
        return {
            "order_id": self.get_text(self.RESULT_ORDER_ID),
            "asset_id": self.get_text(self.RESULT_ASSET_ID),
            "status": self.get_text(self.RESULT_STATUS),
        }
