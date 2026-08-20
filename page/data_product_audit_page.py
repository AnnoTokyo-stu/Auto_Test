"""超级管理员的数据产品审核页面对象。"""

from __future__ import annotations

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base.base_page import BasePage


class DataProductAuditPage(BasePage):
    """按唯一产品名称选行，避免审核列表中的其他真实产品。"""

    PRODUCT_NAME_COLUMN_INDEX = 2

    PAGE_TITLE = (
        By.XPATH,
        "//*[self::h1 or self::h2 or self::h3 or self::div]"
        "[normalize-space()='数据产品审核']",
    )
    PRODUCT_NAME_INPUT = (
        By.XPATH,
        "//section//div[contains(@class,'el-form-item')]"
        "[.//*[normalize-space()='产品名称']]//input",
    )
    QUERY_BUTTON = (
        By.XPATH,
        "//section//button[.//span[normalize-space()='查询']]",
    )
    MAIN_ROWS = (
        By.CSS_SELECTOR,
        ".el-table__body-wrapper tbody > tr",
    )
    ACTION_ROWS = (
        By.CSS_SELECTOR,
        ".el-table__fixed-right .el-table__fixed-body-wrapper tbody > tr",
    )
    AUDIT_DIALOG = (
        By.XPATH,
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//*[normalize-space()='审核']]",
    )
    AUDIT_DIALOG_XPATH = (
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//*[normalize-space()='审核']]"
    )
    OPINION_INPUT = (
        By.XPATH,
        f"{AUDIT_DIALOG_XPATH}//textarea[@placeholder='请输入审核意见']",
    )
    SUBMIT_RESULT_BUTTON = (
        By.XPATH,
        f"{AUDIT_DIALOG_XPATH}//button"
        "[.//span[normalize-space()='提交审核结果']]",
    )
    SUCCESS_MESSAGE = (
        By.CSS_SELECTOR,
        ".el-message.el-message--success",
    )

    def wait_until_loaded(self) -> None:
        self.find_visible(self.PAGE_TITLE)
        self.find_visible(self.QUERY_BUTTON)

    def search_unique_product(self, product_name: str) -> None:
        """筛选后必须恰好命中一条产品，否则不允许继续审核。"""

        self.input(self.PRODUCT_NAME_INPUT, product_name)
        self.click(self.QUERY_BUTTON)

        matches = self._wait().until(
            lambda driver: (
                current
                if len(current := self._matching_row_indexes(product_name)) == 1
                else False
            ),
            message=f"管理员审核列表未唯一匹配产品：{product_name}",
        )
        if len(matches) != 1:
            raise AssertionError(
                f"产品名称匹配数量不是 1：{product_name}，实际 {len(matches)}"
            )

    def approve(self, product_name: str, opinion: str) -> None:
        self.search_unique_product(product_name)
        action_row = self._action_row_for(product_name)
        audit_button = action_row.find_element(
            By.XPATH,
            ".//button[.//span[normalize-space()='审核']]",
        )
        self.scroll_to_element(audit_button)
        try:
            audit_button.click()
        except ElementClickInterceptedException:
            # Element UI 的固定右列会与横向滚动主体重叠。目标行已通过
            # 完整产品名称唯一确认，此处可安全触发该确定按钮的 DOM 点击。
            self.log.info("审核按钮被表格层遮挡，改用唯一目标元素的 JS 点击")
            self.driver.execute_script("arguments[0].click();", audit_button)
        self.find_visible(self.AUDIT_DIALOG)
        self._choose_result("通过")
        self.input(self.OPINION_INPUT, opinion)
        self.click(self.SUBMIT_RESULT_BUTTON)
        self.find_visible(self.SUCCESS_MESSAGE)
        self.wait_gone(self.AUDIT_DIALOG)

    def wait_until_audit_record_available(self, product_name: str) -> bool:
        self.search_unique_product(product_name)
        action_row = self._action_row_for(product_name)
        return any(
            button.is_displayed()
            for button in action_row.find_elements(
                By.XPATH,
                ".//button[.//span[normalize-space()='审核记录']]",
            )
        )

    def _choose_result(self, result: str) -> None:
        label = self.find_visible(
            (
                By.XPATH,
                f"{self.AUDIT_DIALOG_XPATH}//label"
                f"[normalize-space(.)={self._xpath_literal(result)}]",
            )
        )
        if "is-checked" not in (label.get_attribute("class") or ""):
            label.click()

    def _matching_row_indexes(self, product_name: str) -> list[int]:
        indexes: list[int] = []
        for index, row in enumerate(self.driver.find_elements(*self.MAIN_ROWS)):
            try:
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if (
                    row.is_displayed()
                    and len(cells) > self.PRODUCT_NAME_COLUMN_INDEX
                    and cells[self.PRODUCT_NAME_COLUMN_INDEX].text.strip()
                    == product_name
                ):
                    indexes.append(index)
            except StaleElementReferenceException:
                continue
        return indexes

    def _action_row_for(self, product_name: str) -> WebElement:
        indexes = self._matching_row_indexes(product_name)
        if len(indexes) != 1:
            raise AssertionError(
                f"无法安全确定审核目标：{product_name}，匹配数 {len(indexes)}"
            )
        action_rows = self.find_all(self.ACTION_ROWS)
        if indexes[0] >= len(action_rows):
            raise AssertionError("审核操作列与产品列表行数不一致")
        return action_rows[indexes[0]]

    @staticmethod
    def _xpath_literal(value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"
