"""项目级配置。

所有可变配置优先从环境变量读取，避免切换浏览器、地址或等待时间时修改测试代码。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_ENV_FILE = PROJECT_ROOT / ".env.local"

# 本地文件只作为默认值；系统、终端和 PyCharm 已设置的变量拥有更高优先级。
load_dotenv(LOCAL_ENV_FILE, override=False)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


@dataclass(frozen=True)
class Settings:
    """从环境变量加载的不可变运行设置。"""

    base_url: str = os.getenv(
        "WEB_BASE_URL", "http://border.embodatadeglobal.com:18080"
    ).rstrip("/")
    entry_path: str = os.getenv("WEB_ENTRY_PATH", "/system/organization")
    browser: str = os.getenv("WEB_BROWSER", "chrome").strip().lower()
    headless: bool = _env_bool("WEB_HEADLESS", False)
    fast_input: bool = _env_bool("WEB_FAST_INPUT", True)
    explicit_wait: int = _env_int("WEB_EXPLICIT_WAIT", 10)
    page_load_timeout: int = _env_int("WEB_PAGE_LOAD_TIMEOUT", 30)
    manual_captcha_timeout: int = _env_int("WEB_MANUAL_CAPTCHA_TIMEOUT", 120)
    manual_email_code_timeout: int = _env_int(
        "WEB_MANUAL_EMAIL_CODE_TIMEOUT", 300
    )
    page_load_strategy: str = os.getenv(
        "WEB_PAGE_LOAD_STRATEGY", "normal"
    ).strip().lower()
    driver_path: str | None = os.getenv("WEB_DRIVER_PATH") or None
    window_width: int = _env_int("WEB_WINDOW_WIDTH", 1440)
    window_height: int = _env_int("WEB_WINDOW_HEIGHT", 900)

    @property
    def entry_url(self) -> str:
        path = self.entry_path if self.entry_path.startswith("/") else f"/{self.entry_path}"
        return f"{self.base_url}{path}"


SETTINGS = Settings()

DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "log"
REPORT_DIR = PROJECT_ROOT / "report"
REPORT_HTML_DIR = PROJECT_ROOT / "report-html"
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"
DOWNLOAD_DIR = PROJECT_ROOT / "downloads"

SUPPORTED_BROWSERS = ("chrome", "edge")
TODO_VALUE = "__TO_BE_CONFIRMED__"
