import json
import requests
from configparser import ConfigParser
from flask import Flask, request, send_from_directory


app = Flask(__name__)
app.debug = True
my_debug = 4

config: ConfigParser = ConfigParser()
config.read(app.root_path + '/golem.ini')
if 5 <= my_debug:
    app.logger.debug('configuration from golem.ini:\n%s', '\n'.join(
        sorted(
            [f'{s}::{k}: {v}' for s in config.sections() for k, v in config.items(s)]
        )
    ))


@app.route('/', methods=['GET'])
def handle_verification():
    """Verifies facebook webhook subscription
    Successful when verify_token is same as token sent by facebook app
    """
    if 3 <= my_debug:
        app.logger.debug('request.args: %s', request.args)
    if request.args.get('hub.verify_token', '') == config['TOKENS']['VERIFY_TOKEN']:
        # print("successfully verified")
        if 1 <= my_debug:
            app.logger.debug('successfully verified. challenge: %s', request.args.get('hub.challenge', ''))
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong verification token!")
        return "Wrong validation token"


@app.route('/', methods=['POST'])
def handle_message():
    """Handle messages sent by facebook messenger to the application."""
    data = request.get_json()
    print(f'handle_message data:', data)

    try:
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]
                        message_text = messaging_event["message"]["text"]
                        # recipient_id = messaging_event["recipient"]["id"]
                        # msg_timestamp = messaging_event["timestamp"]
                        # msg_id = messaging_event["message"]["mid"]
                        # msg_seq = messaging_event["message"]["seq"]
                        get_sender_info(sender_id)
                        send_message_response(sender_id, parse_user_message(message_text))
    except KeyError as e:
        print(f'KeyError exception: {e}')

    return "ok"


@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


def send_message(sender_id, message_text):
    """Sending response back to the user using facebook graph API"""
    r = requests.post(config['API']['SendMessageUrl'],
                      params={"access_token": config['TOKENS']['PAGE_ACCESS_TOKEN']},
                      headers={"Content-Type": "application/json"},
                      data=json.dumps({
                          "recipient": {"id": sender_id},
                          "message": {
                              "text": message_text,
                              "quick_replies": [
                                  {
                                      "content_type": "text",
                                      "title": "Search",
                                      "payload": "<POSTBACK_PAYLOAD>",
                                      "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Blue_Question.svg"
                                  },
                                  {"content_type": "location"}
                              ],
                          }
                      }))
    if not r:
        app.logger.warning('send_message failed - [%d] %s', r.status_code, r.text)
    else:
        if 3 <= my_debug:
            app.logger.debug('send_message response - [%d] %s', r.status_code, r.text)
    # consider adding to data "messaging_type": "<MESSAGING_TYPE>",
    # MESSAGING_TYPE options: RESPONSE (default), UPDATE (proactive send), MESSAGE_TAG.


def get_sender_info(psid):
    """Get sender's info according to his PSID.

    :param psid: PSID (sender's Page-scoped ID).
    :return:
    """
    response = requests.post(
        f'https://graph.facebook.com/{psid}',
        params={"access_token": config['TOKENS']['PAGE_ACCESS_TOKEN'],
                "fields": "name,first_name,last_name,profile_pic,gender"},
        headers={"Content-Type": "application/json"},
    )
    if not response:
        app.logger.warning('get_sender_info failed - [%d] %s', response.status_code, response.text)
    else:
        sender_info = response.json()
        if 3 <= my_debug:
            app.logger.debug('send_message response - [%d] %s', response.status_code, str(sender_info))


def parse_user_message(user_text):
    """Send the message to API AI which invokes an intent
    and sends the response accordingly
    The bot response is appened with weaher data fetched from
    open weather map client
    """
    return "Sorry, I couldn't understand that question"


def send_message_response(sender_id, message_text):
    sentence_delimiter = ". "
    messages = message_text.split(sentence_delimiter)
    for message in messages:
        send_message(sender_id, message)


if __name__ == "__main__":
    app.run()
