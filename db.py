import sqlite3
from lang_target import get_supported_languages
from settings import project_id


with sqlite3.connect('.venv/bot.sqlite3') as con:  # підключення до БД
    if con:
        print("База даних успішно підключена")

    ''' Опис полів БД
        таблиця users
        telegram_id (INTEGER) - id користувача (беремо з телеграма за командою /start) 
        lang_code (VARCHAR) - код мови, яку додаємо до Вибраних
        interface_lang (BOOL) - мова інтерфейсу, одна з Вибраних
        src_lang (BOOL) - вказує на поточну джерело-мову перекладу (з якою перекладаємо)
        target_lang (BOOL) - вказує на поточну цільову мову перекладу (на яку перекладаємо)
        is_active (BOOL) - видаляє мову з Вибраних, якщо interface_lang=0 і target_lang=0
        
        таблиця languages
        lang_code (VARCHAR) - код мови, яку додаємо до Вибраних (uk)
        lang_name (VARCHAR) - им'я мови, яку додаємо до Вибраних (Ukrainian), це поле заповнюється на мові інтерфейсу
    '''
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER       NOT NULL,
                    lang_code   VARCHAR (255) NOT NULL,
                    interface_lang BOOL       NOT NULL
                                              DEFAULT (0),
                    src_lang BOOL             NOT NULL
                                              DEFAULT (0),                              
                    target_lang BOOL          DEFAULT (0) 
                                              NOT NULL,
                    is_active   BOOL          NOT NULL
                                              DEFAULT (1) 
        )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS languages (
                        lang_code VARCHAR       NOT NULL,
                        lang_name VARCHAR       NOT NULL
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
    LANGDICT = get_supported_languages(project_id, lang_code)

    # записуємо довідник від гугла у БД
    mycursor = con.cursor()
    mycursor.execute("Delete from languages")  # обнуляем базу
    sql = "INSERT INTO languages (lang_code, lang_name) VALUES (?, ?)"

    for key, value in LANGDICT.items():
        val = (key, value)
        mycursor.execute(sql, val)

    con.commit()


# ====================================================== ALL ==============================
def get_langs_all() -> dict:
    mycursor = con.cursor()
    sql = "SELECT lang_code, lang_name FROM languages"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()   # отримуємо список кортежів
    # print(myresult)
    LANGDICT = dict(myresult)
    return LANGDICT


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

# ================================================ Translate CALLBACK ===================
#def set_langs_translate(user_id: str) -> tuple:  # (source_language_code, target_language_code)
