pipeline{
    agent any
    stages{
        stage("test") {
            steps {
                script{
                    echo "testing the app..."
                    echo "executing pipeline for branch $BRANCH_NAME"
                }
            }
        }
        stage("build") {
            when{
                expression{
                    BRANCH_NAME == "master"
                }
            }
            steps {
                script{
                    echo "Building the app..."
                }
            }
        }
        stage("deply") {
            when{
                expression{
                    BRANCH_NAME == "master"
                }
            }
            steps {
                script{
                    echo "deploying the app..."
                }
            }
        }
    }
}
