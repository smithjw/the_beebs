import os
import boto3
import json
import requests

from slackclient import SlackClient

region = os.environ['region']

def getParameter(param_name):

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

def get_top_biebered_self_users():
    return

def get_top_biebered_others_users():
    return

def biebered_self_stats_comment(response_url):
    data = {
        'response_type': 'ephemeral',
        'text': 'Here\'s the leaderboard for Campers being Biebered:',
        'attachments': [
            {
                'fallback': 'Hmmm, this is a fallback message',
                'color': '#f04c5d',
                'title': 'Title',
                'mrkdwn_in': ['fields'],
                'fields': [
                    {
                        'title': 'Field title',
                        'value': 'Field Value'
                    }
                ]
            }
        ]
    }

    response = requests.post(response_url, json=data)

    return response

def biebered_others_stats_comment(response_url):
    data = {
        'response_type': 'ephemeral',
        'text': 'Here\'s the leaderboard for Campers who have Biebered the most people:',
        'attachments': [
            {
                'fallback': 'Hmmm, this is a fallback message',
                'color': '#45ad8f',
                'title': 'Title',
                'mrkdwn_in': ['fields'],
                'fields': [
                    {
                        'title': 'Field title',
                        'value': 'Field Value'
                    }
                ]
            }
        ]
    }

    response = requests.post(response_url, json=data)

    return response


def main(message):
    table_name = os.environ['users_tally_table_name']
    response_url = message['response_url'][0]
    token = getParameter('PA_SLACK_BOT_TOKEN')
    table = get_table(table_name, region)

    biebered_self_stats_comment(response_url)
    biebered_others_stats_comment(response_url)


def lambda_func(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])

    main(message)


if __name__ == '__main__':
    with open('test_data/get_stats_test_event', encoding='utf-8') as event_data:
        event = json.loads(event_data.read())
    message = event['Records'][0]['Sns']['Message']

    main(message)
