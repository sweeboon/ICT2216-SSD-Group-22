pipeline {
    agent any

    environment {
        VENV_PATH = "${WORKSPACE}/venv"
        DOCKER_IMAGE = 'nginx'
        CONTAINER_NAME = 'nginx-container'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout and Update Files') {
            steps {
                script {
                    // If the directory exists, pull the latest changes. Otherwise, clone the repository.
                    sh '''
                        if [ -d "$WORKSPACE/react-flask-app/.git" ]; then
                            cd $WORKSPACE/react-flask-app
                            git pull origin main
                        else
                            git clone https://github.com/sweeboon/ICT2216-SSD-Group-22.git $WORKSPACE/react-flask-app
                        fi
                    '''
                }
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    // Create the virtual environment if it doesn't exist
                    sh 'bash -c "python3 -m venv $VENV_PATH"'
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                script {
                    // Install any dependencies listed in requirements.txt
                    sh 'bash -c "source $VENV_PATH/bin/activate && pip install -r $WORKSPACE/react-flask-app/server/requirements.txt"'
                }
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                script {
                    // Install Node.js dependencies
                    sh 'bash -c "cd $WORKSPACE/react-flask-app/src && yarn install"'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh "docker build -t ${DOCKER_IMAGE}:${env.BUILD_ID} -f $WORKSPACE/react-flask-app/Dockerfile $WORKSPACE/react-flask-app"
                }
            }
        }

        stage('Deploy Docker Image') {
            steps {
                script {
                    sh """
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true
                        docker run -d -p 80:80 --name ${CONTAINER_NAME} ${DOCKER_IMAGE}:${env.BUILD_ID}
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
