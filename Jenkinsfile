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
                        .venv-ci\\Scripts\\python.exe -m pytest ${marker} --run-ui --headless ${destructive} --junitxml=artifacts\\junit.xml
                    """
                }
            }
        }
    }

    post {
        always {
            junit testResults: 'artifacts/junit.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'artifacts/**/*,report/**/*,screenshots/**/*', allowEmptyArchive: true, fingerprint: true
        }
    }
}
