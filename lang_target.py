# Copyright 2020 Google LLC
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/a7533084559578e918637b13c2744ec681b40e43/translate/samples/snippets/translate_v3_get_supported_languages_with_target.py
import json
import sqlite3

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START translate_v3_get_supported_languages_for_target]
from google.cloud import translate
from settings import project_id


def get_supported_languages(project_id=project_id, lang_code='en'):
    """Listing supported languages with target language name."""

    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    # Supported language codes: https://cloud.google.com/translate/docs/languages
    response = client.get_supported_languages(
        display_language_code=lang_code, parent=parent  # target language code - is
    )
    # List language codes of supported languages
    display_language = {}
    #print(response.languages)
    for language in response.languages:
        # print("Language Code: {}".format(language.language_code))
        # print("Display Name: {}".format(language.display_name))
        #print(f'"{language.language_code}": "{language.display_name}"')
        display_language[language.language_code] = language.display_name
    # print(display_language)
    # string_red = json.dumps(display_language)
    # if
    return display_language



def main():
    lang_code = 'de'
    dict_list = get_supported_languages(project_id, lang_code)
    print(dict_list)
    # with sqlite3.connect('.venv/bot.sqlite3') as con:  # підключення до БД
    #     if con:
    #         print("База даних успішно підключена")
    #
    #     for x in dict_list.keys():
    #         print(f" '{x}',", end="")
    #         if x in [
    #               'az', 'ay', 'sq', 'am', 'en', 'ar', 'as', 'af', 'bm', 'eu', 'bn', 'be', 'my', 'bg', 'bs', 'bho', 'vi', 'cy', 'hy', 'haw', 'ht', 'lg', 'hi', 'el', 'ka', 'gn', 'gl', 'gu', 'da', 'doi', 'ee', 'eo', 'et', 'zu', 'iw', 'he', 'ig', 'yi', 'ilo', 'id', 'ga', 'is', 'es', 'it', 'yo', 'kk', 'km', 'kn', 'ca', 'qu', 'ky', 'zh', 'zh-CN', 'zh-TW', 'gom', 'ko', 'co', 'kri', 'ku', 'ckb', 'xh', 'lo', 'la', 'lv', 'lt', 'ln', 'lb', 'mai', 'mk', 'mg', 'ms', 'ml', 'dv', 'mt', 'mi', 'mr', 'mni-Mtei', 'lus',
    #
    #писав цей список, бо в мене гугл на деяких мовах викидав, тому я пропускав всі мови , які пройшли успішно до "глюків"
    #         ]: continue
    #         item_dict = get_supported_languages(project_id, x)
    #         key = x
    #         value = json.dumps(item_dict)
    #         mycursor = con.cursor()
    #         sql = "INSERT INTO transl_but (lang_code, lang_list_name) VALUES (?, ?)"
    #         val = (key, value)
    #         mycursor.execute(sql, val)
    #
    #         con.commit()

if __name__ == '__main__':
    try:
        main()   # заповняв БД всіх назв всіма мовами
    except:
        pass