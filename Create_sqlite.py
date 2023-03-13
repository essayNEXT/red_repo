import sqlite3

# створення файлу БД SQLite та таблиці в ній
con = sqlite3.connect('.venv/bot.sqlite3')
cur = con.cursor()

cur.execute('''CREATE TABLE users (
    telegram_id INTEGER       NOT NULL,
    lang_code   VARCHAR (255) NOT NULL,
    interface_lang BOOL       NOT NULL
                              DEFAULT (0),
    target_lang BOOL          DEFAULT (0) 
                              NOT NULL,
    is_active   BOOL          NOT NULL
                              DEFAULT (1) 
)''')
