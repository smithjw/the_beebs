import os
import json
import boto3

def write_db_data(message, timestamp):
    table_name = os.environ['biebered_table_name']
    #dynamo = boto3.client('dynamodb', region_name='us-east-1')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)

    user_id = message['user_id'][0]
    biebered_by = message['text'][0]

    print(user_id, biebered_by, timestamp)

    # response = dynamo.update_item(
    #     TableName='string',
    #     Key={'user_id': {'S': user_id}},
    #     UpdateExpression={'biebered_by': biebered_by}
    # )

    response = table.update_item(
        Key={
            'user_id': user_id
        },
        UpdateExpression='SET biebered_by = list_append(biebered_by, :vals)',
        ExpressionAttributeValues={
            ':vals': {
                timestamp: [
                    {'timestamp': timestamp},
                    {'name': biebered_by}
                ]
            }
        }
    )

    return response

def main(event, timestamp):
    test_message = json.loads(event)
    print(test_message)

    write_db_data(test_message, timestamp)


def lambda_func(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    timestamp = json.loads(event['Records'][0]['Sns']['Timestamp'])
    main(message, timestamp)


if __name__ == '__main__':
    with open('test_message.json', encoding='utf-8') as json_file:
        message = json_file.read()
    timestamp = '2018-09-05T04:13:39.960Z'

    main(message, timestamp)
