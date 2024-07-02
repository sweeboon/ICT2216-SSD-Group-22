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
                script {
                    // Install git to be able to checkout code
                    sh 'apt-get update && apt-get install -y git'
                    // Checkout code from a source control management system (e.g., Git)
                    git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
                }
            }
        }

        stage('Setup Virtual Environment') {
            agent {
                docker {
                    image 'nginx'
                    args '-u root'
                }
            
            steps {
                script {
                    // Check for the virtual environment, create it if it doesn't exist
                    sh 'bash -c "python3 -m venv $VENV_PATH"'
                    // Activate the virtual environment
                    sh 'bash -c "source $VENV_PATH/bin/activate"'
                }
            }
        }

        stage('Install Python Dependencies') {
            agent {
                docker {
                    image 'nginx'
                    args '-u root'
                }
            
            steps {
                steps {
                // Install any dependencies listed in requirements.txt
                sh 'bash -c "source $VENV_PATH/bin/activate && pip install -r react-flask-app/server/requirements.txt"'
                }
            }
        }

        stage('Install Node.js Dependencies') {
            agent {
                docker {
                    image 'nginx'
                    args '-u root'
                }
            
                steps {
                    // Install Node.js dependencies
                    sh 'bash -c "cd react-flask-app/src && npm install"'
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
    

    post {
        always {
            // Clean up after the pipeline runs
            echo 'Cleaning up...'
            sh 'rm -rf ${VENV_PATH}'
        }
    }
}
