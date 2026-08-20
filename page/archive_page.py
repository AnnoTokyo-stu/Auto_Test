"""合规归档页面对象。"""

from base.base_page import BasePage, todo_locator


class ArchivePage(BasePage):
    # ===== TODO：网页可访问后，在此区域填写真实定位器 =====
    BUSINESS_ID_INPUT = todo_locator("归档业务编号查询输入框")
    SEARCH_BUTTON = todo_locator("归档查询按钮")
    RESULT_BUSINESS_ID = todo_locator("归档结果业务编号")
    DETAIL_BUTTON = todo_locator("归档详情按钮")
    DECLARATION_ID = todo_locator("归档申报编号")
    CONTRACT_ID = todo_locator("归档合同编号")
    ORDER_ID = todo_locator("归档交易订单编号")
    PAYMENT_ID = todo_locator("归档支付编号")
    TRANSFER_ID = todo_locator("归档传输编号")
    EVIDENCE_ID = todo_locator("归档存证编号")
    ARCHIVE_STATUS = todo_locator("归档状态")
    # ===== 定位器填写区域结束 =====

    def search(self, business_id: str) -> str:
        self.input(self.BUSINESS_ID_INPUT, business_id)
        self.click(self.SEARCH_BUTTON)
        return self.get_text(self.RESULT_BUSINESS_ID)

    def detail(self) -> dict[str, str]:
        self.click(self.DETAIL_BUTTON)
        return {
            "declaration_id": self.get_text(self.DECLARATION_ID),
            "contract_id": self.get_text(self.CONTRACT_ID),
            "order_id": self.get_text(self.ORDER_ID),
            "payment_id": self.get_text(self.PAYMENT_ID),
            "transfer_id": self.get_text(self.TRANSFER_ID),
            "evidence_id": self.get_text(self.EVIDENCE_ID),
            "status": self.get_text(self.ARCHIVE_STATUS),
        }
