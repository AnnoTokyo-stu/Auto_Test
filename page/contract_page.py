"""标准合同管理页面对象。"""

from typing import Any

from base.base_page import BasePage, todo_locator


class ContractPage(BasePage):
    # ===== TODO：网页可访问后，在此区域填写真实定位器 =====
    ADD_BUTTON = todo_locator("新建标准合同按钮")
    DECLARATION_SELECT = todo_locator("关联申报单选择控件")
    SUBJECT_NAME = todo_locator("合同主体名称")
    CONTACT_INPUT = todo_locator("合同联系人输入框")
    SAVE_BUTTON = todo_locator("保存合同按钮")
    SUCCESS_MESSAGE = todo_locator("合同保存成功提示")
    CONTRACT_ID = todo_locator("合同编号")
    AVAILABLE_DECLARATIONS = todo_locator("可关联申报单选项列表")
    SEARCH_INPUT = todo_locator("合同编号查询输入框")
    SEARCH_BUTTON = todo_locator("合同查询按钮")
    RESULT_CONTRACT_ID = todo_locator("合同查询结果编号")
    RESULT_DECLARATION_ID = todo_locator("合同结果关联申报编号")
    RESULT_SUBJECT_NAME = todo_locator("合同结果主体名称")
    # ===== 定位器填写区域结束 =====

    def available_declaration_ids(self) -> list[str]:
        self.click(self.DECLARATION_SELECT)
        return [item.text.strip() for item in self.find_all(self.AVAILABLE_DECLARATIONS)]

    def create_contract(self, declaration_id: str, data: dict[str, Any]) -> str:
        self.click(self.ADD_BUTTON)
        self.select_by_text(self.DECLARATION_SELECT, declaration_id)
        if data.get("contact"):
            self.input(self.CONTACT_INPUT, data["contact"])
        self.click(self.SAVE_BUTTON)
        self.find_visible(self.SUCCESS_MESSAGE)
        return self.get_text(self.CONTRACT_ID)

    def inherited_subject_name(self) -> str:
        return self.get_text(self.SUBJECT_NAME)

    def search(self, contract_id: str) -> dict[str, str]:
        self.input(self.SEARCH_INPUT, contract_id)
        self.click(self.SEARCH_BUTTON)
        return {
            "contract_id": self.get_text(self.RESULT_CONTRACT_ID),
            "declaration_id": self.get_text(self.RESULT_DECLARATION_ID),
            "subject_name": self.get_text(self.RESULT_SUBJECT_NAME),
        }
