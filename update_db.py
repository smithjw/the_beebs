import os
import json
import boto3
import re

from botocore.exceptions import ClientError
from slackclient import SlackClient

def getParameter(param_name):
    # Create the SSM Client
    ssm = boto3.client(
        'ssm',
        region_name='us-east-1'
    )
    # Get the requested parameter
    response = ssm.get_parameters(
        Names=[param_name],
        WithDecryption=True
    )
    # Store the credentials in a variable
    credentials = response['Parameters'][0]['Value']

    return credentials


def get_user_info(user_id):
    slack_token = getParameter('PA_SLACK_BOT_TOKEN')
    sc = SlackClient(slack_token)

    user_info = sc.api_call(
      'users.info',
      user=user_id
    )

    return user_info


def extract_user_id(text):
    user_id = re.split('@|\|', text)[1]

    return user_id


def create_user_item(table, timestamp, user_id, uid_first, uid_last, uid_email):
    try:
        table.put_item(
            Item = {
                'user_id': user_id,
                'biebered_by': {},
                'uid_first': uid_first,
                'uid_last': uid_last,
                'uid_email': uid_email
            },
            ConditionExpression = 'attribute_not_exists(user_id)'
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConditionalCheckFailedException':
            print(f'User already exists, updating ID: {user_id}')
        else:
            print(f'Unexpected error: {error_code}')


def write_db_data(timestamp, user_id_info, biebered_by_info):
    table_name = os.environ['biebered_table_name']
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)

    # Info about the user that was Biebered

    # Replace these with .get just in case user doesn't have these items filled in
    user_id = user_id_info['user']['id']
    uid_first = user_id_info['user']['profile']['first_name']
    uid_last = user_id_info['user']['profile']['last_name']
    uid_email = user_id_info['user']['profile']['email']


    # Info about the user that did the Biebering

    # Replace these with .get just in case user doesn't have these items filled in
    # Need to add in checks for if no user is passed
    biebered_by_id = biebered_by_info['user']['id']
    bb_first = biebered_by_info['user']['profile']['first_name']
    bb_last = biebered_by_info['user']['profile']['last_name']
    bb_email = biebered_by_info['user']['profile']['email']

    print(f'Creating Item with ID: {user_id} if it doesn\'t already exist')
    create_user_item(table, timestamp, user_id, uid_first, uid_last, uid_email)

    response = table.update_item(
        Key={'user_id': user_id},
        UpdateExpression = 'SET #bb.#ts = :update',
        ExpressionAttributeNames = {
            '#bb': 'biebered_by',
            '#ts': timestamp
        },
        ExpressionAttributeValues = {
            ":update": {
                'user_id': biebered_by_id,
                'first_name': bb_first,
                'last_name': bb_last,
                'email': bb_email
            }
        }
    )

    return response


def main(message, timestamp):
    user_id = message['user_id'][0]
    biebered_by_id = extract_user_id(message['text'][0])
    user_id_info = get_user_info(user_id)
    biebered_by_info = get_user_info(biebered_by_id)

    write_db_data(timestamp, user_id_info, biebered_by_info)


def lambda_func(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    timestamp = event['Records'][0]['Sns']['Timestamp']
    main(message, timestamp)


if __name__ == '__main__':
    with open('test_message.json', encoding='utf-8') as json_file:
        message = json_file.read()
    timestamp = '2018-09-11T04:13:39.960Z'
    test_message = json.loads(message)


    main(test_message, timestamp)
