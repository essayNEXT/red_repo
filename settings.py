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
#
# try:
environ["GOOGLE_APPLICATION_CREDENTIALS"] = '.venv/translater-key.json'
project_id = environ['PROJECT_ID']
# except Exception as err:
#     logging.critical(
#         f"Не можу прочитати файли ключів Google API Message: {err}")
#     # raise KeyError(err)
#
# # DEFAULT_LANG_CODE = 'uk'
# DEFAULT_LANG_CODE = ['uk', 'en', 'ru']

# Довідник мов Google https://cloud.google.com/translate/docs/languages
# GET https://translation.googleapis.com/v3/projects/PROJECT_NUMBER_OR_ID/locations/global/supportedLanguages?display_language_code=sq
LANGDICT = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'as': 'Assamese',
    'ay': 'Aymara',
    'az': 'azerbaijani',
    'bm': 'Bambara',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bho': 'Bhojpuri',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'dv': 'Dhivehi',
    'doi': 'Dogri',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'ee': 'Ewe',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gn': 'Guarani',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'ilo': 'Ilocano',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'rw': 'Kinyarwanda',
    'gom': 'Konkani',
    'ko': 'Korean',
    'kri': 'Krio',
    'ku': 'Kurdish',
    'ckb': 'Kurdish (Sorani)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'ln': 'Lingala',
    'lt': 'Lithuanian',
    'lg': 'Luganda',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mai': 'Maithili',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mni-Mtei': 'Meiteilon (Manipuri)',
    'lus': 'Mizo',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'ny': 'Nyanja (Chichewa)',
    'or': 'Odia (Oriya)',
    'om': 'Oromo',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'qu': 'Quechua',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'sa': 'Sanskrit',
    'gd': 'Scots Gaelic',
    'nso': 'Sepedi',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tl': 'Tagalog (Filipino)',
    'tg': 'tajik',
    'ta': 'tamil',
    'tt': 'Tatar',
    'te': 'telugu',
    'th': 'thai',
    'ti': 'Tigrinya',
    'ts': 'Tsonga',
    'tr': 'Turkish',
    'tk': 'Turkmen',
    'ak': 'Twi (Akan)',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu'
}
# LANGUES = LANGDICT.values()

LANGUES = '\n'.join([f'{key}: {value}' for key, value in LANGDICT.items()])

lang_list = list(LANGDICT.keys())

# print(LANGUES)
# print(lang_list)

LANGDICT2 = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic'}
