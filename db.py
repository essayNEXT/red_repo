import sqlite3
from lang_target import get_supported_languages
from settings import project_id
import json
from random import randint


with sqlite3.connect('.venv/bot.sqlite3') as con:  # підключення до БД
    if con:
        print("База даних успішно підключена")

    ''' Опис полів БД
        таблиця users
        telegram_id (VARCHAR) - id користувача (беремо з телеграма за командою /start) 
        lang_code (VARCHAR) - код мови, яку додаємо до Вибраних
        interface_lang (BOOL) - мова інтерфейсу, одна з Вибраних
        src_lang (BOOL) - вказує на поточну джерело-мову перекладу (з якою перекладаємо)
        target_lang (BOOL) - вказує на поточну цільову мову перекладу (на яку перекладаємо)
        is_active (BOOL) - видаляє мову з Вибраних, якщо interface_lang=0 і target_lang=0
        
        таблиця languages - убрав
        lang_code (VARCHAR) - код мови, яку додаємо до Вибраних (uk)
        lang_name (VARCHAR) - им'я мови, яку додаємо до Вибраних (Ukrainian), це поле заповнюється на мові інтерфейсу
    
        таблиця transl_but - тут зберігаються переклади службових повідомлень, кнопок
        lang_code VARCHAR 
        lang_list_name VARCHAR
        
        таблиця page - збереження станів клавіатури ADD-NEW
        telegram_id (INTEGER) - id користувача
        page INTEGER        - № сторінка клавіатури ADD-NEW
 
    '''
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    telegram_id VARCHAR       NOT NULL,
                    lang_code   VARCHAR       NOT NULL,
                    interface_lang BOOL       NOT NULL
                                              DEFAULT (0),
                    src_lang BOOL             NOT NULL
                                              DEFAULT (0),                              
                    target_lang BOOL          DEFAULT (0) 
                                              NOT NULL,
                    is_active   BOOL          NOT NULL
                                              DEFAULT (1),
                    PRIMARY KEY(telegram_id, lang_code) 
        )''')
    # cur.execute('''CREATE TABLE IF NOT EXISTS languages (
    #                     lang_code VARCHAR       NOT NULL
    #                                          PRIMARY KEY,
    #                     lang_name VARCHAR       NOT NULL
    #     )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS transl_but (
                        lang_code   VARCHAR        NOT NULL
                                                PRIMARY KEY,
                        lang_dict      TEXT     NOT NULL
        )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS page (
                            telegram_id VARCHAR      NOT NULL
                                                  PRIMARY KEY,
                            page INTEGER             NOT NULL
            )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS cards (
                            telegram_id      VARCHAR NOT NULL,
                            lang_code_src    VARCHAR NOT NULL,
                            txt_src          VARCHAR NOT NULL,
                            lang_code_target VARCHAR NOT NULL,
                            txt_target       VARCHAR NOT NULL,
                            is_active        BOOL    NOT NULL
                                                     DEFAULT (1) 
            )''')

    con.commit()


# ========================================= set_user =======================================
def set_user(user_id: str, lang_code: str) -> None:
    mycursor = con.cursor()  # створюємо об'єкт курсор (для виконання операцій з БД)
    sql = "SELECT * FROM users WHERE telegram_id = ?"
    adr = (user_id,)
    mycursor.execute(sql, adr)
    myresult = mycursor.fetchall()
    print(myresult)
    # перевірка реєстрації користувача, якщо немає - реєструємо
    if myresult is None or myresult == [] or myresult == ():
        mycursor = con.cursor()
        sql = "INSERT INTO users (telegram_id, lang_code, interface_lang, target_lang, src_lang) VALUES (?, ?, ?, ?, ?)"
        val = (user_id, lang_code, 1, 1, 0)
        mycursor.execute(sql, val)

        # если lang_code != 'en' додаємо англ, як src_lang
        if lang_code != 'en':
            val = (user_id, 'en', 0, 0, 1)
            mycursor.execute(sql, val)
        con.commit()
        print("Registered new user")
    else:
        print("You have already register in bot")


# ============================================= set_langs_all =====================================
def set_langs_all(lang_code: str) -> None:
    # отримуємо від гугла список підтримуваних мов мовою користувача
    lang_dict = get_supported_languages(project_id, lang_code)
    print(lang_dict)

    # Преобразуем словарь в строку
    lang_str = json.dumps(lang_dict)
    print(lang_str)

    # записуємо довідник від гугла у БД
    mycursor = con.cursor()
    # mycursor.execute("Delete from languages")  # обнуляем базу
    # sql = "INSERT OR REPLACE INTO languages (lang_code, lang_name) VALUES (?, ?)"

    # створюємо запис (вставити, або замінити, якщо вже є)
    sql = "INSERT OR REPLACE INTO transl_but (lang_code, lang_dict) VALUES (?, ?)"
    val = (lang_code, lang_str)
    mycursor.execute(sql, val)

    # for key, value in LANGDICT.items():
    #     val = (key, value)
    #     mycursor.execute(sql, val)

    # INSERT OR REPLACE INTO TABLE (NAME, DATE, JOB, HOURS) VALUES ('BOB', '12/01/01', 'PM','30');
    con.commit()


# ====================================================== ALL ==============================
def get_langs_all(lang_code: str) -> dict:
    mycursor = con.cursor()
    # sql = "SELECT lang_code, lang_name FROM languages"
    sql = "SELECT lang_dict FROM transl_but WHERE lang_code = ?"
    val = (lang_code,)
    mycursor.execute(sql, val)

    lang_str = mycursor.fetchone()   # отримуємо кортеж
    print(lang_str[0])

    lang_dict = json.loads(lang_str[0])  # зворотне преобразуванне строка-словарь
    print(lang_dict)

    return lang_dict


# ==================================================== ACTIV ================================
def get_langs_activ(user_id: str, is_active=1) -> list:
    mycursor = con.cursor()
    sql = "SELECT lang_code, interface_lang, src_lang, target_lang FROM users " \
          "WHERE telegram_id = ? and is_active = ?"
    adr = (user_id, is_active)
    mycursor.execute(sql, adr)
    lst = mycursor.fetchall()  # отримуємо список кортежів [('uk', 1, 0, 1), ('en', 0, 1, 0), (sq, 0, 0, 0)]
    return lst


# ====================================================== CALLBACKS ==========SET, Fav, Add ==============
def set_langs_flag(user_id: str, lang_call: str, lang_target='', is_active=1) -> None:
    # lang_call - interface_lang чи src_lang коли lang_target != ''
    # pre - префікс callback-a

    # считуємо з БД список Обраних мов
    lst = get_langs_activ(user_id, is_active=is_active)  # отримуємо список кортежів [('uk', 1, 0, 1), ]
    print(f'Read DB > Interface {lst}')

    mycursor = con.cursor()
    sql = "UPDATE users SET interface_lang = ?, src_lang = ?, target_lang = ?, is_active = ? " \
          "WHERE telegram_id = ? and lang_code = ?"

    # змінюємо список згідно нових обраних мов та записуємо нові дані в БД
    if is_active:
        is_new_add = False  # Тимчасовий прапор "Додати нову мову"?
    else:
        is_new_add = True

    for i in lst:
        if is_active:
            interface_lang = i[1]
            src_lang = i[2]
            target_lang = i[3]
            if lang_target == '':  # зміна мови інтерфейсу
                if i[0] == lang_call:
                    interface_lang = '1'
                else:
                    interface_lang = '0'

                val = (interface_lang, src_lang, target_lang, is_active, user_id, i[0])
                mycursor.execute(sql, val)
                print(f'Interface_lang > DB {i[0]} {interface_lang} {src_lang} {target_lang} {is_active}')

            else:                        # зміна src, target мов
                if i[0] == lang_call:
                    src_lang = '1'
                    target_lang = '0'
                elif i[0] == lang_target:
                    target_lang = '1'
                    src_lang = '0'
                else:
                    target_lang = '0'
                    src_lang = '0'
                val = (interface_lang, src_lang, target_lang, is_active, user_id, i[0])
                mycursor.execute(sql, val)
                print(f'src, target_lang > DB {i[0]} {interface_lang} {src_lang} {target_lang} {is_active}')

        else:
            if i[0] == lang_call:  # зміна на is_active = '1' (підйом мови з видалених в Обрані)
                is_active = '1'
                is_new_add = False  # додавати нову мову не треба
                val = (0, 0, 0, is_active, user_id, i[0])
                mycursor.execute(sql, val)
                print(f'lang_activ_0->1 > DB {i[0]} 0 0 0 {is_active}')
                break
    # якщо мова для додавання не входить в считаний список мов з is_active=0, додати мову в БД
    if is_new_add:
        sql = "INSERT INTO users (telegram_id, lang_code) VALUES (?, ?)"
        val = (user_id, lang_call)
        mycursor.execute(sql, val)
        print(f'Додали мову в Обрані - {lang_call}')
    con.commit()


# ====================================================== CALLBACKS ========== Delete ================
def set_del_lang(user_id: str, lang_del: str) -> None:

    # Встановлюемо флаг is_active = 0 для мови, яку треба видалити
    mycursor = con.cursor()
    sql = "UPDATE users SET is_active = ? WHERE telegram_id = ? and lang_code = ?"
    val = (0, user_id, lang_del)
    mycursor.execute(sql, val)
    con.commit()


# =========================================================== Translate ========================
def get_langs_translate(user_id: str) -> tuple:  # (source_language_code, target_language_code)

    # отримуєм мови з src_lang=1 and target_lang = 1"
    mycursor = con.cursor()
    sql = "SELECT lang_code, src_lang, target_lang " \
          "FROM users " \
          "WHERE telegram_id = ? and " \
          "(src_lang=1 or target_lang=1)"

    adr = (user_id,)
    mycursor.execute(sql, adr)
    result = mycursor.fetchall()  # отримуємо список кортежів [('uk', 0, 1), ('en', 1, 0)]
    # print(f' translate input - {result}')

    source_language_code = ''
    target_language_code = ''
    for r in result:
        if r[1] == 1:
            source_language_code = r[0]
        if r[2] == 1:
            target_language_code = r[0]

    print(f' translate out - {source_language_code} > {target_language_code}')
    return source_language_code, target_language_code


# ================================================ Page ========================
def get_user_page(user_id: str) -> tuple:
    # считуєм стан клавіатури ADD-NEW

    mycursor = con.cursor()
    sql = "SELECT page " \
          "FROM page " \
          "WHERE telegram_id = ? "
    adr = (user_id,)
    mycursor.execute(sql, adr)
    result = mycursor.fetchone()

    print(f' get ADD page = {result}')
    return result


def set_user_page(user_id: str, page: int) -> None:
    # перевіряєм чи існує запис в табл. page
    myresult = get_user_page(user_id)

    # запам'ятовуєм стан клавіатури ADD
    mycursor = con.cursor()
    if myresult is None or myresult == [] or myresult == ():
        sql = "INSERT INTO page (telegram_id, page) VALUES (?, ?)"  # створюємо, якщо даних немає
        val = (user_id, page)
        mycursor.execute(sql, val)
    else:
        sql = "UPDATE page SET page = ? WHERE telegram_id = ?"  # обновлюємо, якщо данні є
        val = (page, user_id)
        mycursor.execute(sql, val)

    con.commit()
    print(f' set ADD page = {page}')


# ======================================================= Cards ===============================
def set_cards(user_id: str, lang_code_src: str, txt_src: str, lang_code_target: str, txt_target: str) -> None:
    mycursor = con.cursor()
    sql = "INSERT INTO cards (telegram_id, lang_code_src, txt_src, lang_code_target, txt_target) " \
          "VALUES (?, ?, ?, ?, ?)"  # створюємо запис
    val = (user_id, lang_code_src, txt_src, lang_code_target, txt_target)
    mycursor.execute(sql, val)
    con.commit()


# ============ Тренування ===================
def get_cards(user_id: str, is_active=1) -> tuple:  # випадкова вибірка 1 пари перекладу
    mycursor = con.cursor()
    sql = '''SELECT lang_code_src, txt_src, lang_code_target, txt_target 
             FROM cards 
             WHERE telegram_id = ? and is_active = ?'''
    val = (user_id, is_active)
    mycursor.execute(sql, val)
    lst = mycursor.fetchall()  # отримуємо список кортежів
    print(lst)
    end = len(lst)
    ran = randint(0, end)

    print(lst[ran], ran)
    return lst[ran]  # ('en', 'suit', 'uk', 'костюм')


if __name__ == '__main__':
    lang_code = 'ru'
    # set_langs_all(lang_code)
    get_cards(1327984097)
