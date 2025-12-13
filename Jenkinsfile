pipeline {
    agent any

    environment {
        DOCKER_IMAGE           = "st20285217/admissions-api"
        DOCKERHUB_CREDENTIALS  = "dockerhub-creds"
        EC2_SSH_CREDENTIALS    = "ec2-ssh-key"
        EC2_HOST               = "44.192.14.128"
        PYTHONPATH             = "."
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Test') {
  steps {
    sh '''
      echo "Running tests in isolated Python container (debug first)"
      docker run --rm \
        --volumes-from jenkins-ci \
        -w "$WORKSPACE" \
        -e PYTHONPATH="$WORKSPACE" \
        python:3.13-slim \
        bash -lc '
          set -euxo pipefail
          echo "PWD=$(pwd)"
          echo "Listing workspace:"
          ls -la
          echo "Listing app folder if present:"
          ls -la app || true
          python -c "import sys; print('sys.path='); print('\\n'.join(sys.path))"
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          python -m pytest -q
        '
    '''
  }
}



        stage('Build Docker image') {
            steps {
                sh '''
                  echo "Building Docker image ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                  docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
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
                      docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                      docker push ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: [EC2_SSH_CREDENTIALS]) {
                    sh '''
                      echo "Deploying to EC2 (${EC2_HOST})"
                      ssh -o StrictHostKeyChecking=no ec2-user@${EC2_HOST} '
                        docker pull ${DOCKER_IMAGE}:latest &&
                        docker rm -f admissions-api || true &&
                        docker run -d --name admissions-api --restart unless-stopped -p 80:5000 ${DOCKER_IMAGE}:latest &&
                        curl -s http://localhost/health
                      '
                    '''
                }
            }
        }
    }
}
