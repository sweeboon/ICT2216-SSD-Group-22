pipeline {
    agent any

    environment {
        VENV_PATH = 'react-flask-app/server/venv'
        FLASK_APP = 'react-flask-app/server/api.py'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout code from a source control management system (e.g., Git)
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    // Install Python and virtualenv
                    sh 'sudo apt-get update && sudo apt-get install -y python3 python3-venv'
                    // Check for the virtual environment, create it if it doesn't exist
                    sh 'python3 -m venv $VENV_PATH'
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                script {
                    // Activate the virtual environment and install dependencies
                    sh 'source $VENV_PATH/bin/activate && pip install -r react-flask-app/server/requirements.txt'
                }
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                script {
                    // Install Node.js and npm
                    sh 'curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -'
                    sh 'sudo apt-get install -y nodejs'
                    // Install Node.js dependencies and build the application
                    sh 'cd react-flask-app/src && npm install && npm run build'
                }
            }
        }

        stage('Deploy') {
            agent {
                docker {
                    image 'nginx'
                    args '-u root'
                }
            }
            steps {
                script {
                    // Get the Nginx container ID
                    def nginxContainerId = sh(script: "docker ps -q -f 'ancestor=nginx'", returnStdout: true).trim()
                    // Copy built React app to Nginx html directory
                    sh "docker cp react-flask-app/src/build/. ${nginxContainerId}:/usr/share/nginx/html/"
                }
            }
        }
    }

    post {
        always {
            // Clean up after the pipeline runs
            echo 'Cleaning up...'
            sh 'rm -rf ${VENV_PATH}'
        }
    }
}
