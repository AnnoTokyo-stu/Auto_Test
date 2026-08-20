"""数据使用方的数据交易市场与产品下单页面对象。"""

from __future__ import annotations

from datetime import date
import re

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base.base_page import BasePage


class DataMarketplacePage(BasePage):
    """按唯一产品名称选择卡片并提交采购订单。"""

    PAGE_SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='产品名称/编号/简介']")
    SEARCH_BUTTON = (By.XPATH, "//button[.//span[normalize-space()='搜索']]")
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".product-grid .product-card")
    ORDER_NOW_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'detail-wrap')]"
        "//button[.//span[normalize-space()='立即下单']]",
    )
    ORDER_DIALOG = (
        By.XPATH,
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//*[normalize-space()='提交采购订单']]",
    )
    ORDER_DIALOG_XPATH = (
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//*[normalize-space()='提交采购订单']]"
    )
    PURCHASE_PURPOSE = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//input[contains(@placeholder,'请输入采购用途')]",
    )
    EXPECTED_DELIVERY_DATE = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//input[@placeholder='请选择期望交付时间']",
    )
    DATE_TIME_PANEL_XPATH = (
        "//body/div[contains(@class,'el-picker-panel')]"
        "[contains(@class,'el-date-picker')]"
        "[contains(@class,'has-time')]"
        "[contains(@class,'order-dialog-datetime')]"
    )
    DATE_TIME_PANEL = (By.XPATH, DATE_TIME_PANEL_XPATH)
    DATE_TIME_CONFIRM = (
        By.XPATH,
        f"{DATE_TIME_PANEL_XPATH}"
        "//div[contains(@class,'el-picker-panel__footer')]"
        "//button[.//span[normalize-space()='确定']]",
    )
    QUANTITY_INPUT = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//input[@role='spinbutton']",
    )
    ORDER_REMARK = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//textarea[@placeholder='请输入订单备注']",
    )
    CONTACT_NAME = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//input[@placeholder='请输入联系人']",
    )
    CONTACT_PHONE = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//input[@placeholder='请输入联系电话']",
    )
    CONTACT_EMAIL = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//input[@placeholder='请输入联系人邮箱']",
    )
    SUBMIT_ORDER_BUTTON = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//button[.//span[normalize-space()='提交订单']]",
    )
    ORDER_SUCCESS_DIALOG_XPATH = (
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//*[normalize-space()='下单成功']]"
        "[.//*[contains(normalize-space(.),'订单提交成功')]]"
    )
    ORDER_SUCCESS_DIALOG = (By.XPATH, ORDER_SUCCESS_DIALOG_XPATH)
    GO_TO_ORDER_MANAGEMENT = (
        By.XPATH,
        f"{ORDER_SUCCESS_DIALOG_XPATH}"
        "//button[.//span[normalize-space()='立即前往']]",
    )
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".el-message.el-message--success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".el-message.el-message--error")
    FORM_ERRORS = (
        By.XPATH,
        f"{ORDER_DIALOG_XPATH}//*[contains(@class,'el-form-item__error')]",
    )

    def wait_until_loaded(self) -> None:
        self.find_visible(self.PAGE_SEARCH_INPUT)
        self.find_visible(self.SEARCH_BUTTON)

    def search_unique_product(self, product_name: str) -> str:
        self.input(self.PAGE_SEARCH_INPUT, product_name)
        self.click(self.SEARCH_BUTTON)
        card = self._wait().until(
            lambda driver: self._unique_matching_card(product_name),
            message=f"交易市场未唯一匹配已上架产品：{product_name}",
        )
        return card.text.strip()

    def search_single_product(
        self,
        keyword: str,
        expected_name_prefix: str,
    ) -> str:
        """提交关键词后，从结果卡片中按产品名称前缀唯一匹配产品。"""

        self.input(self.PAGE_SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)
        card = self._wait().until(
            lambda driver: self._unique_prefix_card(expected_name_prefix),
            message=(
                "交易市场未按产品名称前缀唯一匹配已上架产品："
                f"{expected_name_prefix}（搜索词：{keyword}）"
            ),
        )
        visible_count = len(self._visible_product_cards())
        if visible_count > 1:
            self.log.info(
                "产品编号搜索未缩小结果，已从 %s 张卡片中按名称前缀唯一匹配：%s",
                visible_count,
                expected_name_prefix,
            )
        names = [
            element.text.strip()
            for element in card.find_elements(By.CSS_SELECTOR, ".product-name")
            if element.is_displayed() and element.text.strip()
        ]
        if len(names) != 1:
            raise AssertionError(f"唯一产品卡片未显示唯一名称：{keyword}")
        return names[0]

    def open_unique_product_detail(
        self,
        product_name: str,
        expected_product_number: str = "",
    ) -> None:
        card = self._unique_matching_card(product_name)
        if not card:
            raise AssertionError(f"打开详情前未唯一匹配产品：{product_name}")
        self.scroll_to_element(card)
        try:
            card.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", card)
        self.find_visible(self.ORDER_NOW_BUTTON)
        def detail_matches(driver) -> bool:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            return product_name in body_text and (
                not expected_product_number
                or expected_product_number in body_text
            )

        self._wait().until(
            detail_matches,
            message=(
                f"详情页未显示目标产品：{product_name}"
                + (
                    f" / {expected_product_number}"
                    if expected_product_number
                    else ""
                )
            ),
        )

    def submit_order(self, data: dict[str, object]) -> str:
        self.click(self.ORDER_NOW_BUTTON)
        self.find_visible(self.ORDER_DIALOG)
        self.input(self.PURCHASE_PURPOSE, data["purchase_purpose"])
        self._input_date(str(data["expected_delivery_date"]))
        self.input(self.QUANTITY_INPUT, data.get("quantity", 1))
        if data.get("order_remark"):
            self.input(self.ORDER_REMARK, data["order_remark"])
        self._fill_if_empty(
            self.CONTACT_NAME,
            data.get("order_contact_name", ""),
        )
        self._fill_if_empty(
            self.CONTACT_PHONE,
            data.get("order_contact_phone", ""),
        )
        self._fill_if_empty(
            self.CONTACT_EMAIL,
            data.get("order_contact_email", ""),
        )
        self.click(self.SUBMIT_ORDER_BUTTON)
        return self._wait_for_order_result()

    def go_to_order_management(self) -> None:
        """在十秒倒计时结束前点击立即前往，并等待订单管理路由。"""

        self.find_visible(self.ORDER_SUCCESS_DIALOG)
        self.click(self.GO_TO_ORDER_MANAGEMENT)
        self._wait().until(
            lambda driver: "/dataAssetTrade/product-order" in driver.current_url,
            message="点击立即前往后未跳转产品订单管理页面",
        )

    def _input_date(self, date_text: str) -> None:
        target = date.fromisoformat(date_text[:10])
        element = self.find_visible(self.EXPECTED_DELIVERY_DATE)
        self.scroll_to_element(element)
        element.click()
        self.find_visible(self.DATE_TIME_PANEL)
        self._move_calendar_to(target)

        panel = self.find_visible(self.DATE_TIME_PANEL)
        day_cells = panel.find_elements(
            By.XPATH,
            ".//table[contains(@class,'el-date-table')]//td"
            "[contains(@class,'available')]"
            "[not(contains(@class,'disabled'))]"
            "[not(contains(@class,'prev-month'))]"
            "[not(contains(@class,'next-month'))]"
            f"[.//span[normalize-space()='{target.day}']]",
        )
        visible_cells = [cell for cell in day_cells if cell.is_displayed()]
        if len(visible_cells) != 1:
            raise AssertionError(
                f"日期控件未唯一匹配可选交付日期：{target.isoformat()}"
            )
        self.scroll_to_element(visible_cells[0])
        visible_cells[0].click()
        self.click(self.DATE_TIME_CONFIRM)

        self._wait().until(
            lambda driver: target.isoformat()
            in (element.get_attribute("value") or ""),
            message=f"期望交付时间未写入订单表单：{target.isoformat()}",
        )
        self.log.info("已选择期望交付时间：%s", element.get_attribute("value"))

    def _move_calendar_to(self, target: date) -> None:
        """将 Element UI 日期面板切换到目标年月。"""

        for _ in range(24):
            current_year, current_month = self._calendar_year_month()
            month_delta = (target.year - current_year) * 12 + (
                target.month - current_month
            )
            if month_delta == 0:
                return
            panel = self.find_visible(self.DATE_TIME_PANEL)
            button_class = (
                ".el-date-picker__next-btn.el-icon-arrow-right"
                if month_delta > 0
                else ".el-date-picker__prev-btn.el-icon-arrow-left"
            )
            old_month = (current_year, current_month)
            panel.find_element(By.CSS_SELECTOR, button_class).click()
            self._wait().until(
                lambda driver: self._calendar_year_month() != old_month,
                message="日期控件切换月份后未刷新",
            )
        raise AssertionError(f"日期控件无法切换到目标月份：{target:%Y-%m}")

    def _calendar_year_month(self) -> tuple[int, int]:
        panel = self.find_visible(self.DATE_TIME_PANEL)
        labels = panel.find_elements(
            By.CSS_SELECTOR,
            ".el-date-picker__header .el-date-picker__header-label",
        )
        if len(labels) < 2:
            raise AssertionError("日期控件未显示年份和月份标题")
        year_match = re.search(r"\d+", labels[0].text)
        month_match = re.search(r"\d+", labels[1].text)
        if not year_match or not month_match:
            raise AssertionError(
                f"无法解析日期控件年月：{[label.text for label in labels[:2]]}"
            )
        return int(year_match.group()), int(month_match.group())

    def _fill_if_empty(self, locator, fallback: object) -> None:
        element = self.find_visible(locator)
        if not (element.get_attribute("value") or "").strip():
            if not fallback:
                raise AssertionError(f"页面未回填必填联系人数据：{locator[1]}")
            self.input_element(element, fallback)

    def _unique_matching_card(self, product_name: str) -> WebElement | bool:
        matches: list[WebElement] = []
        for card in self.driver.find_elements(*self.PRODUCT_CARDS):
            if not card.is_displayed():
                continue
            names = card.find_elements(By.CSS_SELECTOR, ".product-name")
            if len(names) == 1 and names[0].text.strip() == product_name:
                matches.append(card)
        return matches[0] if len(matches) == 1 else False

    def _visible_product_cards(self) -> list[WebElement]:
        return [
            card
            for card in self.driver.find_elements(*self.PRODUCT_CARDS)
            if card.is_displayed()
        ]

    def _unique_prefix_card(self, product_name_prefix: str) -> WebElement | bool:
        matches: list[WebElement] = []
        for card in self._visible_product_cards():
            names = [
                element.text.strip()
                for element in card.find_elements(By.CSS_SELECTOR, ".product-name")
                if element.is_displayed() and element.text.strip()
            ]
            if len(names) == 1 and names[0].startswith(product_name_prefix):
                matches.append(card)
        return matches[0] if len(matches) == 1 else False

    def _wait_for_order_result(self) -> str:
        outcome, detail = self._wait().until(
            lambda driver: self._order_result(),
            message="提交订单后页面未返回成功或校验结果",
        )
        if outcome == "failure":
            raise AssertionError(f"提交订单被页面拦截：{detail}")
        return detail or "订单提交成功"

    def _order_result(self) -> tuple[str, str] | bool:
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
        success_dialogs = [
            element
            for element in self.driver.find_elements(*self.ORDER_SUCCESS_DIALOG)
            if element.is_displayed()
        ]
        if success_dialogs:
            return ("success", success_dialogs[0].text.strip())
        successes = [
            element.text.strip()
            for element in self.driver.find_elements(*self.SUCCESS_MESSAGE)
            if element.is_displayed()
        ]
        if successes:
            return ("success", next((text for text in successes if text), ""))
        return False
