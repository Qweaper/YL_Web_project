import hashlib
import json
import os

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
    users.insert('admin', '21232f297a57a5a743894a0e4a801fc3', 'ADMIN', 'Admin@mail.ru')
    users.set_user_status('admin', True)
except Exception as e:
    print(e)
session = {}
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
curr_user = ''
FILE_DIR = 'books_files'
if not os.path.exists('books_files'):
    os.mkdir(os.getcwd() + '/' + 'books_files')


def get_booklist_of_user(user_id, list_type):
    with open(list_type, 'r') as lst:
        data = json.loads(lst.read())
        return set(data[str(user_id)])


def remove_book_from_list(book_id, user_id, list_type):
    with open(list_type, 'r') as data:
        lst = json.loads(data.read())
        with open(list_type, 'w') as datawrite:
            del lst[str(user_id)][lst[str(user_id)].index(book_id)]
            datawrite.write(json.dumps(lst))


def add_book_to_list(book_id, user_id, list_type):
    with open(list_type, 'r') as data:
        lst = json.loads(data.read())
        with open(list_type, 'w') as datawrite:
            try:
                lst[str(user_id)] = lst.get(str(user_id), []) + [book_id]
            except:
                new_list = {}
                new_list[str(user_id)] = new_list.get(str(user_id), []) + [book_id]
            datawrite.write(json.dumps(lst))


def check_book_list(user_id, book_id):
    words = {'wishlist': 'желаний', 'readinglist': 'читаемого', 'hreadlist': 'прочитанного'}
    for i in ['wishlist', 'readinglist', 'hreadlist']:
        with open(i + '.json', 'r') as file:
            data = json.loads(file.read())
            if str(user_id) in data.keys():
                if book_id in data[str(user_id)]:
                    return words[i]
    return False


class AddNewBook(FlaskForm):
    author = StringField('Автор', validators=[DataRequired()])
    title = StringField('Название книги', validators=[DataRequired()])
    description = TextAreaField('Описание книги', validators=[DataRequired()])
    isbn = StringField('ISBN (при наличии)')
    file = FileField('Добавить книгу', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    rememberme = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignInForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    view_name = StringField('Отоброжаемое имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = StringField('Mail', validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


class UpdateInfo(FlaskForm):
    username = PasswordField('Новый пароль')
    view_name = StringField('Отоброжаемое имя')
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = StringField('Mail')
    submit = SubmitField('Обновить')


@app.route('/')
@app.route('/index')
@app.route('/main')
def index():
    if 'username' not in session:
        return redirect('/login')
    mod = users.get(session['user_id'])[-3]
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
    username = users.get(session['user_id'])
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
            book_info = []
            wishlist = get_booklist_of_user(session['user_id'], link + '.json')
            for i in wishlist:
                book_info.append(books.get(i)[0])
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
            view_name = form.view_name.data
            mail = form.email.data
            hash_of_passw = hashlib.md5(form.password.data.encode('utf-8'))
            password = hash_of_passw.hexdigest()
            users.insert(user_name, password, view_name, mail)
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
            user_model = UserModel(db.get_connection())
            exists = user_model.exists(user_name, password)
            if exists[0]:
                session['username'] = users.get(exists[1])[-2]
                session['user_id'] = exists[1]
                session['login'] = user_name
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
        f = request.files['file']

        if f.filename[f.filename.index('.') in ALLOWED_EXTENSIONS]:
            books.insert(form.author._value(), form.title._value(), form.description._value(), session['user_id'],
                         request.files['file'].filename, form.isbn.data)

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


@app.route('/delete/<string:path>/<int:book_id>')
def delete(path, book_id):
    if 'username' not in session:
        return redirect('/login')
    remove_book_from_list(book_id, session['user_id'], path + '.json')
    return redirect('/' + path)


@app.route('/library')
def library():
    if 'username' not in session:
        return redirect('/login')
    lst = []
    booklist = books.get_all()
    for i in booklist:
        lst.append(list(i) + [check_book_list(session['user_id'], i[0])])
    return render_template('library.html', username=session['username'], booklist=lst)


@app.route('/add_to_hread/<int:book_id>')
@app.route('/add_to_reading/<int:book_id>')
@app.route('/add_to_wish/<int:book_id>')
def add_book(book_id):
    if 'username' not in session:
        return redirect('/login')
    path = request.path[8:-2]
    add_book_to_list(book_id, session['user_id'], path + 'list.json')
    return redirect('/library')


@app.route('/change/<string:frm>/<string:to>/<int:book_id>')
def change_book_location(book_id, frm, to):
    if 'username' not in session:
        return redirect('/login')
    add_book_to_list(book_id, session['user_id'], to + '.json')
    remove_book_from_list(book_id, session['user_id'], frm + '.json')
    return redirect('/' + frm)


@app.route('/change_user_status/<string:login>/<int:status>')
def stats(login, status):
    if 'username' not in session:
        return redirect('/login')
    users.set_user_status(login, status)
    return redirect('/users_log')


@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/login')
    user = users.get(session['user_id'])
    return render_template('profile.html', user=user, username=session['username'])


@app.route('/download/<int:book_id>')
def download(book_id):
    if 'username' not in session:
        return redirect('/login')
    filename = books.get(book_id)[0][-4]
    return send_from_directory(FILE_DIR, filename)


@app.route('/update_info', methods=['GET', 'POST'])
def update():
    if 'username' not in session:
        return redirect('/login')
    form = UpdateInfo()
    if request.method == 'GET':
        return render_template('update.html', form=form)
    if request.method == 'POST':
        new_view_name = form.view_name.data
        mail = form.email.data
        old_pass = form.username.data
        new_pass = form.password.data
        exists = users.exists(session['login'], hashlib.md5(old_pass.encode('utf-8')).hexdigest())[0]
        if exists:
            if new_pass != '':
                users.edit_password(session['user_id'], new_pass)
            if new_pass != '':
                users.edit_view_name(session['user_id'], new_view_name)
            if new_pass != '':
                users.edit_email(session['user_id'], mail)
            session['username'] = new_view_name
            return redirect('/')
        else:
            return redirect('/error')


@app.route('/users_log')
def users_log():
    if 'username' not in session:
        return redirect('/login')
    if users.get(session['user_id'])[-3] != True:
        return 'Доступ запрещён'
    user_list = [[i[-2], i[-3], i[1]] for i in users.get_users()]
    logs = {}
    for user in user_list:
        us = users.get_id(user[-1])[1]
        logs[user[0]] = len(books.get_all(us))
    return render_template('user_logs.html', logs=logs, user_list=user_list, username=session['username'])


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
    # 0.0.0.0 можно будет смотреть через разные устройства
