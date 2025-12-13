pipeline {
    agent any

    environment {
        DOCKER_IMAGE            = "st20285217/admissions-api"
        DOCKERHUB_CREDENTIALS   = "dockerhub-creds"
        PYTHONPATH              = "."

        // EC2 deploy settings
        EC2_HOST                = "44.192.14.128"
        EC2_USER                = "ec2-user"
        EC2_SSH_CRED            = "ec2-ssh-key"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Test') {
            steps {
                sh '''
                  echo "Installing Python dependencies"
                  python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt

                  echo "Running pytest"
                  python3 -m pytest -q
                '''
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                  echo "Building Docker image ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                  docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .

                  echo "Tagging ${DOCKER_IMAGE}:latest"
                  docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
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

                      echo "Pushing ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                      docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}

                      echo "Pushing ${DOCKER_IMAGE}:latest"
                      docker push ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy locally') {
            steps {
                sh '''
                  echo "Deploying container locally on port 5001"
                  docker rm -f admissions-api-ci || true
                  docker run -d --name admissions-api-ci -p 5001:5000 ${DOCKER_IMAGE}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ["${EC2_SSH_CRED}"]) {
                    sh '''
                      echo "Deploying to EC2 ${EC2_USER}@${EC2_HOST}"

                      ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                        set -e
                        docker pull ${DOCKER_IMAGE}:latest
                        docker rm -f admissions-api || true
                        docker run -d --name admissions-api --restart unless-stopped -p 80:5000 ${DOCKER_IMAGE}:latest
                        curl -s http://localhost/health
                      '
                    '''
                }
            }
        }
    }
}

