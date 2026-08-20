"""申报与合同模块：WEB-021、WEB-029、WEB-030。"""

import allure
import pytest

from page.contract_page import ContractPage
from page.declaration_page import DeclarationPage
from page.evidence_page import EvidencePage
from tools import load_case_data, unique_name


pytestmark = [pytest.mark.ui, pytest.mark.declaration, pytest.mark.p0]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("申报管理")
@allure.title("WEB-021 标准合同申报—完整正常流程")
@pytest.mark.destructive
def test_web_021_complete_standard_declaration(
    driver, login_as, user_credentials, configured_case
):
    data = configured_case(
        load_case_data("declaration_data.json", "WEB-021")[0],
        "subject_name",
        "contact",
        "province",
        "city",
        "scene_name",
        "attachment",
        "draft_status",
        "submitted_status",
    ).copy()
    data["scene_name"] = unique_name(data["scene_name"])

    navigation = login_as(user_credentials)
    navigation.open_declaration_management()
    declaration = DeclarationPage(driver)

    with allure.step("完整填写标准合同申报并保存草稿"):
        declaration.start_standard_declaration()
        declaration.fill_standard_declaration(data)
        declaration.save_draft()
        assert declaration.current_status() == data["draft_status"]

    with allure.step("提交申报并验证编号、状态和列表数据"):
        declaration.submit()
        record_id = declaration.current_record_id()
        assert record_id, "提交后未生成唯一申报编号"
        assert declaration.current_status() == data["submitted_status"]
        result_id, result_status = declaration.search(record_id)
        assert result_id == record_id
        assert result_status == data["submitted_status"]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("申报管理")
@allure.title("WEB-029 申报生成的存证与日志")
def test_web_029_declaration_evidence_and_log(
    driver, login_as, user_credentials, configured_case
):
    data = configured_case(
        load_case_data("declaration_data.json", "WEB-029")[0],
        "business_id",
        "expected_evidence_type",
    )
    navigation = login_as(user_credentials)
    navigation.open_evidence_management()
    evidence_page = EvidencePage(driver)

    with allure.step("按已提交申报编号查询存证"):
        evidence = evidence_page.search_by_business_id(data["business_id"])
        assert evidence["business_id"] == data["business_id"]
        assert evidence["evidence_id"], "申报提交后未生成存证编号"
        assert evidence["type"] == data["expected_evidence_type"]

    with allure.step("按业务编号查询操作日志"):
        assert evidence_page.search_operation_log(data["business_id"]) == data["business_id"]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("标准合同管理")
@allure.title("WEB-030 标准合同创建—仅可关联合法申报单")
@pytest.mark.destructive
def test_web_030_contract_only_links_legal_declaration(
    driver, login_as, user_credentials, configured_case
):
    data = configured_case(
        load_case_data("declaration_data.json", "WEB-030")[0],
        "valid_declaration_id",
        "illegal_declaration_id",
        "contact",
    )
    navigation = login_as(user_credentials)
    navigation.open_contract_management()
    contract_page = ContractPage(driver)

    with allure.step("验证可关联申报单范围"):
        available_ids = contract_page.available_declaration_ids()
        assert data["valid_declaration_id"] in available_ids
        assert data["illegal_declaration_id"] not in available_ids

    with allure.step("关联合法申报单创建合同"):
        contract_id = contract_page.create_contract(
            data["valid_declaration_id"], {"contact": data["contact"]}
        )
        assert contract_id, "合法申报单未成功生成合同"
