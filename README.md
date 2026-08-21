# 数据跨境平台 Web 自动化测试

> 最后核对日期：2026-08-21
> 仓库属性：GitHub 私有仓库
> 自动化现状：以核心业务主流程为主，已实现少量关键反向场景；大量分支、边界、权限、并发、容错和跨模块下游核验尚未自动化。

本项目是基于 Python、Selenium、Page Object 和 Pytest 的 Web UI 自动化测试工程，覆盖账户认证、申报合同、数据产品、交易订单、支付、交付、存证和归档等模块。项目支持本地运行、PyCharm 调试、Allure 报告以及 GitHub 私有仓库 + Jenkins 持续集成。

本文档是项目的主入口和交接基线。新接手人应先完整阅读本文件，再按需查阅 `docs/` 下的专项说明。

## 1. 当前范围与覆盖结论

### 1.1 数量口径

| 项目 | 当前数量 | 说明 |
| --- | ---: | --- |
| Excel 设计用例 | 95 | 编号 WEB-001～WEB-095，见 [`docs/测试用例.xlsx`](docs/测试用例.xlsx) |
| 自动化逻辑测试函数 | 35 | 分布在 `script/test_*.py` 的 10 个文件中 |
| 尚无对应自动化函数的 Excel 用例 | 60 | 需要后续按风险和数据可控程度分批实现 |

注意：**Excel 中存在测试设计，不代表对应功能已经自动化，也不代表已经在真实环境执行通过。** 自动化函数还可能因为账号、业务编号、附件、验证码或生产确认参数缺失而被跳过。

### 1.2 已覆盖重点

- 注册、登录、退出及未登录访问控制。
- 数据提供方认证资料填写的半自动流程。
- 部分角色权限、字典、申报、合同、资产、支付、传输、存证、归档和跨模块一致性骨架。
- 数据产品创建、提交审核、管理员审核、上下架及变更审核。
- 标准产品订单主流程：下单 → 提供方审核 → 运营方审核 → 上传/确认合同 → 支付 → 确认收款 → 交付 → 验收 → 详情核对。
- 少量订单反向场景：运营方驳回、合同驳回后重传、未到账回退、交付必填校验、分批交付后验收驳回及重新交付。

### 1.3 尚未完成的重点

当前项目**主要完成了主流程自动化**，不是全量回归项目。后续仍需补充：

- 60 条已有 Excel 设计但无对应自动化函数的用例。
- 各业务表单的大量必填、格式、长度、边界值、组合条件和非法输入分支。
- 更完整的角色/菜单/数据权限、越权访问和权限变更即时生效场景。
- 重复提交、连续点击、刷新、超时、断网、服务异常、接口失败后的恢复和幂等性。
- 订单金额、双方信息、合同、凭证、备注、时间、操作记录等详情字段的完整一致性断言。
- 验收完成后结算、支付流水/对账、传输记录、存证、操作日志和归档是否自动联动。
- 定制需求、定制订单、资源套餐、阶梯定价、质量定级定价等业务变体。
- 多浏览器兼容、并发执行、稳定性、性能、接口层和数据库层校验。
- WEB-086、WEB-088、WEB-092～WEB-095 等需要人工或受控环境执行的场景自动化。

数据加工平台不属于本项目当前测试范围。

## 2. 技术基础

| 技术 | 用途 |
| --- | --- |
| Python 3.12 | 当前本机和 Jenkins 使用的主要运行时；建议至少 Python 3.10 |
| Selenium 4 | Chrome/Edge 浏览器驱动、页面操作和显式等待 |
| Pytest 8～9 | 用例组织、参数化、Fixture、Marker、失败钩子和 JUnit 结果 |
| Page Object Model | 将页面定位和业务操作与测试断言分层 |
| JSON + python-dotenv | 普通测试数据与本地敏感配置分离 |
| Allure Pytest / Allure CLI | 结果采集、失败附件、在线和单文件离线报告 |
| Jenkins Pipeline | 私有仓库轮询、安装、审计、编译、收集、可选 UI 测试和邮件通知 |
| GitHub 私有仓库 | 源码版本管理，不允许公开项目源码、账号、附件和运行产物 |

依赖版本以 [`requirements.txt`](requirements.txt) 为准：

```text
selenium>=4,<5
pytest>=8,<10
allure-pytest>=2,<3
python-dotenv>=1.2,<2
```

## 3. 项目架构

```text
自动化测试/
├─ base/                         # 基础页面能力与自定义异常
│  ├─ base_page.py              # 点击、输入、等待、滚动、弹窗等通用封装
│  └─ exceptions.py
├─ page/                         # Page Object：定位器与页面业务操作
├─ script/                       # Pytest 测试脚本，函数名保留 WEB 用例编号
├─ data/                         # JSON 测试数据和运行时业务编号
├─ docs/                         # 运行、定位、覆盖、交接说明及测试用例主表
│  └─ 测试用例.xlsx              # 95 条正式测试用例，含覆盖、数据和变更记录
├─ 元素定位/                     # 各角色页面的原始 HTML/定位资料
├─ test_materials/               # 本机模拟附件；默认不提交生成物
├─ ci/                           # Jenkins 任务备份、CI 说明和敏感信息审计
├─ log/                          # 运行日志，生成内容被 Git 忽略
├─ report/                       # Pytest 生成的 Allure 原始结果
├─ report-html/                  # 本地生成的 Allure HTML
├─ screenshots/                  # 用例失败截图
├─ downloads/                    # 浏览器下载文件
├─ config.py                     # 环境变量、路径和浏览器配置
├─ conftest.py                   # CLI 参数、Fixture、跳过规则、失败截图
├─ tools.py                      # 驱动、日志、JSON、敏感信息遮蔽等公共工具
├─ pytest.ini                    # 收集规则、Marker 和 Allure 默认参数
├─ Jenkinsfile                   # Jenkins 声明式流水线
└─ requirements.txt              # Python 依赖
```

### 3.1 分层调用关系

```text
script 测试与断言
    ↓
page 页面对象与业务动作
    ↓
base 通用 Selenium 操作
    ↓
浏览器 / 被测 Web 系统

data JSON ──→ script
.env.local ──→ config / fixture
conftest ──→ driver、账号、跳过规则、失败截图、Allure 附件
```

维护时不要把复杂定位和页面操作直接堆进测试函数；可复用动作放到 `page/`，通用操作放到 `base/`，测试脚本重点保留业务编排和断言。

## 4. 从零开始：本地安装与配置

以下步骤以 Windows PowerShell 为例，并假设使用私有仓库的授权账号。

### 4.1 准备软件

1. 安装 Git。
2. 安装 Python 3.10+，当前建议 Python 3.12。
3. 安装最新版 Chrome 或 Edge。
4. 需要查看本地 Allure 报告时，安装 Java 和 Allure CLI，并确保 `allure --version` 可执行。
5. 确认能够访问测试环境。默认入口由 `.env.example` 中的 `WEB_BASE_URL` 与 `WEB_ENTRY_PATH` 组合得到。

### 4.2 克隆私有仓库

```powershell
git clone https://github.com/AnnoTokyo-stu/Auto_Test.git
Set-Location Auto_Test
```

如果提示认证，使用本人有权访问该私有仓库的 GitHub 账号、SSH Key 或 Fine-grained PAT。不要把 PAT 写入远程地址、脚本或 README。

### 4.3 创建虚拟环境并安装依赖

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

PowerShell 如果阻止激活脚本，可以不激活，后续直接使用：

```powershell
.\.venv\Scripts\python.exe -m pytest --collect-only -q
```

### 4.4 创建本地配置

复制完整变量模板，不要修改并提交模板本身：

```powershell
Copy-Item .env.example .env.local
```

打开 `.env.local`，只填写经批准的专用测试账号、测试业务编号和环境参数。`.env.local` 已被 Git 忽略，仍应避免在聊天、日志、截图或邮件中输出其内容。

配置优先级：终端/PyCharm/Jenkins 环境变量 > `.env.local` > `config.py` 默认值。

### 4.5 核对附件

`test_materials/` 中的模拟附件默认不提交到 Git。接手人需要从合规的内部交接渠道取得或重新生成以下测试专用材料：

- `business_license.png`
- `legal_representative_id.png`
- `operator_id.png`
- `data_product_cover.png`
- `mock_data_product_purchase_contract.docx`
- `mock_payment_voucher.pdf`
- 分批交付所需的模拟资源文件

附件必须显著标明“自动化测试模拟资料”，不得使用真实身份证件、营业执照、合同、签章、银行流水或客户数据。具体要求见 [`test_materials/README.md`](test_materials/README.md)。

### 4.6 首次自检

先做不打开浏览器、不修改业务数据的检查：

```powershell
python ci/security_audit.py
python -m compileall -q base page script config.py conftest.py tools.py
python -m pytest --collect-only -q
```

预期能够成功收集测试。收集成功不等于真实 UI 执行成功；真实执行还依赖账号、验证码、定位器、已有业务数据和环境状态。

## 5. 环境变量说明

### 5.1 浏览器与等待参数

| 变量 | 典型值 | 作用 |
| --- | --- | --- |
| `WEB_BASE_URL` | 测试环境根地址 | 不带末尾 `/` |
| `WEB_ENTRY_PATH` | `/system/organization` | 入口路径 |
| `WEB_BROWSER` | `chrome` / `edge` | 默认浏览器 |
| `WEB_HEADLESS` | `false` | 是否无头运行；人工验证码场景必须为 `false` |
| `WEB_FAST_INPUT` | `true` | 长表单快速赋值；控件不兼容时设为 `false` |
| `WEB_EXPLICIT_WAIT` | `10` | 显式等待秒数 |
| `WEB_PAGE_LOAD_TIMEOUT` | `30` | 页面加载超时秒数 |
| `WEB_MANUAL_CAPTCHA_TIMEOUT` | `120` | 人工图形验证码等待秒数 |
| `WEB_MANUAL_EMAIL_CODE_TIMEOUT` | `300` | 人工邮箱验证码等待秒数 |
| `WEB_PAGE_LOAD_STRATEGY` | `normal` / `eager` | 页面加载策略 |
| `WEB_DRIVER_PATH` | 本地驱动绝对路径 | 可选；留空时使用 Selenium Manager |
| `WEB_WINDOW_WIDTH/HEIGHT` | `1440` / `900` | 浏览器窗口尺寸 |

### 5.2 账号角色

| 变量 | 角色/用途 |
| --- | --- |
| `TEST_USER_NAME/PASSWORD` | 通用测试用户 |
| `TEST_USER_DISPLAY_NAME` | 登录后身份断言 |
| `TEST_ADMIN_NAME/PASSWORD` | 运营管理员/超级管理员 |
| `TEST_RBAC_USER_NAME/PASSWORD` | 权限测试用户 |
| `TEST_DATA_PROVIDER_NAME/PASSWORD` | 数据提供方 |
| `TEST_DATA_CONSUMER_NAME/PASSWORD` | 数据使用方，订单流程不得误用提供方账号 |
| `TEST_WRONG_PASSWORD` | 登录反向用例的错误密码 |
| `TEST_UNKNOWN_USER` | 不存在账号用例 |
| `WEB_REGISTRATION_*` | 生产注册半自动场景的专用模拟注册信息 |

### 5.3 预置业务编号

独立用例通过 `TEST_DECLARATION_ID`、`TEST_CONTRACT_ID`、`TEST_ASSET_ID`、`TEST_ORDER_ID`、`TEST_PAYMENT_ID`、`TEST_TRANSFER_ID`、`TEST_EVIDENCE_ID`、`TEST_ARCHIVE_BUSINESS_ID` 等变量引用测试环境预置数据。编号应来自测试环境，不要写入真实客户或生产业务数据。

JSON 中的完整 `${VARIABLE_NAME}` 会由 `tools.py` 从环境变量替换；`__TO_BE_CONFIRMED__` 表示该字段仍需按环境补齐，缺失时测试会给出跳过原因。

## 6. 测试执行方法

### 6.1 先理解三层安全开关

1. `--run-ui`：允许打开真实浏览器；没有该参数时 UI 用例被跳过。
2. `--run-destructive`：允许新增或修改业务数据；没有该参数时 destructive 用例被跳过。
3. `--confirm-production-*`：对具体高风险业务动作再次确认。只开启前两层仍不能执行对应生产动作。

不要为了“跑全量”一次性开启所有确认参数。先选择单个用例，核对账号、目标数据、附件和可恢复性后再执行。

### 6.2 常用安全命令

只收集用例：

```powershell
python -m pytest --collect-only -q
```

运行可见 Chrome 冒烟测试：

```powershell
python -m pytest -m smoke --run-ui --browser=chrome -s
```

运行无头 Edge：

```powershell
python -m pytest -m smoke --run-ui --browser=edge --headless
```

按文件执行：

```powershell
python -m pytest script/test_01_auth.py --run-ui -s
```

按完整 Node ID 执行：

```powershell
python -m pytest script/test_04_data_product_management.py::test_web_084_provider_deliver_and_consumer_accept_order --run-ui --run-destructive <所需生产确认参数> -s
```

按 Marker 选择：

```powershell
python -m pytest -m "p0 and not destructive" --run-ui
python -m pytest -m "transaction and p0" --run-ui
python -m pytest -m e2e --collect-only -q
```

当前主要 Marker 包括：`ui`、`smoke`、`p0`、`p1`、`auth`、`certification`、`message`、`system`、`declaration`、`transaction`、`transfer`、`archive`、`e2e`、`destructive` 以及多项 `production_*`。

### 6.3 生产动作确认参数

| 参数 | 允许的动作 |
| --- | --- |
| `--confirm-production-registration` | 创建注册账号 |
| `--confirm-production-product-submission` | 提交数据产品审核 |
| `--confirm-production-product-approval` | 管理员提交产品审核结果 |
| `--confirm-production-product-lifecycle` | 上架、下架及产品变更审核 |
| `--confirm-production-product-order` | 数据使用方创建产品订单 |
| `--confirm-production-order-provider-audit` | 数据提供方审核订单 |
| `--confirm-production-order-operations-audit` | 运营方审核订单 |
| `--confirm-production-order-contract-upload` | 上传订单合同 |
| `--confirm-production-order-contract-confirmation` | 提交合同确认结果 |
| `--confirm-production-order-payment` | 上传支付凭证并提交支付 |
| `--confirm-production-order-receipt-confirmation` | 提交收款确认结果 |
| `--confirm-production-order-delivery` | 提交订单交付 |
| `--confirm-production-order-acceptance` | 提交验收结果 |

标准订单正向闭环 WEB-084 需要：

```powershell
python -m pytest script/test_04_data_product_management.py::test_web_084_provider_deliver_and_consumer_accept_order `
  --run-ui --run-destructive `
  --confirm-production-product-order `
  --confirm-production-order-provider-audit `
  --confirm-production-order-operations-audit `
  --confirm-production-order-contract-upload `
  --confirm-production-order-contract-confirmation `
  --confirm-production-order-payment `
  --confirm-production-order-receipt-confirmation `
  --confirm-production-order-delivery `
  --confirm-production-order-acceptance `
  -s
```

该流程会在数据使用方、数据提供方和管理员之间多次重新登录，并需要人工完成验证码。执行前确认已有可下单产品、三类账号、模拟合同、模拟支付凭证和可交付测试资源。

### 6.4 验证码与可见浏览器

登录页图形验证码、注册页图形验证码和邮箱验证码采用人工输入，脚本只负责等待输入完成后继续。因此：

- 不要对这些用例使用 `--headless`。
- 输入验证码后按 `Tab` 使输入框失焦，便于脚本检测。
- 超时可调整 `WEB_MANUAL_CAPTCHA_TIMEOUT` 和 `WEB_MANUAL_EMAIL_CODE_TIMEOUT`。

### 6.5 浏览器驱动

默认由 Selenium Manager 解析驱动。网络受限或解析较慢时，在 `.env.local` 设置 `WEB_DRIVER_PATH`，或执行时传入：

```powershell
python -m pytest -m smoke --run-ui --driver-path "C:\path\to\chromedriver.exe"
```

驱动主版本必须与浏览器兼容。

## 7. 测试数据与运行产物

### 7.1 数据管理规则

- `data/*.json` 保存可版本化的普通测试数据、用例编号和环境变量占位符。
- 账号密码只放在环境变量或 `.env.local`，不能写进 JSON、源码或 Excel。
- 动态名称应使用时间戳/随机后缀，避免与环境中历史模拟数据冲突。
- 跨角色订单测试必须一直传递并核对同一个动态订单编号。
- 页面实际行为与 Excel 不一致时，以已确认的真实行为为准，同时更新 Excel 的步骤、数据、预期和变更记录。

### 7.2 输出目录

| 目录 | 内容 | 是否提交 Git |
| --- | --- | --- |
| `log/` | `web.log`，按天轮转，保留 7 份 | 否 |
| `report/` | Pytest 默认 Allure 原始结果 | 否 |
| `report-html/` | 本地 Allure HTML | 否 |
| `screenshots/` | 失败截图 | 否 |
| `downloads/` | 浏览器下载文件 | 否 |
| `artifacts/` | Jenkins JUnit、Allure 和压缩包 | 否 |

用例在 setup/call 阶段失败时，`conftest.py` 会保存截图，并将截图和当前 URL 附加到 Allure。

## 8. Allure 报告

`pytest.ini` 默认将结果写入 `report/`：

```powershell
python -m pytest -m smoke --run-ui
allure serve report
```

生成普通静态目录：

```powershell
allure generate report -o report-html --clean
```

直接双击普通多文件报告的 `index.html` 可能因浏览器限制本地文件请求而一直显示 `Loading...`。需要邮件传递或直接离线打开时，应生成单文件报告：

```powershell
allure generate report --clean --single-file --output report-html
```

然后打开 `report-html/index.html`。Jenkinsfile 采用的也是 `--single-file`，并将报告目录压缩为 `artifacts/allure-report.zip`。

## 9. Jenkins + GitHub 私有 CI

### 9.1 当前环境

- GitHub 仓库：`AnnoTokyo-stu/Auto_Test`，必须保持 Private。
- Jenkins 启动包：`G:\软件测试\Git+jenkins\Jenkins_test\jenkins.war`。
- Jenkins Home：`C:\Users\jojo\.jenkins`。
- 流水线定义：根目录 [`Jenkinsfile`](Jenkinsfile)。
- Jenkins 任务备份：[`ci/jenkins-job.xml`](ci/jenkins-job.xml)。

以上 Windows 绝对路径只属于当前 Jenkins 主机；迁移到新主机时应重新安装 Java/Jenkins/Allure 并重新配置凭据，不能把整个 Jenkins Home 提交到 GitHub。

启动示例：

```powershell
java -jar "G:\软件测试\Git+jenkins\Jenkins_test\jenkins.war"
```

### 9.2 自动构建做什么

Jenkins 每 5 分钟轮询一次私有仓库。默认 `RUN_UI=false`，流水线只执行：

1. 创建 `.venv-ci`。
2. 安装 `requirements.txt`。
3. 执行 `ci/security_audit.py`。
4. 编译 Python 源码。
5. 收集 Pytest 用例。
6. 归档结果并发送构建邮件。

默认自动构建不会打开浏览器，也不会修改业务数据。

### 9.3 人工触发 UI 测试

进入 Jenkins 任务 → **Build with Parameters**：

| 参数 | 说明 |
| --- | --- |
| `RUN_UI` | 开启真实浏览器测试；Jenkins 中固定无头模式 |
| `RUN_DESTRUCTIVE` | 允许 destructive 用例 |
| `TEST_SCOPE` | `smoke`、`p0` 或 `all` |
| `REPORT_RECIPIENTS` | 收件人，多个地址用英文逗号分隔 |

重要限制：当前 Jenkinsfile **不会自动添加任何 `--confirm-production-*` 参数**。因此即使选择 `RUN_UI=true` 和 `RUN_DESTRUCTIVE=true`，需要生产确认的注册、产品、订单、合同、支付、交付和验收测试仍会跳过。这是安全设计，也意味着完整订单主流程目前仍更适合在本地逐条确认执行。若以后要让 Jenkins 执行这些流程，应增加逐项布尔参数、审批和专用隔离环境，不能简单默认放开。

### 9.4 Jenkins 必需的本机配置

- GitHub 私有仓库只读凭据；任务备份引用凭据 ID `github-private-demo-read`。
- Jenkins 运行账号可执行 Python、Git、Java 和浏览器。
- Allure Jenkins Plugin；全局工具名称必须为 `allure`。
- Email Extension Plugin。
- 163 邮箱 SMTP 服务器、发件账号和**客户端授权码**。授权码只能保存到 Jenkins Credentials/系统配置，不能写入 Jenkinsfile、README 或 GitHub。
- UI 构建所需的测试账号环境变量或 Jenkins Secret File。当前 Jenkinsfile 不负责自动注入 `.env.local`，迁移任务时必须单独配置。

### 9.5 构建产物和邮件

- `artifacts/junit.xml`：JUnit 测试结果。
- `artifacts/allure-results/`：Allure 原始数据。
- `artifacts/allure-report/index.html`：可直接离线打开的单文件报告。
- `artifacts/allure-report.zip`：邮件附件。
- Jenkins Allure 页面：由插件发布。
- 成功和失败均发送 HTML 邮件，并附压缩构建日志；执行 UI 后附加报告压缩包。

更详细的任务配置见 [`ci/README.md`](ci/README.md)。

## 10. 测试用例主表维护

正式基线是 [`docs/测试用例.xlsx`](docs/测试用例.xlsx)，包含：

- `测试用例`：95 条用例的编号、标题、模块、优先级、前置条件、步骤、数据和预期。
- `覆盖说明`：覆盖维度、设计方法、重点和模块映射。
- `测试数据`：建议数据、适用场景和隐私注意事项。
- `变更记录`：用例增删改的版本轨迹。

维护规则：

1. 用例编号稳定，不因删除自动化函数而重排。
2. 页面事实优先，不根据猜测修改预期。
3. 新增或修改用例时同时更新“变更记录”。
4. Excel 设计范围与自动化实现范围分开统计。
5. 账号、真实编号和敏感附件不能写入工作簿。
6. 修改后检查标题、表头、边框、行高、换行、优先级颜色和四个工作表的一致性。

## 11. README 强制同步规则

README 是交付物的一部分。以后每次修改项目，提交前必须检查 README，并按实际变化同步以下内容：

| 变更类型 | README 必须核对的位置 |
| --- | --- |
| 新增/删除测试函数或 Excel 用例 | 覆盖数量、现状、待改进、执行示例 |
| 修改目录或分层 | 项目架构和调用关系 |
| 修改依赖/浏览器/等待策略 | 技术基础、安装步骤、环境变量 |
| 修改 CLI 参数或 Marker | 测试执行方法和安全开关 |
| 修改账号、测试数据或附件要求 | 环境配置、测试数据和隐私规则 |
| 修改 Jenkinsfile | Jenkins 参数、阶段、凭据、产物和邮件说明 |
| 修复重要业务流程 | 已覆盖重点、已知限制、专项文档链接 |

每次提交的完成定义（Definition of Done）：

- [ ] 代码、定位器、测试数据和断言已经同步。
- [ ] 涉及测试设计时，`docs/测试用例.xlsx` 及其“变更记录”已经同步。
- [ ] README 中的数量、命令、参数、路径、状态和限制已经复核并更新。
- [ ] 对应专项文档没有保留与代码冲突的旧结论。
- [ ] `python ci/security_audit.py` 通过。
- [ ] `python -m compileall -q base page script config.py conftest.py tools.py` 通过。
- [ ] `python -m pytest --collect-only -q` 通过。
- [ ] 未提交 `.env.local`、真实附件、日志、截图、报告或其他隐私数据。

如果某次修改确实不影响 README 内容，也必须在代码评审时明确确认“README 已复核，无需修改”，不能默认忽略。

## 12. 常见问题

### 用例显示 skipped

优先检查：是否传入 `--run-ui`、`--run-destructive` 和相应生产确认参数；账号/编号是否配置；JSON 是否仍为 `__TO_BE_CONFIRMED__`。跳过通常是安全保护，不应直接删除 Marker。

### Selenium Manager 很慢或失败

在受限网络准备匹配浏览器版本的本地驱动，并设置 `WEB_DRIVER_PATH` 或 `--driver-path`。

### 登录后一直等待

确认使用可见浏览器，人工输入验证码并按 `Tab`。检查验证码等待时间和页面是否改版。

### 页面找到多条相同按钮

不要改成点击第一条。应先用动态订单号、产品编号或唯一名称锁定目标行，再在同行或固定操作列中定位按钮。

### 上传后没有提交或一直等待

检查上传成功卡片、失败状态、上传中状态、文件名和弹窗 DOM。不要用固定 `sleep` 掩盖异步上传问题。

### Allure 页面一直 Loading

普通目录报告不能可靠地通过 `file://` 直接打开。使用 `allure serve`，或生成 `--single-file` 报告。

### PytestCacheWarning / WinError 5

该警告只影响 `.pytest_cache`。可修复目录权限，或临时添加：

```powershell
python -m pytest --collect-only -q -p no:cacheprovider
```

## 13. 交接检查清单

交付给下一位维护者前，至少完成：

1. 确认 GitHub 仓库仍为 Private，并授予接手人最小必要权限。
2. 确认默认分支、当前开发分支和未合并 PR 状态。
3. 通过安全渠道交接测试环境账号、验证码配合方式、预置业务数据和模拟附件；不要通过 GitHub 传递。
4. 让接手人独立完成创建虚拟环境、安装依赖和 `--collect-only`。
5. 选择一个无副作用用例完成本地真实 UI 验证。
6. 说明标准订单链会创建生产测试数据，执行前需要哪些确认参数和角色账号。
7. 在 Jenkins 上完成一次默认安全构建，并确认 Allure、邮件和归档产物。
8. 指出当前主要是主流程，大量分支未实现，不把“可收集”误认为“全量通过”。
9. 交接 `docs/测试用例.xlsx`、专项运行指南和最新日志/截图结论，但不要提交运行产物。

## 14. 进一步阅读

- [`docs/项目运行指南.md`](docs/项目运行指南.md)：本地参数和安全运行规则。
- [`docs/项目交接文档-2026-08-17.md`](docs/项目交接文档-2026-08-17.md)：历史实现、问题和业务背景。
- [`docs/用例覆盖路线图.md`](docs/用例覆盖路线图.md)：模块级覆盖状态。
- [`docs/元素定位填写指南.md`](docs/元素定位填写指南.md)：页面定位器补充规则。
- [`docs/数据提供方认证运行指南.md`](docs/数据提供方认证运行指南.md)：认证半自动流程。
- [`docs/消息管理自动识别说明.md`](docs/消息管理自动识别说明.md)：动态消息行识别。
- [`docs/数据产品管理运行指南.md`](docs/数据产品管理运行指南.md)：数据产品与订单链路。
- [`ci/README.md`](ci/README.md)：Jenkins 任务、报告和凭据。

---

维护本项目时应始终遵循三条底线：**不泄露敏感信息、不误操作真实业务数据、不让文档状态落后于代码和测试事实。**
