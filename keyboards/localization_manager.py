from keyboards import localization

user_conf = {}


async def get_user_language(complex_id, default_user_lang: str) -> str:
    user_lang_code = user_conf.setdefault(str(complex_id), default_user_lang)
    return user_lang_code


async def get_localized_message(complex_id, message_key: str, *args) -> str:
    try:
        language = user_conf.get(str(complex_id))
        _ = localization.messages[language][message_key]
    except KeyError:
        language = "en"
    try:
        result = localization.messages[language][message_key].format(*args)
    except KeyError:
        result = message_key
    return result


def get_localized_message51(complex_id, message_key: str, *args) -> str:
    try:
        language = user_conf.get(str(complex_id))
        _ = localization.messages[language][message_key]
    except KeyError:
        language = "en"
    try:
        result = localization.messages[language][message_key].format(*args)
    except KeyError:
        result = message_key
    return result

async def get_localized_lang(user_lang: str, *args) -> dict:
    try:
        _ = localization.name_lang[user_lang]
    except KeyError:
        user_lang = "en"
    return localization.name_lang[user_lang]
