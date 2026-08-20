"""角色授权与字典管理页面对象。"""

from base.base_page import BasePage, todo_locator


class SystemPage(BasePage):
    # ===== TODO：角色管理定位器 =====
    ADD_ROLE_BUTTON = todo_locator("新增角色按钮")
    ROLE_NAME_INPUT = todo_locator("角色名称输入框")
    ROLE_CODE_INPUT = todo_locator("角色编码输入框")
    KNOWLEDGE_MENU_CHECKBOX = todo_locator("合规知识库菜单权限复选框")
    CLEAR_ALL_MENUS_BUTTON = todo_locator("清空全部菜单授权按钮")
    SAVE_ROLE_BUTTON = todo_locator("保存角色按钮")
    ROLE_SEARCH_INPUT = todo_locator("角色查询输入框")
    ROLE_SEARCH_BUTTON = todo_locator("角色查询按钮")
    ROLE_RESULT_NAME = todo_locator("角色查询结果名称")
    ASSIGN_USER_BUTTON = todo_locator("为角色分配用户按钮")
    ASSIGN_USER_INPUT = todo_locator("待分配用户名输入框")
    ASSIGN_USER_CONFIRM = todo_locator("确认分配用户按钮")

    # ===== TODO：字典管理定位器 =====
    ADD_DICTIONARY_BUTTON = todo_locator("新增字典值按钮")
    DICTIONARY_TYPE_INPUT = todo_locator("字典类型输入或选择控件")
    DICTIONARY_LABEL_INPUT = todo_locator("字典显示名称输入框")
    DICTIONARY_VALUE_INPUT = todo_locator("字典值输入框")
    SAVE_DICTIONARY_BUTTON = todo_locator("保存字典值按钮")
    DICTIONARY_SEARCH_INPUT = todo_locator("字典值查询输入框")
    DICTIONARY_SEARCH_BUTTON = todo_locator("字典值查询按钮")
    DICTIONARY_RESULT_LABEL = todo_locator("字典查询结果显示名称")
    DICTIONARY_EDIT_BUTTON = todo_locator("字典值编辑按钮")
    DICTIONARY_ENABLED_SWITCH = todo_locator("字典值启停开关")
    DICTIONARY_EDIT_CONFIRM = todo_locator("字典值编辑确认按钮")
    OPERATION_SUCCESS = todo_locator("系统管理操作成功提示")
    # ===== 定位器填写区域结束 =====

    def create_knowledge_only_role(self, name: str, code: str) -> None:
        self.click(self.ADD_ROLE_BUTTON)
        self.input(self.ROLE_NAME_INPUT, name)
        self.input(self.ROLE_CODE_INPUT, code)
        self.click(self.CLEAR_ALL_MENUS_BUTTON)
        self.click(self.KNOWLEDGE_MENU_CHECKBOX)
        self.click(self.SAVE_ROLE_BUTTON)
        self.find_visible(self.OPERATION_SUCCESS)

    def assign_user_to_role(self, username: str) -> None:
        self.click(self.ASSIGN_USER_BUTTON)
        self.input(self.ASSIGN_USER_INPUT, username)
        self.click(self.ASSIGN_USER_CONFIRM)
        self.find_visible(self.OPERATION_SUCCESS)

    def search_role(self, role_name: str) -> str:
        self.input(self.ROLE_SEARCH_INPUT, role_name)
        self.click(self.ROLE_SEARCH_BUTTON)
        return self.get_text(self.ROLE_RESULT_NAME)

    def create_dictionary_value(
        self, dictionary_type: str, label: str, value: str
    ) -> None:
        self.click(self.ADD_DICTIONARY_BUTTON)
        self.input(self.DICTIONARY_TYPE_INPUT, dictionary_type)
        self.input(self.DICTIONARY_LABEL_INPUT, label)
        self.input(self.DICTIONARY_VALUE_INPUT, value)
        self.click(self.SAVE_DICTIONARY_BUTTON)
        self.find_visible(self.OPERATION_SUCCESS)

    def search_dictionary_value(self, label: str) -> str:
        self.input(self.DICTIONARY_SEARCH_INPUT, label)
        self.click(self.DICTIONARY_SEARCH_BUTTON)
        return self.get_text(self.DICTIONARY_RESULT_LABEL)

    def disable_dictionary_value(self, label: str) -> None:
        self.search_dictionary_value(label)
        self.click(self.DICTIONARY_EDIT_BUTTON)
        self.click(self.DICTIONARY_ENABLED_SWITCH)
        self.click(self.DICTIONARY_EDIT_CONFIRM)
        self.find_visible(self.OPERATION_SUCCESS)
