import os
import requests
import boto3

from time import sleep
from flask import abort, Flask, jsonify, request

app = Flask(__name__)


def is_request_valid(request):
    is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
    is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

    return is_token_valid and is_team_id_valid

# Get the full response from the /command and send it into SNS
def publish_to_sns(slash_command_response):

    client = boto3.client('sns',region_name='us-east-1')

    response = client.publish(
        TopicArn='arn:aws:sns:us-east-1:465039758259:Test',
        Message=slash_command_response
    )
    print("Response: {}".format(response))

@app.route('/bieber', methods=['POST'])
def bieber():
    if not is_request_valid:
        abort(400)

    slash_command_response = request.form.to_dict(flat=False)
    publish_to_sns(slash_command_response)

    return jsonify(
        response_type='ephemeral',
        text='You\'ve just Biebered me! To add insult to injury, <jamfselfservice://content?entity=policy&id=337&action=execute|click here> :smiling_imp:',
        )
