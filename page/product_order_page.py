"""数据使用方与数据提供方的产品订单管理页面对象。"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import re
from time import monotonic

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from base.base_page import BasePage


class ProductOrderPage(BasePage):
    """按动态订单编号定位订单行，并完成提供方审核。"""

    STANDARD_ORDER_TAB = (By.CSS_SELECTOR, "#tab-STANDARD_ORDER")
    KEYWORD_INPUT = (
        By.XPATH,
        "(//section//form//input[@placeholder='请输入'])[1]",
    )
    QUERY_BUTTON = (
        By.XPATH,
        "//section//form//button[.//span[normalize-space()='查询']]",
    )
    MAIN_ROWS = (
        By.CSS_SELECTOR,
        "section div.el-table > div.el-table__body-wrapper "
        "tbody > tr.el-table__row",
    )
    FIXED_ACTION_ROWS = (
        By.CSS_SELECTOR,
        "section div.el-table > div.el-table__fixed-right "
        "div.el-table__fixed-body-wrapper "
        "tbody > tr.el-table__row",
    )
    AUDIT_DIALOG_XPATH = (
        "//body/div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//*[normalize-space()='提供方审核']]"
    )
    AUDIT_DIALOG = (By.XPATH, AUDIT_DIALOG_XPATH)
    AUDIT_OPINION = (
        By.XPATH,
        f"{AUDIT_DIALOG_XPATH}//textarea[@placeholder='请输入审核意见']",
    )
    AUDIT_SUBMIT = (
        By.XPATH,
        f"{AUDIT_DIALOG_XPATH}//button[.//span[normalize-space()='提交']]",
    )
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".el-message.el-message--success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".el-message.el-message--error")
    PAGE_MESSAGES = (By.CSS_SELECTOR, ".el-message")
    FORM_ERRORS = (
        By.XPATH,
        f"{AUDIT_DIALOG_XPATH}//*[contains(@class,'el-form-item__error')]",
    )
    CONTRACT_DIALOG_XPATH = (
        "//body/div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//*[normalize-space()='上传合同']]"
        "[.//button[.//span[normalize-space()='提交合同']]]"
    )
    CONTRACT_DIALOG = (By.XPATH, CONTRACT_DIALOG_XPATH)
    CONTRACT_FILE_INPUT = (
        By.XPATH,
        f"{CONTRACT_DIALOG_XPATH}//input[@type='file']"
        "[contains(@accept,'.docx') or contains(@accept,'.doc')]",
    )
    CONTRACT_REMARK = (
        By.XPATH,
        f"{CONTRACT_DIALOG_XPATH}//textarea[@placeholder='请输入备注']",
    )
    CONTRACT_SUBMIT = (
        By.XPATH,
        f"{CONTRACT_DIALOG_XPATH}//button"
        "[.//span[normalize-space()='提交合同']]",
    )
    CONTRACT_UPLOAD_SUCCESS = (
        By.XPATH,
        f"{CONTRACT_DIALOG_XPATH}//*"
        "[contains(concat(' ', normalize-space(@class), ' '), "
        "' el-upload-list__item ') and "
        "contains(concat(' ', normalize-space(@class), ' '), ' is-success ')]",
    )
    CONTRACT_UPLOAD_FAILURE = (
        By.XPATH,
        f"{CONTRACT_DIALOG_XPATH}//*"
        "[contains(concat(' ', normalize-space(@class), ' '), "
        "' el-upload-list__item ') and "
        "(contains(concat(' ', normalize-space(@class), ' '), ' is-fail ') "
        "or contains(concat(' ', normalize-space(@class), ' '), ' is-error '))]",
    )
    CONTRACT_CONFIRM_DIALOG_XPATH = (
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//textarea[@placeholder='请输入合同确认意见']]"
        "[.//button[.//span[normalize-space()='确认']]]"
    )
    CONTRACT_CONFIRM_DIALOG = (By.XPATH, CONTRACT_CONFIRM_DIALOG_XPATH)
    CONTRACT_CONFIRM_OPINION = (
        By.XPATH,
        f"{CONTRACT_CONFIRM_DIALOG_XPATH}"
        "//textarea[@placeholder='请输入合同确认意见']",
    )
    CONTRACT_CONFIRM_SUBMIT = (
        By.XPATH,
        f"{CONTRACT_CONFIRM_DIALOG_XPATH}"
        "//button[.//span[normalize-space()='确认']]",
    )
    PAYMENT_DIALOG_XPATH = (
        "//body/div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//div[contains(@class,'d-uploader')]]"
        "[.//button[.//span[normalize-space()='提交']]]"
    )
    PAYMENT_DIALOG = (By.XPATH, PAYMENT_DIALOG_XPATH)
    PAYMENT_FILE_INPUT = (
        By.XPATH,
        f"{PAYMENT_DIALOG_XPATH}//input[@type='file']"
        "[contains(@accept,'.png') or contains(@accept,'.pdf') "
        "or contains(@accept,'.docx') or contains(@accept,'.doc')]",
    )
    PAYMENT_SUBMIT = (
        By.XPATH,
        f"{PAYMENT_DIALOG_XPATH}//button[.//span[normalize-space()='提交']]",
    )
    PAYMENT_UPLOAD_SUCCESS = (
        By.XPATH,
        f"{PAYMENT_DIALOG_XPATH}//*"
        "[contains(concat(' ', normalize-space(@class), ' '), "
        "' el-upload-list__item ') and "
        "contains(concat(' ', normalize-space(@class), ' '), ' is-success ')]",
    )
    PAYMENT_UPLOAD_FAILURE = (
        By.XPATH,
        f"{PAYMENT_DIALOG_XPATH}//*"
        "[contains(concat(' ', normalize-space(@class), ' '), "
        "' el-upload-list__item ') and "
        "(contains(concat(' ', normalize-space(@class), ' '), ' is-fail ') "
        "or contains(concat(' ', normalize-space(@class), ' '), ' is-error '))]",
    )
    RECEIPT_DIALOG_XPATH = (
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//textarea[@placeholder='请输入收款确认备注']]"
        "[.//button[.//span[normalize-space()='确认收款']]]"
    )
    RECEIPT_DIALOG = (By.XPATH, RECEIPT_DIALOG_XPATH)
    RECEIPT_NOTE = (
        By.XPATH,
        f"{RECEIPT_DIALOG_XPATH}"
        "//textarea[@placeholder='请输入收款确认备注']",
    )
    RECEIPT_SUBMIT = (
        By.XPATH,
        f"{RECEIPT_DIALOG_XPATH}"
        "//button[.//span[normalize-space()='确认收款']]",
    )
    DELIVERY_DIALOG_XPATH = (
        "//body/div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//input[@placeholder='请选择交付方式']]"
        "[.//input[@placeholder='请选择数据资源名称']]"
        "[.//button[.//span[normalize-space()='提交交付']]]"
    )
    DELIVERY_DIALOG = (By.XPATH, DELIVERY_DIALOG_XPATH)
    DELIVERY_METHOD = (
        By.XPATH,
        f"{DELIVERY_DIALOG_XPATH}//input[@placeholder='请选择交付方式']",
    )
    DELIVERY_RESOURCE = (
        By.XPATH,
        f"{DELIVERY_DIALOG_XPATH}"
        "//input[@placeholder='请选择数据资源名称']",
    )
    DELIVERY_SUBMIT = (
        By.XPATH,
        f"{DELIVERY_DIALOG_XPATH}"
        "//button[.//span[normalize-space()='提交交付']]",
    )
    DELIVERY_LAST_BATCH = (
        By.XPATH,
        f"{DELIVERY_DIALOG_XPATH}//label"
        "[contains(normalize-space(.),'本次是否是最后一批交付')]"
        "//input[@type='checkbox']/ancestor::label[1]",
    )
    ACCEPTANCE_DIALOG_XPATH = (
        "//body/div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//textarea[@placeholder='请输入该批次验收意见']]"
    )
    ACCEPTANCE_DIALOG = (By.XPATH, ACCEPTANCE_DIALOG_XPATH)
    ACCEPTANCE_RESULT = (
        By.XPATH,
        f"{ACCEPTANCE_DIALOG_XPATH}//input[@placeholder='请选择']",
    )
    ACCEPTANCE_OPINION = (
        By.XPATH,
        f"{ACCEPTANCE_DIALOG_XPATH}"
        "//textarea[@placeholder='请输入该批次验收意见']",
    )
    ACCEPTANCE_SUBMIT = (
        By.XPATH,
        f"{ACCEPTANCE_DIALOG_XPATH}"
        "//div[contains(@class,'el-dialog__footer')]"
        "//button[contains(@class,'el-button--primary')]",
    )
    ACCEPTANCE_BATCH_ROWS = (
        By.XPATH,
        f"{ACCEPTANCE_DIALOG_XPATH}"
        "//textarea[@placeholder='请输入该批次验收意见']"
        "/ancestor::div[contains(@class,'section-body')][1]"
        "//div[contains(@class,'el-table__body-wrapper')]"
        "//tr[contains(@class,'el-table__row')]",
    )
    REDELIVERY_DIALOG_XPATH = (
        "//body/div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//*[normalize-space()='批次交付记录']]"
    )
    REDELIVERY_DIALOG = (By.XPATH, REDELIVERY_DIALOG_XPATH)
    REDELIVERY_BATCH_ROWS = (
        By.XPATH,
        f"{REDELIVERY_DIALOG_XPATH}//div[contains(@class,'el-table__body-wrapper')]"
        "//tr[contains(@class,'el-table__row')]",
    )
    REDELIVERY_RESOURCE_DIALOG_XPATH = (
        "//body/div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//input[@placeholder='请选择数据资源名称']]"
        "[not(.//input[@placeholder='请选择交付方式'])]"
        "[.//button[.//span[normalize-space()='确认']]]"
    )
    REDELIVERY_RESOURCE_DIALOG = (
        By.XPATH,
        REDELIVERY_RESOURCE_DIALOG_XPATH,
    )
    REDELIVERY_RESOURCE = (
        By.XPATH,
        f"{REDELIVERY_RESOURCE_DIALOG_XPATH}"
        "//input[@placeholder='请选择数据资源名称']",
    )
    REDELIVERY_CONFIRM = (
        By.XPATH,
        f"{REDELIVERY_RESOURCE_DIALOG_XPATH}"
        "//button[.//span[normalize-space()='确认']]",
    )
    DETAIL_SURFACES = (
        By.CSS_SELECTOR,
        ".el-dialog__wrapper, .el-drawer__wrapper",
    )

    def wait_until_loaded(self) -> None:
        self.find_visible(self.STANDARD_ORDER_TAB)
        self._wait().until(
            lambda driver: bool(self._visible_main_rows()),
            message="标准订单页签已显示，但订单主表没有可见数据行",
        )

    def wait_for_recent_order(
        self,
        keyword: str,
        expected_status: str,
        submitted_after: datetime,
    ) -> str:
        """从当前角色列表识别本次刚提交且状态正确的最新订单。"""

        earliest = submitted_after - timedelta(minutes=2)

        def recent_order(driver) -> str | bool:
            candidates: list[tuple[datetime, str]] = []
            for row in self._visible_main_rows():
                # Element UI 横向表格会把右侧单元格裁剪或标记为隐藏，
                # WebElement.text 可能因此丢失产品编号、状态等业务字段。
                # textContent 能读取同一主表行的完整 DOM 内容。
                text = self._row_content(row)
                if keyword not in text or expected_status not in text:
                    continue
                order_match = re.search(
                    r"SO(?P<created_at>\d{14})(?P<sequence>\d+)",
                    text,
                )
                if not order_match:
                    continue
                created_at = datetime.strptime(
                    order_match.group("created_at"),
                    "%Y%m%d%H%M%S",
                )
                if created_at >= earliest:
                    candidates.append((created_at, order_match.group(0)))
            if not candidates:
                return False
            candidates.sort(reverse=True)
            return candidates[0][1]

        order_id = self._wait().until(
            recent_order,
            message=(
                f"未找到本次刚提交且状态为“{expected_status}”的订单：{keyword}"
            ),
        )
        self.log.info(
            "已在当前角色订单列表中从完整行 DOM 识别本次新订单：%s",
            order_id,
        )
        return order_id

    def audit_order(
        self,
        order_id: str,
        result: str,
        opinion: str,
        expected_states: list[str],
    ) -> str:
        """在动态订单行点击审核，并验证审核后的整组状态。"""

        normalized_result = result.upper()
        if normalized_result not in {"PASS", "REJECT"}:
            raise ValueError(f"不支持的提供方审核结果：{result}")

        self._click_row_action(order_id, "审核")
        self.find_visible(self.AUDIT_DIALOG)
        result_locator = (
            By.XPATH,
            f"{self.AUDIT_DIALOG_XPATH}//label"
            f"[.//input[@value='{normalized_result}']]",
        )
        self.click(result_locator)
        self.input(self.AUDIT_OPINION, opinion)
        self.click(self.AUDIT_SUBMIT)
        self._wait_for_audit_result()

        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def wait_for_order_states(
        self,
        order_id: str,
        expected_states: list[str],
    ) -> str:
        last_observed = ""

        def matched(driver) -> str | bool:
            nonlocal last_observed
            text = self._row_text_or_false(order_id)
            if text:
                last_observed = text
                if all(state in text for state in expected_states):
                    return text
            return False

        expected_message = " / ".join(expected_states)
        try:
            return self._wait().until(
                matched,
                message=f"订单 {order_id} 未达到预期状态：{expected_message}",
            )
        except TimeoutException as exc:
            actual_message = last_observed or "<订单行不可见>"
            raise TimeoutException(
                f"订单 {order_id} 未达到预期状态：{expected_message}；"
                f"实际订单行：{actual_message}"
            ) from exc

    def upload_contract(
        self,
        order_id: str,
        contract_path: str | Path,
        remark: str,
        expected_states: list[str],
    ) -> str:
        """在唯一订单行上传合同，并验证提交后的整组状态。"""

        self._click_row_action(order_id, "上传合同")
        self.find_visible(self.CONTRACT_DIALOG)
        selected_path = Path(contract_path).expanduser().resolve()
        self.input(self.CONTRACT_REMARK, remark)
        self.upload(self.CONTRACT_FILE_INPUT, selected_path)
        upload_outcome = self._wait_for_contract_file_uploaded(selected_path.name)
        if upload_outcome != "submitted":
            self.click(self.CONTRACT_SUBMIT)
            self._wait_for_contract_upload_result()

        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def confirm_contract(
        self,
        order_id: str,
        result: str,
        opinion: str,
        expected_states: list[str],
    ) -> str:
        """数据提供方在唯一订单行确认合同，并验证确认后的状态。"""

        normalized_result = result.upper()
        if normalized_result not in {"PASS", "REJECT"}:
            raise ValueError(f"不支持的合同确认结果：{result}")

        self._click_row_action(order_id, "确认合同")
        self.find_visible(self.CONTRACT_CONFIRM_DIALOG)
        result_locator = (
            By.XPATH,
            f"{self.CONTRACT_CONFIRM_DIALOG_XPATH}//label"
            f"[.//input[@value='{normalized_result}']]",
        )
        self.click(result_locator)
        self.input(self.CONTRACT_CONFIRM_OPINION, opinion)
        self.click(self.CONTRACT_CONFIRM_SUBMIT)
        self._wait_for_dialog_submission_result(
            self.CONTRACT_CONFIRM_DIALOG,
            "合同确认",
        )

        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def pay_order(
        self,
        order_id: str,
        voucher_path: str | Path,
        expected_states: list[str],
    ) -> str:
        """数据使用方为唯一订单上传模拟支付凭证并提交支付。"""

        self._click_row_action(order_id, "去支付")
        self.find_visible(self.PAYMENT_DIALOG)
        selected_path = Path(voucher_path).expanduser().resolve()
        self.upload(self.PAYMENT_FILE_INPUT, selected_path)
        upload_outcome = self._wait_for_payment_voucher_uploaded(selected_path.name)
        if upload_outcome != "submitted":
            self.click(self.PAYMENT_SUBMIT)
            self._wait_for_dialog_submission_result(self.PAYMENT_DIALOG, "支付提交")

        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def confirm_receipt(
        self,
        order_id: str,
        result: str,
        note: str,
        expected_states: list[str],
    ) -> str:
        """数据提供方确认收款结果，并验证订单进入交付阶段。"""

        normalized_result = result.upper()
        if normalized_result not in {"E", "F"}:
            raise ValueError(f"不支持的收款确认结果：{result}")

        self._click_row_action(order_id, "确认收款")
        self.find_visible(self.RECEIPT_DIALOG)
        result_locator = (
            By.XPATH,
            f"{self.RECEIPT_DIALOG_XPATH}//label"
            f"[.//input[@value='{normalized_result}']]",
        )
        self.click(result_locator)
        self.input(self.RECEIPT_NOTE, note)
        self.click(self.RECEIPT_SUBMIT)
        self._wait_for_dialog_submission_result(self.RECEIPT_DIALOG, "确认收款")

        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def deliver_order(
        self,
        order_id: str,
        delivery_method: str,
        resource_name: str,
        expected_states: list[str],
        *,
        is_last_batch: bool | None = None,
    ) -> str:
        """数据提供方选择现有数据资源并提交交付。"""

        self._click_row_action(order_id, "去交付")
        self.find_visible(self.DELIVERY_DIALOG)
        self._select_element_option(self.DELIVERY_METHOD, delivery_method)
        self._select_element_option(self.DELIVERY_RESOURCE, resource_name)
        if delivery_method == "分批交付" and is_last_batch is not None:
            # 首次分批交付时页面尚无批次记录，不渲染“最后一批”复选框；
            # 后续批次才显示该控件。首批为 False 时允许控件不存在，
            # 最后一批为 True 时仍必须找到并勾选，避免误提交为普通批次。
            checkbox = None
            if is_last_batch:
                checkbox = self.find_visible(self.DELIVERY_LAST_BATCH)
            elif self.is_visible(self.DELIVERY_LAST_BATCH, timeout=1):
                checkbox = self.find_visible(self.DELIVERY_LAST_BATCH, timeout=1)

            if checkbox is not None:
                checked = "is-checked" in (checkbox.get_attribute("class") or "")
                if checked != is_last_batch:
                    self.click(self.DELIVERY_LAST_BATCH)
        self.click(self.DELIVERY_SUBMIT)
        self._wait_for_dialog_submission_result(self.DELIVERY_DIALOG, "提交交付")

        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def validate_delivery_required_fields(
        self,
        order_id: str,
        expected_states: list[str],
    ) -> str:
        """空提交交付弹窗，确认必填校验后取消且状态不变。"""

        self._click_row_action(order_id, "去交付")
        self.find_visible(self.DELIVERY_DIALOG)
        self.click(self.DELIVERY_SUBMIT)
        messages = self._wait_for_validation_feedback(
            self.DELIVERY_DIALOG,
            "交付必填项",
        )
        self._cancel_visible_dialog(self.DELIVERY_DIALOG)
        self.driver.refresh()
        self.wait_until_loaded()
        row = self.wait_for_order_states(order_id, expected_states)
        if not messages:
            raise AssertionError("交付空提交未返回任何必填提示")
        return row

    def accept_order(
        self,
        order_id: str,
        result: str,
        opinion: str,
        expected_states: list[str],
    ) -> str:
        """数据使用方验收唯一订单的交付批次。"""

        if result not in {"验收通过", "验收驳回"}:
            raise ValueError(f"不支持的验收结果：{result}")

        self._click_row_action(order_id, "确认验收")
        self.find_visible(self.ACCEPTANCE_DIALOG)
        self._select_element_option(self.ACCEPTANCE_RESULT, result)
        self.input(self.ACCEPTANCE_OPINION, opinion)
        self.click(self.ACCEPTANCE_SUBMIT)
        self._wait_for_dialog_submission_result(self.ACCEPTANCE_DIALOG, "确认验收")

        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def accept_pending_batches(
        self,
        order_id: str,
        result: str,
        opinion: str,
        expected_states: list[str],
    ) -> str:
        """对验收弹窗中所有待验收批次提交同一验收结果。"""

        if result not in {"验收通过", "验收驳回"}:
            raise ValueError(f"不支持的验收结果：{result}")

        self._click_row_action(order_id, "确认验收")
        self.find_visible(self.ACCEPTANCE_DIALOG)
        pending_rows = []
        for row in self.driver.find_elements(*self.ACCEPTANCE_BATCH_ROWS):
            if not row.is_displayed():
                continue
            result_inputs = row.find_elements(By.XPATH, ".//input[@placeholder='请选择']")
            opinions = row.find_elements(
                By.XPATH,
                ".//textarea[@placeholder='请输入该批次验收意见']",
            )
            if len(result_inputs) == 1 and len(opinions) == 1:
                pending_rows.append((row, result_inputs[0], opinions[0]))

        if not pending_rows:
            raise AssertionError(
                f"订单 {order_id} 验收弹窗的逐批验收区域中没有可编辑批次"
            )

        for index, (_, result_input, opinion_input) in enumerate(
            pending_rows,
            start=1,
        ):
            self._select_acceptance_result_element(result_input, result)
            opinion_input.clear()
            opinion_input.send_keys(f"{opinion}（批次{index}）")

        self.click(self.ACCEPTANCE_SUBMIT)
        self._wait_for_dialog_submission_result(self.ACCEPTANCE_DIALOG, "确认验收")
        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def redeliver_rejected_batches(
        self,
        order_id: str,
        resource_names: list[str],
        expected_states: list[str],
    ) -> str:
        """逐项重新交付验收驳回批次，并保留原批次历史。"""

        self._click_row_action(order_id, "重新交付")
        self.find_visible(self.REDELIVERY_DIALOG)
        rejected_batches: list[str] = []
        for row in self.driver.find_elements(*self.REDELIVERY_BATCH_ROWS):
            if not row.is_displayed():
                continue
            text = self._element_content(row)
            if "验收驳回" not in text:
                continue
            cells = row.find_elements(By.TAG_NAME, "td")
            batch_id = self._element_content(cells[0]) if cells else text
            if batch_id and batch_id not in rejected_batches:
                rejected_batches.append(batch_id)

        if not rejected_batches:
            raise AssertionError(f"订单 {order_id} 没有可重新交付的驳回批次")
        if len(resource_names) != len(rejected_batches):
            raise AssertionError(
                "重新交付资源数量与驳回批次数量不一致："
                f"resources={len(resource_names)}，batches={len(rejected_batches)}"
            )

        for batch_id, resource_name in zip(rejected_batches, resource_names):
            target_rows = [
                row
                for row in self.driver.find_elements(*self.REDELIVERY_BATCH_ROWS)
                if row.is_displayed()
                and "验收驳回" in self._element_content(row)
                and self._element_content(row).startswith(batch_id)
            ]
            if len(target_rows) != 1:
                raise AssertionError(f"未唯一匹配重新交付批次：{batch_id}")
            buttons = [
                button
                for button in target_rows[0].find_elements(By.TAG_NAME, "button")
                if button.is_displayed() and button.text.strip() == "重新交付"
            ]
            if len(buttons) != 1:
                raise AssertionError(f"批次 {batch_id} 未唯一匹配重新交付按钮")
            self.scroll_to_element(buttons[0])
            self.driver.execute_script("arguments[0].click();", buttons[0])
            self.find_visible(self.REDELIVERY_RESOURCE_DIALOG)
            self._select_element_option(self.REDELIVERY_RESOURCE, resource_name)
            self._wait().until(
                lambda driver: not any(
                    message.is_displayed()
                    for message in driver.find_elements(*self.SUCCESS_MESSAGE)
                ),
                message="上一批重新交付成功提示未及时消失",
            )
            self.click(self.REDELIVERY_CONFIRM)
            self._wait_for_dialog_submission_result(
                self.REDELIVERY_RESOURCE_DIALOG,
                f"批次 {batch_id} 重新交付",
            )

        self._cancel_visible_dialog(self.REDELIVERY_DIALOG, allow_close=True)
        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def has_row_action(self, order_id: str, action_text: str) -> bool:
        """检查唯一订单同行是否显示指定操作按钮。"""

        main_rows = self._visible_main_rows()
        indexes = [
            index
            for index, row in enumerate(main_rows)
            if order_id in self._row_content(row)
        ]
        if len(indexes) != 1:
            raise AssertionError(f"订单列表未唯一匹配订单编号：{order_id}")
        action_rows = self._visible_fixed_action_rows()
        index = indexes[0]
        if index >= len(action_rows):
            raise AssertionError(f"订单 {order_id} 主表与固定操作列行数不一致")
        return any(
            button.is_displayed() and button.text.strip() == action_text
            for button in action_rows[index].find_elements(By.TAG_NAME, "button")
        )

    def view_order_details(
        self,
        order_id: str,
        expected_fragments: list[str],
    ) -> str:
        """打开唯一订单详情，并校验详情容器中的关键业务内容。"""

        previous_url = self.driver.current_url
        self._click_row_action(order_id, "查看详情")

        def visible_details(driver) -> str | bool:
            for surface in driver.find_elements(*self.DETAIL_SURFACES):
                if not surface.is_displayed():
                    continue
                text = self._element_content(surface)
                if order_id in text:
                    return text
            if driver.current_url != previous_url:
                text = self._element_content(driver.find_element(By.TAG_NAME, "body"))
                if order_id in text:
                    return text
            return False

        detail_text = self._wait().until(
            visible_details,
            message=f"点击查看详情后未出现订单 {order_id} 的详情内容",
        )
        missing = [text for text in expected_fragments if text not in detail_text]
        if missing:
            raise AssertionError(
                f"订单 {order_id} 详情缺少预期内容：{' / '.join(missing)}"
            )
        return detail_text

    def _select_element_option(
        self,
        input_locator: tuple[str, str],
        option_text: str,
    ) -> None:
        """选择当前打开的 Element UI 下拉框中的精确文本选项。"""

        input_element = self.find_visible(input_locator)
        self._select_element_option_element(input_element, option_text)

    def _select_acceptance_result_element(
        self,
        input_element: WebElement,
        result: str,
    ) -> None:
        """通过当前行输入框的键盘事件选择验收结果，避免串到其他行浮层。"""

        current_value = (input_element.get_attribute("value") or "").strip()
        if current_value == result:
            return

        option_steps = {"验收通过": 1, "验收驳回": 2}
        if result not in option_steps:
            raise ValueError(f"不支持的验收结果：{result}")

        self.scroll_to_element(input_element)
        try:
            input_element.click()
        except (
            ElementClickInterceptedException,
            ElementNotInteractableException,
        ):
            self.driver.execute_script("arguments[0].click();", input_element)

        # Element UI Select 在空值状态下 hoverIndex 为 -1；第一次向下选择
        # “验收通过”，第二次向下选择“验收驳回”。键盘事件只作用于当前
        # 获得焦点的行，不受页面中隐藏的同名下拉层影响。
        for _ in range(option_steps[result]):
            input_element.send_keys(Keys.ARROW_DOWN)
        input_element.send_keys(Keys.ENTER)

        self._wait().until(
            lambda driver: (
                (input_element.get_attribute("value") or "").strip() == result
            ),
            message=f"当前批次未通过键盘选中验收结果：{result}",
        )
        self.log.info("当前批次已选择验收结果：%s", result)

    def _select_element_option_element(
        self,
        input_element: WebElement,
        option_text: str,
    ) -> None:
        current_value = (input_element.get_attribute("value") or "").strip()
        if current_value == option_text:
            self.log.info(
                "页面已带入下拉框目标值，无需重复选择：%s",
                option_text,
            )
            return

        select_containers = input_element.find_elements(
            By.XPATH,
            "./ancestor::div["
            "contains(concat(' ',normalize-space(@class),' '),' el-select ')"
            "][1]",
        )
        if len(select_containers) != 1:
            raise AssertionError(
                f"未唯一匹配下拉输入框所属组件：{option_text}"
            )
        dropdowns = select_containers[0].find_elements(
            By.XPATH,
            ".//div["
            "contains(concat(' ',normalize-space(@class),' '),"
            "' el-select-dropdown ')"
            "]",
        )
        owning_dropdown = dropdowns[0] if len(dropdowns) == 1 else None

        self.scroll_to_element(input_element)
        try:
            input_element.click()
        except (
            ElementClickInterceptedException,
            ElementNotInteractableException,
        ):
            self.driver.execute_script("arguments[0].click();", input_element)
        self._click_visible_option(input_element, owning_dropdown, option_text)

        def option_selected(driver) -> bool:
            try:
                return (
                    (input_element.get_attribute("value") or "").strip()
                    == option_text
                )
            except StaleElementReferenceException:
                # Element UI 可能在选中后重绘当前表格行；选项已完成点击，
                # 元素失效本身即说明旧输入框已被新状态替换。
                return True

        self._wait().until(
            option_selected,
            message=f"下拉框选择后未显示目标值：{option_text}",
        )
        self.log.info("下拉框已选择目标值：%s", option_text)

    def _click_visible_option(
        self,
        input_element: WebElement,
        owning_dropdown: WebElement | None,
        option_text: str,
    ) -> None:
        relative_option_locator = (
            By.XPATH,
            ".//li[not(contains(@class,'is-disabled'))]"
            f"[normalize-space()='{option_text}' "
            f"or .//span[normalize-space()='{option_text}']]",
        )
        global_option_locator = (
            By.XPATH,
            "//body//div[contains(@class,'el-select-dropdown')]"
            "//li[not(contains(@class,'is-disabled'))]"
            f"[normalize-space()='{option_text}' "
            f"or .//span[normalize-space()='{option_text}']]",
        )

        def visible_option(driver) -> WebElement | bool:
            matches = []
            if owning_dropdown is not None:
                try:
                    matches.extend(
                        owning_dropdown.find_elements(*relative_option_locator)
                    )
                except StaleElementReferenceException:
                    pass
            # 重新交付弹窗会在第二次打开时把下拉层动态移动到 body，
            # 此时输入框组件内部没有选项层，需要回退到页面级候选项。
            matches.extend(driver.find_elements(*global_option_locator))

            visible_matches = []
            seen_ids = set()
            for element in matches:
                try:
                    if (
                        element.id not in seen_ids
                        and element.is_displayed()
                        and element.is_enabled()
                    ):
                        seen_ids.add(element.id)
                        visible_matches.append(element)
                except StaleElementReferenceException:
                    continue
            if not visible_matches:
                return False

            # Element UI 会保留多个共享坐标的下拉浮层，Selenium 的
            # is_displayed() 可能同时把隐藏克隆判为可见，单纯比较距离仍会
            # 选错。使用浏览器命中测试，只接受当前屏幕最上层、鼠标实际
            # 能点到的选项。
            hit_tested = []
            for element in visible_matches:
                try:
                    is_topmost = driver.execute_script(
                        """
                        const option = arguments[0];
                        const rect = option.getBoundingClientRect();
                        if (rect.width <= 0 || rect.height <= 0) return false;
                        const x = rect.left + rect.width / 2;
                        const y = rect.top + rect.height / 2;
                        if (x < 0 || y < 0 || x >= window.innerWidth ||
                            y >= window.innerHeight) return false;
                        const top = document.elementFromPoint(x, y);
                        return Boolean(top &&
                            (top === option || option.contains(top)));
                        """,
                        element,
                    )
                    if is_topmost:
                        hit_tested.append(element)
                except StaleElementReferenceException:
                    continue
            if len(hit_tested) == 1:
                return hit_tested[0]
            if len(hit_tested) > 1:
                # 同一 li 内部不会产生多个候选；这里只处理短暂动画重叠，
                # 取 DOM 中最后出现的顶层浮层。
                return hit_tested[-1]
            return False

        self.log.info("点击当前输入框所属下拉选项：%s", option_text)
        option = self._wait().until(
            visible_option,
            message=f"未找到当前可见且可用的下拉选项：{option_text}",
        )
        try:
            option.click()
        except (
            ElementClickInterceptedException,
            ElementNotInteractableException,
        ):
            self.log.info(
                "下拉选项位于弹窗滚动浮层中，改用 JavaScript 点击：%s",
                option_text,
            )
            self.driver.execute_script("arguments[0].click();", option)

    def _wait_for_validation_feedback(
        self,
        dialog_locator: tuple[str, str],
        description: str,
    ) -> list[str]:
        """读取弹窗内表单错误或页面顶部提示，不依赖固定弹窗序号。"""

        def feedback(driver) -> list[str] | bool:
            messages = [
                element.text.strip()
                for element in driver.find_elements(*self.PAGE_MESSAGES)
                if element.is_displayed() and element.text.strip()
            ]
            dialogs = [
                dialog
                for dialog in driver.find_elements(*dialog_locator)
                if dialog.is_displayed()
            ]
            if dialogs:
                messages.extend(
                    element.text.strip()
                    for element in dialogs[0].find_elements(
                        By.CSS_SELECTOR,
                        ".el-form-item__error",
                    )
                    if element.is_displayed() and element.text.strip()
                )
            unique = list(dict.fromkeys(messages))
            return unique or False

        return self._wait().until(
            feedback,
            message=f"{description}未出现错误提示",
        )

    def _cancel_visible_dialog(
        self,
        dialog_locator: tuple[str, str],
        *,
        allow_close: bool = False,
    ) -> None:
        dialogs = [
            dialog
            for dialog in self.driver.find_elements(*dialog_locator)
            if dialog.is_displayed()
        ]
        if not dialogs and allow_close:
            self.log.info("操作弹窗已由页面自动关闭，无需重复关闭")
            return
        if len(dialogs) != 1:
            raise AssertionError("未唯一匹配需要关闭的操作弹窗")
        dialog = dialogs[0]
        candidates = [
            button
            for button in dialog.find_elements(By.TAG_NAME, "button")
            if button.is_displayed()
            and button.text.strip() in ({"取消", "关闭"} if allow_close else {"取消"})
        ]
        if not candidates and allow_close:
            candidates = [
                button
                for button in dialog.find_elements(
                    By.CSS_SELECTOR,
                    ".el-dialog__headerbtn",
                )
                if button.is_displayed()
            ]
        if not candidates:
            raise AssertionError("操作弹窗未找到取消或关闭按钮")
        self.scroll_to_element(candidates[-1])
        self.driver.execute_script("arguments[0].click();", candidates[-1])
        self._wait().until(
            lambda driver: not any(
                item.is_displayed()
                for item in driver.find_elements(*dialog_locator)
            ),
            message="取消操作后弹窗仍未关闭",
        )

    def _wait_for_contract_file_uploaded(self, expected_name: str) -> str:
        """等待前端异步上传完成，再允许提交合同表单。"""

        outcome, detail = self._wait(30).until(
            lambda driver: self._contract_file_upload_state(expected_name),
            message=f"合同文件未在 30 秒内上传完成：{expected_name}",
        )
        if outcome == "failure":
            raise AssertionError(f"合同文件上传失败：{detail}")
        if outcome == "submitted":
            self.log.info("合同上传弹窗已关闭，跳过重复点击提交合同")
        else:
            self.log.info("合同文件上传完成：%s", expected_name)
        return outcome

    def _contract_file_upload_state(
        self,
        expected_name: str,
    ) -> tuple[str, str] | bool:
        return self._dialog_file_upload_state(
            self.CONTRACT_DIALOG,
            self.CONTRACT_FILE_INPUT,
            self.CONTRACT_UPLOAD_SUCCESS,
            self.CONTRACT_UPLOAD_FAILURE,
            expected_name,
            "_contract_upload_fallback_ready_since",
        )

    def _wait_for_payment_voucher_uploaded(self, expected_name: str) -> str:
        outcome, detail = self._wait(30).until(
            lambda driver: self._payment_voucher_upload_state(expected_name),
            message=f"支付凭证未在 30 秒内上传完成：{expected_name}",
        )
        if outcome == "failure":
            raise AssertionError(f"支付凭证上传失败：{detail}")
        if outcome == "submitted":
            self.log.info("支付弹窗已关闭，跳过重复点击提交")
        else:
            self.log.info("支付凭证上传完成：%s", expected_name)
        return outcome

    def _payment_voucher_upload_state(
        self,
        expected_name: str,
    ) -> tuple[str, str] | bool:
        return self._dialog_file_upload_state(
            self.PAYMENT_DIALOG,
            self.PAYMENT_FILE_INPUT,
            self.PAYMENT_UPLOAD_SUCCESS,
            self.PAYMENT_UPLOAD_FAILURE,
            expected_name,
            "_payment_upload_fallback_ready_since",
        )

    def _dialog_file_upload_state(
        self,
        dialog_locator: tuple[str, str],
        file_input_locator: tuple[str, str],
        success_locator: tuple[str, str],
        failure_locator: tuple[str, str],
        expected_name: str,
        ready_since_attribute: str,
    ) -> tuple[str, str] | bool:
        dialogs = [
            dialog
            for dialog in self.driver.find_elements(*dialog_locator)
            if dialog.is_displayed()
        ]
        if not dialogs:
            return ("submitted", "上传弹窗已关闭")

        # Element UI 达到单文件上限后会重绘上传组件，并移除 file input。
        # 等待谓词中不能使用 find_present，否则 input 消失后会在内层再次
        # 阻塞一个完整显式等待周期，提交按钮也会因旧的弹窗作用域而失效。
        selected_names: list[str] = []
        for file_input in self.driver.find_elements(*file_input_locator):
            try:
                selected_name = self.driver.execute_script(
                    "return arguments[0].files && arguments[0].files.length "
                    "? arguments[0].files[0].name : '';",
                    file_input,
                )
            except StaleElementReferenceException:
                # 上传完成时 input 可能恰好被 Vue 重绘，下一轮直接读取
                # 上传成功列表项即可。
                continue
            if selected_name:
                selected_names.append(str(selected_name))
        unexpected_names = [
            name for name in selected_names if name != expected_name
        ]
        if unexpected_names:
            return (
                "failure",
                f"文件输入框选中了意外文件：{'、'.join(unexpected_names)}",
            )

        upload_failures = [
            element.text.strip()
            for element in self.driver.find_elements(*failure_locator)
            if element.is_displayed()
        ]
        page_errors = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        if upload_failures or page_errors:
            detail = "；".join(
                dict.fromkeys(
                    text or f"页面标记 {expected_name} 上传失败"
                    for text in upload_failures + page_errors
                )
            )
            return ("failure", detail)

        completed = [
            element
            for element in self.driver.find_elements(*success_locator)
            if element.is_displayed()
        ]
        if len(completed) == 1:
            return ("success", expected_name)

        fallback_status, fallback_detail = self._custom_file_upload_state(
            dialogs[0],
            expected_name,
        )
        if fallback_status == "failure":
            return ("failure", fallback_detail)
        if fallback_status == "success":
            # 自定义上传组件不暴露标准 is-success；文件卡片、隐藏的上传
            # 触发器和无上传中状态连续稳定 1 秒后，才允许提交表单。
            ready_since = getattr(
                self,
                ready_since_attribute,
                None,
            )
            if ready_since is None:
                setattr(self, ready_since_attribute, monotonic())
                return False
            if monotonic() - ready_since >= 1:
                return ("success", fallback_detail or expected_name)
        else:
            setattr(self, ready_since_attribute, None)
        return False

    def _custom_file_upload_state(
        self,
        dialog: WebElement,
        expected_name: str,
    ) -> tuple[str, str]:
        """识别未使用 Element UI 标准成功类的单文件上传卡片。"""

        name_prefix = Path(expected_name).stem[:12]
        state = self.driver.execute_script(
            """
            const dialog = arguments[0];
            const expectedName = arguments[1];
            const namePrefix = arguments[2];
            const uploader = dialog.querySelector('.d-uploader') ||
                dialog.querySelector('.el-form-item.is-required');
            if (!uploader) {
                return {status: 'pending', detail: ''};
            }
            const visible = element => {
                if (!element) return false;
                const style = getComputedStyle(element);
                const rect = element.getBoundingClientRect();
                return style.display !== 'none' &&
                    style.visibility !== 'hidden' &&
                    rect.width > 0 && rect.height > 0;
            };
            const nodes = Array.from(uploader.querySelectorAll('*'));
            const failed = nodes.find(element =>
                element.classList.contains('is-fail') ||
                element.classList.contains('is-error')
            );
            if (failed) {
                return {
                    status: 'failure',
                    detail: failed.innerText.trim() || '上传组件返回失败状态'
                };
            }
            const uploading = nodes.some(element =>
                visible(element) && (
                    element.classList.contains('is-uploading') ||
                    element.classList.contains('el-icon-loading') ||
                    element.matches('.el-progress, [class*="uploading"]')
                )
            );
            const filenameNode = nodes.find(element => {
                const values = [
                    element.textContent || '',
                    element.getAttribute('title') || '',
                    element.getAttribute('alt') || '',
                    element.getAttribute('data-name') || '',
                    element.getAttribute('href') || '',
                    element.getAttribute('src') || ''
                ];
                return values.some(value =>
                    value.includes(expectedName) || value.includes(namePrefix)
                );
            });
            const fileCard = filenameNode || uploader.querySelector(
                '.el-upload-list__item, '
                + '[class*="upload-list"] [class*="item"], '
                + 'img[src]'
            );
            const input = uploader.querySelector('input[type="file"]');
            const trigger = input && input.closest('.el-upload');
            const triggerHidden = !input || !visible(trigger);
            if (fileCard && triggerHidden && !uploading) {
                return {
                    status: 'success',
                    detail: '自定义上传文件卡片已稳定显示'
                };
            }
            return {status: 'pending', detail: ''};
            """,
            dialog,
            expected_name,
            name_prefix,
        )
        return (str(state["status"]), str(state["detail"]))

    def _wait_for_dialog_submission_result(
        self,
        dialog_locator: tuple[str, str],
        description: str,
    ) -> str:
        failure_not_before = monotonic() + 1.5
        outcome, detail = self._wait().until(
            lambda driver: self._dialog_submission_result(
                dialog_locator,
                failure_not_before,
            ),
            message=f"{description}后页面未返回结果",
        )
        if outcome == "failure":
            raise AssertionError(f"{description}被页面拦截：{detail}")
        return detail or f"{description}成功"

    def _dialog_submission_result(
        self,
        dialog_locator: tuple[str, str],
        failure_not_before: float,
    ) -> tuple[str, str] | bool:
        # Element UI 可能先渲染必填校验节点，随后才展示成功消息并关闭弹窗。
        # 明确成功消息的优先级最高；短暂错误在观察窗口内继续等待，避免
        # 合同确认、收款、交付和验收把成功操作误判为失败。
        successes = [
            element.text.strip()
            for element in self.driver.find_elements(*self.SUCCESS_MESSAGE)
            if element.is_displayed()
        ]
        if successes:
            return ("success", next((text for text in successes if text), ""))

        dialogs = [
            dialog
            for dialog in self.driver.find_elements(*dialog_locator)
            if dialog.is_displayed()
        ]
        if not dialogs:
            return ("success", "操作弹窗已关闭")

        errors = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        errors.extend(
            element.text.strip()
            for element in dialogs[0].find_elements(
                By.CSS_SELECTOR,
                ".el-form-item__error",
            )
            if element.is_displayed() and element.text.strip()
        )
        if errors:
            if monotonic() < failure_not_before:
                return False
            return ("failure", "；".join(dict.fromkeys(errors)))
        return False

    def _row_text_or_false(self, order_id: str) -> str | bool:
        matches = [
            self._row_content(row)
            for row in self._visible_main_rows()
            if order_id in self._row_content(row)
        ]
        return matches[0] if len(matches) == 1 else False

    def _click_row_action(self, order_id: str, action_text: str) -> None:
        main_rows = self._visible_main_rows()
        indexes = [
            index
            for index, row in enumerate(main_rows)
            if order_id in self._row_content(row)
        ]
        if len(indexes) != 1:
            raise AssertionError(f"订单列表未唯一匹配订单编号：{order_id}")

        action_rows = self._visible_fixed_action_rows()
        index = indexes[0]
        if index >= len(action_rows):
            raise AssertionError(
                f"订单主表与固定操作列行数不一致：{order_id}，"
                f"main={len(main_rows)}，actions={len(action_rows)}"
            )
        buttons = [
            button
            for button in action_rows[index].find_elements(By.TAG_NAME, "button")
            if button.is_displayed() and button.text.strip() == action_text
        ]
        if len(buttons) != 1:
            raise AssertionError(
                f"订单 {order_id} 未唯一匹配操作按钮：{action_text}"
            )
        button = buttons[0]
        self.scroll_to_element(button)
        try:
            button.click()
        except ElementClickInterceptedException:
            self.log.info("订单操作按钮被表格层遮挡，改用同行唯一按钮 JS 点击")
            self.driver.execute_script("arguments[0].click();", button)

    def _visible_main_rows(self) -> list[WebElement]:
        return [
            row
            for row in self.driver.find_elements(*self.MAIN_ROWS)
            if row.is_displayed()
        ]

    def _visible_fixed_action_rows(self) -> list[WebElement]:
        return [
            row
            for row in self.driver.find_elements(*self.FIXED_ACTION_ROWS)
            if row.is_displayed()
        ]

    def _row_content(self, row: WebElement) -> str:
        """读取横向滚动表格行的全部文本，并压缩布局空白。"""

        return self._element_content(row)

    def _element_content(self, element: WebElement) -> str:
        """读取指定容器完整文本，并压缩布局空白。"""

        content = self.driver.execute_script(
            "return arguments[0].textContent || '';",
            element,
        )
        return " ".join(str(content).split())

    def _wait_for_audit_result(self) -> str:
        outcome, detail = self._wait().until(
            lambda driver: self._audit_result(),
            message="提交提供方审核后页面未返回结果",
        )
        if outcome == "failure":
            raise AssertionError(f"提供方审核被页面拦截：{detail}")
        return detail or "提供方审核提交成功"

    def _audit_result(self) -> tuple[str, str] | bool:
        errors = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        errors.extend(
            element.text.strip()
            for element in self.driver.find_elements(*self.FORM_ERRORS)
            if element.is_displayed() and element.text.strip()
        )
        if errors:
            return ("failure", "；".join(dict.fromkeys(errors)))
        successes = [
            element.text.strip()
            for element in self.driver.find_elements(*self.SUCCESS_MESSAGE)
            if element.is_displayed()
        ]
        if successes:
            return ("success", next((text for text in successes if text), ""))
        dialogs = self.driver.find_elements(*self.AUDIT_DIALOG)
        if not any(dialog.is_displayed() for dialog in dialogs):
            return ("success", "提供方审核弹窗已关闭")
        return False

    def _wait_for_contract_upload_result(self) -> str:
        outcome, detail = self._wait().until(
            lambda driver: self._contract_upload_result(),
            message="提交合同后页面未返回结果",
        )
        if outcome == "failure":
            raise AssertionError(f"合同上传被页面拦截：{detail}")
        return detail or "合同提交成功"

    def _contract_upload_result(self) -> tuple[str, str] | bool:
        errors = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        form_error_locator = (
            By.XPATH,
            f"{self.CONTRACT_DIALOG_XPATH}//*"
            "[contains(@class,'el-form-item__error')]",
        )
        errors.extend(
            element.text.strip()
            for element in self.driver.find_elements(*form_error_locator)
            if element.is_displayed() and element.text.strip()
        )
        if errors:
            return ("failure", "；".join(dict.fromkeys(errors)))
        successes = [
            element.text.strip()
            for element in self.driver.find_elements(*self.SUCCESS_MESSAGE)
            if element.is_displayed()
        ]
        if successes:
            return ("success", next((text for text in successes if text), ""))
        dialogs = self.driver.find_elements(*self.CONTRACT_DIALOG)
        if not any(dialog.is_displayed() for dialog in dialogs):
            return ("success", "合同上传弹窗已关闭")
        return False
