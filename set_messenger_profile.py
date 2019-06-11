import os
import json
import requests
import logging
from configparser import ConfigParser
from flask.logging import default_handler


dir_path = os.path.dirname(os.path.realpath(__file__))
# filename='/var/log/golem.log',
logging.basicConfig(format='%(asctime)s [%(name)s::%(levelname)s] %(message)s')
logger = logging.getLogger('golem')
logger.addHandler(default_handler)
my_debug = 5

if 1 <= my_debug:
    logger.setLevel(logging.DEBUG)

config: ConfigParser = ConfigParser()
config.read(dir_path + '/golem.ini')
if 5 <= my_debug:
    logger.debug('configuration from golem.ini:\n%s', '\n'.join(
        sorted(
            [f'{s}::{k}: {v}' for s in config.sections() for k, v in config.items(s)]
        )
    ))


def main():
    values_to_set = {
        "greeting": [
            {
                "locale": "default",
                "text": "גולם המיועד לחבר בין אנשים המעוניינים בזה"
            }
        ],
        "get_started": {
            "payload": "GET_STARTED_PAYLOAD"
        }
    }
    response = requests.post(
        config['API']['MessengerProfile'],
        params={"access_token": config['TOKENS']['PAGE_ACCESS_TOKEN']},
        headers={"Content-Type": "application/json"},
        data=json.dumps(values_to_set)
    )
    if not response:
        logger.warning('MessengerProfile post - [%d] %s', response.status_code, response.text)
    else:
        sender_info = response.json()
        if 3 <= my_debug:
            logger.debug('MessengerProfile response - [%d] %s', response.status_code, str(sender_info))


if __name__ == "__main__":
    main()
