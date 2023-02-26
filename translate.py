from google.cloud import translate
from settings import project_id


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
