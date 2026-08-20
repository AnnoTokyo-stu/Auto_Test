"""框架自定义异常。"""


class AutomationFrameworkError(RuntimeError):
    """自动化测试框架基础异常。"""


class LocatorNotConfiguredError(AutomationFrameworkError):
    """页面定位器仍为 TODO 占位时抛出。"""


class TestDataNotConfiguredError(AutomationFrameworkError):
    """运行所需测试数据尚未配置时抛出。"""
