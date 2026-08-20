"""系统管理模块：WEB-017、WEB-020。"""

import allure
import pytest

from page.declaration_page import DeclarationPage
from page.login_page import LoginPage
from page.navigation_component import NavigationComponent
from page.system_page import SystemPage
from tools import load_case_data, unique_name


pytestmark = [
    pytest.mark.ui,
    pytest.mark.system,
    pytest.mark.p0,
    pytest.mark.destructive,
]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("系统管理")
@allure.title("WEB-017 角色管理—菜单授权生效范围")
def test_web_017_role_menu_permission_scope(
    driver,
    login_as,
    admin_credentials,
    rbac_user_credentials,
    configured_case,
):
    data = configured_case(
        load_case_data("permission_data.json", "WEB-017")[0],
        "role_name_prefix",
        "role_code_prefix",
        "unauthorized_path",
    )
    role_name = unique_name(data["role_name_prefix"])
    role_code = unique_name(data["role_code_prefix"])

    with allure.step("管理员创建仅授权知识库菜单的角色并分配用户"):
        navigation = login_as(admin_credentials)
        navigation.open_role_management()
        system_page = SystemPage(driver)
        system_page.create_knowledge_only_role(role_name, role_code)
        assert system_page.search_role(role_name) == role_name
        system_page.assign_user_to_role(rbac_user_credentials.username)
        navigation.logout()

    with allure.step("被授权用户重新登录并校验菜单范围"):
        navigation = login_as(rbac_user_credentials)
        assert navigation.is_menu_visible(navigation.KNOWLEDGE_MENU)
        assert not navigation.is_menu_visible(navigation.DECLARATION_MENU)

    with allure.step("直接访问未授权地址同样被服务端拒绝"):
        navigation.open(data["unauthorized_path"])
        assert navigation.is_access_denied(), "未授权直链未被拒绝"


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("系统管理")
@allure.title("WEB-020 字典管理—新增、编辑、停用值联动")
def test_web_020_dictionary_value_lifecycle(
    driver, login_as, admin_credentials, user_credentials, configured_case
):
    data = configured_case(
        load_case_data("permission_data.json", "WEB-020")[0],
        "dictionary_type",
        "label_prefix",
        "value_prefix",
    )
    label = unique_name(data["label_prefix"])
    value = unique_name(data["value_prefix"])

    with allure.step("管理员新增业务字典值"):
        navigation = login_as(admin_credentials)
        navigation.open_dictionary_management()
        system_page = SystemPage(driver)
        system_page.create_dictionary_value(data["dictionary_type"], label, value)
        assert system_page.search_dictionary_value(label) == label
        navigation.logout()

    with allure.step("新字典值可用于新申报"):
        navigation = login_as(user_credentials)
        navigation.open_declaration_management()
        declaration_page = DeclarationPage(driver)
        declaration_page.start_standard_declaration()
        assert declaration_page.is_dictionary_option_available(label)
        declaration_page.select_business_type(label)
        declaration_page.save_draft()
        historical_record_id = declaration_page.current_record_id()
        assert historical_record_id, "未生成用于验证历史字典值的草稿记录"
        navigation.logout()

    with allure.step("管理员停用字典值"):
        navigation = login_as(admin_credentials)
        navigation.open_dictionary_management()
        SystemPage(driver).disable_dictionary_value(label)
        navigation.logout()

    with allure.step("新申报不可再选，历史记录仍展示原值"):
        navigation = login_as(user_credentials)
        navigation.open_declaration_management()
        declaration_page.start_standard_declaration()
        assert not declaration_page.is_dictionary_option_available(label)
        navigation.open_declaration_management()
        declaration_page.search(historical_record_id)
        assert declaration_page.result_business_type() == label
