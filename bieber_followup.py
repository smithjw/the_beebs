def bieber_comment(response_url):

    data = {
        'response_type': 'ephemeral',
        # Replace Self Service link to execute policy that changes the desktop background ad locks the screen
        # This policy should be set to no triggering criteria, Ongoing, and available in Self Service only
        'text': 'This will Bieberify the Desktop and lock the screen'
    }

    requests.post(response_url, json=data)
