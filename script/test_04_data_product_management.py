"""数据产品创建、审核、上下架及交易下单主流程。"""

from datetime import date, datetime, timedelta
from pathlib import Path

import allure
import pytest

from page.data_product_page import DataProductPage
from page.data_product_audit_page import DataProductAuditPage
from page.data_marketplace_page import DataMarketplacePage
from page.product_order_page import ProductOrderPage
from page.product_order_audit_page import ProductOrderAuditPage
from page.user_portal_page import UserPortalPage
from tools import load_case_data, unique_name


pytestmark = [
    pytest.mark.ui,
    pytest.mark.transaction,
    pytest.mark.p0,
    pytest.mark.destructive,
]


def _load_order_case(case_id: str) -> dict:
    """读取订单用例；反向场景可继承已验证的 WEB-084 基础数据。"""

    data = load_case_data("order_provider_audit.json", case_id)[0].copy()
    base_case = data.pop("base_case", None)
    if not base_case:
        return data
    base = load_case_data("order_provider_audit.json", str(base_case))[0].copy()
    base.update(data)
    return base


def _open_data_product_page(driver, login_as, credentials) -> DataProductPage:
    navigation = login_as(credentials)
    navigation.ensure_operations_console()
    portal = UserPortalPage(driver)
    portal.wait_until_navigation_loaded()
    portal.open_data_product_management()
    page = DataProductPage(driver)
    page.wait_until_loaded()
    return page


def _relogin_order_page(driver, relogin_as, credentials) -> ProductOrderPage:
    navigation = relogin_as(credentials)
    navigation.ensure_operations_console()
    portal = UserPortalPage(driver)
    portal.wait_until_navigation_loaded()
    portal.open_product_order_management()
    page = ProductOrderPage(driver)
    page.wait_until_loaded()
    return page


def _place_existing_product_order(
    driver,
    login_as,
    data_consumer_credentials,
    data: dict,
) -> tuple[datetime, str]:
    """对已上架产品下单，并返回提交时间与动态产品名称。"""

    data["expected_delivery_date"] = (
        date.today() + timedelta(days=int(data["delivery_days_from_now"]))
    ).isoformat()
    navigation = login_as(data_consumer_credentials)
    navigation.ensure_operations_console()
    portal = UserPortalPage(driver)
    portal.wait_until_navigation_loaded()

    with allure.step("按产品编号唯一查询现有已上架产品并提交订单"):
        portal.open_data_marketplace()
        marketplace = DataMarketplacePage(driver)
        marketplace.wait_until_loaded()
        product_name = marketplace.search_single_product(
            data["existing_product_number"],
            data["expected_product_name_prefix"],
        )
        assert product_name.startswith(data["expected_product_name_prefix"])
        marketplace.open_unique_product_detail(
            product_name,
            data["existing_product_number"],
        )
        submitted_after = datetime.now()
        result = marketplace.submit_order(data)
        assert "订单提交成功" in result

    with allure.step("点击立即前往并确认已进入数据使用方订单管理"):
        marketplace.go_to_order_management()
        order_page = ProductOrderPage(driver)
        order_page.wait_until_loaded()
        return submitted_after, product_name


def _run_provider_order_audit(
    driver,
    login_as,
    relogin_as,
    data_consumer_credentials,
    data_provider_credentials,
    configured_case,
    case_id: str,
    *,
    verify_consumer_result: bool = True,
) -> tuple[dict, str, str]:
    required = (
        "existing_product_number",
        "expected_product_name_prefix",
        "purchase_purpose",
        "delivery_days_from_now",
        "quantity",
        "order_remark",
        "expected_initial_order_status",
        "provider_audit_result",
        "provider_audit_opinion",
        "expected_provider_order_status",
        "expected_contract_status",
        "expected_payment_status",
        "expected_delivery_status",
        "expected_acceptance_status",
    )
    data = configured_case(
        _load_order_case(case_id),
        *required,
    ).copy()
    submitted_after, product_name = _place_existing_product_order(
        driver,
        login_as,
        data_consumer_credentials,
        data,
    )

    with allure.step("订单提交成功后立即切换数据提供方并识别本次新订单"):
        navigation = relogin_as(data_provider_credentials)
        navigation.ensure_operations_console()
        provider_portal = UserPortalPage(driver)
        provider_portal.wait_until_navigation_loaded()
        provider_portal.open_product_order_management()
        order_page = ProductOrderPage(driver)
        order_page.wait_until_loaded()
        order_id = order_page.wait_for_recent_order(
            data["existing_product_number"],
            data["expected_initial_order_status"],
            submitted_after,
        )
        assert order_id.startswith("SO")

    with allure.step(f"数据提供方按动态订单编号审核：{order_id}"):
        initial_row = order_page.wait_for_order_states(
            order_id,
            [
                product_name,
                data["expected_initial_order_status"],
                data["expected_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in initial_row
        result_row = order_page.audit_order(
            order_id,
            data["provider_audit_result"],
            data["provider_audit_opinion"],
            [
                product_name,
                data["expected_provider_order_status"],
                data["expected_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert order_id in result_row

    if verify_consumer_result:
        with allure.step("切回数据使用方并按同一订单编号复核提供方审核结果"):
            navigation = relogin_as(data_consumer_credentials)
            navigation.ensure_operations_console()
            consumer_portal = UserPortalPage(driver)
            consumer_portal.wait_until_navigation_loaded()
            consumer_portal.open_product_order_management()
            consumer_order_page = ProductOrderPage(driver)
            consumer_order_page.wait_until_loaded()
            consumer_row = consumer_order_page.wait_for_order_states(
                order_id,
                [
                    product_name,
                    data["expected_provider_order_status"],
                    data["expected_contract_status"],
                    data["expected_payment_status"],
                    data["expected_delivery_status"],
                    data["expected_acceptance_status"],
                ],
            )
            assert order_id in consumer_row
            assert data["existing_product_number"] in consumer_row

    return data, order_id, product_name


def _run_operations_order_audit(
    driver,
    login_as,
    relogin_as,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
    case_id: str,
) -> tuple[dict, str, str]:
    """完成下单、提供方审核和运营方审核，并返回同一动态订单。"""

    data, order_id, product_name = _run_provider_order_audit(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        configured_case,
        case_id,
        verify_consumer_result=False,
    )
    data = configured_case(
        data,
        "operations_audit_opinion",
        "expected_operations_order_status",
    )
    operations_result = str(data.get("operations_audit_result", "PASS"))

    with allure.step(
        f"运营方按同一订单编号提交审核结果 {operations_result}：{order_id}"
    ):
        navigation = relogin_as(admin_credentials)
        navigation.ensure_operations_console()
        admin_portal = UserPortalPage(driver)
        admin_portal.wait_until_navigation_loaded()
        admin_portal.open_product_order_audit()
        audit_page = ProductOrderAuditPage(driver)
        audit_page.wait_until_loaded()
        before_audit = audit_page.wait_for_order_states(
            order_id,
            [
                product_name,
                data["expected_provider_order_status"],
                data["expected_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in before_audit
        after_audit = audit_page.review_order(
            order_id,
            operations_result,
            data["operations_audit_opinion"],
            [
                product_name,
                data["expected_operations_order_status"],
                data["expected_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert order_id in after_audit

    return data, order_id, product_name


def _run_operations_approve_and_upload_contract(
    driver,
    login_as,
    relogin_as,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
    case_id: str,
) -> tuple[dict, str, str]:
    """完成下单、两级审核及使用方上传合同，并返回同一动态订单。"""

    data, order_id, product_name = _run_operations_order_audit(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        case_id,
    )
    data = configured_case(
        data,
        "contract_file",
        "contract_remark",
        "expected_uploaded_order_status",
        "expected_uploaded_contract_status",
    )

    with allure.step("切回数据使用方确认运营方审核结果与目标订单"):
        navigation = relogin_as(data_consumer_credentials)
        navigation.ensure_operations_console()
        consumer_portal = UserPortalPage(driver)
        consumer_portal.wait_until_navigation_loaded()
        consumer_portal.open_product_order_management()
        order_page = ProductOrderPage(driver)
        order_page.wait_until_loaded()
        confirmed_row = order_page.wait_for_order_states(
            order_id,
            [
                product_name,
                data["expected_operations_order_status"],
                data["expected_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in confirmed_row

    with allure.step("数据使用方为同一订单上传模拟 Word 合同"):
        contract_path = Path(__file__).resolve().parents[1] / data["contract_file"]
        assert contract_path.is_file(), f"模拟合同不存在：{contract_path}"
        uploaded_row = order_page.upload_contract(
            order_id,
            contract_path,
            data["contract_remark"],
            [
                product_name,
                data["expected_uploaded_order_status"],
                data["expected_uploaded_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert order_id in uploaded_row
        assert data["existing_product_number"] in uploaded_row

    return data, order_id, product_name


def _run_provider_confirm_contract_and_consumer_pay(
    driver,
    login_as,
    relogin_as,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
    case_id: str,
) -> tuple[dict, str, str]:
    """完成合同确认与使用方支付，并返回待确认收款的同一订单。"""

    data, order_id, product_name = _run_operations_approve_and_upload_contract(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        case_id,
    )
    data = configured_case(
        data,
        "contract_confirmation_result",
        "contract_confirmation_opinion",
        "expected_confirmed_order_status",
        "expected_confirmed_contract_status",
        "payment_voucher_file",
        "expected_paid_order_status",
        "expected_paid_payment_status",
    )

    with allure.step(f"数据提供方按同一订单编号确认合同通过：{order_id}"):
        navigation = relogin_as(data_provider_credentials)
        navigation.ensure_operations_console()
        provider_portal = UserPortalPage(driver)
        provider_portal.wait_until_navigation_loaded()
        provider_portal.open_product_order_management()
        provider_order_page = ProductOrderPage(driver)
        provider_order_page.wait_until_loaded()
        confirmed_row = provider_order_page.confirm_contract(
            order_id,
            data["contract_confirmation_result"],
            data["contract_confirmation_opinion"],
            [
                product_name,
                data["expected_confirmed_order_status"],
                data["expected_confirmed_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in confirmed_row

    with allure.step("切回数据使用方为同一订单上传模拟支付凭证"):
        navigation = relogin_as(data_consumer_credentials)
        navigation.ensure_operations_console()
        consumer_portal = UserPortalPage(driver)
        consumer_portal.wait_until_navigation_loaded()
        consumer_portal.open_product_order_management()
        consumer_order_page = ProductOrderPage(driver)
        consumer_order_page.wait_until_loaded()
        before_payment = consumer_order_page.wait_for_order_states(
            order_id,
            [
                product_name,
                data["expected_confirmed_order_status"],
                data["expected_confirmed_contract_status"],
                data["expected_payment_status"],
            ],
        )
        assert data["existing_product_number"] in before_payment
        voucher_path = (
            Path(__file__).resolve().parents[1] / data["payment_voucher_file"]
        )
        assert voucher_path.is_file(), f"模拟支付凭证不存在：{voucher_path}"
        paid_row = consumer_order_page.pay_order(
            order_id,
            voucher_path,
            [
                product_name,
                data["expected_paid_order_status"],
                data["expected_confirmed_contract_status"],
                data["expected_paid_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert order_id in paid_row
        assert data["existing_product_number"] in paid_row

    return data, order_id, product_name


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("数据产品管理")
@allure.title("WEB-075 数据产品新增—多场景参数化保存草稿")
def test_web_075_create_multiple_product_drafts(
    driver,
    login_as,
    data_provider_credentials,
    configured_case,
):
    products = load_case_data("data_product.json", "WEB-075")
    product_page = _open_data_product_page(
        driver,
        login_as,
        data_provider_credentials,
    )

    for source in products:
        data = configured_case(
            source,
            "product_name_prefix",
            "cover_file",
            "product_intro",
            "business_scene",
            "task_type",
            "difficulty",
            "package_data_types",
            "data_format",
            "annotation_status",
            "pricing_mode",
            "currency",
            "fixed_price",
            "delivery_cycle",
            "compliance_template",
            "business_contact",
            "contact_email",
            "contact_phone",
            "expected_product_status",
            "expected_audit_status",
        ).copy()
        data["product_name"] = unique_name(data["product_name_prefix"])

        with allure.step(f"填写并保存草稿：{data['scenario']}"):
            product_page.start_new_product()
            product_page.fill_product(data)
            product_page.save_draft()

        with allure.step("按唯一产品名称查询并验证草稿状态"):
            row_text = product_page.search_product(data["product_name"])
            assert data["product_name"] in row_text
            assert data["expected_product_status"] in row_text
            assert data["expected_audit_status"] in row_text


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("数据产品管理")
@allure.title("WEB-076 数据产品新增—资料完整提交审核")
@pytest.mark.production_product_submission
def test_web_076_submit_product_for_review(
    driver,
    login_as,
    data_provider_credentials,
    configured_case,
):
    data = configured_case(
        load_case_data("data_product.json", "WEB-076")[0],
        "product_name_prefix",
        "cover_file",
        "product_intro",
        "business_scene",
        "task_type",
        "difficulty",
        "package_data_types",
        "data_format",
        "annotation_status",
        "pricing_mode",
        "currency",
        "fixed_price",
        "delivery_cycle",
        "compliance_template",
        "business_contact",
        "contact_email",
        "contact_phone",
        "expected_product_status",
        "expected_audit_status",
    ).copy()
    data["product_name"] = unique_name(data["product_name_prefix"])
    product_page = _open_data_product_page(
        driver,
        login_as,
        data_provider_credentials,
    )

    with allure.step("填写完整数据产品资料并提交审核"):
        product_page.start_new_product()
        product_page.fill_product(data)
        product_page.submit_for_review()

    with allure.step("按唯一产品名称查询并验证已进入审核流程"):
        row_text = product_page.search_product(data["product_name"])
        assert data["product_name"] in row_text
        assert data["expected_product_status"] in row_text
        assert data["expected_audit_status"] in row_text


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("数据产品审核")
@allure.title("WEB-077 数据产品—提供方提交与管理员审核通过闭环")
@pytest.mark.production_product_submission
@pytest.mark.production_product_approval
def test_web_077_provider_submit_and_admin_approve_product(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    required = (
        "product_name_prefix",
        "cover_file",
        "product_intro",
        "business_scene",
        "task_type",
        "difficulty",
        "package_data_types",
        "data_format",
        "annotation_status",
        "pricing_mode",
        "currency",
        "fixed_price",
        "delivery_cycle",
        "compliance_template",
        "business_contact",
        "contact_email",
        "contact_phone",
        "admin_audit_result",
        "admin_audit_opinion",
        "expected_submitted_product_status",
        "expected_submitted_audit_status",
        "expected_approved_product_status",
        "expected_approved_audit_status",
    )
    data = configured_case(
        load_case_data("data_product.json", "WEB-077")[0],
        *required,
    ).copy()
    data["product_name"] = unique_name(data["product_name_prefix"])

    with allure.step("数据提供方新增产品并提交审核"):
        product_page = _open_data_product_page(
            driver,
            login_as,
            data_provider_credentials,
        )
        product_page.start_new_product()
        product_page.fill_product(data)
        product_page.submit_for_review()
        submitted_row = product_page.search_product(data["product_name"])
        assert data["expected_submitted_product_status"] in submitted_row
        assert data["expected_submitted_audit_status"] in submitted_row

    with allure.step("清理提供方会话并以超级管理员重新登录"):
        navigation = relogin_as(admin_credentials)
        navigation.ensure_operations_console()
        admin_portal = UserPortalPage(driver)
        admin_portal.wait_until_navigation_loaded()
        admin_portal.open_data_product_audit()

    with allure.step("管理员按唯一产品名称审核通过"):
        audit_page = DataProductAuditPage(driver)
        audit_page.wait_until_loaded()
        assert data["admin_audit_result"] == "通过", "WEB-077 仅执行审核通过主流程"
        audit_page.approve(
            data["product_name"],
            data["admin_audit_opinion"],
        )
        assert audit_page.wait_until_audit_record_available(data["product_name"]), (
            "管理员提交后未出现审核记录入口"
        )

    with allure.step("再次切换为数据提供方并复核审核结果"):
        navigation = relogin_as(data_provider_credentials)
        navigation.ensure_operations_console()
        provider_portal = UserPortalPage(driver)
        provider_portal.wait_until_navigation_loaded()
        provider_portal.open_data_product_management()
        product_page = DataProductPage(driver)
        product_page.wait_until_loaded()
        approved_row = product_page.search_product(data["product_name"])
        assert data["expected_approved_product_status"] in approved_row
        assert data["expected_approved_audit_status"] in approved_row


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("数据产品生命周期")
@allure.title("WEB-078 数据产品—上架、下架、变更及二次审核闭环")
@pytest.mark.production_product_submission
@pytest.mark.production_product_approval
@pytest.mark.production_product_lifecycle
@pytest.mark.e2e
def test_web_078_product_on_off_shelf_and_submit_change_review(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    required = (
        "product_name_prefix",
        "cover_file",
        "product_intro",
        "business_scene",
        "task_type",
        "difficulty",
        "package_data_types",
        "data_format",
        "annotation_status",
        "pricing_mode",
        "currency",
        "fixed_price",
        "delivery_cycle",
        "compliance_template",
        "business_contact",
        "contact_email",
        "contact_phone",
        "admin_audit_result",
        "admin_audit_opinion",
        "admin_change_audit_opinion",
        "changed_product_intro",
        "expected_approved_product_status",
        "expected_approved_audit_status",
        "expected_on_shelf_status",
        "expected_off_shelf_status",
        "expected_changed_product_status",
        "expected_changed_audit_status",
        "expected_change_approved_product_status",
        "expected_change_approved_audit_status",
    )
    data = configured_case(
        load_case_data("data_product.json", "WEB-078")[0],
        *required,
    ).copy()
    data["product_name"] = unique_name(data["product_name_prefix"])
    changed_intro = f"{data['changed_product_intro']} 产品：{data['product_name']}"

    with allure.step("数据提供方创建唯一产品并提交首次审核"):
        product_page = _open_data_product_page(
            driver,
            login_as,
            data_provider_credentials,
        )
        product_page.start_new_product()
        product_page.fill_product(data)
        product_page.submit_for_review()

    with allure.step("超级管理员按唯一产品名称完成首次审核通过"):
        navigation = relogin_as(admin_credentials)
        navigation.ensure_operations_console()
        admin_portal = UserPortalPage(driver)
        admin_portal.wait_until_navigation_loaded()
        admin_portal.open_data_product_audit()
        audit_page = DataProductAuditPage(driver)
        audit_page.wait_until_loaded()
        assert data["admin_audit_result"] == "通过", "WEB-078 仅执行审核通过主流程"
        audit_page.approve(
            data["product_name"],
            data["admin_audit_opinion"],
        )

    with allure.step("切回数据提供方并验证产品处于待上架状态"):
        navigation = relogin_as(data_provider_credentials)
        navigation.ensure_operations_console()
        provider_portal = UserPortalPage(driver)
        provider_portal.wait_until_navigation_loaded()
        provider_portal.open_data_product_management()
        product_page = DataProductPage(driver)
        product_page.wait_until_loaded()
        approved_row = product_page.wait_for_product_states(
            data["product_name"],
            data["expected_approved_product_status"],
            data["expected_approved_audit_status"],
        )
        assert data["product_name"] in approved_row

    with allure.step("上架唯一目标产品并验证已上架"):
        on_shelf_row = product_page.put_on_shelf(data["product_name"])
        assert data["expected_on_shelf_status"] in on_shelf_row

    with allure.step("下架同一产品并验证已下架"):
        off_shelf_row = product_page.take_off_shelf(data["product_name"])
        assert data["expected_off_shelf_status"] in off_shelf_row

    with allure.step("变更已下架产品简介并提交变更审核"):
        product_page.change_and_submit_for_review(
            data["product_name"],
            changed_intro,
        )
        changed_row = product_page.wait_for_product_states(
            data["product_name"],
            data["expected_changed_product_status"],
            data["expected_changed_audit_status"],
        )
        assert data["product_name"] in changed_row

    with allure.step("再次切换超级管理员并审核通过产品变更"):
        navigation = relogin_as(admin_credentials)
        navigation.ensure_operations_console()
        admin_portal = UserPortalPage(driver)
        admin_portal.wait_until_navigation_loaded()
        admin_portal.open_data_product_audit()
        audit_page = DataProductAuditPage(driver)
        audit_page.wait_until_loaded()
        audit_page.approve(
            data["product_name"],
            data["admin_change_audit_opinion"],
        )
        assert audit_page.wait_until_audit_record_available(data["product_name"]), (
            "管理员提交变更审核结果后未出现审核记录入口"
        )

    with allure.step("切回数据提供方并复核变更审核通过状态"):
        navigation = relogin_as(data_provider_credentials)
        navigation.ensure_operations_console()
        provider_portal = UserPortalPage(driver)
        provider_portal.wait_until_navigation_loaded()
        provider_portal.open_data_product_management()
        product_page = DataProductPage(driver)
        product_page.wait_until_loaded()
        final_row = product_page.wait_for_product_states(
            data["product_name"],
            data["expected_change_approved_product_status"],
            data["expected_change_approved_audit_status"],
        )
        assert data["product_name"] in final_row


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("数据交易市场")
@allure.title("WEB-079 数据使用方—搜索已上架产品并提交采购订单")
@pytest.mark.production_product_submission
@pytest.mark.production_product_approval
@pytest.mark.production_product_lifecycle
@pytest.mark.production_product_order
@pytest.mark.e2e
def test_web_079_consumer_order_unique_listed_product(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_provider_credentials,
    data_consumer_credentials,
    admin_credentials,
    configured_case,
):
    required = (
        "product_name_prefix",
        "cover_file",
        "product_intro",
        "business_scene",
        "task_type",
        "difficulty",
        "package_data_types",
        "data_format",
        "annotation_status",
        "pricing_mode",
        "currency",
        "fixed_price",
        "delivery_cycle",
        "compliance_template",
        "business_contact",
        "contact_email",
        "contact_phone",
        "admin_audit_opinion",
        "purchase_purpose",
        "delivery_days_from_now",
        "quantity",
        "order_remark",
        "expected_market_data_format",
        "expected_market_price",
    )
    data = configured_case(
        load_case_data("product_order.json", "WEB-079")[0],
        *required,
    ).copy()
    data["product_name"] = unique_name(data["product_name_prefix"])
    data["expected_delivery_date"] = (
        date.today() + timedelta(days=int(data["delivery_days_from_now"]))
    ).isoformat()
    with allure.step("数据提供方创建唯一产品并提交审核"):
        product_page = _open_data_product_page(
            driver,
            login_as,
            data_provider_credentials,
        )
        product_page.start_new_product()
        product_page.fill_product(data)
        product_page.submit_for_review()

    with allure.step("管理员按唯一产品名称审核通过"):
        navigation = relogin_as(admin_credentials)
        navigation.ensure_operations_console()
        admin_portal = UserPortalPage(driver)
        admin_portal.wait_until_navigation_loaded()
        admin_portal.open_data_product_audit()
        audit_page = DataProductAuditPage(driver)
        audit_page.wait_until_loaded()
        audit_page.approve(data["product_name"], data["admin_audit_opinion"])

    with allure.step("数据提供方将审核通过的唯一产品上架"):
        navigation = relogin_as(data_provider_credentials)
        navigation.ensure_operations_console()
        provider_portal = UserPortalPage(driver)
        provider_portal.wait_until_navigation_loaded()
        provider_portal.open_data_product_management()
        product_page = DataProductPage(driver)
        product_page.wait_until_loaded()
        product_page.put_on_shelf(data["product_name"])

    with allure.step("数据使用方在交易市场精确搜索唯一产品"):
        navigation = relogin_as(data_consumer_credentials)
        navigation.ensure_operations_console()
        consumer_portal = UserPortalPage(driver)
        consumer_portal.wait_until_navigation_loaded()
        consumer_portal.open_data_marketplace()
        marketplace = DataMarketplacePage(driver)
        marketplace.wait_until_loaded()
        card_text = marketplace.search_unique_product(data["product_name"])
        assert data["product_name"] in card_text
        assert data["expected_market_data_format"] in card_text
        assert data["expected_market_price"] in card_text

    with allure.step("打开产品详情并核对目标产品"):
        marketplace.open_unique_product_detail(data["product_name"])

    with allure.step("填写必填采购信息并提交订单"):
        result = marketplace.submit_order(data)
        assert result, "订单提交后未取得成功结果"


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-080 现有产品下单—数据提供方审核通过")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.e2e
def test_web_080_provider_approve_existing_product_order(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    configured_case,
):
    _run_provider_order_audit(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        configured_case,
        "WEB-080",
    )


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-081 现有产品下单—数据提供方审核不通过")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.e2e
def test_web_081_provider_reject_existing_product_order(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    configured_case,
):
    _run_provider_order_audit(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        configured_case,
        "WEB-081",
    )


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-082 订单运营方审核通过—数据使用方上传合同")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.production_order_operations_audit
@pytest.mark.production_order_contract_upload
@pytest.mark.e2e
def test_web_082_operations_approve_and_consumer_upload_contract(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    _run_operations_approve_and_upload_contract(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        "WEB-082",
    )

@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-083 提供方确认合同—数据使用方上传支付凭证")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.production_order_operations_audit
@pytest.mark.production_order_contract_upload
@pytest.mark.production_order_contract_confirmation
@pytest.mark.production_order_payment
@pytest.mark.e2e
def test_web_083_provider_confirm_contract_and_consumer_pay(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    _run_provider_confirm_contract_and_consumer_pay(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        "WEB-083",
    )


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-084 提供方确认收款并交付—数据使用方验收及详情核对")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.production_order_operations_audit
@pytest.mark.production_order_contract_upload
@pytest.mark.production_order_contract_confirmation
@pytest.mark.production_order_payment
@pytest.mark.production_order_receipt_confirmation
@pytest.mark.production_order_delivery
@pytest.mark.production_order_acceptance
@pytest.mark.e2e
def test_web_084_provider_deliver_and_consumer_accept_order(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    data, order_id, product_name = _run_provider_confirm_contract_and_consumer_pay(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        "WEB-084",
    )
    data = configured_case(
        data,
        "receipt_confirmation_result",
        "receipt_confirmation_note",
        "expected_received_order_status",
        "expected_received_payment_status",
        "expected_received_delivery_status",
        "delivery_method",
        "delivery_resource_name",
        "expected_delivered_order_status",
        "expected_delivered_delivery_status",
        "expected_delivered_acceptance_status",
        "acceptance_result",
        "acceptance_opinion",
        "expected_completed_order_status",
        "expected_completed_acceptance_status",
    )

    with allure.step(f"数据提供方确认收款到账并交付同一订单：{order_id}"):
        navigation = relogin_as(data_provider_credentials)
        navigation.ensure_operations_console()
        provider_portal = UserPortalPage(driver)
        provider_portal.wait_until_navigation_loaded()
        provider_portal.open_product_order_management()
        provider_order_page = ProductOrderPage(driver)
        provider_order_page.wait_until_loaded()
        received_row = provider_order_page.confirm_receipt(
            order_id,
            data["receipt_confirmation_result"],
            data["receipt_confirmation_note"],
            [
                product_name,
                data["expected_received_order_status"],
                data["expected_confirmed_contract_status"],
                data["expected_received_payment_status"],
                data["expected_received_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in received_row
        delivered_row = provider_order_page.deliver_order(
            order_id,
            data["delivery_method"],
            data["delivery_resource_name"],
            [
                product_name,
                data["expected_delivered_order_status"],
                data["expected_confirmed_contract_status"],
                data["expected_received_payment_status"],
                data["expected_delivered_delivery_status"],
                data["expected_delivered_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in delivered_row

    with allure.step("切回数据使用方验收交付批次并核对订单详情"):
        navigation = relogin_as(data_consumer_credentials)
        navigation.ensure_operations_console()
        consumer_portal = UserPortalPage(driver)
        consumer_portal.wait_until_navigation_loaded()
        consumer_portal.open_product_order_management()
        consumer_order_page = ProductOrderPage(driver)
        consumer_order_page.wait_until_loaded()
        accepted_row = consumer_order_page.accept_order(
            order_id,
            data["acceptance_result"],
            data["acceptance_opinion"],
            [
                product_name,
                data["expected_completed_order_status"],
                data["expected_confirmed_contract_status"],
                data["expected_received_payment_status"],
                data["expected_delivered_delivery_status"],
                data["expected_completed_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in accepted_row
        detail_text = consumer_order_page.view_order_details(
            order_id,
            [
                product_name,
                data["existing_product_number"],
                data["expected_completed_order_status"],
                data["expected_confirmed_contract_status"],
                data["expected_received_payment_status"],
                data["expected_delivered_delivery_status"],
                data["expected_completed_acceptance_status"],
            ],
        )
        assert order_id in detail_text


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-085 产品订单—运营方审核不通过")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.production_order_operations_audit
@pytest.mark.e2e
def test_web_085_operations_reject_product_order(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    data, order_id, product_name = _run_operations_order_audit(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        "WEB-085",
    )

    for role_name, credentials in (
        ("数据使用方", data_consumer_credentials),
        ("数据提供方", data_provider_credentials),
    ):
        with allure.step(f"{role_name}复核运营方审核不通过及后续阻断"):
            order_page = _relogin_order_page(driver, relogin_as, credentials)
            row = order_page.wait_for_order_states(
                order_id,
                [
                    product_name,
                    data["expected_operations_order_status"],
                    data["expected_contract_status"],
                    data["expected_payment_status"],
                    data["expected_delivery_status"],
                    data["expected_acceptance_status"],
                ],
            )
            assert data["existing_product_number"] in row
            for action in (
                "上传合同",
                "确认合同",
                "去支付",
                "确认收款",
                "去交付",
                "确认验收",
            ):
                assert not order_page.has_row_action(order_id, action)


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-087 产品订单—合同驳回、重传及再次确认")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.production_order_operations_audit
@pytest.mark.production_order_contract_upload
@pytest.mark.production_order_contract_confirmation
@pytest.mark.e2e
def test_web_087_contract_reject_reupload_and_confirm(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    data, order_id, product_name = _run_operations_approve_and_upload_contract(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        "WEB-087",
    )
    data = configured_case(
        data,
        "contract_confirmation_result",
        "contract_confirmation_opinion",
        "expected_rejected_order_status",
        "expected_rejected_contract_status",
        "reuploaded_contract_remark",
        "final_contract_confirmation_result",
        "final_contract_confirmation_opinion",
    )

    with allure.step("提供方驳回合同并核对真实回退状态"):
        provider_page = _relogin_order_page(
            driver,
            relogin_as,
            data_provider_credentials,
        )
        rejected_row = provider_page.confirm_contract(
            order_id,
            data["contract_confirmation_result"],
            data["contract_confirmation_opinion"],
            [
                product_name,
                data["expected_rejected_order_status"],
                data["expected_rejected_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in rejected_row

    with allure.step("使用方从原上传合同入口重新上传补正合同"):
        consumer_page = _relogin_order_page(
            driver,
            relogin_as,
            data_consumer_credentials,
        )
        assert consumer_page.has_row_action(order_id, "上传合同")
        contract_path = Path(__file__).resolve().parents[1] / data["contract_file"]
        reuploaded_row = consumer_page.upload_contract(
            order_id,
            contract_path,
            data["reuploaded_contract_remark"],
            [
                product_name,
                data["expected_uploaded_order_status"],
                data["expected_uploaded_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in reuploaded_row

    with allure.step("提供方再次确认补正合同通过"):
        provider_page = _relogin_order_page(
            driver,
            relogin_as,
            data_provider_credentials,
        )
        confirmed_row = provider_page.confirm_contract(
            order_id,
            data["final_contract_confirmation_result"],
            data["final_contract_confirmation_opinion"],
            [
                product_name,
                data["expected_confirmed_order_status"],
                data["expected_confirmed_contract_status"],
                data["expected_payment_status"],
                data["expected_delivery_status"],
                data["expected_acceptance_status"],
            ],
        )
        assert data["existing_product_number"] in confirmed_row


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-089 产品订单—确认未到账并回退待支付")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.production_order_operations_audit
@pytest.mark.production_order_contract_upload
@pytest.mark.production_order_contract_confirmation
@pytest.mark.production_order_payment
@pytest.mark.production_order_receipt_confirmation
@pytest.mark.e2e
def test_web_089_receipt_not_received_rolls_back_to_payment(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    data, order_id, product_name = _run_provider_confirm_contract_and_consumer_pay(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        "WEB-089",
    )
    data = configured_case(
        data,
        "receipt_confirmation_result",
        "receipt_confirmation_note",
        "expected_unreceived_order_status",
        "expected_unreceived_payment_status",
        "expected_unreceived_delivery_status",
    )
    provider_page = _relogin_order_page(
        driver,
        relogin_as,
        data_provider_credentials,
    )
    rollback_row = provider_page.confirm_receipt(
        order_id,
        data["receipt_confirmation_result"],
        data["receipt_confirmation_note"],
        [
            product_name,
            data["expected_unreceived_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_unreceived_payment_status"],
            data["expected_unreceived_delivery_status"],
            data["expected_acceptance_status"],
        ],
    )
    assert data["existing_product_number"] in rollback_row
    assert not provider_page.has_row_action(order_id, "去交付")

    consumer_page = _relogin_order_page(
        driver,
        relogin_as,
        data_consumer_credentials,
    )
    consumer_row = consumer_page.wait_for_order_states(
        order_id,
        [
            product_name,
            data["expected_unreceived_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_unreceived_payment_status"],
            data["expected_unreceived_delivery_status"],
            data["expected_acceptance_status"],
        ],
    )
    assert data["existing_product_number"] in consumer_row
    assert consumer_page.has_row_action(order_id, "去支付")


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-090 产品订单—交付必填校验与取消")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.production_order_operations_audit
@pytest.mark.production_order_contract_upload
@pytest.mark.production_order_contract_confirmation
@pytest.mark.production_order_payment
@pytest.mark.production_order_receipt_confirmation
@pytest.mark.e2e
def test_web_090_delivery_required_fields_validation(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    data, order_id, product_name = _run_provider_confirm_contract_and_consumer_pay(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        "WEB-090",
    )
    provider_page = _relogin_order_page(
        driver,
        relogin_as,
        data_provider_credentials,
    )
    provider_page.confirm_receipt(
        order_id,
        data["receipt_confirmation_result"],
        data["receipt_confirmation_note"],
        [
            product_name,
            data["expected_received_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_received_payment_status"],
            data["expected_received_delivery_status"],
            data["expected_acceptance_status"],
        ],
    )
    row = provider_page.validate_delivery_required_fields(
        order_id,
        [
            product_name,
            data["expected_received_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_received_payment_status"],
            data["expected_received_delivery_status"],
            data["expected_acceptance_status"],
        ],
    )
    assert data["existing_product_number"] in row


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("产品订单管理")
@allure.title("WEB-091 产品订单—分批交付、验收驳回及重新交付闭环")
@pytest.mark.production_product_order
@pytest.mark.production_order_provider_audit
@pytest.mark.production_order_operations_audit
@pytest.mark.production_order_contract_upload
@pytest.mark.production_order_contract_confirmation
@pytest.mark.production_order_payment
@pytest.mark.production_order_receipt_confirmation
@pytest.mark.production_order_delivery
@pytest.mark.production_order_acceptance
@pytest.mark.e2e
def test_web_091_batch_delivery_reject_and_redeliver(
    driver,
    login_as,
    relogin_as,
    visible_browser_required,
    data_consumer_credentials,
    data_provider_credentials,
    admin_credentials,
    configured_case,
):
    data, order_id, product_name = _run_provider_confirm_contract_and_consumer_pay(
        driver,
        login_as,
        relogin_as,
        data_consumer_credentials,
        data_provider_credentials,
        admin_credentials,
        configured_case,
        "WEB-091",
    )
    data = configured_case(
        data,
        "batch_delivery_resources",
        "expected_partial_delivery_order_status",
        "rejected_acceptance_result",
        "rejected_acceptance_opinion",
        "expected_rejected_order_status",
        "expected_redelivered_order_status",
        "final_acceptance_result",
        "final_acceptance_opinion",
    )
    resources = list(data["batch_delivery_resources"])
    assert len(resources) == 2, "WEB-091 必须配置两个分批交付资源"

    provider_page = _relogin_order_page(
        driver,
        relogin_as,
        data_provider_credentials,
    )
    provider_page.confirm_receipt(
        order_id,
        data["receipt_confirmation_result"],
        data["receipt_confirmation_note"],
        [
            product_name,
            data["expected_received_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_received_payment_status"],
            data["expected_received_delivery_status"],
            data["expected_acceptance_status"],
        ],
    )
    provider_page.deliver_order(
        order_id,
        data["delivery_method"],
        resources[0],
        [
            product_name,
            data["expected_partial_delivery_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_received_payment_status"],
        ],
        is_last_batch=False,
    )
    provider_page.deliver_order(
        order_id,
        data["delivery_method"],
        resources[1],
        [
            product_name,
            data["expected_delivered_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_received_payment_status"],
            data["expected_delivered_acceptance_status"],
        ],
        is_last_batch=True,
    )

    consumer_page = _relogin_order_page(
        driver,
        relogin_as,
        data_consumer_credentials,
    )
    rejected_row = consumer_page.accept_pending_batches(
        order_id,
        data["rejected_acceptance_result"],
        data["rejected_acceptance_opinion"],
        [
            product_name,
            data["expected_rejected_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_received_payment_status"],
        ],
    )
    assert data["existing_product_number"] in rejected_row

    provider_page = _relogin_order_page(
        driver,
        relogin_as,
        data_provider_credentials,
    )
    assert provider_page.has_row_action(order_id, "重新交付")
    redelivered_row = provider_page.redeliver_rejected_batches(
        order_id,
        resources,
        [
            product_name,
            data["expected_redelivered_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_received_payment_status"],
        ],
    )
    assert data["existing_product_number"] in redelivered_row

    consumer_page = _relogin_order_page(
        driver,
        relogin_as,
        data_consumer_credentials,
    )
    completed_row = consumer_page.accept_pending_batches(
        order_id,
        data["final_acceptance_result"],
        data["final_acceptance_opinion"],
        [
            product_name,
            data["expected_completed_order_status"],
            data["expected_confirmed_contract_status"],
            data["expected_received_payment_status"],
            data["expected_delivered_delivery_status"],
            data["expected_completed_acceptance_status"],
        ],
    )
    assert data["existing_product_number"] in completed_row
