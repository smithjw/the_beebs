import os
import boto3
import json
import requests

from slackclient import SlackClient

#token = os.environ['SLACK_BOT_TOKEN']

# This is a test message
# event = {
#   "Type" : "Notification",
#   "MessageId" : "9da349d4-216a-52c6-8618-1dd3f8a856b6",
#   "TopicArn" : "arn:aws:sns:us-east-1:465039758259:Test",
#   "Message" : "{\"token\": [\"CrtKv8RX9lPwjSozqy8tjxKE\"], \"team_id\": [\"T07JFG1AB\"], \"team_domain\": [\"preamp\"], \"channel_id\": [\"CC50SU8BX\"], \"channel_name\": [\"testing\"], \"user_id\": [\"U07JFSV7X\"], \"user_name\": [\"james\"], \"command\": [\"/bieber\"], \"text\": [\"<@U08A5M37C|eve>\"], \"response_url\": [\"https://hooks.slack.com/commands/T07JFG1AB/427688290128/on8TcPHZEW9TtZXzxVsgcNH4\"], \"trigger_id\": [\"429450813431.7627545351.b6f3de5fa98a3a6367a815c45c5efa23\"]}",
#   "Timestamp" : "2018-09-04T00:53:22.671Z",
#   "SignatureVersion" : "1",
#   "Signature" : "pJDko7l2qGTN2lY35yV3Rwx7kaHloXcqbLl8yW9J2F+vmE9EKycdKHf56P1Rj5Ko/YoR5ru1a79hWT9p8rng0wSbfdBEcW+O39tCfhNiiyfeiv4Ih/RlCVujFr9Kep/uIPKQfeMcY7EMcPsm2UUE5fykPe/UkhvtPDcniakKQjvtTcgL8VGl979FIzCdbWEwDn/trqPLP+8BP9wL1DReoG2tiWJJYi3zxV/J6aeK0pZ1BSBcMGqtyFKOORNZBAqQS/tP+wzvKMkU+LDgniwRullxs6QEPg9fj8a51eaceWIX7IMq0b45CPgR+G5Hiaww7ZsXcCTdd/CFbEF59a9Ajw==",
#   "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem",
#   "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:465039758259:Test:a2372930-2352-418b-bb29-e167673e9ad3"
# }

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
    data = {
        'response_type': 'ephemeral',
        'text': 'This will Bieberify the Desktop and lock the screen'
    }

    requests.post(response_url, json=data)

def dm_biebered_user(token, user_id):
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
    slash_command_data = json.loads(event['Message'])
    print(slash_command_data)
    response_url = slash_command_data['response_url'][0]
    user_id = slash_command_data['user_id'][0]
    token = getParameter('PA_SLACK_BOT_TOKEN')

    bieber_comment(response_url)
    dm_biebered_user(token, user_id)

def lambda_func(event, context):
    main(event)


if __name__ == '__main__':
    main(event)
