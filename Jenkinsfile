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
        //         """, odcInstallation: 'OWASP Dependency-Check Vulnerabilities'

        //         dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        //     }
        

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
        stage ('Build') {
            steps {
                sh '/var/jenkins_home/apache-maven-3.9.8/bin/mvn --batch-mode -V -U -e clean
                verify -Dsurefire.useFile=false -Dmaven.test.failure.ignore'
                }
            }
            stage ('Analysis') {
                steps {
                    sh '/var/jenkins_home/apache-maven-3.9.8/bin/mvn --batch-mode -V -U -e
                    checkstyle:checkstyle pmd:pmd pmd:cpd findbugs:findbugs'
                             }
                        }
                    }
                    post {
                        always {
                            junit testResults: '**/target/surefire-reports/TEST-*.xml'
                            recordIssues enabledForFailure: true, tools: [mavenConsole(), java(), javaDoc()]
                            recordIssues enabledForFailure: true, tool: checkStyle()
                            recordIssues enabledForFailure: true, tool: spotBugs(pattern:
                            '**/target/findbugsXml.xml')
                            recordIssues enabledForFailure: true, tool: cpd(pattern: '**/target/cpd.xml')
                            recordIssues enabledForFailure: true, tool: pmdParser(pattern: '**/target/pmd.xml')
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
        // stage('Create Temp .env for Tests') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
        //             sh 'cp .env .env.temp'
        //             sh 'sed -i -e "s/\r//g" .env.temp'
        //         }
        //     }
        // }
        // stage('Convert .env.temp to Unix Line Endings') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
        //             sh 'sed -i -e "s/\r//g" .env.temp'
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
        //  stage('Database Migration') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
        //             sh 'bash -c ". venv/bin/activate && flask db upgrade"'
        //         }
        //     }
        // }
        // stage('Run Tests') {
        //     steps {
        //         dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
        //             sh 'bash -c "set -a && source .env.temp && set +a && export PYTHONPATH=${CUSTOM_WORKSPACE}/react-flask-app/server && . venv/bin/activate && pytest test/test_api.py --junitxml=report.xml"'
        //             sh 'ls -l'  // List files to verify if report.xml is generated
        //         }
        //     }
        // }
    

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
    
       

        

    post {
        always {
            //archive report
            dir("${env.CUSTOM_WORKSPACE}/react-flask-app/server") {
                junit 'report.xml'  // Archive the test results
                cleanWs()
        // success {
        //     dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        // }
        }
        }
    
        
    }
    
}


