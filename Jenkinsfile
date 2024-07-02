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

        // Commented out due to current issues
        // stage('OWASP Dependency Check') {
        //     steps {
        //         dependencyCheck additionalArguments: '''-o ./ --format HTML --format XML --disableYarnAudit --noupdate''', odcInstallation: 'DependencyCheck'
        //     }
        // }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("nginx:${env.BUILD_ID}")
                }
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
