"""存证与操作日志查询页面对象。"""

from base.base_page import BasePage, todo_locator


class EvidencePage(BasePage):
    # ===== TODO：网页可访问后，在此区域填写真实定位器 =====
    EVIDENCE_ID_INPUT = todo_locator("存证编号查询输入框")
    BUSINESS_ID_INPUT = todo_locator("关联业务编号查询输入框")
    SEARCH_BUTTON = todo_locator("存证查询按钮")
    RESULT_EVIDENCE_ID = todo_locator("存证查询结果编号")
    RESULT_BUSINESS_ID = todo_locator("存证结果关联业务编号")
    RESULT_TYPE = todo_locator("存证结果业务类型")
    DETAIL_BUTTON = todo_locator("存证详情按钮")
    DETAIL_OPERATOR = todo_locator("存证详情操作人")
    DETAIL_TIME = todo_locator("存证详情生成时间")
    LOG_TAB = todo_locator("操作日志页签")
    LOG_BUSINESS_ID_INPUT = todo_locator("日志业务编号查询输入框")
    LOG_SEARCH_BUTTON = todo_locator("日志查询按钮")
    LOG_RESULT_BUSINESS_ID = todo_locator("日志结果业务编号")
    # ===== 定位器填写区域结束 =====

    def search_by_business_id(self, business_id: str) -> dict[str, str]:
        self.input(self.BUSINESS_ID_INPUT, business_id)
        self.click(self.SEARCH_BUTTON)
        return {
            "evidence_id": self.get_text(self.RESULT_EVIDENCE_ID),
            "business_id": self.get_text(self.RESULT_BUSINESS_ID),
            "type": self.get_text(self.RESULT_TYPE),
        }

    def search_operation_log(self, business_id: str) -> str:
        self.click(self.LOG_TAB)
        self.input(self.LOG_BUSINESS_ID_INPUT, business_id)
        self.click(self.LOG_SEARCH_BUTTON)
        return self.get_text(self.LOG_RESULT_BUSINESS_ID)
