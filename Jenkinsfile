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
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main'
            }
        }

        stage('Setup Virtual Environment') {
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
            steps {
                // Install any dependencies listed in requirements.txt
                sh 'bash -c "source $VENV_PATH/bin/activate && pip install -r react-flask-app/server/requirements.txt"'
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                // Install Node.js dependencies
                sh 'bash -c "cd react-flask-app/src && npm install"'
            }
        }

        stage('Test') {
            steps {
                // Run your tests here. This is just a placeholder.
                // For example, if you had tests, you might run: pytest for Python tests and npm test for React tests
                echo "Assuming tests are run here. Please replace this with actual test commands."
                // Python tests
                // sh "source $VENV_PATH/bin/activate && pytest"
                // React tests
                // sh 'bash -c "cd react-flask-app/src && npm test"'
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Deploy your Flask and React apps
                    // This step greatly depends on where and how you're deploying your app
                    // For example, if you're deploying to a server you control,
                    // you might use scp, rsync, or SSH commands
                    // If you're using a PaaS (Platform as a Service), you might use a specific CLI tool for that platform
                    echo 'Deploying application...'
                    // Example: sh 'scp -r . user@your_server:/path/to/deploy'
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
