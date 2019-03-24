class UserModel:

    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        if self.exists(user_name, password_hash)[0]:
            raise ValueError
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
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

    def edit(self, user_id, password):
        cursor = self.connection.cursor()

        cursor.execute('''UPDATE users SET password_hash=(?) WHERE id = ?''', (password, str(user_id)))

        cursor.close()
        self.connection.commit()
