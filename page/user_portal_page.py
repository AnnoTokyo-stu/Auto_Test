"""运营管理后台的用户初始页与侧边栏页面对象。"""

from selenium.webdriver.common.by import By

from base.base_page import BasePage


class UserPortalPage(BasePage):
    """封装认证管理初始页及当前已知的用户侧边栏操作。"""

    # 使用业务文字限定组件，避免依赖 #app 层级和 nth-child。
    DATA_USER_CERTIFICATION_CARD = (
        By.XPATH,
        "//div[contains(@class,'auth-card')]"
        "[.//span[contains(@class,'card-title') "
        "and normalize-space()='数据使用方认证']]",
    )
    DATA_PROVIDER_CERTIFICATION_CARD = (
        By.XPATH,
        "//div[contains(@class,'auth-card')]"
        "[.//span[contains(@class,'card-title') "
        "and normalize-space()='数据提供方认证']]",
    )
    UNIFIED_IDENTITY_MENU = (
        By.XPATH,
        "//div[contains(@class,'el-submenu__title')]"
        "[.//span[normalize-space()='统一身份认证']]",
    )
    CERTIFICATION_MANAGEMENT_MENU = (
        By.XPATH,
        "//li[contains(@class,'el-menu-item')]"
        "[.//span[normalize-space()='认证管理']]",
    )
    MY_MESSAGES_MENU = (
        By.XPATH,
        "//div[contains(@class,'el-submenu__title')]"
        "[.//span[normalize-space()='我的消息']]",
    )
    MESSAGE_TODO_MANAGEMENT_MENU = (
        By.XPATH,
        "//li[contains(@class,'el-menu-item')]"
        "[.//span[normalize-space()='消息待办管理']]",
    )
    DATA_PRODUCT_TRANSACTION_MENU = (
        By.XPATH,
        "//div[contains(@class,'el-submenu__title')]"
        "[.//span[contains(normalize-space(.),'数据产品交易')]]",
    )
    DATA_PRODUCT_MANAGEMENT_MENU = (
        By.XPATH,
        "//li[contains(@class,'el-menu-item')]"
        "[.//span[normalize-space()='数据产品管理']]",
    )
    DATA_PRODUCT_AUDIT_MENU = (
        By.XPATH,
        "//li[contains(@class,'el-menu-item')]"
        "[.//span[contains(normalize-space(.),'数据产品审核')]]",
    )
    PRODUCT_ORDER_AUDIT_MENU = (
        By.XPATH,
        "//li[contains(@class,'el-menu-item')]"
        "[.//span[normalize-space()='产品订单审核']]",
    )
    DATA_MARKETPLACE_MENU = (
        By.XPATH,
        "//li[contains(@class,'el-menu-item')]"
        "[.//span[normalize-space()='数据交易市场']]",
    )
    PRODUCT_ORDER_MANAGEMENT_PATH = "/dataAssetTrade/product-order"

    def wait_until_loaded(self) -> None:
        self.find_visible(self.DATA_USER_CERTIFICATION_CARD)

    def wait_until_navigation_loaded(self) -> None:
        """等待登录后公共侧边栏；适用于已认证角色的业务页面。"""

        self.find_visible(self.MY_MESSAGES_MENU)

    def open_data_user_certification(self) -> None:
        self.click(self.DATA_USER_CERTIFICATION_CARD)

    def open_data_provider_certification(self) -> None:
        self.click(self.DATA_PROVIDER_CERTIFICATION_CARD)

    def open_certification_management(self) -> None:
        if not self.is_visible(self.CERTIFICATION_MANAGEMENT_MENU, timeout=1):
            self.click(self.UNIFIED_IDENTITY_MENU)
        self.click(self.CERTIFICATION_MANAGEMENT_MENU)

    def open_message_todo_management(self) -> None:
        if not self.is_visible(self.MESSAGE_TODO_MANAGEMENT_MENU, timeout=1):
            self.click(self.MY_MESSAGES_MENU)
        self.click(self.MESSAGE_TODO_MANAGEMENT_MENU)

    def open_data_product_management(self) -> None:
        if not self.is_visible(self.DATA_PRODUCT_MANAGEMENT_MENU, timeout=1):
            self.click(self.DATA_PRODUCT_TRANSACTION_MENU)
        self.click(self.DATA_PRODUCT_MANAGEMENT_MENU)

    def open_data_product_audit(self) -> None:
        if not self.is_visible(self.DATA_PRODUCT_AUDIT_MENU, timeout=1):
            self.click(self.DATA_PRODUCT_TRANSACTION_MENU)
        self.click(self.DATA_PRODUCT_AUDIT_MENU)

    def open_product_order_audit(self) -> None:
        if not self.is_visible(self.PRODUCT_ORDER_AUDIT_MENU, timeout=1):
            self.click(self.DATA_PRODUCT_TRANSACTION_MENU)
        self.click(self.PRODUCT_ORDER_AUDIT_MENU)

    def open_data_marketplace(self) -> None:
        if not self.is_visible(self.DATA_MARKETPLACE_MENU, timeout=1):
            self.click(self.DATA_PRODUCT_TRANSACTION_MENU)
        self.click(self.DATA_MARKETPLACE_MENU)

    def open_product_order_management(self) -> None:
        """复用当前登录会话，直接进入已知且稳定的订单管理路由。"""

        if self.PRODUCT_ORDER_MANAGEMENT_PATH not in self.driver.current_url:
            self.log.info("直接进入产品订单管理路由")
            self.open(self.PRODUCT_ORDER_MANAGEMENT_PATH)
        self.wait_url_contains(self.PRODUCT_ORDER_MANAGEMENT_PATH)
