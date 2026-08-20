"""生产环境半自动注册：WEB-001。"""

import allure
import pytest

from page.login_page import LoginPage
from page.registration_page import RegistrationPage
from tools import load_case_data


pytestmark = [
    pytest.mark.ui,
    pytest.mark.auth,
    pytest.mark.p0,
    pytest.mark.destructive,
    pytest.mark.production_registration,
]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("首页与账户")
@allure.title("WEB-001 用户注册—必填信息正确提交（生产环境半自动）")
def test_web_001_register_with_valid_required_information(
    driver,
    configured_case,
    visible_browser_required,
):
    data = configured_case(
        load_case_data("registration_data.json", "WEB-001")[0],
        "account",
        "password",
        "name",
        "phone",
        "email",
    )
    login_page = LoginPage(driver)
    registration = RegistrationPage(driver)

    with allure.step("从登录页打开注册弹窗并填写全部基础必填项"):
        login_page.open_entry()
        registration.open_registration()
        registration.fill_basic_information(data)

    with allure.step("人工输入图形验证码后获取邮箱验证码"):
        registration.wait_for_manual_image_captcha()
        registration.request_email_code()

    with allure.step("人工输入邮箱验证码、同意协议并提交注册"):
        registration.wait_for_manual_email_code()
        registration.agree_to_terms()
        registration.submit_registration()

    with allure.step("验证注册弹窗关闭并返回登录界面"):
        assert registration.wait_until_registration_closed(), "注册提交后弹窗未关闭"
        assert login_page.is_login_page(), "注册完成后未返回登录界面"
