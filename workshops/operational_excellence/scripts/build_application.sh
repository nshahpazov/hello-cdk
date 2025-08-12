# #!/bin/bash

# # Build Script
LABEL='latest'
ECR_REPONAME='walab-ops-sample-application'
SAMPLE_APPNAME=$ECR_REPONAME
MAIN_STACK='walab-ops-base-resources'
AWS_REGION=$1
AWS_ACCOUNT=$2
SYSOPSEMAIL=nikola.shahpazov@intellias.com
SYSOWNEREMAIL=nikola.shahpazov@intellias.com

# sudo brew install jq httpd-tools -y -q

# echo '#################################################'
# echo 'Script will deploy application with below details'
# echo '#################################################'
# echo 'Region: ' $AWS_REGION
# echo 'Account: '$AWS_ACCOUNT

# echo 'Repo Name: '$
ECR_REPONAME
# echo 'Label: '$LABEL


# echo '########################'
# echo 'Deploy Baseline Resources Stack'
# echo '########################'

# aws cloudformation create-stack --stack-name $MAIN_STACK \
#                                 --template-body file://../templates/base_resources.yml \
#                                 --capabilities CAPABILITY_NAMED_IAM \
#                                 --tags Key=Application,Value=OpsExcellence-Lab

# aws cloudformation wait stack-create-complete --stack-name $MAIN_STACK

echo '##############################'
echo 'Building Application Container'
echo '##############################'
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
docker build -t $ECR_REPONAME ../src/
docker tag $ECR_REPONAME:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPONAME:$LABEL
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPONAME:$LABEL

echo '########################'
echo 'Deploy Application Stack'
echo '########################'
# aws iam create-service-linked-role --aws-service-name ecs.amazonaws.com
# sleep 10

aws cloudformation create-stack --stack-name $ECR_REPONAME \
                                --template-body file://../templates/base_app.yml \
                                --parameters ParameterKey=BaselineVpcStack,ParameterValue=$MAIN_STACK \
                                            ParameterKey=ECRImageURI,ParameterValue=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPONAME:$LABEL \
                                            ParameterKey=SystemOpsNotificationEmail,ParameterValue=$SYSOPSEMAIL \
                                            ParameterKey=SystemOwnerNotificationEmail,ParameterValue=$SYSOWNEREMAIL \
                                --capabilities CAPABILITY_NAMED_IAM \
                                --tags Key=Application,Value=OpsExcellence-Lab

echo '#########################################'
echo 'Waiting for Application Stack to complete'
echo '#########################################'
aws cloudformation wait stack-create-complete --stack-name $ECR_REPONAME

echo '#########################################'
echo 'Application create complete'
echo '#########################################'