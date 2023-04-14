import logging
from os import environ
from dotenv import load_dotenv


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
load_dotenv()

# try:
#     BOT_TOKEN = environ['BOT_TOKEN']
# except KeyError as err:
#     logging.critical(
#         f"Can't read token from environment variable. Message: {err}")
#     raise KeyError(err)

# environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:/Users/vikaz/OneDrive/Рабочий стол/Work/Project/чернетка/red_repo/translater-bot.json'
# project_id = 'translater-bot-intern'

try:
    GOOGLE = environ['GOOGLE']
except KeyError as err:
    logging.critical(
        f"Can't read token from environment variable. Message: {err}")
    raise KeyError(err)



try:
    KEY = environ['KEY']
except Exception as error:
    logging.critical(
        "Please set/export the environment variable: {}".format(error))
    raise Exception(error)


try:
    REGION = environ['REGION']
except Exception as error:
    logging.critical(
        "Please set/export the environment variable: {}".format(error))
    raise Exception(error)

