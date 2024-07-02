pipeline {
    agent any

    environment {
        VENV_PATH = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main'
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    // Check for the virtual environment, create it if it doesn't exist
                    sh 'python3 -m venv $VENV_PATH'
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                // Install any dependencies listed in requirements.txt
                sh 'bash -c "source $VENV_PATH/bin/activate && pip install -r react-flask-app/server/requirements.txt"'
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                // Install Node.js dependencies
                sh 'bash -c "cd react-flask-app/src && yarn install"'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t nginx:${env.BUILD_ID} .'
                }
            }
        }

        stage('Deploy Docker Image') {
            steps {
                script {
                    sh """
                        docker stop nginx || true
                        docker rm nginx || true
                        docker run -d -p 80:80 --name nginx nginx:${env.BUILD_ID}
                    """
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
