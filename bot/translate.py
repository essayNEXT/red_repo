from os import environ
from google.cloud import translate
from google.cloud import translate_v2 as tr

environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:/Users/vikaz/OneDrive/Рабочий стол/Work/Project/red_repo/translater-bot-intern-b9dec3a171bd.json'
project_id = 'translater-bot-intern'
parent = f"projects/{project_id}"


def translate_message(text):
    # """Detects the text's language"""
    # translate_client = tr.Client()
    # result = translate_client.detect_language(text) 
    # print("Language: {}".format(result["language"])) # Дивилася, наскільки правильно визначає мову

    """Translate text"""
    client = translate.TranslationServiceClient()
            
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            # "source_language_code": , # Google автоматично визначає мову оригіналу; потрібно, якщо ми будемо додавати 
                                        # функцію вибору мови з якої користувач хоче вчити.
            "target_language_code": "en"  # Вказувати мову, на яку треба робити переклад обов'язково
        }
    )
    
    for translation in response.translations:
        return translation.translated_text
    

def list_languages(): 
    """Lists all available languages."""

    translate_client = tr.Client()

    results = translate_client.get_languages()

    for language in results:
        print(u"{name} ({language})".format(**language))


# if __name__ == '__main__':
#     list_languages()
    



    
