from os import environ

from google.cloud import translate
environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'/home/hedgehog/my-translation-sa-key.json'
project_id = 'translater-bot-intern'
parent = f"projects/{project_id}"
client = translate.TranslationServiceClient()

sample_text = "Hello world!"
target_language_code = "uk"

response = client.translate_text(
    contents=[sample_text],
    target_language_code=target_language_code,
    parent=parent,
)

for translation in response.translations:
    print(translation.translated_text)
