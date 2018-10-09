# Welcome to The Biebs

## Setup

### Setting up AWS Encryption Keys
I suggest setting up a new encryption key for the key/value pairs that we'll be storing in AWS to make this all work. You can follow the instructions [here](https://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html#create-keys-console) to set one up. Make sure to select the same region as you'll be deploying this to.

### Install Python Dependencies
`pip install -r requirements.txt`

### Install Serverless Dependencies
`npm install`

### Deploy The Biebs
`sls deploy --aws-profile AWS_CONFIG_NAME --region AWS_REGION --stage STAGE_NAME --keyid AWS_ENCRYPTION_KEY_ID --selfserviceurl SELF_SERVICE_POLICY_LINK`
·
