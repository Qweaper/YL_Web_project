class BooksModel:

    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             title VARCHAR(100),
                             description VARCHAR(1000),
                             book_filename VARCHAR (50),
                             user_id INTEGER,
                             author VARCHAR (30),
                             isbn VARCHAR (30) DEFAULT ''
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, author, title, description, user_id, book_filename, isbn=''):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO books 
                          (author, title, description, user_id, book_filename, isbn) 
                          VALUES (?,?,?,?,?,?)''', (author, str(title), str(description), str(user_id),
                                                    str(book_filename), isbn))
        cursor.close()
        self.connection.commit()

    def get(self, book_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (str(book_id)))
        row = cursor.fetchall()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM books WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        return rows

    def get_book_id(self, title, description, user_id, book_filename):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT id FROM books WHERE 
                              title=? AND description=? AND user_id=? AND book_filename=? 
                              ''',
                       (str(title), str(description), str(user_id), str(book_filename)))
        info = cursor.fetchone()
        cursor.close()
        self.connection.commit()
        return info

    def delete(self, book_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM books WHERE id = ?''', (str(book_id)))
        cursor.close()
        self.connection.commit()
