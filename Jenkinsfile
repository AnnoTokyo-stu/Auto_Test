pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
    }

    parameters {
        booleanParam(
            name: 'RUN_UI',
            defaultValue: false,
            description: '人工启用真实浏览器 UI 测试；自动构建保持关闭'
        )
        booleanParam(
            name: 'RUN_DESTRUCTIVE',
            defaultValue: false,
            description: '允许执行会新增或修改测试数据的用例；生产确认参数仍不会自动启用'
        )
        choice(
            name: 'TEST_SCOPE',
            choices: ['smoke', 'p0', 'all'],
            description: '人工 UI 构建的用例范围'
        )
        string(
            name: 'REPORT_RECIPIENTS',
            defaultValue: '13108697141@163.com',
            description: '测试报告收件人；多个地址使用英文逗号分隔'
        )
    }

    environment {
        PYTHONUTF8 = '1'
        WEB_HEADLESS = 'true'
    }

    stages {
        stage('Environment') {
            steps {
                bat 'python --version'
                bat 'python -m venv .venv-ci'
            }
        }

        stage('Install') {
            steps {
                bat '.venv-ci\\Scripts\\python.exe -m pip install --disable-pip-version-check -r requirements.txt'
            }
        }

        stage('Security Audit') {
            steps {
                bat '.venv-ci\\Scripts\\python.exe ci\\security_audit.py'
            }
        }

        stage('Compile') {
            steps {
                bat '.venv-ci\\Scripts\\python.exe -m compileall -q base page script config.py conftest.py tools.py'
            }
        }

        stage('Collect Tests') {
            steps {
                bat '.venv-ci\\Scripts\\python.exe -m pytest --collect-only -q'
            }
        }

        stage('Optional UI Tests') {
            when {
                expression { return params.RUN_UI }
            }
            steps {
                script {
                    def marker = params.TEST_SCOPE == 'all' ? '' : "-m ${params.TEST_SCOPE}"
                    def destructive = params.RUN_DESTRUCTIVE ? '--run-destructive' : ''
                    bat """
                        if not exist artifacts mkdir artifacts
                        .venv-ci\\Scripts\\python.exe -m pytest ${marker} --run-ui --headless ${destructive} --junitxml=artifacts\\junit.xml --alluredir=artifacts\\allure-results --clean-alluredir
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('artifacts/allure-results')) {
                    try {
                        def allureHome = tool(
                            name: 'allure',
                            type: 'ru.yandex.qatools.allure.jenkins.tools.AllureCommandlineInstallation'
                        )
                        withEnv(['ALLURE_NO_ANALYTICS=1']) {
                            bat """
                                "${allureHome}\\bin\\allure.bat" generate artifacts\\allure-results --clean --single-file --output artifacts\\allure-report
                                powershell -NoProfile -Command "Compress-Archive -Path 'artifacts\\allure-report\\*' -DestinationPath 'artifacts\\allure-report.zip' -Force"
                            """
                        }
                        allure includeProperties: false,
                               jdk: '',
                               results: [[path: 'artifacts/allure-results']]
                    } catch (reportError) {
                        currentBuild.result = 'FAILURE'
                        echo "Allure 报告生成或发布失败：${reportError}"
                    }
                }
            }
            junit testResults: 'artifacts/junit.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'artifacts/**/*,report/**/*,screenshots/**/*', allowEmptyArchive: true, fingerprint: true
            emailext(
                to: params.REPORT_RECIPIENTS,
                subject: "[${currentBuild.currentResult}] ${env.JOB_NAME} #${env.BUILD_NUMBER} 自动化测试报告",
                mimeType: 'text/html',
                body: """
                    <h2>${env.JOB_NAME} #${env.BUILD_NUMBER}</h2>
                    <p><b>构建结果：</b>${currentBuild.currentResult}</p>
                    <p><b>测试范围：</b>${params.RUN_UI ? params.TEST_SCOPE : 'CI 安全检查（未执行 UI）'}</p>
                    <p><b>UI 测试：</b>${params.RUN_UI ? '已启用（无头模式）' : '未启用'}</p>
                    <p><b>破坏性测试：</b>${params.RUN_DESTRUCTIVE ? '已启用' : '未启用'}</p>
                    <p><a href="${env.BUILD_URL}">查看 Jenkins 构建详情</a></p>
                    <p>若本次执行了 UI 测试，附件 allure-report.zip 中的 index.html 可离线打开。</p>
                """,
                attachmentsPattern: 'artifacts/allure-report.zip',
                attachLog: true,
                compressLog: true
            )
        }
    }
}
