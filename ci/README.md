# 私有仓库 CI 说明

## 自动构建

Jenkins 每 5 分钟轮询一次私有 GitHub 仓库。自动构建只执行：

1. 安装 Python 依赖；
2. 检查是否跟踪本地敏感文件或高可信密钥；
3. 编译 Python 源码；
4. 收集 Pytest 用例。

自动构建不会打开浏览器，也不会修改真实环境数据。

## 人工 UI 构建

在 Jenkins 中选择 **Build with Parameters**：

- `RUN_UI=true`：运行真实浏览器 UI 测试；
- `TEST_SCOPE=smoke|p0|all`：选择范围；
- `RUN_DESTRUCTIVE=true`：允许新增或修改测试数据。
- `REPORT_RECIPIENTS`：测试报告收件人，多个地址使用英文逗号分隔。

即使启用 `RUN_DESTRUCTIVE`，生产注册、产品提交、审核、订单、合同、支付、交付和验收仍需要对应的 Pytest 生产确认参数。Jenkinsfile 不会自动添加这些参数。

UI 构建会生成 `artifacts/allure-results`，在 Jenkins 中发布 Allure 报告，并额外生成可离线打开的单文件报告 `artifacts/allure-report/index.html`。邮件在成功和失败时都会发送；有 UI 测试结果时附带 `allure-report.zip`，同时附带压缩构建日志。

## 凭据

GitHub 凭据仅用于 Jenkins 克隆私有仓库，应使用只读 Fine-grained PAT，并存放在 Jenkins Credentials 中。项目账号和密码继续保存在本机 `.env.local` 或专用 Jenkins Secret File 中，禁止提交到 Git。

仓库内的 `ci/jenkins-job.xml` 是任务配置备份，任务名为 `Auto_Test-CI`，引用 Jenkins 凭据 ID `github-private-demo-read`；XML 中不包含 Token。
