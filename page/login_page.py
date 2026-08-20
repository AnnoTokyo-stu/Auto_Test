"""登录页面对象。"""

from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from base.base_page import BasePage, todo_locator
from config import SETTINGS


class LoginPage(BasePage):
    # ===== 已根据 2026-08-11 登录页 DOM 完成定位 =====
    LOGIN_FORM = (By.CSS_SELECTOR, ".form-box form.login-form")
    USERNAME_INPUT = (
        By.CSS_SELECTOR,
        ".login-form input[placeholder='请输入账号']",
    )
    PASSWORD_INPUT = (
        By.CSS_SELECTOR,
        ".login-form input[placeholder='请输入密码']",
    )
    CAPTCHA_INPUT = (
        By.CSS_SELECTOR,
        ".login-form input[placeholder='请输入图形验证码']",
    )
    CAPTCHA_IMAGE = (By.CSS_SELECTOR, ".login-form .captcha-image img")
    LOGIN_BUTTON = (By.CSS_SELECTOR, ".form-box button.btn-login")
    FIELD_ERROR_MESSAGE = (By.CSS_SELECTOR, ".login-form .el-form-item__error")

    # TODO：完成一次错误密码登录后，补充“账号或密码错误”等认证错误提示定位器。
    ERROR_MESSAGE = todo_locator("错误密码或不存在账号的认证错误提示")
    # ===== 定位器填写区域结束 =====

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def open_entry(self) -> None:
        self.open(SETTINGS.entry_url)
        self.find_visible(self.LOGIN_FORM)

    def login(
        self,
        username: str,
        password: str,
        *,
        wait_for_manual_captcha: bool = True,
    ) -> None:
        self.input(self.USERNAME_INPUT, username)
        self.input(self.PASSWORD_INPUT, password)
        if wait_for_manual_captcha:
            self.wait_for_manual_captcha()
        self.click(self.LOGIN_BUTTON)

    def wait_for_manual_captcha(self) -> str:
        """等待测试人员在可见浏览器中人工输入 4 位图形验证码。"""

        locator = self._validate_locator(self.CAPTCHA_INPUT)
        self.find_visible(self.CAPTCHA_IMAGE)
        self.log.info(
            "请在浏览器中输入图形验证码，最长等待 %s 秒",
            SETTINGS.manual_captcha_timeout,
        )

        def _captcha_completed(driver: WebDriver) -> str | bool:
            value = (driver.find_element(*locator).get_attribute("value") or "").strip()
            return value if len(value) == 4 else False

        return self._wait(SETTINGS.manual_captcha_timeout).until(
            _captcha_completed,
            message="等待人工输入 4 位图形验证码超时",
        )

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def wait_until_login_redirected(self) -> str:
        """等待成功登录后 URL 离开 /login，避免加载中提前验证导航元素。"""

        def _left_login_page(driver: WebDriver) -> str | bool:
            current_url = driver.current_url
            return current_url if urlparse(current_url).path.rstrip("/") != "/login" else False

        return self._wait(SETTINGS.page_load_timeout).until(
            _left_login_page,
            message="登录提交后未在规定时间内离开登录页",
        )

    def get_field_error_message(self) -> str:
        return self.get_text(self.FIELD_ERROR_MESSAGE)

    def is_login_page(self) -> bool:
        return self.is_visible(self.LOGIN_FORM, timeout=self.timeout)
