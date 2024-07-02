pipeline {
    options {
        disableConcurrentBuilds()
    }
    agent any
    environment {
        CI = 'true'
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }

        // stage('OWASP Dependency Check') {
        //     steps {
        //         dependencyCheck additionalArguments: '''-o ./ --format HTML --format XML --disableYarnAudit --noupdate''', odcInstallation: 'DependencyCheck'
        //     }
        // }

        stage('Setup Virtual Environment') {
            steps {
                sh 'python3 -m venv react-flask-app/server/venv'
                sh 'source react-flask-app/server/venv/bin/activate'
            }
        }

        stage('Install Python Dependencies') {
            steps {
                sh 'source react-flask-app/server/venv/bin/activate && pip install -r react-flask-app/server/requirements.txt'
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                sh 'cd react-flask-app/src && npm install && yarn install'
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('', '') { // No need for registry credentials
                        dockerImage.push("${env.BUILD_ID}")
                        dockerImage.push("latest")
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            // Commented out due to current issues
            // dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        }
    }
}
