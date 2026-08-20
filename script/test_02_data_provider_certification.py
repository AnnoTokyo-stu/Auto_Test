"""认证管理：WEB-011 数据提供方认证的提交前资料填写阶段。"""

import allure
import pytest

from page.data_provider_certification_page import DataProviderCertificationPage
from page.user_portal_page import UserPortalPage
from tools import load_case_data


pytestmark = [
    pytest.mark.ui,
    pytest.mark.certification,
    pytest.mark.p0,
    pytest.mark.destructive,
]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("认证管理")
@allure.title("WEB-011 数据提供方认证—完整资料填写（提交前阶段）")
def test_web_011_fill_data_provider_certification_for_review(
    driver,
    login_as,
    user_credentials,
    configured_case,
):
    data = configured_case(
        load_case_data("data_provider_certification.json", "WEB-011")[0],
        "subject",
        "legal_representative",
        "operator",
        "cny_account",
    )
    DataProviderCertificationPage.validate_attachment_files(data)

    with allure.step("登录并进入运营管理后台的认证管理页面"):
        navigation = login_as(user_credentials)
        navigation.open_operations_console()
        portal = UserPortalPage(driver)
        portal.wait_until_loaded()
        portal.open_data_provider_certification()

    with allure.step("填写主体、法定代表人、经办人及人民币收款账户资料"):
        certification = DataProviderCertificationPage(driver)
        certification.wait_until_loaded()
        certification.fill_complete_application(data)

    with allure.step("验证资料已填写并停留在提交前供人工审查"):
        assert certification.is_ready_for_review(data), "资料填写结果与模拟数据不一致"
        allure.attach(
            driver.get_screenshot_as_png(),
            name="数据提供方认证提交前页面",
            attachment_type=allure.attachment_type.PNG,
        )
        # 生产环境中不自动点击“提交”；待人工审查数据和页面状态后再扩展提交验证。
