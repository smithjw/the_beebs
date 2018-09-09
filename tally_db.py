import os
import json
import boto3

from boto3.dynamodb.conditions import Key, Attr

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


def table(table_name, region):
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


def update_user_record(user_id, update_item, item_count):

    response = table.update_item(
        Key={'user_id': user_id},
        UpdateExpression = 'SET #ui = :update',
        ExpressionAttributeNames = {
            '#ui': update_item
        },
        ExpressionAttributeValues = {
            ':update': item_count
        }
    )

    return response


def get_latest_date(dates_data):
    dates = []
    for key in dates_data:
        dates.append(key)

    dates_sorted = sorted(dates, reverse=True)
    latest_date = dates_sorted[0]

    return latest_date


def biebered_self(event):
    biebered_self_count = None

    biebered_self_count = len(event['Records'][0]['dynamodb']['NewImage']['biebered_by']['M'])
    print(biebered_self_count)

    return biebered_self_count


def biebered_others(event):
    biebered_others_count = None
    dates_data = event['Records'][0]['dynamodb']['NewImage']['biebered_by']['M']
    latest_date = get_latest_date(dates_data)
    dict = event['Records'][0]['dynamodb']['NewImage']['biebered_by']['M'][latest_date]
    print(dict)


    return biebered_others_count




def main(event):

    # table_name = os.environ['users_tally_table_name']
    # region = 'us-east-1'
    # user_id = event['Records'][0]['dynamodb']['NewImage']['user_id']['S']
    # uid_first = event['Records'][0]['dynamodb']['NewImage']['uid_first']['S']
    # uid_last = event['Records'][0]['dynamodb']['NewImage']['uid_last']['S']
    # uid_email = event['Records'][0]['dynamodb']['NewImage']['uid_email']['S']
    #
    # table = table(table_name, region)
    #
    # create_user_record(table, user_id, uid_first, uid_last, uid_email)
    #
    # biebered_self_count = biebered_self(event)
    # update_user_record(user_id, 'biebered_self_count', biebered_self_count)

    biebered_others_count = biebered_others(event)




def lambda_func(event, context):

    main(event)


if __name__ == '__main__':
    with open('dynamodb_stream_test_data', encoding='utf-8') as stream_data:
        event = json.loads(stream_data.read())

        main(event)
