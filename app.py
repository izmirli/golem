import sys, json, requests
from flask import Flask, request


app = Flask(__name__)

# your_facebook_page_access_token
PAT = 'EAAGOFl2SmbQBALtYhsORXXhAp6k9PCUQKEO6clu5flB08dwZCJ7B0G53oK31w2O6ypYeH7rKnUUcN0ZAZBTOXtmnj3noNtcsjVqh9s8M5gZBGOYmqfSy2QAPC7W7ajdnV5L6PKyDgbVZCwZAEC2Dzb4fgKJN4USbpReupKCXoSYKQRLNPC4M0HbzKZCnWDZBZAEcZD'
# my webhook_verification_token
VERIFY_TOKEN = 'ay2QAPC7W7ajdnV5L6PKyDgbVZCwZAEC2Dzb4fgKJN4USbpReupKCXoSYKQRLNPC4M0Hw'

"""
@app.route('/')
def hello_world():
	return 'Hello, World!'
"""

@app.route('/', methods=['GET'])
def handle_verification():
    '''Verifies facebook webhook subscription
    Successful when verify_token is same as token sent by facebook app
    '''
    # print "Bla"
    #return '{"bla: "bla"}'
    
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        print("succefully verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong verification token!")
        return "Wrong validation token"


@app.route('/', methods=['POST'])
def handle_message():
    '''Handle messages sent by facebook messenger to the applicaiton'''
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


def send_message(sender_id, message_text):
    '''Sending response back to the user using facebook graph API'''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": PAT},
        headers={"Content-Type": "application/json"}, 
        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))


def parse_user_message(user_text):
    '''Send the message to API AI which invokes an intent
    and sends the response accordingly
    The bot response is appened with weaher data fetched from
    open weather map client
    '''
    return ("Sorry, I couldn't understand that question")


def send_message_response(sender_id, message_text):
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)
    for message in messages:
        send_message(sender_id, message)


if __name__ == "__main__":
    app.run()
