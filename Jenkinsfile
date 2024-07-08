pipeline {
    agent any
    environment {
        CUSTOM_WORKSPACE = '/var/jenkins_home/workspace/ICT2216'
    }

    stages {
        // stage('OWASP Dependency-Check Vulnerabilities') {
        //     steps {
        //         dependencyCheck additionalArguments: """
        //             -o './'
        //             -s './'
        //             -f 'ALL'
        //             --prettyPrint
        //             --nvdApiKey ae60ce14-527f-411f-8f50-6de6638bed18
        //         """, odcInstallation: 'OWASP Dependency-Check Vulnerabilities'

        //         dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        //     }
        // }

        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }
        stage('Checkout') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}") {
                    git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
                }
            }
        }
        stage('Copy .env File') {
            steps {
                script {
                    withCredentials([file(credentialsId: '51cacb7c-db19-4619-b7ca-bcc8892add5f', variable: 'SECRET_ENV_FILE')]) {
                        sh 'cp $SECRET_ENV_FILE $CUSTOM_WORKSPACE/react-flask-app/server/.env'
                        sh 'ls -l $CUSTOM_WORKSPACE/react-flask-app/server/.env'  // Verify the .env file is copied
                    }
                }
            }
        }
        stage('Create Temp .env for Tests') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
                    sh 'cp .env .env.temp'
                    sh 'sed -i -e "s/\\r//g" .env.temp'
                }
            }
        }
        stage('Setup Python Environment') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
                    sh 'bash -c "python3 -m venv venv"'
                    sh 'bash -c ". venv/bin/activate && pip install -r requirements.txt"'
                }
            }
        }
        stage('Install Frontend Dependencies') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}/react-flask-app/client") {
                    sh 'yarn install'
                }
            }
        }
        stage('Database Migration') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
                    sh 'bash -c ". venv/bin/activate && flask db upgrade"'
                }
            }
        }
        stage('Run Unit Tests') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
                    sh 'bash -c "set -a && source .env.temp && set +a && export PYTHONPATH=${CUSTOM_WORKSPACE}/react-flask-app/server && . venv/bin/activate && pytest test/test_api.py --junitxml=report.xml"'
                  
                }
            }
        }
        stage('Clean Up') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    sh 'docker system prune -af'
                    sh 'docker volume prune -f'
                }
            }
        }
        stage('Stop and Remove Existing Containers') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    sh 'docker-compose -f $CUSTOM_WORKSPACE/react-flask-app/docker-compose.yml down'
                }
            }
        }
        stage('Build and Start Docker Containers') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    dir("${env.CUSTOM_WORKSPACE}/react-flask-app") {
                        sh 'docker-compose up -d --build'
                    }
                }
            }
        }
        stage('Run UI Tests') {
            steps {
                script {
                    dir("${env.CUSTOM_WORKSPACE}/react-flask-app/client") {
                        sh 'npm run cypress:run'
                    }
                }
            }
        }
        
    }
    post {
        always {
            // Archive test results and clean workspace
            dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
                archiveArtifacts artifacts: 'report.xml', allowEmptyArchive: true
            }
            dir("${env.CUSTOM_WORKSPACE}/react-flask-app/client/cypress/results") {
                archiveArtifacts artifacts: '*.xml', allowEmptyArchive: true
            }
            cleanWs()
        }
    }
}