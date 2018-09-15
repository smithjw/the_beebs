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


def is_request_valid(request):
    token = getParameter('PA_SLACK_VERIFICATION_TOKEN')
    team_id = getParameter('PA_SLACK_TEAM_ID')
    print(token, team_id)

    is_token_valid = request.form['token'] == token
    is_team_id_valid = request.form['team_id'] == team_id

    return is_token_valid and is_team_id_valid

# Get the full response from the /command and send it into SNS


def publish_to_sns(slash_command_response, sns_arn):

    sns = boto3.client('sns', region_name='us-east-1')

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
                        'value': '`/bieber @username` will bieber the Camper and give a point to @username'
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
    data = {
        'text': f'You\'ve just Biebered <@{user_id}>\'s Mac! Clicking the button below will Bieberify the Desktop and Lock the Screen',
        'response_type': 'ephemeral',
        'attachments': [
            {
                'fallback': 'Click here to Bieberfy my Mac <jamfselfservice://content?entity=policy&id=337&action=execute|click here>',
                'actions': [
                    {
                        'type': 'button',
                        'text': 'Bieberify this Mac',
                        'url': 'jamfselfservice://content?entity=policy&id=337&action=execute',
                        'style': 'danger'
                    }
                ]
            }
        ]
    }

    requests.post(response_url, json=data)

# Need to fetch these from Parameter Store
# client_id = getParameter('SLACK_CLIENT_ID')
# client_secret = getParameter('SLACK_CLIENT_SECRET')
# oauth_scope = getParameter('SLACK_BOT_SCOPE')


@app.route('/begin_auth', methods=['GET'])
def pre_install():
    return '''
        <a href='https://slack.com/oauth/authorize?scope=incoming-webhook,commands,bot&client_id=7627545351.425890268918'><img alt='Add to Slack' height='40' width='139' src='https://platform.slack-edge.com/img/add_to_slack.png' srcset='https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x' /></a>
    '''.format(oauth_scope, client_id)


@app.route('/finish_auth', methods=['GET', 'POST'])
def post_install():

    # Retrieve the auth code from the request params
    auth_code = request.args['code']

    # An empty string is a valid token for this request
    sc = SlackClient('')

    # Request the auth tokens from Slack
    auth_response = sc.api_call(
        'oauth.access',
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )

    # Save the bot token to an environmental variable or to your data store
    # for later use
    os.environ['SLACK_USER_TOKEN'] = auth_response['access_token']
    os.environ['SLACK_BOT_TOKEN'] = auth_response['bot']['bot_access_token']

    print(auth_code)

    # Don't forget to let the user know that auth has succeeded!
    return 'Auth complete!'


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
