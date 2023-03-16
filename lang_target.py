# Copyright 2020 Google LLC
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/a7533084559578e918637b13c2744ec681b40e43/translate/samples/snippets/translate_v3_get_supported_languages_with_target.py

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
    return display_language


if __name__ == '__main__':
    lang_code = 'uk'
    get_supported_languages(project_id, lang_code)
