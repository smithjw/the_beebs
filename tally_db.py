import os
import json
import boto3

from boto3.dynamodb.conditions import Key, Attr

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


def read_db_data():
    table_name = os.environ['users_table_name']
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)

    response = table.scan()

    items = response['Items']
    length_data = len(items)

    for i in range(0, length_data):
        f_name = items[i]['uid_first']
        l_name = items[i]['uid_last']
        biebered_count = len(items[i]['biebered_by'])

        print(f'{f_name} {l_name} has been Biebered {biebered_count} times')




def main():
    read_db_data()


def lambda_func(event, context):
    print(event)
    main()


if __name__ == '__main__':
    with open('dynamodb_stream_test_data', encoding='utf-8') as event:
        stream_data = json.loads(event.read())
        print(stream_data['Records'][0]['dynamodb']['NewImage']['biebered_by']['M'])

        biebered_count = len(stream_data['Records'][0]['dynamodb']['NewImage']['biebered_by']['M'])
        print(biebered_count)


    #main()
