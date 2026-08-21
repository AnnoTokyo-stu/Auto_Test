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
                to: params.REPORT_RECIPIENTS ?: '13108697141@163.com',
                subject: "[${currentBuild.currentResult}] ${env.JOB_NAME} #${env.BUILD_NUMBER} \u81EA\u52A8\u5316\u6D4B\u8BD5\u62A5\u544A",
                mimeType: 'text/html; charset=UTF-8',
                body: """
                    <h2>${env.JOB_NAME} #${env.BUILD_NUMBER}</h2>
                    <p><b>&#26500;&#24314;&#32467;&#26524;&#65306;</b>${currentBuild.currentResult}</p>
                    <p><b>&#27979;&#35797;&#33539;&#22260;&#65306;</b>${params.RUN_UI ? params.TEST_SCOPE : 'CI &#23433;&#20840;&#26816;&#26597;&#65288;&#26410;&#25191;&#34892; UI&#65289;'}</p>
                    <p><b>UI &#27979;&#35797;&#65306;</b>${params.RUN_UI ? '&#24050;&#21551;&#29992;&#65288;&#26080;&#22836;&#27169;&#24335;&#65289;' : '&#26410;&#21551;&#29992;'}</p>
                    <p><b>&#30772;&#22351;&#24615;&#27979;&#35797;&#65306;</b>${params.RUN_DESTRUCTIVE ? '&#24050;&#21551;&#29992;' : '&#26410;&#21551;&#29992;'}</p>
                    <p><a href="${env.BUILD_URL}">&#26597;&#30475; Jenkins &#26500;&#24314;&#35814;&#24773;</a></p>
                    <p>&#33509;&#26412;&#27425;&#25191;&#34892;&#20102; UI &#27979;&#35797;&#65292;&#38468;&#20214; allure-report.zip &#20013;&#30340; index.html &#21487;&#31163;&#32447;&#25171;&#24320;&#12290;</p>
                """,
                attachmentsPattern: 'artifacts/allure-report.zip',
                attachLog: true,
                compressLog: true
            )
        }
    }
}
