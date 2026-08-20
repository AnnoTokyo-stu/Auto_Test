"""数据提供方的数据产品管理页面对象。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base.base_page import BasePage, Locator
from config import PROJECT_ROOT


class DataProductPage(BasePage):
    """封装列表查询、新增长表单、草稿保存和提交审核操作。"""

    def __init__(self, driver, timeout: int | None = None) -> None:
        super().__init__(driver, timeout)
        self._cover_path: Path | None = None

    PAGE_TITLE = (
        By.XPATH,
        "//*[self::h1 or self::h2 or self::h3 or self::div]"
        "[normalize-space()='数据产品管理']",
    )
    NAME_SEARCH_INPUT = (
        By.CSS_SELECTOR,
        "form input[placeholder='请输入产品名称']",
    )
    QUERY_BUTTON = (
        By.XPATH,
        "//section//button[.//span[normalize-space()='查询']]",
    )
    ADD_BUTTON = (
        By.XPATH,
        "//section//button[.//span[normalize-space()='新增数据产品']]",
    )
    TABLE_ROWS = (
        By.CSS_SELECTOR,
        ".el-table__body-wrapper tbody > tr",
    )
    ACTION_ROWS = (
        By.CSS_SELECTOR,
        ".el-table__fixed-right .el-table__fixed-body-wrapper tbody > tr",
    )
    PRODUCT_NAME_COLUMN_INDEX = 2

    DIALOG = (
        By.XPATH,
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//*[normalize-space()='新增数据产品']]",
    )
    DIALOG_XPATH = (
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[.//*[normalize-space()='新增数据产品']]"
    )
    PRODUCT_NAME = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请输入产品名称']",
    )
    PRODUCT_VERSION = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请输入产品版本']",
    )
    PRODUCT_COVER = (
        By.XPATH,
        f"{DIALOG_XPATH}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'产品封面图')]]"
        "//input[@type='file']",
    )
    PRODUCT_IMAGE = (
        By.XPATH,
        f"{DIALOG_XPATH}//div[contains(@class,'el-form-item')]"
        "[.//label[normalize-space()='产品图片']]//input[@type='file']",
    )
    PRODUCT_INTRO = (
        By.XPATH,
        f"{DIALOG_XPATH}//textarea[@placeholder='请输入产品简介']",
    )
    BUSINESS_SCENE = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请选择业务场景分类']",
    )
    TASK_TYPE = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请选择任务类型']",
    )
    SCENE_DESCRIPTION = (
        By.XPATH,
        f"{DIALOG_XPATH}//textarea[@placeholder='请输入场景描述']",
    )
    TASK_GOAL = (
        By.XPATH,
        f"{DIALOG_XPATH}//textarea[@placeholder='请输入任务目标说明']",
    )
    SAMPLE_DATA_FILE = (
        By.XPATH,
        f"{DIALOG_XPATH}//div[contains(@class,'el-form-item')]"
        "[.//label[normalize-space()='样例数据文件']]//input[@type='file']",
    )
    DATA_DOCUMENT_FILE = (
        By.XPATH,
        f"{DIALOG_XPATH}//div[contains(@class,'el-form-item')]"
        "[.//label[normalize-space()='数据说明文档']]//input[@type='file']",
    )
    DATA_FORMAT = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请选择数据格式']",
    )
    ANNOTATION_STATUS = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请选择标注情况']",
    )
    ANNOTATION_CONTENT = (
        By.XPATH,
        f"{DIALOG_XPATH}//textarea[@placeholder='请输入标注内容说明']",
    )
    DATA_QUALITY = (
        By.XPATH,
        f"{DIALOG_XPATH}//textarea[@placeholder='请输入数据质量说明']",
    )
    FIELD_STRUCTURE = (
        By.XPATH,
        f"{DIALOG_XPATH}//textarea[@placeholder='请输入字段结构说明']",
    )
    PRICING_MODE = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请选择计价模式']",
    )
    CURRENCY = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请选择币种']",
    )
    FIXED_PRICE = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请输入固定价格']",
    )
    PRICE_DESCRIPTION = (
        By.XPATH,
        f"{DIALOG_XPATH}//textarea[@placeholder='请输入价格说明']",
    )
    DELIVERY_CYCLE = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请选择交付周期']",
    )
    COMPLIANCE_TEMPLATE = (
        By.XPATH,
        f"{DIALOG_XPATH}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'合规策略')]]//input",
    )
    ATTACHMENT_FILE = (
        By.XPATH,
        f"{DIALOG_XPATH}//div[contains(@class,'el-form-item')]"
        "[.//label[normalize-space()='附件材料']]//input[@type='file']",
    )
    BUSINESS_CONTACT = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请输入业务联系人']",
    )
    CONTACT_EMAIL = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请输入联系邮箱']",
    )
    CONTACT_PHONE = (
        By.XPATH,
        f"{DIALOG_XPATH}//input[@placeholder='请输入联系电话']",
    )
    SAVE_DRAFT_BUTTON = (
        By.XPATH,
        f"{DIALOG_XPATH}//button[.//span[normalize-space()='保存草稿']]",
    )
    SUBMIT_REVIEW_BUTTON = (
        By.XPATH,
        f"{DIALOG_XPATH}//button[.//span[normalize-space()='提交审核']]",
    )
    DIALOG_CLOSE_BUTTON = (
        By.XPATH,
        f"{DIALOG_XPATH}//button[contains(@class,'el-dialog__headerbtn')]",
    )
    SUCCESS_MESSAGE = (
        By.CSS_SELECTOR,
        ".el-message.el-message--success",
    )
    ERROR_MESSAGE = (
        By.CSS_SELECTOR,
        ".el-message.el-message--error",
    )
    FORM_ERRORS = (
        By.XPATH,
        f"{DIALOG_XPATH}//*[contains(@class,'el-form-item__error')]",
    )
    CONFIRM_SUBMIT_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'el-message-box__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "//button[.//span[normalize-space()='确定']]",
    )
    CHANGE_DIALOG = (
        By.XPATH,
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//textarea[@placeholder='请输入产品简介']]"
        "[.//button[.//span[normalize-space()='提交审核']]]",
    )
    CHANGE_DIALOG_XPATH = (
        "//div[contains(@class,'el-dialog__wrapper')]"
        "[not(contains(@style,'display: none'))]"
        "[contains(@class,'data-asset-trade-page')]"
        "[.//textarea[@placeholder='请输入产品简介']]"
        "[.//button[.//span[normalize-space()='提交审核']]]"
    )
    CHANGE_PRODUCT_INTRO = (
        By.XPATH,
        f"{CHANGE_DIALOG_XPATH}//textarea[@placeholder='请输入产品简介']",
    )
    CHANGE_SUBMIT_REVIEW_BUTTON = (
        By.XPATH,
        f"{CHANGE_DIALOG_XPATH}//button[.//span[normalize-space()='提交审核']]",
    )
    CHANGE_FORM_ERRORS = (
        By.XPATH,
        f"{CHANGE_DIALOG_XPATH}//*[contains(@class,'el-form-item__error')]",
    )

    def wait_until_loaded(self) -> None:
        self.find_visible(self.PAGE_TITLE)
        self.find_visible(self.ADD_BUTTON)

    def start_new_product(self) -> None:
        self.click(self.ADD_BUTTON)
        self.find_visible(self.DIALOG)

    def fill_product(self, data: dict[str, Any]) -> None:
        """按页面分区填写产品；字段和数据保持分离。"""

        self.input(self.PRODUCT_NAME, data["product_name"])
        self.input(self.PRODUCT_VERSION, data.get("product_version", "V1.0"))
        self._cover_path = self._material(data["cover_file"])
        self.upload(self.PRODUCT_COVER, self._cover_path)
        self._wait_for_upload_ready(self.PRODUCT_COVER, "产品封面图")
        if data.get("product_image"):
            self.upload(self.PRODUCT_IMAGE, self._material(data["product_image"]))
            self._wait_for_upload_ready(self.PRODUCT_IMAGE, "产品图片")
        self.input(self.PRODUCT_INTRO, data["product_intro"])

        self._select_option(self.BUSINESS_SCENE, data["business_scene"])
        self._select_option(self.TASK_TYPE, data["task_type"])
        self._choose_label("难度等级", data["difficulty"])
        self.input(self.SCENE_DESCRIPTION, data.get("scene_description", ""))
        self.input(self.TASK_GOAL, data.get("task_goal", ""))

        for data_type in data["package_data_types"]:
            self._choose_label("压缩包包含数据类型", data_type)
        if data.get("sample_data_file"):
            self.upload(
                self.SAMPLE_DATA_FILE,
                self._material(data["sample_data_file"]),
            )
        if data.get("data_document_file"):
            self.upload(
                self.DATA_DOCUMENT_FILE,
                self._material(data["data_document_file"]),
            )

        self._select_option(self.DATA_FORMAT, data["data_format"])
        self._select_option(self.ANNOTATION_STATUS, data["annotation_status"])
        self.input(self.ANNOTATION_CONTENT, data.get("annotation_content", ""))
        self.input(self.DATA_QUALITY, data.get("data_quality", ""))
        self.input(self.FIELD_STRUCTURE, data.get("field_structure", ""))

        # 当前定位资料仅覆盖“一口价”的参数区域；其他计价模型后续单独扩展。
        if data["pricing_mode"] != "一口价":
            raise ValueError("当前自动化只支持已完成定位的一口价计价模式")
        self._select_option(self.PRICING_MODE, data["pricing_mode"])
        self._select_option(self.CURRENCY, data["currency"])
        self.input(self.FIXED_PRICE, data["fixed_price"])
        self.input(self.PRICE_DESCRIPTION, data.get("price_description", ""))

        self._select_option(self.DELIVERY_CYCLE, data["delivery_cycle"])
        if data.get("compliance_template"):
            self._select_option(
                self.COMPLIANCE_TEMPLATE,
                data["compliance_template"],
            )
        if data.get("attachment_file"):
            self.upload(
                self.ATTACHMENT_FILE,
                self._material(data["attachment_file"]),
            )

        self.input(self.BUSINESS_CONTACT, data["business_contact"])
        self.input(self.CONTACT_EMAIL, data["contact_email"])
        self.input(self.CONTACT_PHONE, data["contact_phone"])

    def save_draft(self) -> None:
        self.click(self.SAVE_DRAFT_BUTTON)
        self._wait_for_submission_outcome("保存草稿")

    def submit_for_review(self) -> None:
        try:
            self._submit_review_once()
        except AssertionError as error:
            if "请上传产品封面图" not in str(error) or self._cover_path is None:
                raise
            self.log.warning("页面未保存产品封面，重新上传后重试提交")
            self._reset_file_input(self.PRODUCT_COVER)
            self.upload(self.PRODUCT_COVER, self._cover_path)
            self._wait_for_upload_ready(self.PRODUCT_COVER, "产品封面图")
            self._submit_review_once()

    def _submit_review_once(self) -> None:
        self.click(self.SUBMIT_REVIEW_BUTTON)
        self._wait_for_submission_outcome("提交审核", allow_confirm=True)

    def search_product(self, product_name: str) -> str:
        self.input(self.NAME_SEARCH_INPUT, product_name)
        self.click(self.QUERY_BUTTON)
        row = self._wait().until(
            lambda driver: self._unique_product_row(product_name),
            message=f"产品列表未唯一匹配：{product_name}",
        )
        return row.text.strip()

    def wait_for_product_states(
        self,
        product_name: str,
        *expected_states: str,
    ) -> str:
        """重新查询并等待唯一目标行出现全部预期状态。"""

        self.input(self.NAME_SEARCH_INPUT, product_name)
        self.click(self.QUERY_BUTTON)
        row = self._wait().until(
            lambda driver: self._row_with_states(product_name, expected_states),
            message=(
                f"产品状态未更新：{product_name}，"
                f"预期包含 {'、'.join(expected_states)}"
            ),
        )
        return row.text.strip()

    def put_on_shelf(self, product_name: str) -> str:
        """将唯一匹配且审核通过的产品上架。"""

        self.search_product(product_name)
        self._click_row_action(product_name, "上架")
        return self.wait_for_product_states(product_name, "已上架")

    def take_off_shelf(self, product_name: str) -> str:
        """将唯一匹配的已上架产品下架。"""

        self.search_product(product_name)
        self._click_row_action(product_name, "下架")
        return self.wait_for_product_states(product_name, "已下架")

    def change_and_submit_for_review(
        self,
        product_name: str,
        changed_intro: str,
    ) -> None:
        """打开已下架产品的变更表单，修改简介并提交变更审核。"""

        self.search_product(product_name)
        self._click_row_action(product_name, "变更", wait_for_result=False)
        self.find_visible(self.CHANGE_DIALOG)
        self.input(self.CHANGE_PRODUCT_INTRO, changed_intro)
        submit = self.find_visible(self.CHANGE_SUBMIT_REVIEW_BUTTON)
        self._wait().until(
            lambda driver: submit.is_enabled()
            and "is-disabled" not in (submit.get_attribute("class") or ""),
            message="修改产品简介后，变更提交审核按钮仍不可用",
        )
        self.click(self.CHANGE_SUBMIT_REVIEW_BUTTON)
        self._wait_for_change_submission_outcome()

    def _unique_product_row(self, product_name: str) -> WebElement | bool:
        indexes = self._matching_row_indexes(product_name)
        if len(indexes) != 1:
            return False
        rows = self.driver.find_elements(*self.TABLE_ROWS)
        return rows[indexes[0]] if indexes[0] < len(rows) else False

    def _row_with_states(
        self,
        product_name: str,
        expected_states: tuple[str, ...],
    ) -> WebElement | bool:
        row = self._unique_product_row(product_name)
        if not row:
            return False
        text = row.text.strip()
        return row if all(state in text for state in expected_states) else False

    def _matching_row_indexes(self, product_name: str) -> list[int]:
        indexes: list[int] = []
        for index, row in enumerate(self.driver.find_elements(*self.TABLE_ROWS)):
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
                f"无法安全确定产品操作目标：{product_name}，匹配数 {len(indexes)}"
            )
        action_rows = self.find_all(self.ACTION_ROWS)
        if indexes[0] >= len(action_rows):
            raise AssertionError("产品操作列与产品列表行数不一致")
        return action_rows[indexes[0]]

    def _click_row_action(
        self,
        product_name: str,
        action_text: str,
        *,
        wait_for_result: bool = True,
    ) -> None:
        self._wait_for_transient_messages_to_clear()
        action_row = self._action_row_for(product_name)
        buttons = action_row.find_elements(
            By.XPATH,
            f".//button[.//span[normalize-space()={self._xpath_literal(action_text)}]]",
        )
        visible = [button for button in buttons if button.is_displayed()]
        if len(visible) != 1:
            raise AssertionError(
                f"产品 {product_name} 的“{action_text}”按钮匹配数不是 1：{len(visible)}"
            )
        button = visible[0]
        self.scroll_to_element(button)
        try:
            button.click()
        except ElementClickInterceptedException:
            self.log.info("%s按钮被固定列表层遮挡，改用唯一目标元素的 JS 点击", action_text)
            self.driver.execute_script("arguments[0].click();", button)
        if wait_for_result:
            self._wait_for_list_action_outcome(action_text)

    def _wait_for_transient_messages_to_clear(self) -> None:
        """避免把上一个连续操作尚未消失的提示当成本次结果。"""

        self._wait().until(
            lambda driver: not any(
                element.is_displayed()
                for locator in (self.SUCCESS_MESSAGE, self.ERROR_MESSAGE)
                for element in driver.find_elements(*locator)
            ),
            message="上一操作提示在超时后仍未消失",
        )

    def _wait_for_list_action_outcome(self, action_text: str) -> None:
        outcome, detail = self._wait().until(
            lambda driver: self._list_action_outcome(),
            message=f"{action_text}后页面未返回确认或执行结果",
        )
        if outcome == "confirm":
            self.click(self.CONFIRM_SUBMIT_BUTTON)
            outcome, detail = self._wait().until(
                lambda driver: self._list_action_outcome(ignore_confirm=True),
                message=f"确认{action_text}后页面未返回执行结果",
            )
        if outcome == "failure":
            raise AssertionError(f"{action_text}失败：{detail}")

    def _list_action_outcome(
        self,
        *,
        ignore_confirm: bool = False,
    ) -> tuple[str, str] | bool:
        if not ignore_confirm:
            confirms = self.driver.find_elements(*self.CONFIRM_SUBMIT_BUTTON)
            if any(element.is_displayed() for element in confirms):
                return ("confirm", "")
        errors = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        if errors:
            return ("failure", "；".join(errors))
        successes = self.driver.find_elements(*self.SUCCESS_MESSAGE)
        if any(element.is_displayed() for element in successes):
            return ("success", "")
        return False

    def _wait_for_change_submission_outcome(self) -> None:
        outcome, detail = self._wait().until(
            lambda driver: self._change_submission_outcome(True),
            message="提交变更审核后页面未返回成功或校验结果",
        )
        if outcome == "confirm":
            self.click(self.CONFIRM_SUBMIT_BUTTON)
            outcome, detail = self._wait().until(
                lambda driver: self._change_submission_outcome(False),
                message="确认提交变更审核后页面未返回结果",
            )
        if outcome == "failure":
            raise AssertionError(f"提交变更审核被页面拦截：{detail}")
        if outcome != "closed":
            self.wait_gone(self.CHANGE_DIALOG)

    def _change_submission_outcome(
        self,
        allow_confirm: bool,
    ) -> tuple[str, str] | bool:
        if allow_confirm:
            confirms = self.driver.find_elements(*self.CONFIRM_SUBMIT_BUTTON)
            if any(element.is_displayed() for element in confirms):
                return ("confirm", "")
        errors = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        errors.extend(
            element.text.strip()
            for element in self.driver.find_elements(*self.CHANGE_FORM_ERRORS)
            if element.is_displayed() and element.text.strip()
        )
        if errors:
            return ("failure", "；".join(dict.fromkeys(errors)))
        dialogs = self.driver.find_elements(*self.CHANGE_DIALOG)
        if not any(element.is_displayed() for element in dialogs):
            return ("closed", "")
        successes = self.driver.find_elements(*self.SUCCESS_MESSAGE)
        if any(element.is_displayed() for element in successes):
            return ("success", "")
        return False

    def _select_option(self, input_locator: Locator, text: str) -> None:
        """只在当前可见浮层中选择，避免命中弹窗后方的列表文本。"""

        input_element = self.find_visible(input_locator)
        self.scroll_to_element(input_element)
        input_element.click()
        element = self._wait().until(
            lambda driver: self._visible_overlay_option(text),
            message=f"下拉选项不可用：{text}",
        )
        self.scroll_to_element(element)
        try:
            element.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            # 浮层动画或内部文本节点可能短暂拦截原生点击，重新取当前浮层元素。
            element = self._wait().until(
                lambda driver: self._visible_overlay_option(text),
                message=f"下拉选项点击前已失效：{text}",
            )
            self.driver.execute_script("arguments[0].click();", element)
        self._wait().until(
            lambda driver: (
                (self.find_present(input_locator).get_attribute("value") or "").strip()
                == text
            ),
            message=f"选择后字段未回填：{text}",
        )

    def _choose_label(self, group_label: str, option_text: str) -> None:
        locator = (
            By.XPATH,
            f"{self.DIALOG_XPATH}//div[contains(@class,'el-form-item')]"
            f"[.//label[contains(normalize-space(.),{self._xpath_literal(group_label)})]]"
            f"//label[contains(normalize-space(.),{self._xpath_literal(option_text)})]",
        )
        element = self.find_visible(locator)
        classes = element.get_attribute("class") or ""
        if "is-checked" not in classes:
            self.scroll_to_element(element)
            element.click()

    def _wait_for_submission_outcome(
        self,
        operation: str,
        *,
        allow_confirm: bool = False,
    ) -> None:
        """同时监听成功、弹窗关闭、确认框及校验错误，避免漏掉短暂提示。"""

        outcome, detail = self._wait().until(
            lambda driver: self._submission_outcome(allow_confirm),
            message=f"{operation}后页面未返回成功或校验结果",
        )
        if outcome == "confirm":
            self.click(self.CONFIRM_SUBMIT_BUTTON)
            outcome, detail = self._wait().until(
                lambda driver: self._submission_outcome(False),
                message=f"确认{operation}后页面未返回结果",
            )
        if outcome == "failure":
            raise AssertionError(f"{operation}被页面拦截：{detail}")
        if outcome == "closed":
            return

        try:
            self.wait_gone(self.DIALOG)
        except TimeoutException:
            self.click(self.DIALOG_CLOSE_BUTTON)
            self.wait_gone(self.DIALOG)

    def _submission_outcome(
        self,
        allow_confirm: bool,
    ) -> tuple[str, str] | bool:
        if allow_confirm:
            confirms = self.driver.find_elements(*self.CONFIRM_SUBMIT_BUTTON)
            if any(element.is_displayed() for element in confirms):
                return ("confirm", "")

        error_messages = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        if error_messages:
            return ("failure", "；".join(error_messages))

        form_errors = [
            element.text.strip()
            for element in self.driver.find_elements(*self.FORM_ERRORS)
            if element.is_displayed() and element.text.strip()
        ]
        if form_errors:
            return ("failure", "；".join(dict.fromkeys(form_errors)))

        dialogs = self.driver.find_elements(*self.DIALOG)
        if not any(element.is_displayed() for element in dialogs):
            return ("closed", "")

        successes = self.driver.find_elements(*self.SUCCESS_MESSAGE)
        if any(element.is_displayed() for element in successes):
            return ("success", "")
        return False

    def _wait_for_upload_ready(
        self,
        input_locator: Locator,
        description: str,
    ) -> None:
        try:
            outcome, detail = self._wait(8).until(
                lambda driver: self._upload_outcome(input_locator),
                message=f"{description}上传组件未暴露完成状态",
            )
        except TimeoutException:
            self.log.info(
                "%s已选择文件；页面未暴露标准完成状态，交由提交校验确认",
                description,
            )
            return
        if outcome == "failure":
            raise AssertionError(f"{description}上传失败：{detail}")
        self.log.info("%s上传完成", description)

    def _upload_outcome(
        self,
        input_locator: Locator,
    ) -> tuple[str, str] | bool:
        error_messages = [
            element.text.strip()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
            if element.is_displayed() and element.text.strip()
        ]
        if error_messages:
            return ("failure", "；".join(error_messages))

        input_element = self.driver.find_element(*input_locator)
        state = self.driver.execute_script(
            """
            const input = arguments[0];
            const root = input.closest('.el-form-item') || input.parentElement;
            if (!root) return {status: 'pending', detail: ''};
            const items = Array.from(root.querySelectorAll(
                '.el-upload-list__item, [class*="upload-list"] [class*="item"]'
            ));
            const failed = items.find(item =>
                item.classList.contains('is-fail') ||
                item.classList.contains('is-error')
            );
            if (failed) {
                return {
                    status: 'failure',
                    detail: failed.innerText.trim() || '上传组件返回失败状态'
                };
            }
            const succeeded = items.find(item =>
                item.classList.contains('is-success')
            );
            if (succeeded) return {status: 'success', detail: ''};
            const preview = Array.from(root.querySelectorAll('img')).find(img =>
                img.src && img.getBoundingClientRect().width > 0
            );
            if (preview) return {status: 'success', detail: ''};
            const trigger = input.closest('.el-upload');
            if (trigger && getComputedStyle(trigger).display === 'none') {
                return {status: 'success', detail: ''};
            }
            return {status: 'pending', detail: ''};
            """,
            input_element,
        )
        if state["status"] == "success":
            return ("success", "")
        if state["status"] == "failure":
            return ("failure", state["detail"])
        return False

    def _reset_file_input(self, locator: Locator) -> None:
        element = self.find_present(locator)
        self.driver.execute_script(
            "arguments[0].value = ''; arguments[0].dispatchEvent("
            "new Event('change', {bubbles: true}));",
            element,
        )

    def _visible_overlay_option(self, text: str) -> WebElement | bool:
        """从最上层可见 Element UI 浮层中寻找精确文本选项。"""

        literal = self._xpath_literal(text)
        containers = self.driver.find_elements(
            By.CSS_SELECTOR,
            ".el-select-dropdown, .el-cascader__dropdown, "
            ".el-dialog__wrapper, .el-popover",
        )
        for container in reversed(containers):
            try:
                if not container.is_displayed():
                    continue
                candidates = container.find_elements(
                    By.XPATH,
                    ".//li[contains(@class,'el-select-dropdown__item')]"
                    f"[normalize-space(.)={literal}]"
                    " | .//li[contains(@class,'el-cascader-node')]"
                    f"[normalize-space(.)={literal}]"
                    f" | .//td[normalize-space(.)={literal}]"
                    f" | .//button[normalize-space(.)={literal}]"
                    f" | .//span[normalize-space(.)={literal}]",
                )
                option = next(
                    (
                        item
                        for item in candidates
                        if item.is_displayed() and item.is_enabled()
                    ),
                    None,
                )
                if option is not None:
                    return option
            except StaleElementReferenceException:
                continue
        return False

    @staticmethod
    def _xpath_literal(value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"

    @staticmethod
    def _material(relative_path: str) -> Path:
        path = (PROJECT_ROOT / relative_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"测试附件不存在：{path}")
        return path
