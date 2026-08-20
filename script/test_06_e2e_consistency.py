"""跨模块一致性回归：WEB-073。"""

import allure
import pytest

from page.archive_page import ArchivePage
from page.contract_page import ContractPage
from page.data_asset_page import DataAssetPage
from page.declaration_page import DeclarationPage
from page.evidence_page import EvidencePage
from page.payment_page import PaymentPage
from page.transaction_page import TransactionPage
from page.transfer_page import TransferPage
from tools import load_case_data


pytestmark = [
    pytest.mark.ui,
    pytest.mark.e2e,
    pytest.mark.p0,
]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("通用交互")
@allure.title("WEB-073 跨模块数据一致性回归")
def test_web_073_cross_module_business_consistency(
    driver, login_as, user_credentials, configured_case
):
    required_fields = (
        "business_id",
        "subject_name",
        "asset_id",
        "declaration_id",
        "contract_id",
        "order_id",
        "amount",
        "payment_id",
        "transfer_id",
        "evidence_id",
    )
    data = configured_case(
        load_case_data("runtime_data.json", "WEB-073")[0], *required_fields
    )
    navigation = login_as(user_credentials)

    with allure.step("在数据资产模块核对资产标识"):
        navigation.open_data_asset_management()
        asset = DataAssetPage(driver).search(data["asset_id"])
        assert asset["asset_id"] == data["asset_id"]

    with allure.step("在申报模块核对申报编号和主体"):
        navigation.open_declaration_management()
        declaration_page = DeclarationPage(driver)
        declaration_id, declaration_status = declaration_page.search(
            data["declaration_id"]
        )
        assert declaration_id == data["declaration_id"]
        assert declaration_page.result_subject_name() == data["subject_name"]
        assert declaration_status, "申报状态为空"

    with allure.step("在合同模块核对申报关联和主体"):
        navigation.open_contract_management()
        contract = ContractPage(driver).search(data["contract_id"])
        assert contract["contract_id"] == data["contract_id"]
        assert contract["declaration_id"] == data["declaration_id"]
        assert contract["subject_name"] == data["subject_name"]

    with allure.step("在交易模块核对资产、合同、申报和金额"):
        navigation.open_transaction_management()
        order = TransactionPage(driver).search(data["order_id"])
        assert order["asset_id"] == data["asset_id"]
        assert order["declaration_id"] == data["declaration_id"]
        assert order["contract_id"] == data["contract_id"]
        assert order["amount"] == data["amount"]

    with allure.step("在支付模块核对订单与金额"):
        navigation.open_payment_management()
        payment = PaymentPage(driver).search(data["order_id"])
        assert payment["order_id"] == data["order_id"]
        assert payment["amount"] == data["amount"]

    with allure.step("在传输模块核对资产与传输订单"):
        navigation.open_transfer_management()
        transfer = TransferPage(driver).search(data["transfer_id"])
        assert transfer["order_id"] == data["transfer_id"]
        assert transfer["asset_id"] == data["asset_id"]

    with allure.step("在存证和归档模块核对完整业务关系"):
        navigation.open_evidence_management()
        evidence = EvidencePage(driver).search_by_business_id(data["business_id"])
        assert evidence["evidence_id"] == data["evidence_id"]

        navigation.open_archive_management()
        archive_page = ArchivePage(driver)
        assert archive_page.search(data["business_id"]) == data["business_id"]
        archive = archive_page.detail()
        assert archive["declaration_id"] == data["declaration_id"]
        assert archive["contract_id"] == data["contract_id"]
        assert archive["order_id"] == data["order_id"]
        assert archive["payment_id"] == data["payment_id"]
        assert archive["transfer_id"] == data["transfer_id"]
        assert archive["evidence_id"] == data["evidence_id"]
