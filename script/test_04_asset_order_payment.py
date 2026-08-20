"""数据资产、交易与支付模块：WEB-044、WEB-058、WEB-061。"""

import allure
import pytest

from page.data_asset_page import DataAssetPage
from page.payment_page import PaymentPage
from page.transaction_page import TransactionPage
from tools import load_case_data, unique_name


pytestmark = [
    pytest.mark.ui,
    pytest.mark.transaction,
    pytest.mark.p0,
    pytest.mark.destructive,
]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("数据资产管理")
@allure.title("WEB-044 数据资产新增—分类分级与唯一标识")
def test_web_044_create_classified_data_asset(
    driver, login_as, user_credentials, configured_case
):
    data = configured_case(
        load_case_data("transaction_data.json", "WEB-044")[0],
        "asset_name_prefix",
        "category",
        "level",
        "source",
    ).copy()
    data["asset_name"] = unique_name(data["asset_name_prefix"])

    navigation = login_as(user_credentials)
    navigation.open_data_asset_management()
    asset_page = DataAssetPage(driver)

    with allure.step("新增带分类分级的数据资产"):
        asset_id = asset_page.create_asset(data)
        assert asset_id, "资产未生成唯一标识"

    with allure.step("查询并核对资产分类分级"):
        result = asset_page.search(asset_id)
        assert result["asset_id"] == asset_id
        assert result["category"] == data["category"]
        assert result["level"] == data["level"]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("交易管理")
@allure.title("WEB-058 交易订单创建—{case_data[scenario]}")
@pytest.mark.parametrize(
    "case_data",
    load_case_data("transaction_data.json", "WEB-058"),
    ids=lambda row: row["scenario"],
)
def test_web_058_validate_asset_contract_declaration_chain(
    driver, login_as, user_credentials, configured_case, case_data
):
    case_data = configured_case(
        case_data,
        "asset_id",
        "declaration_id",
        "contract_id",
        "quantity",
    )
    navigation = login_as(user_credentials)
    navigation.open_transaction_management()
    transaction = TransactionPage(driver)

    with allure.step("使用资产、申报和合同链路创建交易订单"):
        transaction.fill_order(case_data)
        transaction.submit_order()

    if case_data["expected_allowed"]:
        with allure.step("有效链路生成待支付订单"):
            transaction.find_visible(transaction.SUCCESS_MESSAGE)
            assert transaction.get_text(transaction.ORDER_ID)
    else:
        with allure.step("不完整或无效链路被阻断"):
            assert transaction.get_block_message(), "无效业务链未给出阻断原因"


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("支付结算")
@allure.title("WEB-061 支付发起—{case_data[scenario]}")
@pytest.mark.parametrize(
    "case_data",
    load_case_data("transaction_data.json", "WEB-061"),
    ids=lambda row: row["scenario"],
)
def test_web_061_bind_payment_voucher_to_order(
    driver, login_as, user_credentials, configured_case, case_data
):
    case_data = configured_case(
        case_data, "order_id", "amount", "payment_time", "voucher"
    )
    navigation = login_as(user_credentials)
    navigation.open_payment_management()
    payment = PaymentPage(driver)

    with allure.step("填写订单、金额、支付时间并上传凭证"):
        payment.fill_payment(case_data)
        payment.submit()

    if case_data["expected_allowed"]:
        with allure.step("匹配订单信息的支付申请被受理"):
            payment.find_visible(payment.SUCCESS_MESSAGE)
            assert payment.current_status()
    else:
        with allure.step("不匹配的订单或金额被阻断"):
            assert payment.get_block_message(), "不匹配支付未给出阻断原因"
