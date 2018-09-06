import os
import requests
import boto3
import json
import re

from flask import abort, Flask, jsonify, request

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

    sns = boto3.client('sns',region_name='us-east-1')

    response = sns.publish(
        TopicArn=sns_arn,
        Message=slash_command_response
    )
    print("Response: {}".format(response))

@app.route('/bieber', methods=['POST'])
def bieber():
    if not is_request_valid:
        abort(400)

    slash_command_response = request.form.to_dict(flat=False)
    sns_message = json.dumps(slash_command_response)
    text = slash_command_response['text'][0]

    if any(re.findall(r'stat', text, re.IGNORECASE)):
        # Can this be replaced with an Env Var from the serverless.yml file?
        sns_arn = os.environ['stats_sns']

        # Ucomment this when additional function is written to pull stats from DynamoDB
        # publish_to_sns(sns_message, sns_arn)

        return jsonify(
            response_type = 'in_channel',
            text = 'Here are the stats for the most Biebered individual:',
            )

    elif any(re.findall(r'<@U', text, re.IGNORECASE)):
        sns_arn = os.environ['biebered_sns']
        publish_to_sns(sns_message, sns_arn)

        # Should turn the link in the following message into a Slack Button
        return jsonify(
            response_type='ephemeral',
            text='You\'ve just Biebered me! To add insult to injury, <jamfselfservice://content?entity=policy&id=337&action=execute|click here> :smiling_imp:',
            )

    elif any(re.findall(r'help', text, re.IGNORECASE)):
        return jsonify(
            response_type = 'ephemeral',
            text = 'Here\'s what I can do!'
            # I should put a Slack Attachment in here
        )

    else:
        return jsonify(
            response_type = 'ephemeral',
            text = 'That\'s not a valid command, try `/bieber help`'
            # I should put a Slack Attachment in here
        )
