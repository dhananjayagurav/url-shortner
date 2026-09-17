pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Install') {
      steps {
        sh 'pip install --break-system-packages -e ".[dev]"'
      }
    }
    stage('Lint') {
      steps {
        sh 'python3 -m ruff check .'
      }
    }
    stage('Unit tests') {
      steps {
        sh 'python3 -m pytest tests/unit -v'
      }
    }
  }

  post {
    always {
      echo 'Pipeline finished.'
    }
  }
}