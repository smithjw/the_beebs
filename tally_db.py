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
    print(f'Creating user record for {uid_first} {uid_last} if it doesn\'t already exist')
    try:
        response = table.put_item(
            Item = {
                'user_id': user_id,
                'biebered_others_count': 0,
                'biebered_self_count': 0,
                'uid_first': uid_first,
                'uid_last': uid_last,
                'uid_email': uid_email
            },
            ConditionExpression = 'attribute_not_exists(user_id)'
        )
        print('User record created 👍🏽')

        return response

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConditionalCheckFailedException':
            print('User already exists')
        else:
            print(f'Unexpected error: {error_code}')


def update_user_record(table, user_id, update_item):

    response = table.update_item(
        Key={'user_id': user_id},
        UpdateExpression = 'SET #ui = #ui + :increment',
        ExpressionAttributeNames = {
            '#ui': update_item
        },
        ExpressionAttributeValues = {
            ':increment': 1
        }
    )

    print(f'User record for ID: {user_id} has succeeded')

    return response


def get_latest_date(dates_data):
    dates = []
    print(dates)
    for key in dates_data:
        dates.append(key)
        print(dates)

    dates_sorted = sorted(dates, reverse=True)
    print(dates_sorted)
    latest_date = dates_sorted[0]

    return latest_date


def biebered_self(event, table):
    # Let's try to create the User record first
    print(event['Records'][0]['dynamodb']['NewImage'])

    user_id = event['Records'][0]['dynamodb']['NewImage']['user_id'].get('S', 'Unknown')
    uid_first = event['Records'][0]['dynamodb']['NewImage']['uid_first'].get('S', 'Unknown')
    uid_last = event['Records'][0]['dynamodb']['NewImage']['uid_last'].get('S', 'Unknown')
    uid_email = event['Records'][0]['dynamodb']['NewImage']['uid_email'].get('S', 'Unknown')

    create_user_record(table, user_id, uid_first, uid_last, uid_email)

    # Now we will see how many times this user has been Biebered and update their record to reflect this
    biebered_self_count = len(event['Records'][0]['dynamodb']['NewImage']['biebered_by']['M'])
    response = update_user_record(table, user_id, 'biebered_self_count')

    return response


def biebered_others(event, table):
    print(event)
    biebered_others_count = None
    dates_data = event['Records'][0]['dynamodb']['NewImage']['biebered_by']['M']
    latest_date = get_latest_date(dates_data)
    data = event['Records'][0]['dynamodb']['NewImage']['biebered_by']['M'][latest_date]

    # Let's try to create the User record first
    user_id = data['M']['user_id'].get('S', 'Unknown')
    uid_first = data['M']['first_name'].get('S', 'Unknown')
    uid_last = data['M']['last_name'].get('S', 'Unknown')
    uid_email = data['M']['email'].get('S', 'Unknown')
    print(user_id, uid_first, uid_last, uid_email)

    create_user_record(table, user_id, uid_first, uid_last, uid_email)

    update_user_record(table, user_id, 'biebered_others_count')

    return biebered_others_count




def main(event):
    # Setting up some variables
    table_name = os.environ['users_tally_table_name']
    region = 'us-east-1'
    table = get_table(table_name, region)
    biebered_self(event, table)

    biebered_others(event, table)



# These two functions take care of either loading in data from Lambda triggers or from a test file if run locally
# They then pass this event data onto the main() function with takes care of the rest
def lambda_func(event, context):

    main(event)

if __name__ == '__main__':
    with open('dynamodb_stream_test_data', encoding='utf-8') as stream_data:
        event = json.loads(stream_data.read())

        main(event)
