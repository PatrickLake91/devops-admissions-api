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
                      ssh -o StrictHostKeyChecking=no ec2-user@${EC2_HOST} 'bash -se' <<'REMOTE'
                        set -euo pipefail

                        IMAGE="${DOCKER_IMAGE}:latest"
                        NAME="admissions-api"
                        HEALTH_URL="http://localhost/health"

                        echo "Pulling $IMAGE..."
                        docker pull "$IMAGE"

                        echo "Stopping/removing existing container (if any)..."
                        docker rm -f "$NAME" >/dev/null 2>&1 || true

                        echo "Starting new container..."
                        docker run -d --name "$NAME" --restart unless-stopped -p 80:5000 "$IMAGE" >/dev/null

                        echo "Waiting for health endpoint: $HEALTH_URL"
                        # Retry up to ~60s (30 * 2s)
                        for i in $(seq 1 30); do
                          if curl -fsS --max-time 2 "$HEALTH_URL" >/dev/null; then
                            echo "Healthy on attempt $i"
                            curl -fsS --max-time 2 "$HEALTH_URL" || true
                            exit 0
                          fi

                          echo "Not healthy yet (attempt $i/30). Diagnostics:"
                          docker ps --filter "name=$NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true
                          docker logs --tail 50 "$NAME" || true
                          sleep 2
                        done

                        echo "ERROR: Service did not become healthy in time."
                        echo "Final diagnostics:"
                        docker ps --filter "name=$NAME" || true
                        docker logs --tail 200 "$NAME" || true
                        exit 1
REMOTE
                    '''
                }
            }
        }
    }
}

