"""消息管理与待办管理页面对象。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base.base_page import BasePage


@dataclass(frozen=True)
class MessageRecord:
    """从消息列表一行解析出的稳定业务数据。"""

    message_id: str
    title: str
    content: str
    sent_at: str
    status: str


class MessageTodoPage(BasePage):
    MESSAGE_TAB = (By.ID, "tab-message")
    MESSAGE_PANE = (By.ID, "pane-message")
    MESSAGE_ROWS = (
        By.CSS_SELECTOR,
        "#pane-message .el-table__body-wrapper tbody > tr",
    )
    QUERY_BUTTON = (
        By.XPATH,
        "//*[@id='pane-message']//button[.//span[normalize-space()='查询']]",
    )
    MARK_ALL_READ_BUTTON = (
        By.XPATH,
        "//*[@id='pane-message']//button[.//span[normalize-space()='全部已读']]",
    )
    NEXT_PAGE_BUTTON = (
        By.CSS_SELECTOR,
        "#pane-message .el-pagination .btn-next",
    )
    PAGE_NUMBER_BUTTONS = (
        By.CSS_SELECTOR,
        "#pane-message .el-pagination .el-pager > li.number",
    )
    DETAIL_DIALOGS = (
        By.CSS_SELECTOR,
        "#pane-message .el-dialog__wrapper",
    )

    def wait_until_loaded(self) -> None:
        self.find_visible(self.MESSAGE_TAB)
        self.find_visible(self.MESSAGE_PANE)
        self.find_present(self.MARK_ALL_READ_BUTTON)

    def is_mark_all_read_available(self) -> bool:
        """只检查“全部已读”可操作性，不点击、不改变生产消息。"""

        return self.find_visible(self.MARK_ALL_READ_BUTTON).is_enabled()

    def find_and_open_message(
        self,
        *,
        status: str,
        message_id: str = "",
        title_contains: str = "",
        max_pages: int = 20,
    ) -> MessageRecord | None:
        """按 ID/状态/标题自动选行，并点击该行内部的详情按钮。"""

        self._go_to_first_page()
        for _ in range(max_pages):
            match = self._matching_row(
                status=status,
                message_id=message_id,
                title_contains=title_contains,
            )
            if match is not None:
                record, row = match
                self.log.info(
                    "自动选择消息：id=%s, status=%s, title=%s",
                    record.message_id,
                    record.status,
                    record.title,
                )
                detail_button = row.find_element(
                    By.XPATH,
                    ".//button[.//span[normalize-space()='详情']]",
                )
                self.scroll_to_element(detail_button)
                detail_button.click()
                self._wait_for_detail_dialog()
                return record
            if not self._go_to_next_page():
                return None
        return None

    def detail_dialog_text(self) -> str:
        return self._visible_detail_dialog().text.strip()

    def is_detail_action_available(self) -> bool:
        dialog = self._visible_detail_dialog()
        action = dialog.find_element(
            By.XPATH,
            ".//button[.//span[normalize-space()='点击查看']]",
        )
        return action.is_displayed() and action.is_enabled()

    def close_detail(self) -> None:
        dialog = self._visible_detail_dialog()
        close_button = dialog.find_element(
            By.CSS_SELECTOR,
            ".el-dialog__headerbtn",
        )
        close_button.click()
        self._wait().until(
            lambda driver: not self._visible_detail_dialog_or_false(),
            message="消息详情弹窗未关闭",
        )

    def refresh_list(self) -> None:
        """使用页面查询刷新状态，不刷新浏览器、不丢失当前会话。"""

        self.click(self.QUERY_BUTTON)
        self.find_present(self.MESSAGE_ROWS)

    def wait_for_message_status(
        self,
        message_id: str,
        expected: str,
        max_pages: int = 20,
    ) -> bool:
        """按消息 ID 跨页复核状态，不依赖打开详情前所在页。"""

        self._go_to_first_page()
        for _ in range(max_pages):
            for row in self.find_all(self.MESSAGE_ROWS):
                record = self._parse_row(row)
                if record and record.message_id == message_id:
                    assert record.status == expected, (
                        f"消息 {message_id} 期望状态为{expected}，"
                        f"实际为{record.status}"
                    )
                    return True
            if not self._go_to_next_page():
                break
        raise AssertionError(f"刷新后未找到消息：{message_id}")

    def _matching_row(
        self,
        *,
        status: str,
        message_id: str,
        title_contains: str,
    ) -> tuple[MessageRecord, WebElement] | None:
        for row in self.find_all(self.MESSAGE_ROWS):
            record = self._parse_row(row)
            if record is None or record.status != status:
                continue
            if message_id and record.message_id != message_id:
                continue
            if title_contains and title_contains not in record.title:
                continue
            return record, row
        return None

    @staticmethod
    def _parse_row(row: WebElement) -> MessageRecord | None:
        try:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if len(cells) < 6:
                return None
            values = [cell.text.strip() for cell in cells]
            status = values[4].replace("•", "").strip()
            return MessageRecord(
                message_id=values[0],
                title=values[1],
                content=values[2],
                sent_at=values[3],
                status=status,
            )
        except StaleElementReferenceException:
            return None

    def _wait_for_detail_dialog(self) -> WebElement:
        return self._wait().until(
            lambda driver: self._visible_detail_dialog_or_false(),
            message="点击详情后消息弹窗未出现",
        )

    def _visible_detail_dialog(self) -> WebElement:
        dialog = self._visible_detail_dialog_or_false()
        if not dialog:
            raise AssertionError("当前没有可见的消息详情弹窗")
        return dialog

    def _visible_detail_dialog_or_false(self) -> WebElement | bool:
        dialogs = self.driver.find_elements(*self.DETAIL_DIALOGS)
        return next((dialog for dialog in dialogs if dialog.is_displayed()), False)

    def _go_to_next_page(self) -> bool:
        buttons = self.driver.find_elements(*self.NEXT_PAGE_BUTTON)
        if not buttons:
            return False
        button = buttons[0]
        classes = button.get_attribute("class") or ""
        if button.get_attribute("disabled") is not None or "disabled" in classes:
            return False
        old_ids = [
            record.message_id
            for row in self.driver.find_elements(*self.MESSAGE_ROWS)
            if (record := self._parse_row(row)) is not None
        ]
        self.scroll_to_element(button)
        button.click()
        self._wait().until(
            lambda driver: [
                record.message_id
                for row in driver.find_elements(*self.MESSAGE_ROWS)
                if (record := self._parse_row(row)) is not None
            ]
            != old_ids,
            message="点击下一页后消息列表未更新",
        )
        return True

    def _go_to_first_page(self) -> None:
        page_buttons = self.driver.find_elements(*self.PAGE_NUMBER_BUTTONS)
        first_page = next(
            (button for button in page_buttons if button.text.strip() == "1"),
            None,
        )
        if first_page is None:
            return
        classes = first_page.get_attribute("class") or ""
        if "active" in classes:
            return
        old_ids = [
            record.message_id
            for row in self.driver.find_elements(*self.MESSAGE_ROWS)
            if (record := self._parse_row(row)) is not None
        ]
        self.scroll_to_element(first_page)
        first_page.click()
        self._wait().until(
            lambda driver: [
                record.message_id
                for row in driver.find_elements(*self.MESSAGE_ROWS)
                if (record := self._parse_row(row)) is not None
            ]
            != old_ids,
            message="返回消息第一页后列表未更新",
        )

    def _row_snapshot(self, rows: list[WebElement]) -> list[tuple[str, str]]:
        snapshot: list[tuple[str, str]] = []
        for row in rows:
            record = self._parse_row(row)
            if record:
                snapshot.append((record.message_id, record.status))
        return snapshot
