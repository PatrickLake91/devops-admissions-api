# Ansible deployment (assessment evidence)

This folder demonstrates configuration management using Ansible.

Target: Amazon Linux 2023 EC2 instance (devops-admissions-api-ansible)

What it does:
- Updates packages
- Installs and starts Docker
- Pulls the latest Admissions API image from Docker Hub
- Recreates the container and maps port 80 -> 5000
- Waits until /health returns HTTP 200

Run (from Windows using Docker):
docker run --rm -it -v ${PWD}:/work -w /work cytopia/ansible:latest sh -lc "apk add --no-cache openssh-client && chmod 600 ec2-key.pem && ansible-playbook -i inventory.ini playbook.yml"

