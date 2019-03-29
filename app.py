import hashlib
import json

from flask import Flask, redirect, render_template, request, send_from_directory
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired

from booksDB import BooksModel
from database import DB
from userDB import UserModel

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['pdf', 'txt', 'f2b'])
db = DB()

users = UserModel(db.get_connection())
users.init_table()

books = BooksModel(db.get_connection())
books.init_table()
try:
    users.insert('admin', '21232f297a57a5a743894a0e4a801fc3')
except Exception:
    pass
session = {}
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
curr_user = ''
FILE_DIR = 'books_files'


def get_booklist_of_user(user_id, list_type):
    with open(list_type, 'r') as lst:
        data = json.loads(lst.read())
        return set(data[str(user_id)])


def remove_book_from_list(book_id, user_id, list_type):
    with open(list_type, 'r') as data:
        lst = json.loads(data.read())
        print(lst)
        with open(list_type, 'w') as datawrite:
            del lst[str(user_id)][lst[str(user_id)].index(book_id)]
            datawrite.write(json.dumps(lst))


def add_book_to_list(book_id, user_id, list_type):
    with open(list_type, 'r') as data:
        lst = json.loads(data.read())
        with open(list_type, 'w') as datawrite:
            if book_id not in lst[str(user_id)]:
                lst[str(user_id)] = lst.get(str(user_id), []) + [book_id]
                datawrite.write(json.dumps(lst))


def check_book_list(user_id, book_id):
    words = {'wishlist': 'желаний', 'readinglist': 'читаемого', 'hreadlist': 'прочитанного'}
    for i in ['wishlist', 'readinglist', 'hreadlist']:
        with open(i + '.json', 'r') as file:
            data = json.loads(file.read())
            if book_id in data[str(user_id)]:
                return words[i]
    return False


class AddNewBook(FlaskForm):
    author = StringField('Автор', validators=[DataRequired()])
    title = StringField('Название книги', validators=[DataRequired()])
    description = TextAreaField('Описание книги', validators=[DataRequired()])
    file = FileField('Добавить книгу', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    rememberme = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignInForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


@app.route('/')
@app.route('/index')
@app.route('/main')
def index():
    if 'username' not in session:
        return redirect('/login')
    mod = 0
    if session['username'] == 'admin':
        mod = 1
    try:
        wishlist = get_booklist_of_user(session['user_id'], 'wishlist.json')
    except Exception:
        wishlist = []
    try:
        readinglist = get_booklist_of_user(session['user_id'], 'readinglist.json')
    except Exception:
        readinglist = []
    try:
        hreadlist = get_booklist_of_user(session['user_id'], 'hreadlist.json')
    except Exception:
        hreadlist = []
    return render_template('main_page.html', mod=mod, username=session['username'],
                           num_of_wishes=len(wishlist), num_of_reading=len(readinglist), num_of_hread=len(hreadlist))


@app.route('/success')
def success():
    return '''success'''


@app.route('/error')
def error():
    return '''error'''


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/wishlist', methods=['POST', 'GET'])
@app.route('/readinglist', methods=['POST', 'GET'])
@app.route('/hreadlist', methods=['POST', 'GET'])
def lists():
    if 'username' not in session:
        return redirect('/login')
    link = request.path[1:]
    try:
        if request.method == 'GET':
            wishlist = get_booklist_of_user(session['user_id'], link + '.json')
            for i in wishlist:
                book_info = books.get(i)
            return render_template('wishlist.html', username=session['username'], booklist=book_info, path=link)
    except Exception:
        return render_template('wishlist.html', booklist=-1, username=session['username'])
    if request.method == 'POST':
        pass


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    try:
        form = SignInForm()
        if request.method == 'GET':
            return render_template('sign_in.html', form=form)
        if request.method == 'POST':
            user_name = form.username.data
            hash_of_passw = hashlib.md5(form.password.data.encode('utf-8'))
            password = hash_of_passw.hexdigest()
            print(password)
            users.insert(user_name, password)
            return redirect('/login')
    except ValueError:
        return redirect('/error')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', title='Авторизация', form=form)
    if request.method == 'POST':
        try:
            user_name = form.username.data
            hash_of_passw = hashlib.md5(form.password.data.encode('utf-8'))
            password = hash_of_passw.hexdigest()
            print(password)
            user_model = UserModel(db.get_connection())
            exists = user_model.exists(user_name, password)
            if exists[0]:
                session['username'] = user_name
                session['user_id'] = exists[1]

            return redirect("/index")
        except ValueError:
            return redirect('/error')


@app.route('/download_file', methods=['POST', 'GET'])
def sample_file_upload():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewBook()
    if request.method == 'GET':
        return render_template('download_file.html', form=form, username=session['username'])
    elif request.method == 'POST':
        # try:
        f = request.files['file']

        if f.filename[f.filename.index('.') in ALLOWED_EXTENSIONS]:
            books.insert(form.author._value(), form.title._value(), form.description._value(), session['user_id'],
                         request.files['file'].filename)

        book_id = books.get_book_id(form.title._value(), form.description._value(), session['user_id'],
                                    request.files['file'].filename)[0]

        add_book_to_list(book_id, session['user_id'], 'readinglist.json')

        users.increase_num_of_books(session['user_id'])

        with open('books_files/' + f.filename, 'wb') as file:
            data = f.read()
            file.write(data)

        return redirect('/')
    else:
        return '''Wrong extension of the file'''
# except Exception:
#     return redirect('/error')


@app.route('/delete/<string:path>/<int:book_id>')
def delete(path, book_id):
    print(path)
    remove_book_from_list(book_id, session['user_id'], path + '.json')
    return redirect('/' + path)


# добавить функцию, говорящую о расположение книги в списке
@app.route('/library')
def library():
    booklist = books.get_all()
    # exceptions = books.get_all(session['user_id'])
    for i in booklist:
        lst = [list(i) + [check_book_list(session['user_id'], i[0])]]
    return render_template('library.html', username=session['username'], booklist=lst)


@app.route('/add_to_hread/<int:book_id>')
@app.route('/add_to_reading/<int:book_id>')
@app.route('/add_to_wishes/<int:book_id>')
def add_book(book_id):
    path = request.path[8:-2]
    print(path)
    add_book_to_list(book_id, session['user_id'], path + 'list.json')
    return redirect('/library')


@app.route('/change/<string:frm>/<string:to>/<int:book_id>')
def change_book_location(book_id, frm, to):
    add_book_to_list(book_id, session['user_id'], to + '.json')
    remove_book_from_list(book_id, session['user_id'], frm + '.json')
    return redirect('/' + frm)


@app.route('/download/<int:book_id>')
def download(book_id):
    filename = books.get(book_id)[0][-3]
    return send_from_directory(FILE_DIR, filename)


@app.route('/users_log')
def users_log():
    if 'username' not in session:
        return redirect('/login')
    user_list = [i[1] for i in users.get_users()]
    logs = {}
    for user in list(set(user_list)):
        us = users.get_id(user)[1]
        logs[user] = len(books.get_all(us))
        users.get(session['user_id'])
    return render_template('user_logs.html', logs=logs, user_list=user_list, username='admin')


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
    # 0.0.0.0 можно будет смотреть через разные устройства
