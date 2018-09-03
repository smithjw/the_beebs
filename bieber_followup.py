import boto3

from slackclient import SlackClient

def bieber_comment(event, context):

    response_url = event.get('Message', None)

    data = {
        'response_type': 'ephemeral',
        # Replace Self Service link to execute policy that changes the desktop background ad locks the screen
        # This policy should be set to no triggering criteria, Ongoing, and available in Self Service only
        'text': 'This will Bieberify the Desktop and lock the screen'
    }

    requests.post(response_url, json=data)

def dm_biebered_user():
    # Should get the token from Parameter Store
    sc = SlackClient(token)

    sc.api_call(
        "chat.postMessage",
        channel=['ID'],
        as_user=False,
        text="Hello, you've just been Biebered :sob:. <https://cultureamp.atlassian.net/wiki/spaces/Prod/pages/700744276/How+to+not+get+biebered|Click here> to view our Confluence article on how not to be Biebered in the future!"
    )
