import os
import requests
import boto3
import json
import re

from flask import abort, Flask, jsonify, request, Response
from slackclient import SlackClient

app = Flask(__name__)


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


def is_request_valid(request):
    token = getParameter('bieber_slack_verification_token')
    team_id = getParameter('bieber_team_id')
    print(token, team_id)

    is_token_valid = request.form['token'] == token
    is_team_id_valid = request.form['team_id'] == team_id

    return is_token_valid and is_team_id_valid

# Get the full response from the /command and send it into SNS


def publish_to_sns(slash_command_response, sns_arn):
    region = os.environ['region']
    sns = boto3.client('sns', region_name=region)

    response = sns.publish(
        TopicArn=sns_arn,
        Message=slash_command_response
    )
    print('Response: {}'.format(response))


def help_comment(response_url, comment_text):
    data = {
        'response_type': 'ephemeral',
        'text': comment_text,
        'attachments': [
            {
                'fallback': 'Hmmm, this is a fallback message',
                'color': '#f04c5d',
                'title': 'Supported Bieber Commands',
                'mrkdwn_in': ['fields'],
                'fields': [
                    {
                        'title': 'Help',
                        'value': 'Will display the supported commands'
                    },
                    {
                        'title': 'Bieber',
                        'value': '`/bieber @username` will Bieber the host computer and give a point to @username'
                    },
                    {
                        'title': 'Stats',
                        'value': '`/bieber stats` will display the leaderboard'
                    }
                ]
            }
        ]
    }

    requests.post(response_url, json=data)


def initial_comment(response_url, user_id):
    ss_url = os.environ['self_service_url']
    data = {
        'text': f'You\'ve just Biebered <@{user_id}>\'s Mac! Clicking the button below will Bieberify the Desktop and Lock the Screen',
        'response_type': 'ephemeral',
        'attachments': [
            {
                'fallback': f'Click here to Bieberfy my Mac <{ss_url}|click here>',
                'actions': [
                    {
                        'type': 'button',
                        'text': 'Bieberify this Mac',
                        'url': f'{ss_url}',
                        'style': 'danger'
                    }
                ]
            }
        ]
    }

    requests.post(response_url, json=data)


@app.route('/bieber', methods=['POST'])
def bieber():
    if not is_request_valid:
        abort(400)

    slash_command_response = request.form.to_dict(flat=False)
    response_url = slash_command_response['response_url'][0]
    user_id = slash_command_response['user_id'][0]
    sns_message = json.dumps(slash_command_response)
    text = slash_command_response['text'][0]

    if any(re.findall(r'stat', text, re.IGNORECASE)):
        sns_arn = os.environ['stats_sns_arn']
        publish_to_sns(sns_message, sns_arn)

        return Response()

    elif any(re.findall(r'<@U', text, re.IGNORECASE)):
        sns_arn = os.environ['biebered_sns_arn']
        publish_to_sns(sns_message, sns_arn)
        initial_comment(response_url, user_id)

        # Should turn the link in the following message into a Slack Button
        return Response()

    elif any(re.findall(r'help', text, re.IGNORECASE)):
        comment_text = 'Here\'s what I can do!'
        help_comment(response_url, comment_text)

        return Response()

    else:
        comment_text = 'Hmmm, I don\'t recognise that command. Here are some handy hints!'
        help_comment(response_url, comment_text)
        return Response()
