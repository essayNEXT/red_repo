from google.cloud import translate
from google.cloud import translate_v2 as tr
from settings import project_id


parent = f"projects/{project_id}"


def translate_message(text, source_language_code, target_language_code):
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        request={
            'parent': parent,
            'contents': [text],
            "mime_type": "text/plain",
            'source_language_code': source_language_code,
            'target_language_code': target_language_code,
        }
        )

    for translation in response.translations:
        return translation.translated_text


def list_languages():
    """Lists all available languages."""

    translate_client = tr.Client()

    results = translate_client.get_languages()

    #print(results)  # [{'language': 'af', 'name': 'Afrikaans'}, {'language': 'ak', 'name': 'Akan'},...]

    #for language in results:
        #print(u"{name} ({language})".format(**language))
        #print(language)


if __name__ == '__main__':
    list_languages()
