"""页面对象共享的 Selenium 原子操作。"""

from __future__ import annotations

from pathlib import Path
from typing import TypeAlias

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from base.exceptions import LocatorNotConfiguredError
from config import SETTINGS
from tools import LogFactory


Locator: TypeAlias = tuple[str, str]


def todo_locator(description: str) -> Locator:
    """生成可被框架识别的待填写定位器。"""

    return ("TODO", description)


class BasePage:
    """仅封装通用浏览器操作，不包含具体业务断言。"""

    def __init__(self, driver: WebDriver, timeout: int | None = None) -> None:
        self.driver = driver
        self.timeout = timeout or SETTINGS.explicit_wait
        self.log = LogFactory.get_logger()

    def open(self, url_or_path: str) -> None:
        url = (
            url_or_path
            if url_or_path.startswith(("http://", "https://"))
            else f"{SETTINGS.base_url}/{url_or_path.lstrip('/')}"
        )
        self.log.info("打开页面：%s", url)
        self.driver.get(url)

    def find_visible(self, locator: Locator, timeout: int | None = None) -> WebElement:
        return self._wait(timeout).until(
            EC.visibility_of_element_located(self._validate_locator(locator))
        )

    def find_present(self, locator: Locator, timeout: int | None = None) -> WebElement:
        return self._wait(timeout).until(
            EC.presence_of_element_located(self._validate_locator(locator))
        )

    def find_all(self, locator: Locator, timeout: int | None = None) -> list[WebElement]:
        return self._wait(timeout).until(
            EC.presence_of_all_elements_located(self._validate_locator(locator))
        )

    def click(self, locator: Locator, timeout: int | None = None) -> None:
        checked = self._validate_locator(locator)
        self.log.info("点击元素：%s", checked)
        element = self._wait(timeout).until(EC.presence_of_element_located(checked))
        self.scroll_to_element(element)
        self._wait(timeout).until(EC.element_to_be_clickable(element)).click()

    def input(self, locator: Locator, text: object, *, clear: bool = True) -> None:
        self.input_element(self.find_visible(locator), text, clear=clear)

    def input_element(
        self,
        element: WebElement,
        text: object,
        *,
        clear: bool = True,
    ) -> None:
        """输入文本；默认使用事件兼容的快速赋值，失败时回退到 send_keys。"""

        self.scroll_to_element(element)
        value = str(text)
        if not clear:
            value = f"{element.get_attribute('value') or ''}{value}"

        if SETTINGS.fast_input and element.tag_name.lower() in {"input", "textarea"}:
            try:
                self.driver.execute_script(
                    """
                    const element = arguments[0];
                    const value = arguments[1];
                    const prototype = element.tagName === 'TEXTAREA'
                        ? window.HTMLTextAreaElement.prototype
                        : window.HTMLInputElement.prototype;
                    const descriptor = Object.getOwnPropertyDescriptor(
                        prototype, 'value'
                    );
                    if (!descriptor || !descriptor.set) {
                        throw new Error('native value setter unavailable');
                    }
                    element.focus();
                    descriptor.set.call(element, value);
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    """,
                    element,
                    value,
                )
                return
            except Exception:
                self.log.warning("快速输入失败，回退到 send_keys", exc_info=True)

        if clear:
            element.clear()
        element.send_keys(str(text))

    def upload(self, locator: Locator, file_path: str | Path) -> None:
        path = Path(file_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"上传文件不存在：{path}")
        self.log.info("上传文件：%s", path.name)
        element = self.find_present(locator)
        if element.is_displayed():
            self.scroll_to_element(element)
        element.send_keys(str(path))

    def scroll_to(self, locator: Locator, timeout: int | None = None) -> WebElement:
        """将目标滚动到视口中部，并返回元素。"""

        element = self.find_present(locator, timeout)
        self.scroll_to_element(element)
        return element

    def scroll_to_element(self, element: WebElement) -> None:
        """滚动窗口及可滚动祖先，使长页面中的目标进入可操作区域。"""

        self.driver.execute_script(
            """
            arguments[0].scrollIntoView({
                // Chromium 支持 instant，可避免页面 CSS 的 smooth 滚动拖慢长表单。
                behavior: 'instant',
                block: 'center',
                inline: 'nearest'
            });
            """,
            element,
        )

    def select_by_text(self, locator: Locator, text: str) -> None:
        Select(self.find_visible(locator)).select_by_visible_text(text)

    def select_by_value(self, locator: Locator, value: str) -> None:
        Select(self.find_visible(locator)).select_by_value(value)

    def get_text(self, locator: Locator) -> str:
        return self.find_visible(locator).text.strip()

    def get_attribute(self, locator: Locator, name: str) -> str | None:
        return self.find_present(locator).get_attribute(name)

    def is_visible(self, locator: Locator, timeout: int = 2) -> bool:
        try:
            self.find_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def wait_text(self, locator: Locator, text: str) -> bool:
        return self._wait().until(
            EC.text_to_be_present_in_element(self._validate_locator(locator), text)
        )

    def wait_url_contains(self, value: str) -> bool:
        return self._wait().until(EC.url_contains(value))

    def wait_url_changes(self, old_url: str) -> bool:
        return self._wait().until(EC.url_changes(old_url))

    def wait_gone(self, locator: Locator) -> bool:
        return self._wait().until(
            EC.invisibility_of_element_located(self._validate_locator(locator))
        )

    def switch_to_frame(self, locator: Locator) -> None:
        self._wait().until(
            EC.frame_to_be_available_and_switch_to_it(self._validate_locator(locator))
        )

    def switch_to_default_content(self) -> None:
        self.driver.switch_to.default_content()

    def switch_to_new_window(self, original_handles: set[str]) -> None:
        self._wait().until(lambda driver: len(driver.window_handles) > len(original_handles))
        new_handle = next(
            handle for handle in self.driver.window_handles if handle not in original_handles
        )
        self.driver.switch_to.window(new_handle)

    def refresh(self) -> None:
        self.driver.refresh()

    def back(self) -> None:
        self.driver.back()

    def screenshot(self, path: str | Path) -> bool:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        return self.driver.save_screenshot(str(target))

    def _wait(self, timeout: int | None = None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or self.timeout)

    @staticmethod
    def _validate_locator(locator: Locator) -> Locator:
        if not isinstance(locator, tuple) or len(locator) != 2:
            raise LocatorNotConfiguredError(f"定位器必须是二元元组：{locator!r}")
        by, value = locator
        if by == "TODO" or not value:
            raise LocatorNotConfiguredError(
                f"页面元素定位器尚未填写：{value or locator!r}。"
                "请参照 docs/元素定位填写指南.md 完成定位。"
            )
        return locator
