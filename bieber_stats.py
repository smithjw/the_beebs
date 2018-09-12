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

def get_top_biebered_self_users(items):
    items_sorted = sorted(items["Items"], key=lambda d: d["biebered_self_count"], reverse=True)

    return items_sorted

def get_top_biebered_others_users(items):
    items_sorted = sorted(items["Items"], key=lambda d: d["biebered_others_count"], reverse=True)

    return items_sorted

def biebered_stats_comment(response_url, self_stats, other_stats):
    # The leaderboard for Campers biebering others will be posted to the channel
    if len(self_stats) > 4 and len(other_stats) > 4:
        data = {
            'response_type': 'ephemeral',
            'text': 'Here are the leaderboards for Campers being Biebered and Biebering others:',
            'attachments': [
                {
                    'fallback': 'Hmmm, this is a fallback message',
                    'color': '#45ad8f',
                    'mrkdwn_in': ['fields'],
                    'fields': [
                        {
                            'title': 'Leaderboard',
                            'short': True
                        },{
                            'title': 'Failboard',
                            'short': True
                        },{
                            'title': f'{other_stats[0]["uid_first"]} {other_stats[0]["uid_last"]}',
                            'value': f'Total times Biebering others: `{other_stats[0]["biebered_others_count"]}`',
                            'short': True
                        },{
                            'title': f'{self_stats[0]["uid_first"]} {self_stats[0]["uid_last"]}',
                            'value': f'Total times Biebered: `{self_stats[0]["biebered_self_count"]}`',
                            'short': True
                        },{
                            'title': f'{other_stats[1]["uid_first"]} {other_stats[1]["uid_last"]}',
                            'value': f'Total times Biebering others: `{other_stats[1]["biebered_others_count"]}`',
                            'short': True
                        },{
                            'title': f'{self_stats[1]["uid_first"]} {self_stats[1]["uid_last"]}',
                            'value': f'Total times Biebered: `{self_stats[1]["biebered_self_count"]}`',
                            'short': True
                        },{
                            'title': f'{other_stats[2]["uid_first"]} {other_stats[2]["uid_last"]}',
                            'value': f'Total times Biebering others: `{other_stats[2]["biebered_others_count"]}`',
                            'short': True
                        },{
                            'title': f'{self_stats[2]["uid_first"]} {self_stats[2]["uid_last"]}',
                            'value': f'Total times Biebered: `{self_stats[2]["biebered_self_count"]}`',
                            'short': True
                        },{
                            'title': f'{other_stats[3]["uid_first"]} {other_stats[3]["uid_last"]}',
                            'value': f'Total times Biebering others: `{other_stats[3]["biebered_others_count"]}`',
                            'short': True
                        },{
                            'title': f'{self_stats[3]["uid_first"]} {self_stats[3]["uid_last"]}',
                            'value': f'Total times Biebered: `{self_stats[3]["biebered_self_count"]}`',
                            'short': True
                        },{
                            'title': f'{other_stats[4]["uid_first"]} {other_stats[4]["uid_last"]}',
                            'value': f'Total times Biebering others: `{other_stats[4]["biebered_others_count"]}`',
                            'short': True
                        },{
                            'title': f'{self_stats[4]["uid_first"]} {self_stats[4]["uid_last"]}',
                            'value': f'Total times Biebered: `{self_stats[4]["biebered_self_count"]}`',
                            'short': True
                        }
                    ]
                }
            ]
        }

    else:
        data = {
            'response_type': 'ephemeral',
            'text': 'There aren\'t enough results to display the leaderboard just yet. Please cherck again soon'
        }

    response = requests.post(response_url, json=data)

    return response

def biebered_others_stats_comment(response_url, stats):
    # The leaderboard for Campers being Beibered will only display to the user running the command
    if len(stats) > 4:
        data = {
            'response_type': 'in_channel',
            'text': 'Here\'s the leaderboard for Campers who have Biebered the most people:',
            'attachments': [
                {
                    'fallback': 'Hmmm, this is a fallback message',
                    'color': '#45ad8f',
                    'title': 'Leaderboard',
                    'mrkdwn_in': ['fields'],
                    'fields': [
                        {
                            'title': f'{other_stats[0]["uid_first"]} {other_stats[0]["uid_last"]}',
                            'value': f'Total times Biebering others: {other_stats[0]["biebered_others_count"]}',
                            'short': True
                        },{
                            'title': f'{other_stats[1]["uid_first"]} {other_stats[1]["uid_last"]}',
                            'value': f'Total times Biebering others: {other_stats[1]["biebered_others_count"]}',
                            'short': True
                        },{
                            'title': f'{other_stats[2]["uid_first"]} {other_stats[2]["uid_last"]}',
                            'value': f'Total times Biebering others: {other_stats[2]["biebered_others_count"]}',
                            'short': True
                        },{
                            'title': f'{other_stats[3]["uid_first"]} {other_stats[3]["uid_last"]}',
                            'value': f'Total times Biebering others: {other_stats[3]["biebered_others_count"]}',
                            'short': True
                        },{
                            'title': f'{other_stats[4]["uid_first"]} {other_stats[4]["uid_last"]}',
                            'value': f'Total times Biebering others: {other_stats[4]["biebered_others_count"]}',
                            'short': True
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
    items = table.scan()
    self_stats = get_top_biebered_self_users(items)
    others_stats = get_top_biebered_others_users(items)

    biebered_stats_comment(response_url, self_stats, others_stats)
    # biebered_others_stats_comment(response_url, others_stats)


def lambda_func(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])

    main(message)


if __name__ == '__main__':
    with open('test_data/get_stats_test_event', encoding='utf-8') as event_data:
        event = json.loads(event_data.read())
    message = event['Records'][0]['Sns']['Message']

    main(message)
