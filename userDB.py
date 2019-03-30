import hashlib


class UserModel:

    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128),
                             book_num INTEGER,
                             admin INTEGER DEFAULT 0,
                             view_name VARCHAR(50),
                             mail VARCHAR (50)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash, view_name, mail):
        if self.exists(user_name, password_hash)[0]:
            raise ValueError
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, book_num, view_name, mail) 
                          VALUES (?,?,?,?,?)''', (user_name, password_hash, '0', view_name, mail))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def get_users(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        list = cursor.fetchall()
        return list

    def get_id(self, user_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?",
                       (user_name,))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def get_info(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT * FROM users WHERE id = ?''', (user_id,))
        info = cursor.fetchall()
        return info

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM users WHERE id = ?''', (str(news_id)))
        cursor.close()
        self.connection.commit()

    def exists_by_id(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?",
                       (user_id,))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def edit_email(self, user_id, new_email):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE users SET mail = (?) WHERE id = ?''', (new_email, str(user_id)))

        cursor.close()
        self.connection.commit()

    def edit_view_name(self, user_id, view_name):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE users SET view_name=(?) WHERE id = ?''', (view_name, str(user_id)))

        cursor.close()
        self.connection.commit()

    def edit_password(self, user_id, password):
        cursor = self.connection.cursor()
        hash_of_passw = hashlib.md5(password.encode('utf-8'))
        password = hash_of_passw.hexdigest()
        cursor.execute('''UPDATE users SET password_hash=(?) WHERE id = ?''', (password, str(user_id)))

        cursor.close()
        self.connection.commit()

    def set_user_status(self, login, status):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE users SET admin = (?) WHERE user_name = ?''', (status, login))
        cursor.close()
        self.connection.commit()

    def increase_num_of_books(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT book_num FROM users WHERE id = ?''', (user_id,))
        number = cursor.fetchone()[0]
        cursor.execute('''UPDATE users SET book_num=(?) WHERE id = ?''', (number + 1, user_id))
        cursor.close()
        self.connection.commit()
