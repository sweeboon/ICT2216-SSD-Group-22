pipeline {
    agent any
   
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }
        stage('Verify Checkout') {
            steps {
                script {
                    sh 'echo "Current workspace: $WORKSPACE"'
                    sh 'ls -l $WORKSPACE'
                    sh 'ls -l $WORKSPACE/react-flask-app'
                }
            }
        }
        stage('Clean Up') {
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
                    user 'root'
                }
            }
            steps {
                script {
                    sh '''
                        existing_container=$(docker ps -q --filter ancestor=jwilder/nginx-proxy)
                        if [ ! -z "$existing_container" ]; then
                            docker stop $existing_container
                            docker rm $existing_container
                        fi
                    '''
                    sh 'docker-compose -f $WORKSPACE/react-flask-app/docker-compose.yml down'
                }
            }
        }
        stage('Deploy Application') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                    user 'root'
                }
            }
            steps {
                script {
                    sh 'docker-compose -f $WORKSPACE/react-flask-app/docker-compose.yml up -d --build'
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
