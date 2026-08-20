"""标准合同申报页面对象。"""

from typing import Any

from base.base_page import BasePage, todo_locator


class DeclarationPage(BasePage):
    # ===== TODO：网页可访问后，在此区域填写真实定位器 =====
    ADD_BUTTON = todo_locator("新建标准合同申报按钮")
    SUBJECT_NAME_INPUT = todo_locator("申报主体名称输入框")
    CONTACT_INPUT = todo_locator("联系人输入框")
    PROVINCE_SELECT = todo_locator("省份下拉框")
    CITY_SELECT = todo_locator("城市下拉框")
    SCENE_NAME_INPUT = todo_locator("出境场景名称输入框")
    ATTACHMENT_INPUT = todo_locator("申报附件上传控件")
    NEXT_BUTTON = todo_locator("申报步骤下一步按钮")
    SAVE_DRAFT_BUTTON = todo_locator("保存申报草稿按钮")
    SUBMIT_BUTTON = todo_locator("提交申报按钮")
    CONFIRM_SUBMIT_BUTTON = todo_locator("确认提交申报按钮")
    SUCCESS_MESSAGE = todo_locator("申报操作成功提示")
    RECORD_ID = todo_locator("申报编号")
    RECORD_STATUS = todo_locator("申报状态")
    SEARCH_ID_INPUT = todo_locator("申报编号查询输入框")
    SEARCH_BUTTON = todo_locator("申报查询按钮")
    RESULT_ID = todo_locator("申报列表结果编号")
    RESULT_STATUS = todo_locator("申报列表结果状态")
    RESULT_SUBJECT_NAME = todo_locator("申报列表或详情主体名称")
    RESULT_BUSINESS_TYPE = todo_locator("申报列表或详情业务类型")
    BUSINESS_TYPE_SELECT = todo_locator("业务类型下拉框")
    BUSINESS_TYPE_OPTIONS = todo_locator("业务类型下拉选项列表")
    # ===== 定位器填写区域结束 =====

    def start_standard_declaration(self) -> None:
        self.click(self.ADD_BUTTON)

    def fill_standard_declaration(self, data: dict[str, Any]) -> None:
        self.input(self.SUBJECT_NAME_INPUT, data["subject_name"])
        self.input(self.CONTACT_INPUT, data["contact"])
        self.select_by_text(self.PROVINCE_SELECT, data["province"])
        self.select_by_text(self.CITY_SELECT, data["city"])
        self.input(self.SCENE_NAME_INPUT, data["scene_name"])
        if data.get("attachment"):
            self.upload(self.ATTACHMENT_INPUT, data["attachment"])

    def save_draft(self) -> None:
        self.click(self.SAVE_DRAFT_BUTTON)
        self.find_visible(self.SUCCESS_MESSAGE)

    def submit(self) -> None:
        self.click(self.SUBMIT_BUTTON)
        self.click(self.CONFIRM_SUBMIT_BUTTON)
        self.find_visible(self.SUCCESS_MESSAGE)

    def current_record_id(self) -> str:
        return self.get_text(self.RECORD_ID)

    def current_status(self) -> str:
        return self.get_text(self.RECORD_STATUS)

    def search(self, record_id: str) -> tuple[str, str]:
        self.input(self.SEARCH_ID_INPUT, record_id)
        self.click(self.SEARCH_BUTTON)
        return self.get_text(self.RESULT_ID), self.get_text(self.RESULT_STATUS)

    def result_subject_name(self) -> str:
        return self.get_text(self.RESULT_SUBJECT_NAME)

    def result_business_type(self) -> str:
        return self.get_text(self.RESULT_BUSINESS_TYPE)

    def is_dictionary_option_available(self, label: str) -> bool:
        self.click(self.BUSINESS_TYPE_SELECT)
        options = self.find_all(self.BUSINESS_TYPE_OPTIONS)
        return any(item.text.strip() == label for item in options)

    def select_business_type(self, label: str) -> None:
        self.select_by_text(self.BUSINESS_TYPE_SELECT, label)
