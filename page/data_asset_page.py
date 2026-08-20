"""数据资产管理页面对象。"""

from typing import Any

from base.base_page import BasePage, todo_locator


class DataAssetPage(BasePage):
    # ===== TODO：网页可访问后，在此区域填写真实定位器 =====
    ADD_BUTTON = todo_locator("新增数据资产按钮")
    NAME_INPUT = todo_locator("资产名称输入框")
    CATEGORY_SELECT = todo_locator("资产分类下拉框")
    LEVEL_SELECT = todo_locator("资产分级下拉框")
    SOURCE_INPUT = todo_locator("资产来源输入框")
    SAVE_BUTTON = todo_locator("保存资产按钮")
    SUCCESS_MESSAGE = todo_locator("资产保存成功提示")
    ASSET_ID = todo_locator("资产唯一标识")
    ASSET_STATUS = todo_locator("资产状态")
    SEARCH_INPUT = todo_locator("资产查询输入框")
    SEARCH_BUTTON = todo_locator("资产查询按钮")
    RESULT_ID = todo_locator("资产查询结果标识")
    RESULT_CATEGORY = todo_locator("资产查询结果分类")
    RESULT_LEVEL = todo_locator("资产查询结果分级")
    # ===== 定位器填写区域结束 =====

    def create_asset(self, data: dict[str, Any]) -> str:
        self.click(self.ADD_BUTTON)
        self.input(self.NAME_INPUT, data["asset_name"])
        self.select_by_text(self.CATEGORY_SELECT, data["category"])
        self.select_by_text(self.LEVEL_SELECT, data["level"])
        self.input(self.SOURCE_INPUT, data["source"])
        self.click(self.SAVE_BUTTON)
        self.find_visible(self.SUCCESS_MESSAGE)
        return self.get_text(self.ASSET_ID)

    def search(self, asset_id: str) -> dict[str, str]:
        self.input(self.SEARCH_INPUT, asset_id)
        self.click(self.SEARCH_BUTTON)
        return {
            "asset_id": self.get_text(self.RESULT_ID),
            "category": self.get_text(self.RESULT_CATEGORY),
            "level": self.get_text(self.RESULT_LEVEL),
        }
