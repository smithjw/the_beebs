import os
import boto3
import json
import requests

from time import sleep
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


def bieber_comment(response_url):
    sleep(1)
    data = {
        'response_type': 'ephemeral',
        'text': 'This will Bieberify the Desktop and lock the screen'
    }

    requests.post(response_url, json=data)

def dm_biebered_user(token, user_id):
    sleep(1)
    sc = SlackClient(token)

    slack_response = sc.api_call(
        'chat.postMessage',
        channel=user_id,
        as_user=False,
        icon_emoji=':bieber:',
        username='Bieber',
        text='Hello, you\'ve just been Biebered :sob:. <https://cultureamp.atlassian.net/wiki/spaces/Prod/pages/700744276/How+to+not+get+biebered|Click here> to view our Confluence article on how not to be :bieber:Biebered:bieber: in the future!'
    )


def main(event):
    slash_command_data = json.loads(event['Records'][0]['Sns']['Message'])
    response_url = slash_command_data['response_url'][0]
    user_id = slash_command_data['user_id'][0]
    token = getParameter('PA_SLACK_BOT_TOKEN')

    # bieber_comment(response_url)
    dm_biebered_user(token, user_id)


def lambda_func(event, context):
    main(event)


if __name__ == '__main__':
    main(event)
