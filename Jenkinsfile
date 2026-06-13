pipeline {
    agent any
    environment {
        DEPLOY_HOST = '157.22.175.213'
        DEPLOY_USER = 'root'
        DEPLOY_PATH = '/var/www/newprod'
        SSH_KEY_ID = 'jenkins-ssh-key'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Deploy to VPS') {
            steps {
                withCredentials([sshUserPrivateKey(
                    credentialsId: env.SSH_KEY_ID,
                    keyFileVariable: 'SSH_KEY'
                )]) {
                    sh '''
                        echo "🚀 Deploying to ${DEPLOY_PATH}..."
                        ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} 'mkdir -p /tmp/deploy'
                        ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} 'rm -f /tmp/deploy/files.tar.gz'

                        tar -czf - store/ users/ newprod/ templates/ static/ media/ \
                            --exclude='__pycache__' --exclude='*.pyc' | \
                            ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} 'cat > /tmp/deploy/files.tar.gz'

                        ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                            cd /var/www/newprod &&
                            rm -rf store/ users/ newprod/ templates/ static/ media/ &&
                            tar -xzf /tmp/deploy/files.tar.gz &&
                            rm /tmp/deploy/files.tar.gz &&
                            echo "✅ Files deployed."
                        '
                    '''
                }
            }
        }

        stage('Restart backend') {
            steps {
                withCredentials([sshUserPrivateKey(
                    credentialsId: env.SSH_KEY_ID,
                    keyFileVariable: 'SSH_KEY'
                )]) {
                    sh '''
                        ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                            cd /var/www/newprod &&
                            docker compose restart backend &&
                            sleep 5 &&
                            docker compose ps backend
                        '
                    '''
                }
            }
        }
    }
}