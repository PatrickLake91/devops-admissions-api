pipeline {
    agent any

    environment {
        DOCKER_IMAGE          = "st20285217/admissions-api"
        DOCKERHUB_CREDENTIALS = "dockerhub-creds"
        EC2_SSH_CREDENTIALS   = "ec2-ssh-key"
        EC2_HOST              = "44.192.14.128"
    }

    stages {

   stage('Test') {
    steps {
        sh '''
          echo "Running tests in isolated Python container (using Jenkins volume)"
          docker run --rm \
            --volumes-from jenkins-ci \
            -w /var/jenkins_home/workspace/devops-admissions-api-pipeline \
            python:3.13-slim bash -lc "
              export PYTHONPATH=/var/jenkins_home/workspace/devops-admissions-api-pipeline &&
              python -m pip install --upgrade pip &&
              pip install -r requirements.txt &&
              pytest -q
            "
        '''
    }
}



        stage('Build Docker image') {
            steps {
                sh '''
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
          set -e

          docker pull ${DOCKER_IMAGE}:latest
          docker rm -f admissions-api || true
          docker run -d --name admissions-api --restart unless-stopped -p 80:5000 ${DOCKER_IMAGE}:latest

          echo "Waiting for /health..."
          for i in {1..20}; do
            if curl -fsS http://localhost/health > /dev/null; then
              echo "Health check OK"
              exit 0
            fi
            echo "Not ready yet ($i/20) - sleeping 2s"
            sleep 2
          done

          echo "Health check failed after retries"
          docker logs --tail 80 admissions-api || true
          exit 1
        '
      '''
    }
  }
}

