import os
import boto3
import json
import requests
import re

from time import sleep
from slackclient import SlackClient


def getParameter(param_name):
    # Create the SSM Client
    ssm = boto3.client(
        'ssm',
        region_name=os.environ['region']
    )
    # Get the requested parameter
    response = ssm.get_parameters(
        Names=[param_name],
        WithDecryption=True
    )
    # Store the credentials in a variable
    credentials = response['Parameters'][0]['Value']

    return credentials

def extract_user_id(text):
    user_id = re.split('@|\|', text)[1]

    return user_id


def followup_comments(token, user_id, biebered_by):
    sleep(1)
    sc = SlackClient(token)
    channel = os.environ['biebered_slack_chanel']

    dm = sc.api_call(
        'chat.postMessage',
        channel=user_id,
        as_user=False,
        icon_emoji=':bieber:',
        username='Bieber',
        text='Hello, you\'ve just been Biebered :sob:. <https://cultureamp.atlassian.net/wiki/spaces/Prod/pages/700744276/How+to+not+get+biebered|Click here> to view our Confluence article on how not to be :bieber:Biebered:bieber: in the future!'
    )

    stream = sc.api_call(
        'chat.postMessage',
        channel=channel,
        as_user=False,
        icon_emoji=':bieber:',
        username='Bieber',
        text=f'<@{user_id}> was just Biebered by <@{biebered_by}>!'
    )

def main(event):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    print(message)
    response_url = message['response_url'][0]
    user_id = message['user_id'][0]
    biebered_by = extract_user_id(message['text'][0])
    token = getParameter('bieber_slack_bot_token')

    followup_comments(token, user_id, biebered_by)


def lambda_func(event, context):
    main(event)


if __name__ == '__main__':
    main(event)
