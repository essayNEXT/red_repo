import psycopg2

def insert_translation(word, translated_word, table_name):

    conn = psycopg2.connect(database="db_name", user="username", password="password", host="host", port="port")
    cur = conn.cursor()
    sql = f"INSERT INTO {table_name} (word, translation) VALUES ('{word}', '{translated_word}')"
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
