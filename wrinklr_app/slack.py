import re
import requests
import logging
import json

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

def form_slash_response(matchup):
    return {
        "text": "Who is older?",
        "response_type": "in_channel",
        "attachments": [{
            "fallback": "You are unable to choose a game",
            "callback_id": create_callback_id(matchup),
            "color": "#3AA3E3",
            "attachment_type": "default",
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

def form_action_response(guess, matchup):
    correct = guess == matchup.older

    return {
        'response_type': 'ephemeral',
        'replace_original': False,
        'text': '%s!\n%s is %s\n%s is %s'
            % ('Correct' if correct else 'Incorrect', 
               matchup.person1.name, matchup.person1.age_str,
               matchup.person2.name, matchup.person2.age_str)
    }

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

def respond_to_url(url, data):
    logger.info('posting %s to %s' % (data, url))
    headers = {'Content-Type': 'application/json'}
    result = requests.post(url, json=data, headers=headers)
    result.raise_for_status()

