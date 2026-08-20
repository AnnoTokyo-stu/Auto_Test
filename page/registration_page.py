"""生产环境用户注册页面对象。

验证码采用人工输入、显式等待检测的半自动方式，不尝试绕过生产安全控制。
"""

from __future__ import annotations

from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from base.base_page import BasePage
from config import SETTINGS


class RegistrationPage(BasePage):
    # 使用注册弹窗和字段标签限定范围，避免依赖 #app 下易变化的 nth-child。
    OPEN_REGISTER_BUTTON = (
        By.XPATH,
        "//button[.//span[contains(normalize-space(.),'立即注册')]]",
    )
    REGISTER_DIALOG = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')][.//div[contains(@class,'el-dialog__header')][contains(.,'注册')]]",
    )
    ACCOUNT_INPUT = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//div[contains(@class,'el-form-item')][.//label[contains(normalize-space(.),'账号')]]//input[1]",
    )
    PASSWORD_INPUT = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//div[contains(@class,'el-form-item')][.//label[contains(normalize-space(.),'密码') and not(contains(normalize-space(.),'确认'))]]//input[1]",
    )
    CONFIRM_PASSWORD_INPUT = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//div[contains(@class,'el-form-item')][.//label[contains(normalize-space(.),'确认密码')]]//input[1]",
    )
    NAME_INPUT = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//div[contains(@class,'el-form-item')][.//label[contains(normalize-space(.),'姓名')]]//input[1]",
    )
    PHONE_INPUT = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//div[contains(@class,'el-form-item')][.//label[contains(normalize-space(.),'手机号')]]//input[not(@readonly)][1]",
    )
    EMAIL_INPUT = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//div[contains(@class,'el-form-item')][.//label[contains(normalize-space(.),'电子邮箱')]]//input[1]",
    )
    IMAGE_CAPTCHA_INPUT = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//div[contains(@class,'el-form-item')][.//label[contains(normalize-space(.),'图形验证码')]]//input[1]",
    )
    IMAGE_CAPTCHA = (
        By.CSS_SELECTOR,
        ".el-dialog .captcha-form-item .captcha-image img",
    )
    EMAIL_CODE_INPUT = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//div[contains(@class,'el-form-item')][.//label[contains(normalize-space(.),'邮箱验证码')]]//input[1]",
    )
    GET_EMAIL_CODE_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//button[.//span[contains(normalize-space(.),'获取邮箱验证码')]]",
    )
    AGREEMENT_INPUT = (
        By.CSS_SELECTOR,
        ".el-dialog .agreement-form-item input[type='checkbox']",
    )
    AGREEMENT_CHECKBOX = (
        By.CSS_SELECTOR,
        ".el-dialog .agreement-form-item .el-checkbox__inner",
    )
    REGISTER_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'el-dialog')]//button[.//span[normalize-space(.)='注册']]",
    )
    FIELD_ERROR_MESSAGES = (
        By.CSS_SELECTOR,
        ".el-dialog form .el-form-item__error",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def open_registration(self) -> None:
        self.click(self.OPEN_REGISTER_BUTTON)
        self.find_visible(self.REGISTER_DIALOG)

    def fill_basic_information(self, data: dict[str, Any]) -> None:
        self.input(self.ACCOUNT_INPUT, data["account"])
        self.input(self.PASSWORD_INPUT, data["password"])
        self.input(self.CONFIRM_PASSWORD_INPUT, data["password"])
        self.input(self.NAME_INPUT, data["name"])
        self.input(self.PHONE_INPUT, data["phone"])
        self.input(self.EMAIL_INPUT, data["email"])

    def wait_for_manual_image_captcha(self) -> str:
        self.find_visible(self.IMAGE_CAPTCHA)
        return self._wait_for_manual_input(
            self.IMAGE_CAPTCHA_INPUT,
            SETTINGS.manual_captcha_timeout,
            "请在注册弹窗中完整输入图形验证码，完成后按 Tab",
        )

    def request_email_code(self) -> None:
        self.click(self.GET_EMAIL_CODE_BUTTON)

    def wait_for_manual_email_code(self) -> str:
        return self._wait_for_manual_input(
            self.EMAIL_CODE_INPUT,
            SETTINGS.manual_email_code_timeout,
            "请从测试邮箱读取验证码并完整输入注册弹窗，完成后按 Tab",
        )

    def agree_to_terms(self) -> None:
        checkbox = self.find_present(self.AGREEMENT_INPUT)
        if not checkbox.is_selected():
            self.click(self.AGREEMENT_CHECKBOX)

    def submit_registration(self) -> None:
        self.click(self.REGISTER_BUTTON)

    def wait_until_registration_closed(self) -> bool:
        return self.wait_gone(self.REGISTER_DIALOG)

    def field_error_messages(self) -> list[str]:
        return [item.text.strip() for item in self.find_all(self.FIELD_ERROR_MESSAGES)]

    def _wait_for_manual_input(
        self, locator: tuple[str, str], timeout: int, prompt: str
    ) -> str:
        checked = self._validate_locator(locator)
        self.log.info("%s，最长等待 %s 秒", prompt, timeout)

        def _input_completed(driver: WebDriver) -> str | bool:
            element = driver.find_element(*checked)
            value = (element.get_attribute("value") or "").strip()
            input_finished = value and driver.switch_to.active_element != element
            return value if input_finished else False

        return self._wait(timeout).until(
            _input_completed,
            message=f"{prompt}超时",
        )
