import os
import json
import boto3
import re
from botocore.exceptions import ClientError


def extract_user_id(text):
    user_id = re.split('@|\|', text)[1]

    return user_id

def create_user_item(table, user_id, timestamp):
    try:
        table.put_item(
            #Key = {'user_id': user_id},
            Item = {'user_id': user_id, 'biebered_by': {}},
            #UpdateExpression = 'SET biebered_by = {}',
            ConditionExpression = 'attribute_not_exists(user_id)'
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConditionalCheckFailedException':
            print(f'User already exists, updating ID: {user_id}')
        else:
            print(f'Unexpected error: {error_code}')

def write_db_data(message, timestamp):
    table_name = os.environ['biebered_table_name']
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)

    user_id = message['user_id'][0]
    biebered_by_id = extract_user_id(message['text'][0])

    #print(user_id, biebered_by_id, timestamp)

    print(f'Creating Item with ID: {user_id} if it doesn\'t already exist')
    create_user_item(table, user_id, timestamp)

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
                # Call out to Slack API to grab biebered_by User information
                'first_name': 'first_name'
            }
        }
    )

    return response


def main(event, timestamp):
    test_message = json.loads(event)

    write_db_data(test_message, timestamp)


def lambda_func(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    timestamp = json.loads(event['Records'][0]['Sns']['Timestamp'])
    main(message, timestamp)


if __name__ == '__main__':
    with open('test_message.json', encoding='utf-8') as json_file:
        message = json_file.read()
    timestamp = '2018-09-11T04:13:39.960Z'

    main(message, timestamp)
