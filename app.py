import json
from flask import Flask, redirect, render_template, request
from userDB import UserModel
from database import DB
from booksDB import BooksModel
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['pdf', 'txt', 'f2b'])
db = DB()

users = UserModel(db.get_connection())
users.init_table()

books = BooksModel(db.get_connection())
books.init_table()
try:
    users.insert('admin', 'admin')
except Exception:
    pass
session = {}
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
curr_user = ''


def get_booklist_of_user(user_id, list_type):
    with open(list_type, 'r') as lst:
        data = json.loads(lst.read())
        return data[str(user_id)]


def remove_book_from_list(book_id, user_id, list_type):
    with open(list_type, 'r') as data:
        lst = json.loads(data.read())
        print(lst)
        with open(list_type, 'w') as datawrite:
            del lst[str(user_id)][lst[str(user_id)].index(book_id)]
            datawrite.write(json.dumps(lst))


def add_user_to_list(book_id, user_id, list_type):
    with open(list_type, 'r') as data:
        lst = json.loads(data.read())

        with open(list_type, 'w') as datawrite:
            lst[str(user_id)] = lst.get(str(user_id), []) + [book_id]
            datawrite.write(json.dumps(lst))


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
    link = request.path
    try:
        if request.method == 'GET':
            wishlist = get_booklist_of_user(session['user_id'], link[1:] + '.json')
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
            password = form.password.data
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
            password = form.password.data
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
                         request.files['file'])

            book_id = books.get_book_id(form.title._value(), form.description._value(), session['user_id'],
                                        request.files['file'])[0]

            add_user_to_list(book_id, session['user_id'], 'readinglist.json')

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
    remove_book_from_list(book_id, session['user_id'], path + '.json')
    return redirect('/' + path)


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
    app.run(port=8080, host='127.0.0.1', debug=True)
