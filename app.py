import sys, json, requests, configparser
from flask import Flask, request, send_from_directory


app = Flask(__name__)
app.debug = True

config = configparser.ConfigParser()
config.read(app.root_path + '/golem.ini')


@app.route('/', methods=['GET'])
def handle_verification():
    """Verifies facebook webhook subscription
    Successful when verify_token is same as token sent by facebook app
    """
    if request.args.get('hub.verify_token', '') == config['TOKENS']['VERIFY_TOKEN']:
        print("successfully verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong verification token!")
        return "Wrong validation token"


@app.route('/', methods=['POST'])
def handle_message():
    """Handle messages sent by facebook messenger to the application."""
    data = request.get_json()

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  
                    sender_id = messaging_event["sender"]["id"]        
                    recipient_id = messaging_event["recipient"]["id"]  
                    message_text = messaging_event["message"]["text"]  
                    send_message_response(sender_id, parse_user_message(message_text)) 

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
                          "message": {"text": message_text}
                      }))


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
