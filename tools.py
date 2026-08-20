"""驱动、日志、测试数据等公共工具。"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

from config import (
    DATA_DIR,
    DOWNLOAD_DIR,
    LOG_DIR,
    REPORT_DIR,
    REPORT_HTML_DIR,
    SCREENSHOT_DIR,
    SETTINGS,
    SUPPORTED_BROWSERS,
    TODO_VALUE,
)
from base.exceptions import TestDataNotConfiguredError


_ENV_PATTERN = re.compile(r"^\$\{([A-Z][A-Z0-9_]*)\}$")


def ensure_runtime_directories() -> None:
    """创建执行过程需要的输出目录。"""

    for path in (
        LOG_DIR,
        REPORT_DIR,
        REPORT_HTML_DIR,
        SCREENSHOT_DIR,
        DOWNLOAD_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


class LogFactory:
    """创建按天轮转且全项目复用的日志器。"""

    _logger: logging.Logger | None = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is not None:
            return cls._logger

        ensure_runtime_directories()
        logger = logging.getLogger("web_automation")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if not logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
            file_handler = TimedRotatingFileHandler(
                LOG_DIR / "web.log",
                when="midnight",
                interval=1,
                backupCount=7,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        cls._logger = logger
        return logger


def load_json(file_name: str) -> Any:
    """读取 data 目录下的 UTF-8 JSON，并解析完整环境变量占位符。"""

    path = DATA_DIR / file_name
    if not path.is_file():
        raise FileNotFoundError(f"测试数据文件不存在：{path}")
    with path.open("r", encoding="utf-8") as file:
        return _resolve_env_placeholders(json.load(file))


def load_case_data(file_name: str, case_id: str) -> list[dict[str, Any]]:
    """按 Excel 用例编号筛选参数化数据。"""

    data = load_json(file_name)
    if not isinstance(data, list):
        raise TypeError(f"{file_name} 顶层必须是 JSON 数组")
    rows = [item for item in data if item.get("case_id") == case_id]
    if not rows:
        raise TestDataNotConfiguredError(
            f"{file_name} 中未配置用例 {case_id} 的测试数据"
        )
    return rows


def _resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _resolve_env_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_env_placeholders(item) for item in value]
    if isinstance(value, str):
        match = _ENV_PATTERN.fullmatch(value)
        if match:
            return os.getenv(match.group(1), value)
    return value


def require_value(value: Any, description: str) -> Any:
    """在真实 UI 执行前校验运行数据已经补齐。"""

    if value in (None, "", TODO_VALUE) or (
        isinstance(value, str) and _ENV_PATTERN.fullmatch(value)
    ):
        raise TestDataNotConfiguredError(f"待补充测试数据：{description}")
    return value


def require_env(name: str) -> str:
    """读取必需环境变量，缺失时给出不泄露敏感值的提示。"""

    value = os.getenv(name)
    if not value:
        raise TestDataNotConfiguredError(f"未设置环境变量：{name}")
    return value


def unique_name(prefix: str) -> str:
    """生成并发安全的测试实体名称。"""

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}_{uuid.uuid4().hex[:6]}"


def mask_sensitive(value: str, visible: int = 2) -> str:
    """日志输出前遮蔽账号、手机号等敏感内容。"""

    if not value:
        return ""
    if len(value) <= visible * 2:
        return "*" * len(value)
    return f"{value[:visible]}{'*' * (len(value) - visible * 2)}{value[-visible:]}"


class DriverFactory:
    """按参数创建 Chrome 或 Edge WebDriver。默认 Chrome。"""

    @staticmethod
    def create(
        browser: str = SETTINGS.browser,
        *,
        headless: bool = SETTINGS.headless,
        driver_path: str | None = SETTINGS.driver_path,
    ):
        browser = browser.strip().lower()
        if browser not in SUPPORTED_BROWSERS:
            raise ValueError(
                f"不支持的浏览器：{browser}；可选值：{', '.join(SUPPORTED_BROWSERS)}"
            )

        ensure_runtime_directories()
        if browser == "chrome":
            return DriverFactory._create_chrome(headless, driver_path)
        return DriverFactory._create_edge(headless, driver_path)

    @staticmethod
    def _common_arguments(headless: bool) -> list[str]:
        arguments = [
            "--disable-notifications",
            "--disable-popup-blocking",
            "--no-first-run",
            "--no-default-browser-check",
            f"--window-size={SETTINGS.window_width},{SETTINGS.window_height}",
        ]
        if headless:
            arguments.append("--headless=new")
        return arguments

    @staticmethod
    def _create_chrome(headless: bool, driver_path: str | None):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        options = Options()
        options.page_load_strategy = SETTINGS.page_load_strategy
        for argument in DriverFactory._common_arguments(headless):
            options.add_argument(argument)
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(DOWNLOAD_DIR),
                "download.prompt_for_download": False,
            },
        )
        service = Service(executable_path=driver_path) if driver_path else Service()
        return webdriver.Chrome(service=service, options=options)

    @staticmethod
    def _create_edge(headless: bool, driver_path: str | None):
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.edge.service import Service

        options = Options()
        options.page_load_strategy = SETTINGS.page_load_strategy
        for argument in DriverFactory._common_arguments(headless):
            options.add_argument(argument)
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(DOWNLOAD_DIR),
                "download.prompt_for_download": False,
            },
        )
        service = Service(executable_path=driver_path) if driver_path else Service()
        return webdriver.Edge(service=service, options=options)
