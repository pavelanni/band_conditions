# coding=utf-8

# Band Conditions
# By Pavel Anni AC4PA <pavel.anni@gmail.com>
#
# This skill report current conditions on ham radio bands

import re
import requests
import logging
from collections import namedtuple
from datetime import datetime
from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement


__author__ = 'Pavel Anni AC4PA'
__email__ = 'pavel.anni@gmail.com'


app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


def verbalize(level):
    Band = namedtuple('Band', ['level', 'lower', 'upper'])
    bands = []
    bands.append(Band(level='Great', lower=95, upper=100))
    bands.append(Band(level='Good', lower=70, upper=94))
    bands.append(Band(level='Fair', lower=35, upper=69))
    bands.append(Band(level='Poor', lower=16, upper=34))
    bands.append(Band(level='Dead', lower=0, upper=15))

    for b in bands:
        if level <= b.upper and level >= b.lower:
            return b.level

    # None of the above
    return 'Unknown'


def get_conditions():
    conditions = {}

    url = 'http://75.35.171.117/index.htm'
    r = requests.get(url)
    p = re.compile('(^\d+).*bandcondx.com/(\d+)\.jpg')

    for s in r.text.split('\r\n'):
        found = p.search(s)
        if found:
            conditions[found.group(1)] = verbalize(int(found.group(2)))

    return conditions


def speak_conditions(band='all'):
    conditions = get_conditions()
    bands = ['160', '80', '40', '30', '20', '17', '15']
    response = 'Band conditions now... '

    if band == 'all':
        for b in bands:
            response += f'{b} meter band is {conditions[b]}... '
    elif band in bands:
        response += f'{band} meter band is {conditions[band]}... '
    else:
        response = 'Wrong band...'

    return response


# Session starter
#
# This intent is fired automatically at the point of launch (= when the session starts).
# Use it to register a state machine for things you want to keep track of, such as what the last intent was, so as to be
# able to give contextual help.

@ask.on_session_started
def start_session():
    """
    Fired at the start of the session, this is a great place to initialise state variables and the like.
    """
    logging.debug("Session started at {}".format(datetime.now().isoformat()))

# Launch intent
#
# This intent is fired automatically at the point of launch.
# Use it as a way to introduce your Skill and say hello to the user. If you envisage your Skill to work using the
# one-shot paradigm (i.e. the invocation statement contains all the parameters that are required for returning the
# result


@ask.launch
def handle_launch():
    """
    (QUESTION) Responds to the launch of the Skill with a welcome statement and a card.

    Templates:
    * Initial statement: 'welcome'
    * Reprompt statement: 'welcome_re'
    * Card title: 'Band Conditions
    * Card body: 'welcome_card'
    """

    all_bands = speak_conditions()
    welcome_card_text = render_template('welcome_card')

    return statement(all_bands).standard_card(title="Band Conditions",
                                              text=all_bands)


@ask.intent('BandIntent')
def band_intent(band):
    response = speak_conditions(band)

    return statement(response).standard_card(title="Band Conditions",
                                             text=response)


# Built-in intents
#
# These intents are built-in intents. Conveniently, built-in intents do not need you to define utterances, so you can
# use them straight out of the box. Depending on whether you wish to implement these in your application, you may keep
# or delete them/comment them out.
#
# More about built-in intents: http://d.pr/KKyx

@ask.intent('AMAZON.StopIntent')
def handle_stop():
    """
    (STATEMENT) Handles the 'stop' built-in intention.
    """
    farewell_text = render_template('stop_bye')
    return statement(farewell_text)


@ask.intent('AMAZON.CancelIntent')
def handle_cancel():
    """
    (STATEMENT) Handles the 'cancel' built-in intention.
    """
    farewell_text = render_template('cancel_bye')
    return statement(farewell_text)


@ask.intent('AMAZON.HelpIntent')
def handle_help():
    """
    (QUESTION) Handles the 'help' built-in intention.

    You can provide context-specific help here by rendering templates conditional on the help referrer.
    """

    help_text = render_template('help_text')
    return question(help_text)


@ask.intent('AMAZON.NoIntent')
def handle_no():
    """
    (?) Handles the 'no' built-in intention.
    """
    pass


@ask.intent('AMAZON.YesIntent')
def handle_yes():
    """
    (?) Handles the 'yes'  built-in intention.
    """
    pass


@ask.intent('AMAZON.PreviousIntent')
def handle_back():
    """
    (?) Handles the 'go back!'  built-in intention.
    """
    pass


@ask.intent('AMAZON.StartOverIntent')
def start_over():
    """
    (QUESTION) Handles the 'start over!'  built-in intention.
    """
    pass


# Ending session
#
# This intention ends the session.

@ask.session_ended
def session_ended():
    """
    Returns an empty for `session_ended`.

    .. warning::

    The status of this is somewhat controversial. The `official documentation`_ states that you cannot return a response
    to ``SessionEndedRequest``. However, if it only returns a ``200/OK``, the quit utterance (which is a default test
    utterance!) will return an error and the skill will not validate.

    """
    return statement("")


if __name__ == '__main__':
    app.run(debug=True)
