pipeline {
    agent any

    environment {
        VENV_PATH = 'react-flask-app/server/venv'
        FLASK_APP = 'react-flask-app/server/api.py'
    }

    stages {
        stage('Checkout') {
            agent {
                docker {
                    image 'nginx'
                    args '-u root'
                }
            }
            steps {
                // Checkout code from a source control management system (e.g., Git)
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }

        stage('Setup Virtual Environment') {
            agent {
                docker {
                    image 'nginx'
                    args '-u root'
                }
            }
            steps {
                script {
                    // Install Python if not available (typically not part of nginx image)
                    sh 'apt-get update && apt-get install -y python3 python3-venv'
                    // Check for the virtual environment, create it if it doesn't exist
                    sh 'python3 -m venv $VENV_PATH'
                }
            }
        }

        stage('Install Python Dependencies') {
            agent {
                docker {
                    image 'nginx'
                    args '-u root'
                }
            }
            steps {
                script {
                    // Activate the virtual environment and install dependencies
                    sh 'apt-get update && apt-get install -y python3-pip'
                    sh 'source $VENV_PATH/bin/activate && pip install -r react-flask-app/server/requirements.txt'
                }
            }
        }

        stage('Install Node.js Dependencies') {
            agent {
                docker {
                    image 'nginx'
                    args '-u root'
                }
            }
            steps {
                script {
                    // Install Node.js and npm if not available (typically not part of nginx image)
                    sh 'apt-get update && apt-get install -y curl'
                    sh 'curl -sL https://deb.nodesource.com/setup_14.x | bash -'
                    sh 'apt-get install -y nodejs'
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
