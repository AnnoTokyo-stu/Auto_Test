"""Pytest 命令行参数、fixture 与失败取证。"""

from __future__ import annotations

import re
import os
from time import perf_counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import allure
import pytest

from base.exceptions import TestDataNotConfiguredError
from config import SCREENSHOT_DIR, SETTINGS, SUPPORTED_BROWSERS
from page.login_page import LoginPage
from page.navigation_component import NavigationComponent
from tools import DriverFactory, LogFactory, ensure_runtime_directories, require_env, require_value


@dataclass(frozen=True)
class Credentials:
    username: str = field(repr=False)
    password: str = field(repr=False)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("web-ui", "Web UI 自动化参数")
    group.addoption(
        "--run-ui",
        action="store_true",
        default=False,
        help="启用真实浏览器 UI 测试；默认只收集并跳过 UI 用例",
    )
    group.addoption(
        "--run-destructive",
        action="store_true",
        default=False,
        help="允许执行会新增或修改环境数据的用例",
    )
    group.addoption(
        "--confirm-production-registration",
        action="store_true",
        default=False,
        help="明确确认允许在生产环境创建真实注册账号",
    )
    group.addoption(
        "--confirm-production-product-submission",
        action="store_true",
        default=False,
        help="明确确认允许在生产环境提交数据产品审核",
    )
    group.addoption(
        "--confirm-production-product-approval",
        action="store_true",
        default=False,
        help="明确确认允许管理员在生产环境提交数据产品审核结果",
    )
    group.addoption(
        "--confirm-production-product-lifecycle",
        action="store_true",
        default=False,
        help="明确确认允许在生产环境上架、下架并提交产品变更审核",
    )
    group.addoption(
        "--confirm-production-product-order",
        action="store_true",
        default=False,
        help="明确确认允许数据使用方在生产环境提交产品采购订单",
    )
    group.addoption(
        "--confirm-production-order-provider-audit",
        action="store_true",
        default=False,
        help="明确确认允许数据提供方在生产环境提交产品订单审核结果",
    )
    group.addoption(
        "--confirm-production-order-operations-audit",
        action="store_true",
        default=False,
        help="明确确认允许运营方在生产环境提交产品订单审核结果",
    )
    group.addoption(
        "--confirm-production-order-contract-upload",
        action="store_true",
        default=False,
        help="明确确认允许数据使用方在生产环境上传产品订单合同",
    )
    group.addoption(
        "--confirm-production-order-contract-confirmation",
        action="store_true",
        default=False,
        help="明确确认允许数据提供方在生产环境提交合同确认结果",
    )
    group.addoption(
        "--confirm-production-order-payment",
        action="store_true",
        default=False,
        help="明确确认允许数据使用方在生产环境上传支付凭证并提交支付",
    )
    group.addoption(
        "--confirm-production-order-receipt-confirmation",
        action="store_true",
        default=False,
        help="明确确认允许数据提供方在生产环境提交收款确认结果",
    )
    group.addoption(
        "--confirm-production-order-delivery",
        action="store_true",
        default=False,
        help="明确确认允许数据提供方在生产环境提交产品订单交付",
    )
    group.addoption(
        "--confirm-production-order-acceptance",
        action="store_true",
        default=False,
        help="明确确认允许数据使用方在生产环境提交订单验收结果",
    )
    group.addoption(
        "--browser",
        action="store",
        choices=SUPPORTED_BROWSERS,
        default=SETTINGS.browser,
        help="浏览器类型，默认 chrome",
    )
    group.addoption(
        "--headless",
        action="store_true",
        default=SETTINGS.headless,
        help="使用无头模式运行浏览器",
    )
    group.addoption(
        "--driver-path",
        action="store",
        default=SETTINGS.driver_path,
        help="可选的浏览器驱动路径；未设置时使用 Selenium Manager",
    )


def pytest_configure() -> None:
    ensure_runtime_directories()


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    run_ui = config.getoption("--run-ui")
    run_destructive = config.getoption("--run-destructive")
    confirm_production_registration = config.getoption(
        "--confirm-production-registration"
    )
    confirm_production_product_submission = config.getoption(
        "--confirm-production-product-submission"
    )
    confirm_production_product_approval = config.getoption(
        "--confirm-production-product-approval"
    )
    confirm_production_product_lifecycle = config.getoption(
        "--confirm-production-product-lifecycle"
    )
    confirm_production_product_order = config.getoption(
        "--confirm-production-product-order"
    )
    confirm_production_order_provider_audit = config.getoption(
        "--confirm-production-order-provider-audit"
    )
    confirm_production_order_operations_audit = config.getoption(
        "--confirm-production-order-operations-audit"
    )
    confirm_production_order_contract_upload = config.getoption(
        "--confirm-production-order-contract-upload"
    )
    confirm_production_order_contract_confirmation = config.getoption(
        "--confirm-production-order-contract-confirmation"
    )
    confirm_production_order_payment = config.getoption(
        "--confirm-production-order-payment"
    )
    confirm_production_order_receipt_confirmation = config.getoption(
        "--confirm-production-order-receipt-confirmation"
    )
    confirm_production_order_delivery = config.getoption(
        "--confirm-production-order-delivery"
    )
    confirm_production_order_acceptance = config.getoption(
        "--confirm-production-order-acceptance"
    )
    ui_skip = pytest.mark.skip(reason="真实 UI 默认关闭；使用 --run-ui 启用")
    destructive_skip = pytest.mark.skip(
        reason="该用例会新增或修改测试数据；使用 --run-destructive 明确启用"
    )
    production_registration_skip = pytest.mark.skip(
        reason=(
            "该用例会在生产环境创建真实账号；"
            "使用 --confirm-production-registration 明确确认"
        )
    )
    production_product_submission_skip = pytest.mark.skip(
        reason=(
            "该用例会在生产环境提交真实产品审核；"
            "使用 --confirm-production-product-submission 明确确认"
        )
    )
    production_product_approval_skip = pytest.mark.skip(
        reason=(
            "该用例会由管理员在生产环境提交数据产品审核结果；"
            "使用 --confirm-production-product-approval 明确确认"
        )
    )
    production_product_lifecycle_skip = pytest.mark.skip(
        reason=(
            "该用例会在生产环境上架、下架并提交产品变更审核；"
            "使用 --confirm-production-product-lifecycle 明确确认"
        )
    )
    production_product_order_skip = pytest.mark.skip(
        reason=(
            "该用例会由数据使用方在生产环境创建产品采购订单；"
            "使用 --confirm-production-product-order 明确确认"
        )
    )
    production_order_provider_audit_skip = pytest.mark.skip(
        reason=(
            "该用例会由数据提供方在生产环境提交产品订单审核结果；"
            "使用 --confirm-production-order-provider-audit 明确确认"
        )
    )
    production_order_operations_audit_skip = pytest.mark.skip(
        reason=(
            "该用例会由运营方在生产环境提交产品订单审核结果；"
            "使用 --confirm-production-order-operations-audit 明确确认"
        )
    )
    production_order_contract_upload_skip = pytest.mark.skip(
        reason=(
            "该用例会由数据使用方在生产环境上传产品订单合同；"
            "使用 --confirm-production-order-contract-upload 明确确认"
        )
    )
    production_order_contract_confirmation_skip = pytest.mark.skip(
        reason=(
            "该用例会由数据提供方在生产环境提交合同确认结果；"
            "使用 --confirm-production-order-contract-confirmation 明确确认"
        )
    )
    production_order_payment_skip = pytest.mark.skip(
        reason=(
            "该用例会由数据使用方在生产环境上传支付凭证并提交支付；"
            "使用 --confirm-production-order-payment 明确确认"
        )
    )
    production_order_receipt_confirmation_skip = pytest.mark.skip(
        reason=(
            "该用例会由数据提供方在生产环境提交收款确认结果；"
            "使用 --confirm-production-order-receipt-confirmation 明确确认"
        )
    )
    production_order_delivery_skip = pytest.mark.skip(
        reason=(
            "该用例会由数据提供方在生产环境提交订单交付；"
            "使用 --confirm-production-order-delivery 明确确认"
        )
    )
    production_order_acceptance_skip = pytest.mark.skip(
        reason=(
            "该用例会由数据使用方在生产环境提交验收结果；"
            "使用 --confirm-production-order-acceptance 明确确认"
        )
    )

    for item in items:
        if "ui" in item.keywords and not run_ui:
            item.add_marker(ui_skip)
        if "destructive" in item.keywords and not run_destructive:
            item.add_marker(destructive_skip)
        if (
            "production_registration" in item.keywords
            and not confirm_production_registration
        ):
            item.add_marker(production_registration_skip)
        if (
            "production_product_submission" in item.keywords
            and not confirm_production_product_submission
        ):
            item.add_marker(production_product_submission_skip)
        if (
            "production_product_approval" in item.keywords
            and not confirm_production_product_approval
        ):
            item.add_marker(production_product_approval_skip)
        if (
            "production_product_lifecycle" in item.keywords
            and not confirm_production_product_lifecycle
        ):
            item.add_marker(production_product_lifecycle_skip)
        if (
            "production_product_order" in item.keywords
            and not confirm_production_product_order
        ):
            item.add_marker(production_product_order_skip)
        if (
            "production_order_provider_audit" in item.keywords
            and not confirm_production_order_provider_audit
        ):
            item.add_marker(production_order_provider_audit_skip)
        if (
            "production_order_operations_audit" in item.keywords
            and not confirm_production_order_operations_audit
        ):
            item.add_marker(production_order_operations_audit_skip)
        if (
            "production_order_contract_upload" in item.keywords
            and not confirm_production_order_contract_upload
        ):
            item.add_marker(production_order_contract_upload_skip)
        if (
            "production_order_contract_confirmation" in item.keywords
            and not confirm_production_order_contract_confirmation
        ):
            item.add_marker(production_order_contract_confirmation_skip)
        if (
            "production_order_payment" in item.keywords
            and not confirm_production_order_payment
        ):
            item.add_marker(production_order_payment_skip)
        if (
            "production_order_receipt_confirmation" in item.keywords
            and not confirm_production_order_receipt_confirmation
        ):
            item.add_marker(production_order_receipt_confirmation_skip)
        if (
            "production_order_delivery" in item.keywords
            and not confirm_production_order_delivery
        ):
            item.add_marker(production_order_delivery_skip)
        if (
            "production_order_acceptance" in item.keywords
            and not confirm_production_order_acceptance
        ):
            item.add_marker(production_order_acceptance_skip)


@pytest.fixture
def driver(request: pytest.FixtureRequest):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    driver_path = request.config.getoption("--driver-path")
    log = LogFactory.get_logger()
    log.info("创建浏览器：browser=%s, headless=%s", browser, headless)
    started_at = perf_counter()
    web_driver = DriverFactory.create(
        browser,
        headless=headless,
        driver_path=driver_path,
    )
    log.info("浏览器创建完成，耗时 %.2f 秒", perf_counter() - started_at)
    web_driver.set_page_load_timeout(SETTINGS.page_load_timeout)
    if not headless:
        web_driver.maximize_window()
    yield web_driver
    log.info("退出浏览器：%s", browser)
    web_driver.quit()


def _credentials(username_env: str, password_env: str) -> Credentials:
    try:
        return Credentials(
            username=require_env(username_env),
            password=require_env(password_env),
        )
    except TestDataNotConfiguredError as error:
        pytest.skip(str(error))


@pytest.fixture
def user_credentials() -> Credentials:
    return _credentials("TEST_USER_NAME", "TEST_USER_PASSWORD")


@pytest.fixture
def user_display_name() -> str:
    try:
        return require_env("TEST_USER_DISPLAY_NAME")
    except TestDataNotConfiguredError as error:
        pytest.skip(str(error))


@pytest.fixture
def admin_credentials() -> Credentials:
    return _credentials("TEST_ADMIN_NAME", "TEST_ADMIN_PASSWORD")


@pytest.fixture
def rbac_user_credentials() -> Credentials:
    return _credentials("TEST_RBAC_USER_NAME", "TEST_RBAC_USER_PASSWORD")


@pytest.fixture
def data_provider_credentials() -> Credentials:
    """读取数据提供方凭据；未单独配置时复用通用测试用户。"""

    if os.getenv("TEST_DATA_PROVIDER_NAME") or os.getenv(
        "TEST_DATA_PROVIDER_PASSWORD"
    ):
        return _credentials(
            "TEST_DATA_PROVIDER_NAME",
            "TEST_DATA_PROVIDER_PASSWORD",
        )
    return _credentials("TEST_USER_NAME", "TEST_USER_PASSWORD")


@pytest.fixture
def data_consumer_credentials() -> Credentials:
    """读取独立的数据使用方账号，禁止复用数据提供方身份下单。"""

    return _credentials("TEST_DATA_CONSUMER_NAME", "TEST_DATA_CONSUMER_PASSWORD")


@pytest.fixture
def configured_value() -> Callable[[object, str], object]:
    def _configured(value: object, description: str) -> object:
        try:
            return require_value(value, description)
        except TestDataNotConfiguredError as error:
            pytest.skip(str(error))

    return _configured


@pytest.fixture
def configured_case() -> Callable[..., dict]:
    """校验一条参数化数据的必填字段；未补齐时给出明确跳过原因。"""

    def _configured(data: dict, *required_fields: str) -> dict:
        case_id = data.get("case_id", "UNKNOWN")
        try:
            for field in required_fields:
                require_value(data.get(field), f"{case_id}.{field}")
        except TestDataNotConfiguredError as error:
            pytest.skip(str(error))
        return data

    return _configured


@pytest.fixture
def visible_browser_required(request: pytest.FixtureRequest) -> None:
    if request.config.getoption("--headless"):
        pytest.skip("人工验证码用例必须使用可见浏览器，不能启用 --headless")


@pytest.fixture
def login_as(driver) -> Callable[[Credentials], NavigationComponent]:
    def _login(credentials: Credentials) -> NavigationComponent:
        login_page = LoginPage(driver)
        login_page.open_entry()
        login_page.login(credentials.username, credentials.password)
        login_page.wait_until_login_redirected()
        navigation = NavigationComponent(driver)
        navigation.wait_until_authenticated(credentials.username)
        return navigation

    return _login


@pytest.fixture
def relogin_as(driver) -> Callable[[Credentials], NavigationComponent]:
    """清理浏览器身份后重新登录，供跨角色端到端用例使用。"""

    def _relogin(credentials: Credentials) -> NavigationComponent:
        active_handle = driver.current_window_handle
        for handle in list(driver.window_handles):
            if handle == active_handle:
                continue
            driver.switch_to.window(handle)
            driver.close()
        driver.switch_to.window(active_handle)

        try:
            driver.execute_script(
                "window.localStorage.clear(); window.sessionStorage.clear();"
            )
        finally:
            driver.delete_all_cookies()

        login_page = LoginPage(driver)
        login_page.open_entry()
        login_page.login(credentials.username, credentials.password)
        login_page.wait_until_login_redirected()
        navigation = NavigationComponent(driver)
        navigation.wait_until_authenticated(credentials.username)
        return navigation

    return _relogin


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when not in {"setup", "call"} or not report.failed:
        return
    web_driver = item.funcargs.get("driver")
    if web_driver is None:
        return

    safe_name = re.sub(r"[^0-9A-Za-z_.-]+", "_", item.nodeid)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    screenshot_path = Path(SCREENSHOT_DIR) / f"{safe_name}_{timestamp}.png"
    try:
        png = web_driver.get_screenshot_as_png()
        screenshot_path.write_bytes(png)
        allure.attach(
            png,
            name="失败截图",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            web_driver.current_url,
            name="失败时页面地址",
            attachment_type=allure.attachment_type.TEXT,
        )
        LogFactory.get_logger().error("用例失败截图：%s", screenshot_path)
    except Exception:
        LogFactory.get_logger().exception("保存失败截图时发生异常")
