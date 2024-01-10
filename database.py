import sqlite3
import pickle

db = sqlite3.connect("test.db")
cursor = db.cursor()

table = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER UNSIGNED,
    text BLOB
)
"""

cursor.execute(table)
db.commit()


def insert_user(tg_id):
    sql = """INSERT INTO users (tg_id, text) VALUES (?, ?)"""
    cursor.execute(sql, (tg_id, pickle.dumps([])))
    db.commit()


def get_text(tg_id):
    sql = "SELECT text FROM users where tg_id = ?"
    result = cursor.execute(sql, (tg_id, )).fetchone()[0]
    return pickle.loads(result)


def update_invite_status(tg_id, link):
    user_text = get_text(tg_id)
    for text in user_text:
        tlink = text["tlink"]
        array_index = user_text.index(text)
        if link == tlink:
            text["invite_status"] = 1
            user_text[array_index] = text
            sql = "UPDATE users SET text = ? WHERE tg_id = ?"
            cursor.execute(sql, (pickle.dumps(user_text), tg_id))
            db.commit()

def update_text(tg_id, text, priority, tlink):
    user_text = get_text(tg_id)
    json_object = {
        "text": text,
        "priority": priority,
        "tlink": tlink,
        "invite_status": 0
    }
    user_text.append(json_object)
    sql = "UPDATE users SET text = ? WHERE tg_id = ?"
    cursor.execute(sql, (pickle.dumps(user_text), tg_id))
    db.commit()


def delete_text(tg_id, text):
    user_text = get_text(tg_id)
    new_user_text = [item for item in user_text if item["text"] != text]
    sql = "update users set text = ? where tg_id = ?"
    cursor.execute(sql, (pickle.dumps(new_user_text), tg_id))
    db.commit()


def add_text(tg_id, text):
    sql = "INSERT INTO users (tg_id, text) VALUES (?, ?)"
    cursor.execute(sql, (tg_id, text))
    db.commit()


def get_user_by_tg_id(tg_id):
    sql = "SELECT * FROM users WHERE tg_id = ?"
    result = cursor.execute(sql, (tg_id, )).fetchone()
    return result

def get_user_ids():
    sql = "SELECT tg_id FROM users"
    result = cursor.execute(sql).fetchall()
    return result

def priority(tg_id, word):
    sql = "select priority from users WHERE tg_id = ? and text = ?"
    result = cursor.execute(sql, (tg_id, word)).fetchone()[0]
    return result


def update_priority(tg_id, text):
    sql = "UPDATE users set priority = 1 WHERE tg_id = ? and text = ?"
    cursor.execute(sql, (tg_id, text))
    db.commit()
