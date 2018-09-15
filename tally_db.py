import os
import json
import boto3

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


def getParameter(param_name, region):
    # Create the SSM Client
    ssm = boto3.client(
        'ssm',
        region_name=region
    )
    # Get the requested parameter
    response = ssm.get_parameters(
        Names=[param_name],
        WithDecryption=True
    )
    # Store the credentials in a variable
    credentials = response['Parameters'][0]['Value']

    return credentials


def get_table(table_name, region):
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)

    return table


def create_user_record(table, user_id, uid_first, uid_last, uid_email):
    if uid_first == 'Unknown' or uid_first == 'Unknown':
        uid = user_id
    else:
        uid = f'{uid_first} {uid_last}'

    print(f'Creating Item for user {uid} if it doesn\'t already exist')
    try:
        response = table.put_item(
            Item={
                'user_id': user_id,
                'biebered_others_count': 0,
                'biebered_self_count': 0,
                'uid_first': uid_first,
                'uid_last': uid_last,
                'uid_email': uid_email
            },
            ConditionExpression='attribute_not_exists(user_id)'
        )
        print('User record created 👍🏽')

        return response

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConditionalCheckFailedException':
            print(f'Item for user {uid} already exists')
        else:
            print(f'Unexpected error: {error_code}')


def update_user_record(table, user_id, update_item):

    response = table.update_item(
        Key={'user_id': user_id},
        UpdateExpression='SET #ui = #ui + :increment',
        ExpressionAttributeNames={
            '#ui': update_item
        },
        ExpressionAttributeValues={
            ':increment': 1
        }
    )

    print(f'Updating Item with ID: {user_id} has succeeded')

    return response


def get_latest_date(dates_data):
    dates = []
    for key in dates_data:
        dates.append(key)

    dates_sorted = sorted(dates, reverse=True)
    latest_date = dates_sorted[0]

    # Printing out some data here while testing
    print(dates_sorted)
    print(latest_date)

    return latest_date


def biebered_self(record, table):
    user_id = record['dynamodb']['NewImage']['user_id'].get('S', 'Unknown')
    uid_first = record['dynamodb']['NewImage']['uid_first'].get('S', 'Unknown')
    uid_last = record['dynamodb']['NewImage']['uid_last'].get('S', 'Unknown')
    uid_email = record['dynamodb']['NewImage']['uid_email'].get('S', 'Unknown')

    # Let's try to create the User record first
    create_user_record(table, user_id, uid_first, uid_last, uid_email)

    # Now we will see how many times this user has been Biebered and update their record to reflect this
    biebered_self_count = len(record['dynamodb']['NewImage']['biebered_by']['M'])
    response = update_user_record(table, user_id, 'biebered_self_count')

    return response


def biebered_others(record, table):
    dates_data = record['dynamodb']['NewImage']['biebered_by']['M']
    latest_date = get_latest_date(dates_data)
    data = record['dynamodb']['NewImage']['biebered_by']['M'][latest_date]

    user_id = data['M']['user_id'].get('S', 'Unknown')
    uid_first = data['M']['first_name'].get('S', 'Unknown')
    uid_last = data['M']['last_name'].get('S', 'Unknown')
    uid_email = data['M']['email'].get('S', 'Unknown')

    # Let's try to create the User record first
    create_user_record(table, user_id, uid_first, uid_last, uid_email)

    response = update_user_record(table, user_id, 'biebered_others_count')

    return response


def main(event):
    length_data = len(event['Records'])

    # This is used where events come from the DynamoDB Stream with two event objects
    for i in range(0, length_data):
        event_name = event['Records'][i]['eventName']
        if event_name == 'MODIFY':
            record = event['Records'][i]

            break

    # Printing out some data here while testing
    print(event)
    print(record)

    # Setting up some variables
    table_name = os.environ['users_tally_table_name']
    region = os.environ['region']
    table = get_table(table_name, region)
    biebered_self(record, table)

    biebered_others(record, table)


# These two functions take care of either loading in data from Lambda triggers or from a test file if run locally
# They then pass this event data onto the main() function with takes care of the rest
def lambda_func(event, context):

    main(event)


if __name__ == '__main__':
    with open('dynamodb_stream_test_data', encoding='utf-8') as stream_data:
        event = json.loads(stream_data.read())

        main(event)
