pipeline {
    agent any
    environment {
        CUSTOM_WORKSPACE = '/var/jenkins_home/workspace/ICT2216'
    }

    stages {
        //  stage('OWASP Dependency-Check Vulnerabilities') {
        //     steps {
        //         dependencyCheck additionalArguments: """
        //             -o './'
        //             -s './'
        //             -f 'ALL'
        //             --prettyPrint
        //             --nvdApiKey ae60ce14-527f-411f-8f50-6de6638bed18
        //             --format HTML --format XML
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
        stage('Verify Checkout') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}") {
                    sh 'echo "Current workspace: $CUSTOM_WORKSPACE"'
                    sh 'ls -l $CUSTOM_WORKSPACE'
                    sh 'ls -l $CUSTOM_WORKSPACE/react-flask-app'
                }
            }
        }
        stage('Copy .env File') {
            steps {
                script {
                    withCredentials([file(credentialsId: '177c064b-8394-453c-aaf9-252718ad9498', variable: 'SECRET_ENV_FILE')]) {
                        sh 'cp $SECRET_ENV_FILE $CUSTOM_WORKSPACE/react-flask-app/server/.env'
                        sh 'ls -l $CUSTOM_WORKSPACE/react-flask-app/server/.env'  // Verify the .env file is copied
                    }
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
        stage('Database Migration') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
                    sh 'bash -c ". venv/bin/activate && flask db upgrade"'
                }
            }
        }
        stage('Run Tests') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
                    sh 'bash -c "export PYTHONPATH=${CUSTOM_WORKSPACE}/react-flask-app/server && . venv/bin/activate && pytest test/test_api.py --junitxml=report.xml"'
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
        stage('Deploy Application') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    dir("${env.CUSTOM_WORKSPACE}") {
                        sh 'echo "Current workspace during deploy: $CUSTOM_WORKSPACE"'
                        sh 'ls -l $CUSTOM_WORKSPACE/react-flask-app/server/.env'  // Ensure .env file is present before build
                        sh 'docker-compose -f $CUSTOM_WORKSPACE/react-flask-app/docker-compose.yml up -d --build'
                    }
                }
            }
        }
        
    }
    post {
        always {
            cleanWs()
        }
        // success {
        //     dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        // }
    }
}