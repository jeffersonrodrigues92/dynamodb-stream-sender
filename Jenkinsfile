#!groovy

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

pipeline {
    agent any
    tools {
        maven 'M2'
        jdk 'Jdk1.8u191'
    }
    environment {

        RUN_PRE_BUILD = true
        RUN_POST_BUILD = true
        RUN_COMPILE = true
        RUN_CHECKS = true
        S3_BUCKET_ARTIFACT = "cdt-devops-tools-lambda-functions-artifacts"
        S3_BUCKET_TEMPLATE = "cdt-devops-tools-lambda-functions-template"


    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '50'))
        timeout(time: 20, unit: 'MINUTES')
    }


    stages {

        stage('Check commit message') {
          steps {
            script {
              current_commit_message = sh(script: '''
                git rev-list --format=%B --max-count=1 HEAD |head -2 |tail -1
              ''', returnStdout: true).trim()

              if (current_commit_message == 'Prepare for next Release') {
                currentBuild.result = 'ABORTED'
                error('Parando build por ser um commit de CI.')
              }
            }
          }
        }

        stage('Check Branch Name') {
            steps {
                script {
                    if (BRANCH_NAME.startsWith("master") || BRANCH_NAME.startsWith("feature") || BRANCH_NAME.startsWith("develop") || BRANCH_NAME.startsWith("release") || BRANCH_NAME.startsWith("hotfix")) {
                        echo "***** Let's go to the Build *****"

                    } else {
                        currentBuild.result = 'ABORTED'
                        error('Parando o build por não estar de acordo com a nomenclatura de Branch.')
                    }
                }
            }
        }

        stage('Notify') {
            steps {
                echo sh(returnStdout: true, script: 'env')
                notifyBuild('STARTED')
            }
        }

        stage('Pre-Build CheckList') {
            when {
                environment name: 'RUN_CHECKS', value: 'true'
            }
            steps {
                checkCommitBehind()
            }
        }

        stage('compile') {
            steps {
                script{
                    sh 'source /var/lib/jenkins/pvenvs/python/bin/activate'
                    sh 'npm install --save-dev serverless-python-requirements fs-extra jszip'
                    sh 'serverless package'
                }
            }
        }
        stage('Pre-Build') {
            when {
                environment name: 'RUN_PRE_BUILD', value: 'true'
            }
            steps {

                script {
                    env['REPO_NAME_STACK'] = sh(script: '''
                                             git remote show -n origin | grep Fetch | sed -r 's,.*:(.*).git,\\1,' |tr -d '\n'
                                             ''', returnStdout: true).trim()

                   env['stack_name'] = sh(script: '''
                                                 echo $(git remote -v |grep fetch |sed -r 's,.*\\.com:[^/]*/(.*)\\.git.*,\\1,')
                                              ''', returnStdout: true).trim()

                    env['RUN_BUILD_BRANCH'] = false
                    env['RUN_BUILD_MASTER'] = false

                    if (BRANCH_NAME.startsWith("master")) {
                        echo "***** PERFORMING STEPS ON MASTER *****"
                        env['RUN_BUILD_MASTER'] = true
                        env['environment'] = "prd"
                        env['RUN_DEPLOY'] = true
                        updateVersion(true)

                    } else if (BRANCH_NAME.startsWith("develop")) {
                        echo "***** PERFORMING STEPS ON RELEASE BRANCH *****"
                        env['RUN_BUILD_BRANCH'] = true
                        env['environment'] = "dev"
                        env['RUN_DEPLOY'] = false
                        updateVersion(false)

                    } else if (BRANCH_NAME.startsWith("feature")) {
                        echo "***** PERFORMING STEPS ON RELEASE BRANCH *****"
                        env['RUN_BUILD_BRANCH'] = true
                        env['environment'] = "hml"
                        env['RUN_DEPLOY'] = false
                        updateVersion(false)

                    } else if (BRANCH_NAME.startsWith("release")) {
                        echo "***** PERFORMING STEPS ON RELEASE BRANCH *****"
                        env['RUN_BUILD_BRANCH'] = true
                        env['environment'] = "hml"
                        env['RUN_DEPLOY'] = false
                        updateVersion(false)

                    } else if (BRANCH_NAME.startsWith("hotfix")) {
                        echo "***** PERFORMING STEPS ON RELEASE BRANCH *****"
                        env['RUN_BUILD_BRANCH'] = true
                        env['environment'] = "hml"
                        env['RUN_DEPLOY'] = false
                        updateVersion(false)

                    }
                    else {
                        echo "***** BRANCHES MUST START WITH DEVELOPER OR HOTFIX *****"
                        echo "***** STOPPED BUILD *****"
                        currentBuild.result = 'FAILURE'
                    }
                }

                echo "***** FINISHED PRE-BUILD STEP *****"
            }
        }

        stage('package-sam') {
            steps {
              script{
                sh 'aws cloudformation package --template-file cloudformation/template/cloudformation.yml --s3-bucket ${S3_BUCKET_ARTIFACT}  --output-template-file cloudformation/output/cloudformation.yml'
                env['fileOutput'] = 'cloudformation.yml'
              }
            }
        }

        stage('upload cloudformation templates and parameter files') {
            steps {
                script{
                    echo "upload template to s3://${env.S3_BUCKET_TEMPLATE}/dynamodb-replica-data/${newVersion}/templates/"
                    sh "aws s3 cp cloudformation/output/cloudformation.yml s3://${S3_BUCKET_TEMPLATE}/dynamodb-replica-data/${newVersion}/templates/"
                    echo "upload parameter files to s3://${env.S3_BUCKET_TEMPLATE}/dynamodb-replica-data/${newVersion}/parameters/"
                    sh "aws s3 sync cloudformation/parameters/ s3://${env.S3_BUCKET_TEMPLATE}/dynamodb-replica-data/${newVersion}/parameters/"
                }
            }
        }

        stage('Deploy stack') {
          steps {
            script{
              echo "deploy stack dynamodb-replica-data ${env.environment} to cloudformation"
                script {
                    if (BRANCH_NAME.startsWith("master")) {
                        echo "Iniciando o deploy no ambiente de PRD"
                        sh(script: '''
                            curl -D - -X "POST" -H "Accept: application/json" -H "Content-Type: application/json" -H "X-Rundeck-Auth-Token: wRPCmvpA3F230lLvaxlXKTtKLkLsvvn9" -d '{"argString":"-template '${fileOutput}' -version '${newVersion}' -path dynamodb-replica-data -Arquitetura Serverless"}' http://rundeck.devtools.caradhras.io:4440/api/19/job/e7f60eb3-81ac-4667-ae9d-791a49bfa6e7/executions
                        ''',)
                    }
                }
            }
          }
      }
        stage('Deploy stack DR') {
          steps {
            script{
              echo "deploy stack dynamodb-replica-data ${env.environment} to cloudformation"
                script {
                    if (BRANCH_NAME.startsWith("master")) {
                        echo "Iniciando o deploy no ambiente de DR"
                        deploy('dr', '97f9bc60-7d2c-4a4c-b2bb-becde0c9e04f')
                    }
                }
            }
          }
      }
    }
    post {
        success {
            notifyBuild('SUCCESSFUL')
            echo "success"
        }
        failure {
            notifyBuild('FAILED')
            echo "failure"
        }
        always {
            deleteDir()
        }
    }
}

def notifyBuild(String buildStatus = 'STARTED') {
    buildStatus = buildStatus ?: 'SUCCESSFUL'

    String colorCode = '#FF0000'
    String subject = "${buildStatus}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
    String summary = "${subject} \n (${env.BUILD_URL})  "
    String details = """<p>${buildStatus}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
    <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>"""


    JSONArray attachments = new JSONArray();
    JSONObject attachment = new JSONObject();

  if (buildStatus == 'STARTED') {
        colorCode = '#FFFF00'
        attachment.put('text','Replicando mudança')
        attachment.put('thumb_url','https://s3.us-east-2.amazonaws.com/upload-icon/uploads/icons/png/9820297401540553608-512.png')
    } else if (buildStatus == 'SUCCESSFUL') {
        colorCode = '#00FF00'
        attachment.put('text','Replicação Finalizada Com Sucesso!')
        attachment.put('thumb_url','https://s3.us-east-2.amazonaws.com/upload-icon/uploads/icons/png/9820297401540553608-512.png')

        JSONArray fields = new JSONArray();
        JSONObject field = new JSONObject();

        field.put('title', 'URL Template S3');
        field.put('value', env['fileOutput']);
        fields.add(field);

        field = new JSONObject();

        field.put('title', 'Version');
        field.put('value', env['newVersion']);
        fields.add(field);

        field.put('title', 'Path');
        field.put('value', 'dynamodb-replica-data');
        fields.add(field);

        attachment.put('fields',fields);

    } else {
        attachment.put('text','Erro ao Replicar Mudanças')
        attachment.put('thumb_url','https://s3.us-east-2.amazonaws.com/upload-icon/uploads/icons/png/9820297401540553608-512.png')
        colorCode = '#FF0000'
    }

    String buildUrl = "${env.BUILD_URL}";
    attachment.put('title', subject);
    attachment.put('callback_id', buildUrl);
    attachment.put('title_link', buildUrl);
    attachment.put('fallback', subject);
    attachment.put('color', colorCode);

    attachments.add(attachment);

    echo attachments.toString();
    slackSend(attachments: attachments.toString())
}

def updateVersion(boolean isMaster){
    version_code_tag()
    def oldVersion = "${env.bumpci_tag}".tokenize('.')
    major = oldVersion[0].toInteger()
    minor = oldVersion[1].toInteger()
    patch = oldVersion[2].toInteger()

    if(isMaster){
      minor += 1
      patch = 0
    }else{
      patch += 1
    }
    env['newVersion'] = major + '.' + minor + '.' + patch

    bump_version_tag()

}

def version_code_tag() {
    echo "getting Git version Tag"
    script {
        sh "git fetch --tags"
        env['bumpci_tag'] = sh(script: '''
            current_tag=`git tag -n9 -l |grep version |awk '{print $1}' |sort -V |tail -1`
            if [[ $current_tag == '' ]]
              then
                current_tag=0.0.1
            fi
            echo ${current_tag}
            ''', returnStdout: true).trim()
    }
  }

  def bump_version_tag() {
    echo "Bumping version CI Tag"
    script {
        sh "git tag -a ${newVersion} -m version && git push origin refs/tags/${newVersion}"
    }
  }

def get_envs(){
  script{
    def URL_COMMIT = "https://api.github.com/repos/${env.REPO_NAME_STACK}-infra/commits"
    def response_commit = httpRequest authentication: 'github-user', httpMode: 'GET', url: "${URL_COMMIT}"
    def response_payload = readJSON text: response_commit.content

    def sha_tree = ""
    for (commits in response_payload){
        sha_tree = commits['commit']['tree']['sha']
        break;
    }

    def URL_TREE = "https://api.github.com/repos/${env.REPO_NAME_STACK}-infra/git/trees/${sha_tree}?recursive=1'"
    def response_tree = httpRequest authentication: 'github-user', httpMode: 'GET', url: "${URL_TREE}"
    def response_tree_payload = readJSON text: response_tree.content

    def envs = []
    for(tree in response_tree_payload['tree']){
        def regex = ".*/(.*)\\.json"
        path_match = tree['path'] ==~ regex
        if(path_match){
            def matcher = tree['path'] =~ regex
            def env_infra = matcher[0][1]
            envIsprd = env_infra ==~ 'prd|blue|green'
            if(!envIsprd){
              envs.add(matcher[0][1])
            }
        }
    }
    return envs
  }
}
def checkCommitBehind() {
    sh 'echo "Verifica se branch necessita de merge com master."'
    script {
        sh(script: '''set +x; set +e;
                      git config --add remote.origin.fetch +refs/heads/master:refs/remotes/origin/master
                      git fetch --no-tags
                      commitsBehind=$(git rev-list --left-right --count origin/master... |awk '{print $1}')
                      if [ "${commitsBehind}" -ne 0 ]
                      then
                        echo "Esta branch está ${commitsBehind} commits atrás da master!"
                        exit 1
                      else
                       echo "Esta branch não tem commits atrás da master."
                      fi''')
    }
}
