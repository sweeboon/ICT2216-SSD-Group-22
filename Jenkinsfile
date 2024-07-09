pipeline {
    agent any
    environment {
        CUSTOM_WORKSPACE = '/var/jenkins_home/workspace/ICT2216'
    }

    stages {
        //Stage 1
        stage('OWASP Dependency-Check Vulnerabilities') {
            steps {
                dependencyCheck additionalArguments: """
                    -o './'
                    -s './'
                    -f 'ALL'
                    --prettyPrint
                    --nvdApiKey ae60ce14-527f-411f-8f50-6de6638bed18
                """, odcInstallation: 'OWASP Dependency-Check Vulnerabilities'

                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }
        //Stage 2
        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }
        //Stage 3
        stage('Checkout') {
            steps {
                dir("${env.CUSTOM_WORKSPACE}") {
                    git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
                }
            }
        }
        //Stage 4
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
        //-----------------------------------------------------------------------------uncomment for Unit testing------------------------------------------------------------------
        // stage('Create Temp .env for Tests') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
        //             sh 'cp .env .env.temp'
        //             sh 'sed -i -e "s/\\r//g" .env.temp'
        //         }
        //     }
        // }
        // stage('Setup Python Environment') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
        //             sh 'bash -c "python3 -m venv venv"'
        //             sh 'bash -c ". venv/bin/activate && pip install -r requirements.txt"'
        //         }
        //     }
        // }
        // stage('Install Frontend Dependencies') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/client") {
        //             sh 'yarn install'
        //         }
        //     }
        // }
        // stage('Database Migration') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
        //             sh 'bash -c ". venv/bin/activate && flask db upgrade"'
        //         }
        //     }
        // }
        // stage('Run Unit Tests') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
        //             sh 'bash -c "set -a && source .env.temp && set +a && export PYTHONPATH=${CUSTOM_WORKSPACE}/react-flask-app/server && . venv/bin/activate && pytest test/test_api.py --junitxml=report.xml"'
                  
        //         }
        //     }
        // }
        //----------------------------------------------------------Uncomment for unit testing----------------------------------------------------------------------------------
        //Stage 5
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
        //Stage 6
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
        //Stage 7
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
        //------------------------------------------------------------Uncomment for UI testing----------------------------------------
        // stage('Run UI Tests') {
        //     steps {
        //         script {
        //             dir("${env.CUSTOM_WORKSPACE}/react-flask-app/client") {
        //                 sh 'npm run cypress:run'
        //             }
        //         }
        //     }
        // }
        
    }
        //------------------------------------------------------------Uncomment for UI testing----------------------------------------
    post {
        always {
                //------------------------------------------------------------Uncomment for Unit testing----------------------------------------
            // Archive test results and clean workspace
            // dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
            //     junit 'report.xml'
            // }
             //------------------------------------------------------------Uncomment for Unit testing----------------------------------------


                //------------------------------------------------------------Uncomment for UI testing----------------------------------------
            // dir("${env.CUSTOM_WORKSPACE}/react-flask-app/client/cypress/results") {
            //     archiveArtifacts artifacts: '*.xml', allowEmptyArchive: true
            // }
                //------------------------------------------------------------Uncomment for UI testing----------------------------------------
            //stage 7
            cleanWs()
        }
    }
}