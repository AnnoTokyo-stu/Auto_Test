"""数据传输、存证与归档：WEB-054、WEB-055、WEB-065、WEB-069。"""

import re

import allure
import pytest

from page.archive_page import ArchivePage
from page.evidence_page import EvidencePage
from page.transfer_page import TransferPage
from tools import load_case_data


pytestmark = [pytest.mark.ui, pytest.mark.p0]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("数据传输")
@allure.title("WEB-054 传输订单—{case_data[scenario]}")
@pytest.mark.transfer
@pytest.mark.destructive
@pytest.mark.parametrize(
    "case_data",
    load_case_data("transfer_data.json", "WEB-054"),
    ids=lambda row: row["scenario"],
)
def test_web_054_authorization_certificate_route_validation(
    driver, login_as, user_credentials, configured_case, case_data
):
    case_data = configured_case(
        case_data, "asset_id", "certificate", "route", "transfer_method"
    )
    navigation = login_as(user_credentials)
    navigation.open_transfer_management()
    transfer = TransferPage(driver)

    if case_data["scenario"] == "unauthorized_asset":
        with allure.step("无权资产不出现在传输订单可选范围"):
            transfer.start_new_order()
            assert case_data["asset_id"] not in transfer.available_asset_ids()
        return

    with allure.step("选择资产、证书、路由和传输方式并保存"):
        transfer.fill_order(case_data)
        transfer.save_order()

    if case_data["expected_allowed"]:
        with allure.step("授权资产、有效证书和合规路由可创建订单"):
            transfer.find_visible(transfer.SUCCESS_MESSAGE)
            assert transfer.get_text(transfer.ORDER_ID)
    else:
        with allure.step("任一前置条件无效时阻断并说明原因"):
            assert transfer.get_block_message()


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("数据传输")
@allure.title("WEB-055 传输订单—状态流转与重复提交")
@pytest.mark.transfer
@pytest.mark.destructive
def test_web_055_transfer_state_and_idempotency(
    driver,
    login_as,
    user_credentials,
    configured_case,
    configured_value,
):
    data = configured_case(
        load_case_data("transfer_data.json", "WEB-055")[0],
        "order_id",
        "completed_order_id",
        "processing_status",
        "terminal_statuses",
    )
    terminal_statuses = [
        configured_value(item, "WEB-055.terminal_statuses")
        for item in data["terminal_statuses"]
    ]
    navigation = login_as(user_credentials)
    navigation.open_transfer_management()
    transfer = TransferPage(driver)

    with allure.step("启动待处理传输订单并校验状态变化"):
        assert transfer.search(data["order_id"])["order_id"] == data["order_id"]
        transfer.start()
        assert transfer.status() in [data["processing_status"], *terminal_statuses]

    with allure.step("处理中重复启动应保持幂等或明确拒绝"):
        if transfer.is_visible(transfer.START_BUTTON):
            transfer.start_without_wait()
            assert transfer.is_visible(transfer.SUCCESS_MESSAGE) or transfer.is_visible(
                transfer.BLOCK_MESSAGE
            )

    with allure.step("已完成订单不可再次启动"):
        completed = transfer.search(data["completed_order_id"])
        assert completed["status"] in terminal_statuses
        if transfer.is_visible(transfer.START_BUTTON):
            transfer.start_without_wait()
            assert transfer.get_block_message()


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("存证管理")
@allure.title("WEB-065 存证列表—编号/类型查询及详情")
@pytest.mark.archive
def test_web_065_search_evidence_by_id_and_type(
    driver, login_as, user_credentials, configured_case
):
    data = configured_case(
        load_case_data("transfer_data.json", "WEB-065")[0],
        "business_id",
        "expected_evidence_type",
        "evidence_id_pattern",
    )
    navigation = login_as(user_credentials)
    navigation.open_evidence_management()
    evidence = EvidencePage(driver).search_by_business_id(data["business_id"])

    assert evidence["business_id"] == data["business_id"]
    assert evidence["type"] == data["expected_evidence_type"]
    assert re.fullmatch(data["evidence_id_pattern"], evidence["evidence_id"]), (
        "存证编号不符合测试用例规定的编号规则"
    )


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("合规归档")
@allure.title("WEB-069 业务闭环自动归档完整性")
@pytest.mark.archive
def test_web_069_completed_business_archive_integrity(
    driver, login_as, user_credentials, configured_case
):
    required = (
        "business_id",
        "declaration_id",
        "contract_id",
        "order_id",
        "payment_id",
        "transfer_id",
        "evidence_id",
        "completed_status",
    )
    data = configured_case(
        load_case_data("transfer_data.json", "WEB-069")[0], *required
    )
    navigation = login_as(user_credentials)
    navigation.open_archive_management()
    archive = ArchivePage(driver)

    with allure.step("按完整业务编号查询自动归档记录"):
        assert archive.search(data["business_id"]) == data["business_id"]
        detail = archive.detail()

    with allure.step("核对申报、合同、交易、支付、传输和存证材料"):
        for field in required[1:-1]:
            assert detail[field] == data[field], f"归档字段不一致：{field}"
        assert detail["status"] == data["completed_status"]
