import re
import requests
import logging
import json
import slackclient

logger = logging.getLogger('slack')

def parse_slash_command(text):
    match = re.match('^(.*)vs(.*)$', text)
    lhs, rhs = None, None
    if match:
        lhs = match.group(1).strip() or None
        rhs = match.group(2).strip() or None
    return lhs, rhs

def form_parse_error(text):
    text = 'Sorry, could not parse "%s"' % text
    return form_error(text)

def form_error_response(err_names):
    text = 'Sorry, could not find birthday for (%s)' % ', '.join(err_names)
    return form_error(text)

def form_error(text):
    return {
        "response_type": "ephemeral",
        "text": text
    }

def form_slash_response(matchup, footer = ""):
    return {
        "text": "Who is older?",
        "response_type": "in_channel",
        "attachments": [{
            "fallback": "",
            "callback_id": create_callback_id(matchup),
            "color": "#3AA3E3",
            "attachment_type": "default",
            "footer": footer,
            "actions": [{
                "name": "person1",
                "text": matchup.person1.name,
                "type": "button",
                "value": matchup.person1.id
            }, {
                "name": "person2",
                "text": matchup.person2.name,
                "type": "button",
                "value": matchup.person2.id
            }]
        }]
    }

def get_solution_text(matchup):
    return '%s is %s\n%s is %s' % (matchup.person1.name, 
                                   matchup.person1.age_str,
                                   matchup.person2.name,
                                   matchup.person2.age_str)

def get_user_guess_text(user, guess, matchup):
    correct = guess == matchup.older
    return '%s guessed %s. %s!' % (user, 
                                   guess.name, 
                                   'Correct' if correct else 'Incorrect')

def create_callback_id(matchup):
    return json.dumps({
        'type': 'wrinklr_choice',
        'matchup_id': matchup.id
    })

def parse_callback_id(callback_id):
    data = json.loads(callback_id)
    if data['type'] == 'wrinklr_choice':
        return data['matchup_id']
    return None

def update_footer(msg, user, guess, matchup):
    correct = guess == matchup.older
    sym = '✔' if correct else '✖'
    new_line = '%s %s' % (sym, user)

    footer = msg['attachments'][0].get('footer')
    if footer:
        if user in footer:
            return None
        footer += '\n' + new_line
    else:
        footer = new_line

    return footer


def respond_to_url(url, data):
    logger.info('posting %s to %s' % (data, url))
    headers = {'Content-Type': 'application/json'}
    result = requests.post(url, json=data, headers=headers)
    result.raise_for_status()

class Client(object):
    def __init__(self, token):
        self.client = slackclient.SlackClient(token)

    def send_thread_message(self, text, channel, thread_ts):
        rc = self.client.api_call('chat.postMessage',
                             text=text,
                             channel=channel,
                             thread_ts=thread_ts)
