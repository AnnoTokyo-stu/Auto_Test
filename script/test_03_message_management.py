"""消息管理：WEB-074 自动识别已读与未读消息详情。"""

import allure
import pytest

from page.message_todo_page import MessageTodoPage
from page.user_portal_page import UserPortalPage
from tools import load_case_data


pytestmark = [
    pytest.mark.ui,
    pytest.mark.message,
    pytest.mark.p0,
    pytest.mark.destructive,
]


@allure.epic("中国电信银河数据跨境平台")
@allure.feature("消息与待办")
@allure.title("WEB-074 消息管理—自动识别已读与未读详情")
def test_web_074_auto_select_read_and_unread_message_details(
    driver,
    login_as,
    data_provider_credentials,
    configured_case,
):
    data = configured_case(
        load_case_data("message_data.json", "WEB-074")[0],
        "selections",
    )

    with allure.step("登录并进入消息待办管理"):
        navigation = login_as(data_provider_credentials)
        navigation.open_operations_console()
        portal = UserPortalPage(driver)
        portal.wait_until_navigation_loaded()
        portal.open_message_todo_management()
        messages = MessageTodoPage(driver)
        messages.wait_until_loaded()

    with allure.step("只验证全部已读按钮可用，不触发批量状态变更"):
        assert messages.is_mark_all_read_available(), "全部已读按钮不可用"

    for selection in data["selections"]:
        status = selection["status"]
        with allure.step(f"自动选择一条{status}消息并打开详情"):
            record = messages.find_and_open_message(
                status=status,
                message_id=selection.get("message_id", ""),
                title_contains=selection.get("title_contains", ""),
            )
            assert record is not None, f"当前测试账号没有可用于 WEB-074 的{status}消息"
            allure.attach(
                f"消息ID：{record.message_id}\n标题：{record.title}\n"
                f"发送时间：{record.sent_at}\n操作前状态：{record.status}",
                name=f"自动选中的{status}消息",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert messages.detail_dialog_text(), "消息详情弹窗内容为空"
            assert messages.is_detail_action_available(), "详情内点击查看按钮不可用"
            messages.close_detail()

        with allure.step(f"验证{status}消息打开详情后的状态"):
            messages.refresh_list()
            assert messages.wait_for_message_status(record.message_id, "已读")
