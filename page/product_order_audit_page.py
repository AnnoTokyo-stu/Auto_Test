"""运营方的产品订单审核页面对象。"""

from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from page.product_order_page import ProductOrderPage


class ProductOrderAuditPage(ProductOrderPage):
    """按动态订单编号完成运营方审核，复用订单表格行绑定能力。"""

    OPERATIONS_AUDIT_DIALOG_XPATH = (
        "//body/div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//textarea[@placeholder='请输入审核意见']]"
        "[.//button[.//span[normalize-space()='提交审核结果']]]"
    )
    OPERATIONS_AUDIT_DIALOG = (By.XPATH, OPERATIONS_AUDIT_DIALOG_XPATH)
    OPERATIONS_AUDIT_OPINION = (
        By.XPATH,
        f"{OPERATIONS_AUDIT_DIALOG_XPATH}"
        "//textarea[@placeholder='请输入审核意见']",
    )
    OPERATIONS_AUDIT_SUBMIT = (
        By.XPATH,
        f"{OPERATIONS_AUDIT_DIALOG_XPATH}//button"
        "[.//span[normalize-space()='提交审核结果']]",
    )

    def approve_order(
        self,
        order_id: str,
        opinion: str,
        expected_states: list[str],
    ) -> str:
        return self.review_order(
            order_id,
            "PASS",
            opinion,
            expected_states,
        )

    def review_order(
        self,
        order_id: str,
        result: str,
        opinion: str,
        expected_states: list[str],
    ) -> str:
        normalized_result = result.upper()
        if normalized_result not in {"PASS", "REJECT"}:
            raise ValueError(f"不支持的运营方审核结果：{result}")

        self._click_row_action(order_id, "审核")
        self.find_visible(self.OPERATIONS_AUDIT_DIALOG)
        result_text = "通过" if normalized_result == "PASS" else "不通过"
        result_label = (
            By.XPATH,
            f"{self.OPERATIONS_AUDIT_DIALOG_XPATH}"
            "//label"
            "[.//span[contains(@class,'el-radio__label')]"
            f"[normalize-space()='{result_text}']]",
        )
        self.click(result_label)
        self._wait().until(
            lambda driver: any(
                element.get_attribute("aria-checked") == "true"
                or "is-checked" in (element.get_attribute("class") or "").split()
                for element in driver.find_elements(*result_label)
            ),
            message=f"运营方审核结果未选中：{result_text}",
        )
        self._input_opinion_stably(opinion)
        self.click(self.OPERATIONS_AUDIT_SUBMIT)
        self._wait_for_operations_audit_result()

        self.driver.refresh()
        self.wait_until_loaded()
        return self.wait_for_order_states(order_id, expected_states)

    def _input_opinion_stably(self, opinion: str) -> None:
        """等待单选项触发的表单重绘结束，并确认审核意见没有被清空。"""

        expected = str(opinion)
        stable_since: float | None = None

        def opinion_is_stable(driver) -> bool:
            nonlocal stable_since
            candidates = [
                element
                for element in driver.find_elements(*self.OPERATIONS_AUDIT_OPINION)
                if element.is_displayed()
            ]
            if not candidates:
                stable_since = None
                return False

            element = candidates[-1]
            if (element.get_attribute("value") or "") != expected:
                self.scroll_to_element(element)
                element.click()
                element.clear()
                element.send_keys(expected)
                element.send_keys(Keys.TAB)
                stable_since = None
                return False

            now = time.monotonic()
            if stable_since is None:
                stable_since = now
                return False
            return now - stable_since >= 0.5

        self._wait().until(
            opinion_is_stable,
            message="运营方审核意见在表单重绘后未能稳定写入",
        )

    def _wait_for_operations_audit_result(self) -> str:
        outcome, detail = self._wait().until(
            lambda driver: self._operations_audit_result(),
            message="提交运营方审核后页面未返回结果",
        )
        if outcome == "failure":
            raise AssertionError(f"运营方审核被页面拦截：{detail}")
        return detail or "运营方审核提交成功"

    def _operations_audit_result(self) -> tuple[str, str] | bool:
        # Element UI 提交成功后可能在弹窗关闭动画期间清空表单，并短暂保留
        # “请输入审核意见”的校验节点。明确的成功消息必须优先于该残留错误。
        successes = [
            element.text.strip()
            for element in self.driver.find_elements(*self.SUCCESS_MESSAGE)
            if element.is_displayed()
        ]
        if successes:
            return ("success", next((text for text in successes if text), ""))

        dialogs = self.driver.find_elements(*self.OPERATIONS_AUDIT_DIALOG)
        if not any(dialog.is_displayed() for dialog in dialogs):
            return ("success", "运营方审核弹窗已关闭")

        errors = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        errors.extend(
            element.text.strip()
            for element in self.driver.find_elements(
                By.XPATH,
                f"{self.OPERATIONS_AUDIT_DIALOG_XPATH}//*"
                "[contains(@class,'el-form-item__error')]",
            )
            if element.is_displayed() and element.text.strip()
        )
        if errors:
            return ("failure", "；".join(dict.fromkeys(errors)))
        return False
