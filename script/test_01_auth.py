"""首页与账户模块：WEB-006～WEB-009。"""

import allure
import pytest

from page.login_page import LoginPage
from page.navigation_component import NavigationComponent
from tools import load_case_data


pytestmark = [pytest.mark.ui, pytest.mark.auth, pytest.mark.p0]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("首页与账户")
@allure.title("WEB-006 用户登录—正确凭据")
@pytest.mark.smoke
def test_web_006_login_with_valid_credentials(
    driver, user_credentials, user_display_name
):
    login_page = LoginPage(driver)
    navigation = NavigationComponent(driver)

    with allure.step("从系统入口跳转登录页并输入正确凭据"):
        login_page.open_entry()
        login_page.login(user_credentials.username, user_credentials.password)
        login_page.wait_until_login_redirected()

    with allure.step("验证登录成功、显示当前用户身份并建立会话"):
        identity = navigation.wait_until_authenticated()
        assert identity, "登录后未显示当前用户身份"
        assert user_display_name in identity, "页面显示的当前用户身份不正确"


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("首页与账户")
@allure.title("WEB-007 用户登录—错误密码与不存在账号：{case_data[scenario]}")
@pytest.mark.parametrize(
    "case_data",
    load_case_data("login_data.json", "WEB-007"),
    ids=lambda row: row["scenario"],
)
def test_web_007_reject_invalid_credentials(driver, configured_case, case_data):
    case_data = configured_case(
        case_data, "username", "password", "expected_error_text"
    )
    login_page = LoginPage(driver)

    with allure.step("提交错误密码或不存在账号"):
        login_page.open_entry()
        login_page.login(case_data["username"], case_data["password"])

    with allure.step("验证不建立会话并显示统一错误提示"):
        message = login_page.get_error_message()
        assert message == case_data["expected_error_text"]
        assert case_data["username"] not in message, "错误提示泄露了登录账号"
        assert login_page.is_login_page(), "失败登录不应离开登录页"


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("首页与账户")
@allure.title("WEB-008 登录态与退出登录")
@pytest.mark.smoke
def test_web_008_session_and_logout(driver, user_credentials):
    login_page = LoginPage(driver)
    navigation = NavigationComponent(driver)

    login_page.open_entry()
    login_page.login(user_credentials.username, user_credentials.password)
    login_page.wait_until_login_redirected()
    navigation.wait_until_authenticated()

    with allure.step("刷新受限页面后会话仍有效"):
        navigation.refresh()
        assert navigation.current_identity(), "刷新后登录会话失效"

    with allure.step("退出后返回受限页面不能恢复登录内容"):
        navigation.logout()
        assert login_page.is_login_page(), "退出后未返回登录页"
        login_page.back()
        assert login_page.is_login_page(), "浏览器返回恢复了已退出的受限内容"


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("首页与账户")
@allure.title("WEB-009 未登录访问受限功能")
@pytest.mark.smoke
def test_web_009_redirect_unauthenticated_user(driver):
    login_page = LoginPage(driver)

    with allure.step("未登录直接访问受限入口"):
        login_page.open_entry()

    with allure.step("验证跳转登录页且不展示业务数据"):
        assert login_page.is_login_page(), "未登录访问受限入口未跳转登录页"
