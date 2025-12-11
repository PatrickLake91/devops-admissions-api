pipeline {
    agent any

    environment {
        DOCKER_IMAGE        = "st20285217/admissions-api"
        DOCKERHUB_CREDENTIALS = "dockerhub-creds"
        PYTHONPATH          = "."
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

                stage('Test') {
            steps {
                sh '''
                  echo "Installing Python dependencies"
                  python3 -m pip install --no-cache-dir -r requirements.txt

                  echo "Running pytest for admissions eligibility API"
                  python3 -m pytest -q
                '''
            }
        }


        stage('Build Docker image') {
            steps {
                sh '''
                  echo "Building Docker image ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                  docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: DOCKERHUB_CREDENTIALS,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                      echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                      docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Deploy locally') {
            steps {
                sh '''
                  echo "Deploying container on port 5001"
                  docker rm -f admissions-api-ci || true
                  docker run -d --name admissions-api-ci -p 5001:5000 ${DOCKER_IMAGE}:${BUILD_NUMBER}
                '''
            }
        }
    }
}
