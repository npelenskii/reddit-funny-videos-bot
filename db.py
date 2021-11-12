import sqlite3

conn = sqlite3.connect('users.db')

cur = conn.cursor()

def user_add(user_chat_id, video_type):
        
    cur.execute("INSERT INTO users VALUES(?, ?);", (user_chat_id, video_type))
    print('Complete')
    conn.commit()

def remove_category(chat_id, video_type_sel):

    cur.execute(f"DELETE FROM users WHERE chat_id ='{chat_id}' AND video_type ='{video_type_sel}'")
    conn.commit()