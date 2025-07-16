from flask import g
import psycopg2
from psycopg2 import sql, extras, Binary
from psycopg2.extras import DictCursor
import time
from flask import flash


def datetime():
    sec = time.time()
    struct = time.localtime(sec)
    res = time.strftime('%Y-%m-%d %H:%M:%S', struct)
    return res

def connect_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            dbname='messenger',
            user='postgres',
            password='565441', 
            host='localhost'
            )
    return g.db


def init_db():
    with connect_db() as conn, conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(80) NOT NULL,
                    last_name VARCHAR(80) NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    date_of_birth DATE,
                    gender VARCHAR(8),
                    password_hash VARCHAR(300)
                )
            """)
        
    with connect_db() as conn, conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS menu (
                    title VARCHAR(80) NOT NULL,
                    url VARCHAR(80) NOT NULL
                )
            """)

        conn.commit()


class UseDB:
    def __init__(self, data_base_conn):
        self.conn = data_base_conn


    def create_user(self, first_name, last_name, position, email, date_of_birth, gender, password_hash):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""INSERT INTO users (first_name, last_name, position, email, date_of_birth, gender, password_hash) values (%s, %s, %s, %s, %s, %s, %s)""",  (first_name, last_name, position, email, date_of_birth, gender, password_hash))
            self.conn.commit()
            print('Пользователь добавлен в БД')
            return True
        except Exception as e:
            print('Ошибка добавления пользователя в БД ' + str(e))
            return False

    def get_user_by_email(self, email):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM users WHERE email = %s AND deleted = 'false' """, (email,))
                user = cur.fetchone()
                if user:
                    return dict(user) 
                else: 
                    flash('Пользователя с таким email нет в БД', category='error')
                    print('Пользователя с таким email нет в БД')

        except Exception as e:
            print('Ошибка получения данных пользователя по email в БД ' + str(e))
            flash('Ошибка получения данных пользователя по email в БД', category='error')

    def get_user_by_id(self, id):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM users WHERE id = '{id}' """)
                print('Пользователь получен по id из БД')
                return dict(cur.fetchone()) 
        except Exception as e:
            print('Ошибка получения данных пользователя по id в БД ' + str(e))

    def get_all_users(self):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM users WHERE deleted = 'false' """)
                print('Все пользователи получены из БД')
                return cur.fetchall()
        except Exception as e:
            print('Ошибка получения данных всех пользователей из БД ' + str(e))

    def get_menu(self):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM menu""")
                return cur.fetchall()
        except Exception as e:
            print('Ошибка получения меню в БД ' + str(e))


    def upload_user_avatar(self, id, img):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                imgb = Binary(img)
                cur.execute(f"""UPDATE users set avatar = (%s) WHERE id = (%s) """, (imgb, id))
                self.conn.commit()
                print('Новый аватар загружен в БД')
        except Exception as e:
            print('Ошибка при загрузке аватара в БД ' + str(e))

    def load_user_avatar(self, id):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT avatar FROM users WHERE id = (%s) """, (id,))
                print('аватар загружен из БД')
                return cur.fetchone()[0]
        except Exception as e:
            print('Ошибка при загрузке аватара из БД ' + str(e))

    def send_message_to_user(self, id_sender, id_recipient, message):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""INSERT INTO messages (id_sender, id_recipient, datetime, message) values (%s, %s, %s, %s)""",  (id_sender, id_recipient, datetime(), message))
                print('Сообщение отправлено в БД')
                self.conn.commit()
                self.add_chat(id_sender, id_recipient)
                self.add_chat(id_recipient, id_sender)
                
        except Exception as e:
            print('Ошибка отправления сообщения в БД ' + str(e))

    def get_chat_messages(self, id_user1, id_user2):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT first_name, last_name, datetime, message FROM (SELECT id_sender, datetime, message FROM messages
WHERE id_sender::integer = {id_user1}::integer and id_recipient::integer = {id_user2}::integer or id_sender::integer = {id_user2}::integer and id_recipient::integer = {id_user1}::integer)
JOIN users ON id_sender::integer = users.id::integer; """)
                print('Сообщения пользователей получены из БД')
                return cur.fetchall()
            
        except Exception as e:
            print('Ошибка получения сообщений пользователей из БД ' + str(e))

    def add_chat(self, id_user, id_companion):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""INSERT INTO users_chats (id_user, id_companion) values (%s, %s)""",  (id_user, id_companion))
                print('Чат добавлен пользователю в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка добавления чата пользователю в БД ' + str(e))


    def delete_chat(self, id_user, id_companion):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""DELETE FROM users_chats WHERE id_user::INTEGER = %s::INTEGER AND id_companion::INTEGER = %s::INTEGER""",  (id_user, id_companion))
                print('Чат удален из БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка удаления чата из БД ' + str(e))

    def get_users_by_chats(self, id_user):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM users WHERE id::integer in (SELECT id_companion::integer FROM users_chats WHERE id_user::integer = {id_user});""")
                print('Пользователи из чатов пользователя получены из БД')
                return cur.fetchall()
            
        except Exception as e:
            print('Ошибка получения пользователей из чатов пользователя из БД ' + str(e))

    def get_all_departments(self):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM departments """)
                print('Все отделы получены из БД')
                return cur.fetchall()
        except Exception as e:
            print('Ошибка получения все отделов из БД ' + str(e))

    
    def get_department(self, id):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM departments WHERE id = %s""", (id,))
                print('Отдел получен из БД')
                return cur.fetchone()
        except Exception as e:
            print('Ошибка получения отдела из БД ' + str(e))


    def load_department_logo(self, id):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT logo FROM departments WHERE id = (%s) """, (id,))
                print('логотип загружен из БД')
                return cur.fetchone()[0]
        except Exception as e:
            print('Ошибка при загрузке аватара из БД ' + str(e))


    def create_department(self, title, describtion, logo, id_owner):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""INSERT INTO departments (title, describtion, logo, owners) values (%s, %s, %s, %s)""",  (title, describtion, logo, [id_owner, ]))
                print('Отдел добавлен в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка добавления отдела в БД ' + str(e))

    def delete_department(self, id_department):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""UPDATE departments SET deleted = 'true' WHERE id = %s """,  (id_department,))
                print('Отдел удален в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка удаления отдела в БД ' + str(e))


    def get_departments_by_owner(self, id_owner):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM departments WHERE {id_owner} = ANY(owners) """)
                print('Отделы получены из БД')
                return cur.fetchall()
        except Exception as e:
            print('Ошибка получения отдела из БД ' + str(e))

    def add_user_to_department (self, id_user, id_department):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""UPDATE departments SET members = array_append(members, %s) WHERE id = %s AND NOT (%s = ANY(members))""",  (id_user, id_department, id_user))
                print('Пользователь добавлен в отдел в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка добавления пользователя в отдел в БД ' + str(e))

    def get_department_messages(self, id_department):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT first_name, last_name, datetime, message FROM department_messages 
                                JOIN users ON id_sender::integer = users.id::integer
                                WHERE id_department = {id_department};""")
                print('Сообщения отдела получены из БД')
                return cur.fetchall()
            
        except Exception as e:
            print('Ошибка получения сообщений отдела из БД ' + str(e))


    
    def send_message_to_department_chat(self, id_sender, id_department, message):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""INSERT INTO department_messages (id_sender, id_department, datetime, message) values (%s, %s, %s, %s)""",  (id_sender, id_department, datetime(), message))
                print('Сообщение отдела отправлено в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка отправления сообщения отдела в БД ' + str(e))



    
    def get_departments_by_user(self, id_user):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""SELECT * FROM departments WHERE {id_user} = ANY(owners) or {id_user} = ANY(members) """)
                print('Отделы пользователя получены из БД')
                return cur.fetchall()
        except Exception as e:
            print('Ошибка пользователя получения отдела из БД ' + str(e))


    def change_user_data(self, id, first_name, last_name, position, email, date_of_birth, gender, user_class, password_hash):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""UPDATE users SET first_name = %s, last_name = %s, position = %s, email = %s, date_of_birth = %s, gender = %s, class = %s, password_hash = %s WHERE id = %s""",  (first_name, last_name, position, email, date_of_birth, gender, user_class, password_hash, id))
            self.conn.commit()
            print('Данные пользователя обновлены в БД')
        except Exception as e:
            print('Ошибка обновления данных пользователя в БД ' + str(e))

    def change_department_data(self, title, describtion, logo, id_department):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""UPDATE departments SET title = %s, describtion = %s, logo = %s WHERE id = %s""",  (title, describtion, logo, id_department))
                print('Отдел обновлен в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка обновления отдела в БД ' + str(e))

    def delete_user_from_department(self, id_user, id_department):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""UPDATE departments SET members = array_remove(members, %s) WHERE id = %s""",  (id_user, id_department))
                cur.execute(f"""UPDATE departments SET owners = array_remove(owners, %s) WHERE id = %s""",  (id_user, id_department))
                print('Пользователь удален из отдела в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка удаления пользователя из отдела в БД ' + str(e))


    def make_owner(self, id_user, id_department):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""UPDATE departments SET owners = array_append(owners, %s) WHERE id = %s AND NOT (%s = ANY(owners))""",  (id_user, id_department, id_user))
                print('Пользователь наделен правами руководителя отдела в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка наделения пользователя правами руководителя в БД ' + str(e))

    def lose_owner(self, id_user, id_department):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(f"""UPDATE departments SET owners = array_remove(owners, %s) WHERE id = %s""",  (id_user, id_department))
                print('Пользователь лишен прав руководителя в БД')
                self.conn.commit()
        except Exception as e:
            print('Ошибка лишения пользователя прав руководителя в БД ' + str(e))





if __name__ == '__main__':
    print(datetime())



