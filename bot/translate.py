from os import environ
from google.cloud import translate

environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:/Users/vikaz/OneDrive/Рабочий стол/Work/Project/red_repo/translater-bot-intern-b9dec3a171bd.json'
project_id = 'translater-bot-intern'
parent = f"projects/{project_id}"


def translate_message(text):
    client = translate.TranslationServiceClient()
    target_language_code = "en"
        
    response = client.translate_text(
        contents=[text], 
        target_language_code=target_language_code,
        parent=parent,
        )
    
    for translation in response.translations:
        return translation.translated_text


# def list_languages():
#     """Lists all available languages."""
#     from google.cloud import translate_v2 as translate

#     translate_client = translate.Client()

#     results = translate_client.get_languages(target_language=target)

#     for language in results:
#         print(u"{name} ({language})".format(**language))



    
