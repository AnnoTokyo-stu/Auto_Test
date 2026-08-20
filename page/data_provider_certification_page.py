"""数据提供方认证资料填写页面对象。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base.base_page import BasePage, Locator
from config import PROJECT_ROOT


class DataProviderCertificationPage(BasePage):
    """按业务分区封装认证表单，不在页面对象中保存测试数据。"""

    FORM = (
        By.XPATH,
        "//form[.//h2[normalize-space()='主体基本情况']]"
        "[.//h2[contains(normalize-space(.),'经办人')]]",
    )
    SUBJECT_SECTION = (
        "//form/div[./div[contains(@class,'fx-center')]"
        "/h2[normalize-space()='主体基本情况']]"
    )
    LEGAL_SECTION = (
        "//form/div[./div[contains(@class,'fx-center')]"
        "/h2[normalize-space()='法定代表人信息']]"
    )
    OPERATOR_SECTION = (
        "//form/div[./div[contains(@class,'fx-center')]"
        "/h2[contains(normalize-space(.),'经办人')]]"
    )

    COMPANY_NAME = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'单位名称')]]//input",
    )
    PROVINCE = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'单位注册所在省份')]]//input",
    )
    OFFICE_ADDRESS = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'办公所在地')]]//input",
    )
    INDUSTRY = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'所属行业')]]//input",
    )
    UNIFIED_SOCIAL_CREDIT_CODE = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'统一社会信用代码')]]//input",
    )
    REGISTERED_ADDRESS = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'单位注册地址')]]//input",
    )
    EMPLOYEE_COUNT = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'员工数量')]]//input[not(@readonly)]",
    )
    EMPLOYEE_UNIT = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'员工数量')]]"
        "/..//input[@readonly]",
    )
    BUSINESS_LONG_TERM = (
        By.XPATH,
        f"{SUBJECT_SECTION}//label[contains(@class,'el-checkbox')]"
        "[contains(normalize-space(.),'是否长期')]",
    )
    BUSINESS_EXPIRY_DATE = (
        By.XPATH,
        f"{SUBJECT_SECTION}//input[contains(@placeholder,'日期')]",
    )
    ORGANIZATION_NATURE = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'单位性质')]]//input",
    )
    BUSINESS_SCOPE = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'经营范围')]]//input",
    )
    BUSINESS_LICENSE_FILE = (
        By.XPATH,
        f"{SUBJECT_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'统一社会信用代码证')]]"
        "//input[@type='file']",
    )

    NO_LEGAL_REPRESENTATIVE = (
        By.XPATH,
        f"{LEGAL_SECTION}//label[contains(@class,'el-checkbox')]"
        "[contains(normalize-space(.),'无法定代表人')]",
    )
    LEGAL_NAME = (
        By.XPATH,
        f"{LEGAL_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'姓名')]]//input",
    )
    LEGAL_PHONE = (
        By.XPATH,
        f"{LEGAL_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'联系电话')]]"
        "//input[@placeholder='请输入']",
    )
    LEGAL_POSITION = (
        By.XPATH,
        f"{LEGAL_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'职务')]]//input",
    )
    LEGAL_EMAIL = (
        By.XPATH,
        f"{LEGAL_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'邮箱')]]//input",
    )
    LEGAL_ID_TYPE = (
        By.XPATH,
        f"{LEGAL_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'证件类型')]]//input",
    )
    LEGAL_ID_NUMBER = (
        By.XPATH,
        f"{LEGAL_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'证件号码')]]//input",
    )
    LEGAL_ID_FILE = (
        By.XPATH,
        f"{LEGAL_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'证件附件')]]//input[@type='file']",
    )

    OPERATOR_POSITION = (
        By.XPATH,
        f"{OPERATOR_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'职务')]]//input",
    )
    OPERATOR_ID_TYPE = (
        By.XPATH,
        f"{OPERATOR_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'证件类型')]]//input",
    )
    OPERATOR_ID_NUMBER = (
        By.XPATH,
        f"{OPERATOR_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'证件号码')]]//input",
    )
    OPERATOR_ID_FILE = (
        By.XPATH,
        f"{OPERATOR_SECTION}//div[contains(@class,'el-form-item')]"
        "[.//label[contains(normalize-space(.),'证件附件')]]//input[@type='file']",
    )

    CNY_ACCOUNT_CARD = (
        By.XPATH,
        "//div[contains(concat(' ',normalize-space(@class),' '),' account-card ')]"
        "[.//span[contains(concat(' ',normalize-space(@class),' '),"
        "' account-label ') and normalize-space()='CNY人民币账户']]",
    )
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button.save-btn")
    BACK_BUTTON = (By.CSS_SELECTOR, "button.back-btn")

    def wait_until_loaded(self) -> None:
        self.find_visible(self.FORM)

    def fill_complete_application(self, data: dict[str, Any]) -> None:
        self._fill_subject(data["subject"])
        self._fill_legal_representative(data["legal_representative"])
        self._fill_operator(data["operator"])
        self._fill_cny_account(data["cny_account"])

    def _fill_subject(self, data: dict[str, Any]) -> None:
        self.input(self.COMPANY_NAME, data["company_name"])
        self.select_option(self.PROVINCE, data["province"])
        self.input(self.OFFICE_ADDRESS, data["office_address"])
        self.select_option(self.INDUSTRY, data["industry"])
        self.input(self.UNIFIED_SOCIAL_CREDIT_CODE, data["credit_code"])
        self.input(self.REGISTERED_ADDRESS, data["registered_address"])
        self.input(self.EMPLOYEE_COUNT, data["employee_count"])
        self.select_option(self.EMPLOYEE_UNIT, data["employee_unit"])
        if data.get("business_license_long_term", False):
            self._set_checkbox(self.BUSINESS_LONG_TERM, True)
        else:
            self.input(self.BUSINESS_EXPIRY_DATE, data["business_expiry_date"])
        self.select_option(self.ORGANIZATION_NATURE, data["organization_nature"])
        self.input(self.BUSINESS_SCOPE, data["business_scope"])
        self._upload_project_file(
            self.BUSINESS_LICENSE_FILE, data["business_license_file"]
        )

    def _fill_legal_representative(self, data: dict[str, Any]) -> None:
        if data.get("absent", False):
            self._set_checkbox(self.NO_LEGAL_REPRESENTATIVE, True)
            return
        self.input(self.LEGAL_NAME, data["name"])
        self.input(self.LEGAL_PHONE, data["phone"])
        self.input(self.LEGAL_POSITION, data["position"])
        self.input(self.LEGAL_EMAIL, data["email"])
        self.select_option(self.LEGAL_ID_TYPE, data["id_type"])
        self.input(self.LEGAL_ID_NUMBER, data["id_number"])
        self._upload_project_file(self.LEGAL_ID_FILE, data["id_file"])

    def _fill_operator(self, data: dict[str, Any]) -> None:
        self.input(self.OPERATOR_POSITION, data["position"])
        self.select_option(self.OPERATOR_ID_TYPE, data["id_type"])
        self.input(self.OPERATOR_ID_NUMBER, data["id_number"])
        self._upload_project_file(self.OPERATOR_ID_FILE, data["id_file"])

    def _fill_cny_account(self, data: dict[str, Any]) -> None:
        self.click(self.CNY_ACCOUNT_CARD)
        dialog = self._wait_for_cny_dialog()
        self._dialog_input(dialog, "收款公司中文全称", data["company_name"])
        self._dialog_input(dialog, "人民币对公收款账号", data["account_number"])
        self._dialog_input(dialog, "开户行（中文）", data["bank_name"])
        self._dialog_input(dialog, "开户支行（中文）", data["branch_name"])
        self._dialog_input(dialog, "预设转账附言", data["remittance_note"])
        confirm = dialog.find_element(
            By.XPATH,
            ".//button[contains(@class,'el-button--primary')]"
            "[.//span[normalize-space()='确定']]",
        )
        confirm.click()
        self._wait().until(
            lambda driver: "未配置"
            not in driver.find_element(*self.CNY_ACCOUNT_CARD).text,
            message="人民币收款账户确认后仍显示未配置",
        )

    def _wait_for_cny_dialog(self) -> WebElement:
        """等待 CNY 弹窗；若打开了其他币种，立即给出明确错误。"""

        def _visible_account_dialog(driver) -> WebElement | bool:
            dialogs = driver.find_elements(
                By.XPATH,
                "//div[contains(concat(' ',normalize-space(@class),' '),"
                "' el-dialog ')]",
            )
            visible = [dialog for dialog in dialogs if dialog.is_displayed()]
            if not visible:
                return False
            dialog = visible[-1]
            title = dialog.find_element(
                By.XPATH,
                ".//div[contains(concat(' ',normalize-space(@class),' '),"
                "' el-dialog__header ')]",
            ).text.strip()
            if "CNY人民币账户" not in title:
                raise AssertionError(
                    f"期望打开 CNY人民币账户，实际打开：{title or '未知弹窗'}"
                )
            return dialog

        return self._wait().until(
            _visible_account_dialog,
            message="点击 CNY 卡片后人民币账户弹窗未出现",
        )

    def select_option(self, input_locator: Locator, text: str) -> None:
        self.click(input_locator)

        def _visible_option(driver) -> WebElement | bool:
            options = driver.find_elements(
                By.XPATH,
                "//li[contains(@class,'el-select-dropdown__item')]",
            )
            visible = [option for option in options if option.is_displayed()]
            expected = str(text).strip()
            exact = next(
                (option for option in visible if option.text.strip() == expected),
                None,
            )
            if exact:
                return exact
            return next(
                (
                    option
                    for option in visible
                    if expected in option.text.strip()
                    or option.text.strip() in expected
                ),
                False,
            )

        self._wait().until(
            _visible_option,
            message=f"下拉选项未出现：{text}",
        ).click()

    def is_ready_for_review(self, data: dict[str, Any]) -> bool:
        expected_values = (
            (self.COMPANY_NAME, data["subject"]["company_name"]),
            (
                self.UNIFIED_SOCIAL_CREDIT_CODE,
                data["subject"]["credit_code"],
            ),
            (self.LEGAL_NAME, data["legal_representative"]["name"]),
            (
                self.LEGAL_ID_NUMBER,
                data["legal_representative"]["id_number"],
            ),
            (self.OPERATOR_POSITION, data["operator"]["position"]),
            (self.OPERATOR_ID_NUMBER, data["operator"]["id_number"]),
        )
        values_match = all(
            (self.get_attribute(locator, "value") or "").strip() == str(value)
            for locator, value in expected_values
        )
        account_configured = "未配置" not in self.get_text(self.CNY_ACCOUNT_CARD)
        return (
            values_match
            and account_configured
            and self.find_visible(self.SUBMIT_BUTTON).is_enabled()
        )

    @staticmethod
    def validate_attachment_files(data: dict[str, Any]) -> None:
        allowed_suffixes = {".png", ".jpg", ".jpeg", ".pdf"}
        relative_paths = (
            data["subject"]["business_license_file"],
            data["legal_representative"]["id_file"],
            data["operator"]["id_file"],
        )
        for value in relative_paths:
            target = Path(value)
            if not target.is_absolute():
                target = PROJECT_ROOT / target
            if not target.is_file():
                raise FileNotFoundError(f"认证测试附件不存在：{target}")
            if target.suffix.lower() not in allowed_suffixes:
                raise ValueError(f"认证测试附件格式不允许：{target.name}")
            if target.stat().st_size > 2 * 1024 * 1024:
                raise ValueError(f"认证测试附件超过 2 MB：{target.name}")

    def _set_checkbox(self, locator: Locator, checked: bool) -> None:
        checkbox = self.find_visible(locator)
        native_checkbox = checkbox.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        current = native_checkbox.is_selected()
        if current != checked:
            self.scroll_to_element(checkbox)
            checkbox.click()

    def _upload_project_file(self, locator: Locator, path: str) -> None:
        target = Path(path)
        if not target.is_absolute():
            target = PROJECT_ROOT / target
        self.upload(locator, target)
        checked = self._validate_locator(locator)

        def _file_selected(driver) -> bool:
            file_input = driver.find_element(*checked)
            return bool(
                driver.execute_script(
                    """
                    const input = arguments[0];
                    const expectedName = arguments[1];
                    const selected = input.files && input.files.length > 0
                        && input.files[0].name === expectedName;
                    const formItem = input.closest('.el-form-item');
                    const previewReady = formItem
                        && Array.from(formItem.querySelectorAll('img')).some(
                            image => image.complete && image.naturalWidth > 0
                        );
                    return Boolean(selected || previewReady);
                    """,
                    file_input,
                    target.name,
                )
            )

        self._wait().until(
            _file_selected,
            message=f"浏览器未接收上传文件：{target.name}",
        )

    def _dialog_input(self, dialog: WebElement, label: str, value: Any) -> None:
        element = dialog.find_element(
            By.XPATH,
            ".//div[contains(@class,'el-form-item')]"
            f"[.//label[contains(normalize-space(.),'{label}')]]//input",
        )
        self.log.info("填写人民币收款账户字段：%s", label)
        self.input_element(element, value)
        expected = str(value)
        self._wait().until(
            lambda driver: (element.get_attribute("value") or "") == expected,
            message=f"人民币收款账户字段写入失败：{label}",
        )
