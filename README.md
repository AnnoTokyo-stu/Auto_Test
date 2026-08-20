# 中国电信银河数据跨境平台 Web 自动化测试

基于 Python、Selenium、Page Object 与 Pytest 的 Web UI 主流程自动化项目。测试入口默认为：

```text
http://border.embodatadeglobal.com:18080/system/organization
```

访问该入口后应跳转登录页面。

## 设计目标

- 页面操作、页面对象、测试脚本、测试数据和环境配置分层。
- 默认 Chrome，可通过参数切换 Edge。
- 统一显式等待，不使用固定休眠。
- 失败自动记录日志、截图并附加到 Allure。
- 账号密码只从环境变量读取。
- 本机可通过被忽略的 `.env.local` 自动加载专用测试账号。
- 测试函数严格保留原 Excel 用例编号。
- 默认不操作真实环境；写数据用例需要显式授权参数。

## 快速开始

```powershell
python -m pip install -r requirements.txt
pytest --collect-only
pytest -m smoke --run-ui --browser=chrome
```

执行真实 UI 前必须阅读：

- `docs/元素定位填写指南.md`
- `docs/项目运行指南.md`
- `docs/用例覆盖路线图.md`

数据提供方认证资料填写另请阅读：

- `docs/数据提供方认证运行指南.md`

消息详情自动选行测试另请阅读：

- `docs/消息管理自动识别说明.md`

当前测试用例主表共 95 条，自动化项目已构建 35 个逻辑测试函数：原 73 条用例已构建 19 条，实际测试扩展共 22 条（WEB-074～095，Excel 中完整保留）。数据产品标准订单正向链路已通过 WEB-075～084 覆盖到验收完成和详情核对；WEB-085、WEB-087、WEB-089、WEB-090 已由用户确认真实执行通过，WEB-091 已完成核心反向分支自动化首轮实现、待真实执行；WEB-086、WEB-088 作为文件上传规则手工/可控环境用例保留在 Excel，WEB-092～095 作为人工或受控环境校验用例保留。原用例仍有 54 条待逐批补全，具体状态以 `docs/项目交接文档-2026-08-17.md` 和 `docs/用例覆盖路线图.md` 为准。

## 私有 CI

仓库根目录的 `Jenkinsfile` 定义 Jenkins 持续集成。Push 自动构建仅执行敏感文件检查、Python 编译和用例收集，不访问真实业务系统。需要浏览器或写入业务数据的测试必须通过 Jenkins 参数人工启用，详见 `ci/README.md`。
