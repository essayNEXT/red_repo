from os import environ
from google.cloud import translate
from dotenv import load_dotenv


load_dotenv()
environ["GOOGLE_APPLICATION_CREDENTIALS"] = '.venv/translater-key.json'
project_id = environ['PROJECT_ID']
parent = f"projects/{project_id}"

def translate_message(text, target_language_code):
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        contents=[text], 
        target_language_code=target_language_code,
        parent=parent,
        )

    for translation in response.translations:
        return translation.translated_text
