"""登录后公共导航、身份与退出组件。"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from base.base_page import BasePage, Locator, todo_locator


class NavigationComponent(BasePage):
    # ===== 已根据 2026-08-12 用户主页 DOM 完成定位 =====
    # 不使用动态 aria-controls（例如 dropdown-menu-5174）。
    USER_IDENTITY = (By.CSS_SELECTOR, ".user-menu .user-trigger .user-name")
    USER_MENU = (By.CSS_SELECTOR, ".user-menu .user-trigger")
    OPERATIONS_CONSOLE = (
        By.XPATH,
        "//li[contains(@class,'el-dropdown-menu__item')]"
        "[contains(normalize-space(.),'运营管理后台')]",
    )
    OPERATIONS_SHELL = (
        By.XPATH,
        "//div[contains(@class,'el-submenu__title')]"
        "[.//span[normalize-space()='我的消息']]",
    )
    LOGOUT_BUTTON = (
        By.XPATH,
        "//li[contains(@class,'el-dropdown-menu__item')]"
        "[contains(normalize-space(.),'退出登录')]",
    )

    # ===== TODO：运营管理后台业务菜单，后续按模块逐步补充 =====
    KNOWLEDGE_MENU = todo_locator("合规知识库菜单")
    DECLARATION_MENU = todo_locator("申报管理菜单")
    ROLE_MENU = todo_locator("角色管理菜单")
    DICTIONARY_MENU = todo_locator("字典管理菜单")
    CONTRACT_MENU = todo_locator("标准合同管理菜单")
    DATA_ASSET_MENU = todo_locator("数据资产管理菜单")
    TRANSACTION_MENU = todo_locator("交易管理菜单")
    PAYMENT_MENU = todo_locator("支付结算菜单")
    TRANSFER_MENU = todo_locator("数据传输菜单")
    EVIDENCE_MENU = todo_locator("存证管理菜单")
    ARCHIVE_MENU = todo_locator("合规归档菜单")
    ACCESS_DENIED_MESSAGE = todo_locator("无权限访问提示")
    # ===== 定位器填写区域结束 =====

    def wait_until_authenticated(self, expected_identity: str | None = None) -> str:
        """兼容普通用户首页和管理员直接进入运营后台两种登录落点。"""

        if expected_identity:
            return self._wait().until(
                lambda driver: self._visible_exact_text(expected_identity),
                message=f"登录后未显示预期账号：{expected_identity}",
            )
        return self.get_text(self.USER_IDENTITY)

    def current_identity(self) -> str:
        return self.get_text(self.USER_IDENTITY)

    def logout(self) -> None:
        self.click(self.USER_MENU)
        self.click(self.LOGOUT_BUTTON)

    def open_operations_console(self) -> None:
        original_handles = set(self.driver.window_handles)
        self.click(self.USER_MENU)
        self.click(self.OPERATIONS_CONSOLE)
        try:
            self._wait(3).until(
                lambda driver: len(driver.window_handles) > len(original_handles)
            )
        except TimeoutException:
            return
        self.switch_to_new_window(original_handles)

    def ensure_operations_console(self) -> None:
        """管理员登录后已在后台时不再重复点击入口。"""

        if self.is_visible(self.OPERATIONS_SHELL, timeout=2):
            return
        self.open_operations_console()
        self.find_visible(self.OPERATIONS_SHELL)

    def _visible_exact_text(self, text: str) -> str | bool:
        literal = self._xpath_literal(text)
        elements = self.driver.find_elements(
            By.XPATH,
            f"//*[normalize-space(.)={literal}]",
        )
        return next(
            (
                element.text.strip()
                for element in elements
                if element.is_displayed() and element.text.strip() == text
            ),
            False,
        )

    @staticmethod
    def _xpath_literal(value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"

    def open_role_management(self) -> None:
        self.click(self.ROLE_MENU)

    def open_dictionary_management(self) -> None:
        self.click(self.DICTIONARY_MENU)

    def open_declaration_management(self) -> None:
        self.click(self.DECLARATION_MENU)

    def open_contract_management(self) -> None:
        self.click(self.CONTRACT_MENU)

    def open_data_asset_management(self) -> None:
        self.click(self.DATA_ASSET_MENU)

    def open_transaction_management(self) -> None:
        self.click(self.TRANSACTION_MENU)

    def open_payment_management(self) -> None:
        self.click(self.PAYMENT_MENU)

    def open_transfer_management(self) -> None:
        self.click(self.TRANSFER_MENU)

    def open_evidence_management(self) -> None:
        self.click(self.EVIDENCE_MENU)

    def open_archive_management(self) -> None:
        self.click(self.ARCHIVE_MENU)

    def is_menu_visible(self, locator: Locator) -> bool:
        return self.is_visible(locator)

    def is_access_denied(self) -> bool:
        return self.is_visible(self.ACCESS_DENIED_MESSAGE, timeout=self.timeout)
