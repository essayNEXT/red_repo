import logging
from os import environ
from dotenv import load_dotenv


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
load_dotenv()

try:
    BOT_TOKEN = environ['BOT_TOKEN']
except KeyError as err:
    logging.critical(
        f"Can't read token from environment variable. Message: {err}")
    raise KeyError(err)

environ["GOOGLE_APPLICATION_CREDENTIALS"] = '.venv/translater-key.json'
project_id = environ['PROJECT_ID']

