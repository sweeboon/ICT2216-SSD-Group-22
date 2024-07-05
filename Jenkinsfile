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
        stage('Create start.sh Script') {
            steps {
                script {
                    sh '''
                        cat << 'EOF' > $WORKSPACE/react-flask-app/start.sh
                        #!/bin/bash
                        # Start the Flask app
                        cd /usr/src/app/server
                        source venv/bin/activate
                        flask run --host=0.0.0.0 --port=5000 &
                        # Start the React app
                        cd /usr/src/app
                        yarn start
                        EOF
                        chmod +x $WORKSPACE/react-flask-app/start.sh
                    '''
                }
            }
        }
        stage('Commit start.sh Script') {
            steps {
                script {
                    sh '''
                        cd $WORKSPACE/react-flask-app
                        git add start.sh
                        git commit -m "Add start.sh script"
                        git push origin main
                    '''
                }
            }
        }
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
        stage('Stop and Remove Existing Containers') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    sh 'docker-compose -f $WORKSPACE/react-flask-app/docker-compose.yml down'
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
